"""Нормализация и проверка метаданных PE-файлов (.exe/.dll), которые выдают
момент и машину сборки.

  python tools/scrub_pe.py --verify  dist/ProxyPulse/ProxyPulse.exe
  python tools/scrub_pe.py --clean   dist/ProxyPulse/ProxyPulse.exe
  python tools/scrub_pe.py --selftest

Что нормализуем (раздел 6-7 методички):
  * FILE_HEADER.TimeDateStamp — момент компоновки с точностью до секунды;
  * TimeDateStamp в каталогах DEBUG и EXPORT и у корня ресурсов;
  * абсолютный путь к .pdb в CodeView-записи (логин + структура каталогов) —
    урезаем до имени файла;
  * пересчитываем PE-checksum, иначе антивирус заметит несходство.

Чего НЕ трогаем сознательно:
  * Rich header (раздел 8): правка заголовка у НЕподписанного exe провоцирует
    SmartScreen сильнее, чем сам отпечаток. Детектор его показывает, но не валит.
  * Чужие вендорские .dll/.pyd (Python, Qt, OpenSSL): их таймстемпы одинаковы у
    всех и их правка бессмысленна и рискованна (раздел 5, правило 5). Передавай
    сюда только СВОЙ ProxyPulse.exe и setup.exe.

Единый источник времени — 1980-01-01 UTC (0x12cea600 = 315532800): эпоха ZIP,
совпадает с датами членов base_library.zip у PyInstaller, рассинхрона не вносит.
"""
import os
import sys

import pefile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

EPOCH = 315532800          # 1980-01-01T00:00:00Z


def _debug_entries(pe):
    return list(getattr(pe, 'DIRECTORY_ENTRY_DEBUG', []) or [])


def _pdb_path(pe):
    """Абсолютный путь к .pdb из CodeView-записи, если он есть."""
    for d in _debug_entries(pe):
        name = getattr(getattr(d, 'entry', None), 'PdbFileName', b'')
        if name:
            s = name.split(b'\x00', 1)[0].decode('latin-1', 'replace')
            if s:
                return s
    return ''


def _strip_pdb_path(data, pe):
    """Заменяет абсолютный путь к .pdb на одно имя файла прямо в байтах.
    Длину записи сохраняем (добиваем нулями) — смещения не едут."""
    changed = False
    for d in _debug_entries(pe):
        entry = getattr(d, 'entry', None)
        name = getattr(entry, 'PdbFileName', b'') if entry else b''
        if not name:
            continue
        raw = name.split(b'\x00', 1)[0]
        if b'\\' not in raw and b'/' not in raw:
            continue                                    # уже чистое имя
        base = raw.replace(b'/', b'\\').split(b'\\')[-1]
        # CodeView RSDS: Signature(4)+GUID(16)+Age(4)=24, дальше путь.
        off = d.struct.PointerToRawData + 24
        total = len(raw)
        if data[off:off + total] == raw:
            data[off:off + total] = base + b'\x00' * (total - len(base))
            changed = True
    return changed


def normalize(path):
    """Правит файл на месте. Возвращает True, если что-то изменилось."""
    pe = pefile.PE(data=open(path, "rb").read(), fast_load=False)       # в память, не mmap: безопасно писать
    data = bytearray(pe.__data__)
    changed = False

    def setts(obj, field):
        nonlocal changed
        if getattr(obj, field) != EPOCH:
            setattr(obj, field, EPOCH)
            changed = True

    setts(pe.FILE_HEADER, 'TimeDateStamp')
    for d in _debug_entries(pe):
        setts(d.struct, 'TimeDateStamp')
    exp = getattr(pe, 'DIRECTORY_ENTRY_EXPORT', None)
    if exp is not None:
        setts(exp.struct, 'TimeDateStamp')
    res = getattr(pe, 'DIRECTORY_ENTRY_RESOURCE', None)
    if res is not None and hasattr(res, 'struct'):
        setts(res.struct, 'TimeDateStamp')

    pe.__data__ = bytes(data) if isinstance(data, bytearray) else data
    # Сначала применяем структурные правки pefile, затем правим сырые байты пути.
    buf = bytearray(pe.write())
    pe2 = pefile.PE(data=bytes(buf), fast_load=False)
    if _strip_pdb_path(buf, pe2):
        changed = True
    # Пересчёт контрольной суммы по финальным байтам.
    pe3 = pefile.PE(data=bytes(buf), fast_load=False)
    newsum = pe3.generate_checksum()
    if pe3.OPTIONAL_HEADER.CheckSum != newsum:
        pe3.OPTIONAL_HEADER.CheckSum = newsum
        changed = True
    final = pe3.write()
    pe.close(); pe2.close(); pe3.close()
    if changed:
        with open(path, 'wb') as fh:
            fh.write(final)
    return changed


def problems(path):
    """Список оставшихся следов в файле (для --verify)."""
    pe = pefile.PE(data=open(path, "rb").read(), fast_load=False)
    out = []
    if pe.FILE_HEADER.TimeDateStamp not in (0, EPOCH):
        out.append('FILE_HEADER.TimeDateStamp=0x%x (момент сборки)'
                   % pe.FILE_HEADER.TimeDateStamp)
    for d in _debug_entries(pe):
        if d.struct.TimeDateStamp not in (0, EPOCH):
            out.append('DEBUG.TimeDateStamp=0x%x' % d.struct.TimeDateStamp)
    pdb = _pdb_path(pe)
    if pdb and ('\\' in pdb or '/' in pdb):
        out.append('PDB-путь: %s' % pdb)
    # Rich header — только сообщаем, не валим (раздел 8).
    try:
        rich = pe.parse_rich_header()
    except Exception:
        rich = None
    pe.close()
    return out, bool(rich)


def run_verify(paths):
    ok = True
    for p in paths:
        if not os.path.exists(p):
            print('  НЕТ ФАЙЛА: %s' % p); ok = False; continue
        probs, rich = problems(p)
        tag = 'rich-header присутствует (оставлен сознательно)' if rich else 'rich-header нет'
        if probs:
            ok = False
            print('  %s:' % p)
            for pr in probs:
                print('    - %s' % pr)
            print('    (%s)' % tag)
        else:
            print('  %s: таймстемпы и PDB-путь чисты; %s' % (p, tag))
    if ok:
        print('PE SCRUB OK')
    return ok


def run_clean(paths):
    for p in paths:
        if not os.path.exists(p):
            print('  НЕТ ФАЙЛА: %s' % p); continue
        ch = normalize(p)
        print('  %s: %s' % (p, 'нормализован' if ch else 'уже чист'))
    return True


def _find_sample_pe():
    """Любой обычный копируемый PE для негативного контроля. sys.executable не
    годится: у Python из Microsoft Store это reparse-заглушка, которую нельзя
    скопировать. Берём .pyd/.dll из site-packages — они есть у зависимостей."""
    import glob
    import site
    roots = []
    try:
        roots += site.getsitepackages()
    except Exception:
        pass
    try:
        roots.append(site.getusersitepackages())
    except Exception:
        pass
    roots.append(os.path.dirname(pefile.__file__))
    for root in roots:
        for pat in ('*.pyd', '*.dll'):
            for cand in glob.glob(os.path.join(root, '**', pat), recursive=True):
                try:
                    p = pefile.PE(cand, fast_load=True); p.close()
                    return cand
                except Exception:
                    continue
    return None


def run_selftest():
    """Негативный контроль на копии настоящего PE: грязный таймстемп обязан
    ловиться, нормализация обязана быть идемпотентной."""
    import shutil
    import tempfile
    src = _find_sample_pe()
    if not src:
        print('  НЕГАТИВНЫЙ КОНТРОЛЬ НЕ ВЫПОЛНЕН: не найден образец PE')
        return False
    tmp = os.path.join(tempfile.gettempdir(), 'scrub_pe_selftest.exe')
    shutil.copy2(src, tmp)
    fails = []
    try:
        # Пачкаем: ставим заведомо «свежий» таймстемп.
        pe = pefile.PE(data=open(tmp, "rb").read(), fast_load=False)
        pe.FILE_HEADER.TimeDateStamp = 0x66000000
        open(tmp, 'wb').write(pe.write()); pe.close()
        probs, _ = problems(tmp)
        if not any('FILE_HEADER' in x for x in probs):
            fails.append('детектор не поймал свежий таймстемп')
        # Чистим и проверяем.
        normalize(tmp)
        probs2, _ = problems(tmp)
        if any('TimeDateStamp' in x for x in probs2):
            fails.append('после нормализации таймстемп остался грязным')
        # Идемпотентность: повторный прогон ничего не меняет.
        if normalize(tmp):
            fails.append('повторная нормализация изменила уже чистый файл')
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    if fails:
        for f in fails:
            print('  НЕГАТИВНЫЙ КОНТРОЛЬ ПРОВАЛЕН: %s' % f)
        return False
    print('PE SCRUB SELFTEST OK')
    return True


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args or args[0] not in ('--verify', '--clean', '--selftest'):
        print('использование: --verify|--clean <pe>... | --selftest')
        sys.exit(2)
    mode, rest = args[0], args[1:]
    if mode == '--selftest':
        sys.exit(0 if run_selftest() else 1)
    if not rest:
        print('нужен хотя бы один путь к PE'); sys.exit(2)
    if mode == '--verify':
        sys.exit(0 if run_verify(rest) else 1)
    sys.exit(0 if run_clean(rest) else 1)
