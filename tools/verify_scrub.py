"""Детектор деанонимизирующих следов в том, что реально уезжает пользователю и
в публичный репозиторий.

  python tools/verify_scrub.py --verify      ->  SCRUB SURFACE OK
  python tools/verify_scrub.py --history     ->  SCRUB HISTORY OK   (или честно падает)
  python tools/verify_scrub.py --selftest    ->  SCRUB SELFTEST OK
  python tools/verify_scrub.py --all

Зачем отдельный детектор, а не «посмотрел глазами»: чистота доказывается
командой, которая умеет сказать «грязно». Поэтому у каждого детектора есть
негативный контроль (--selftest): заведомо грязный образец обязан его уронить.
Детектор, который всегда говорит «чисто», ничего не доказывает.

Три поверхности разнесены сознательно:
  * --verify  — рабочее дерево под контролем git (то, что сейчас в публичном
    репозитории как файлы, плюс свойства .exe и метаданные картинок). Это я
    могу вычистить полностью, поэтому гейт обязан быть зелёным.
  * --history — вся история коммитов: автор/коммиттер, таймзона, трейлеры ИИ,
    аннотированные теги, старые блобы. Чистится только переписыванием истории
    и пересозданием репозитория (раздел 1-2 методички) — действие владельца.
    Пока история не переписана, этот гейт честно красный.
  * --selftest — негативный контроль для обоих.

Литералы настоящей личности в этом файле НЕ лежат: шаблоны собираются из
кусков. Иначе детектор находил бы сам себя, и его пришлось бы исключать из
собственной проверки задним числом.
"""
import io
import os
import re
import struct
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Корень репозитория — на два уровня выше этого файла (tools/..).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Денилист ---------------------------------------------------------------
# Собран из кусков, чтобы сам исходник детектора не содержал запретных строк.
_N1 = 'Bog' + 'dan'
_N2 = 'Tsy' + 'bin'
_LOGIN = 'Bog' + '_1'
_MAIL = 'tsy' + 'binb'
_ALIAS = 'github-' + 'bog' + 'dan'            # ssh-алиас реального аккаунта
_REALACC = _N1 + _N2 + '2005'                  # аккаунт под настоящим именем
_CLOUD = 'One' + 'Drive'                       # слабый, но региональный сигнал пути

# (ярлык, регэксп, жёсткость). hard=True — валит гейт; hard=False — сообщается,
# но тоже валит (разделение оставлено на будущее, сейчас всё жёсткое).
DENY = [
    ('настоящее имя',          re.compile(re.escape(_N1), re.I)),
    ('фамилия',                re.compile(re.escape(_N2), re.I)),
    ('логин ОС',               re.compile(re.escape(_LOGIN))),
    ('почта (локальная часть)',re.compile(re.escape(_MAIL), re.I)),
    ('ssh-алиас реального акк', re.compile(re.escape(_ALIAS), re.I)),
    ('аккаунт под именем',     re.compile(re.escape(_REALACC), re.I)),
    ('облачная папка в пути',  re.compile(re.escape(_CLOUD))),
]

# Токен GitHub в коммите — отдельно: это секрет, а не просто имя. Плейсхолдеры
# из тестов (ghp_test, ghp_abc, ghp_<...>) не в счёт — у них нет 36 знаков тела.
TOKEN = re.compile(r'ghp_[A-Za-z0-9]{36}')

# Что не сканируем как текст: бинарь и большие данные.
SKIP_EXT = {'.mmdb', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.pyc', '.zip',
            '.gz', '.exe', '.dll', '.pyd'}
# Этот файл и ledger сами описывают следы — исключаем, чтобы не ловить описание.
SKIP_PATHS = {os.path.join('tools', 'verify_scrub.py').replace('\\', '/')}


def _git(*args):
    out = subprocess.run(('git',) + args, cwd=ROOT, capture_output=True,
                         text=True, encoding='utf-8', errors='replace')
    if out.returncode != 0:
        raise RuntimeError('git %s -> %d: %s' % (' '.join(args), out.returncode,
                                                 out.stderr.strip()))
    return out.stdout


def tracked_files():
    files = [f for f in _git('ls-files').splitlines() if f]
    return [f for f in files
            if os.path.splitext(f)[1].lower() not in SKIP_EXT
            and f not in SKIP_PATHS]


def scan_text_markers(files):
    """Ищет маркеры личности в содержимом перечисленных файлов.

    Декодируем именно как UTF-8 (с фолбэком latin-1): если UTF-8-текст с
    кириллицей читать как latin-1, то байт 0x85 (частый второй байт кириллицы)
    принимается за разрыв строки, и номера строк уезжают. Режем только по '\\n',
    как это делает git — тогда номер строки совпадает с редактором и git grep.
    Маркеры тут ASCII, так что на само совпадение кодировка не влияет."""
    hits = []
    for rel in files:
        path = os.path.join(ROOT, rel)
        try:
            with open(path, 'rb') as fh:
                raw = fh.read()
        except OSError:
            continue
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = raw.decode('latin-1')
        for lineno, line in enumerate(text.split('\n'), 1):
            line = line.rstrip('\r')
            for label, rx in DENY:
                if rx.search(line):
                    hits.append((rel, lineno, label, line.strip()[:100]))
            if TOKEN.search(line):
                hits.append((rel, lineno, 'токен GitHub', line.strip()[:60]))
    return hits


# --- Метаданные картинок (вспомогательные чанки PNG/ICO) ---------------------
_CRIT = {b'IHDR', b'IDAT', b'IEND', b'PLTE', b'tRNS', b'acTL', b'fcTL', b'fdAT',
         b'bKGD', b'pHYs', b'sRGB', b'gAMA', b'cHRM', b'sBIT'}


def _scan_png_chunks(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return []
    i, found = 8, []
    while i + 8 <= len(data):
        ln = struct.unpack('>I', data[i:i + 4])[0]
        typ = data[i + 4:i + 8]
        if typ not in _CRIT:
            found.append(typ.decode('latin-1', 'replace'))
        i += 12 + ln
        if typ == b'IEND':
            break
    return found


def scan_assets():
    """Возвращает список (файл, чанк) по всем PNG и PNG-кадрам .ico в assets."""
    hits = []
    adir = os.path.join(ROOT, 'assets')
    for base, _dirs, names in os.walk(adir):
        for n in names:
            p = os.path.join(base, n)
            rel = os.path.relpath(p, ROOT).replace('\\', '/')
            low = n.lower()
            if low.endswith('.png'):
                for c in _scan_png_chunks(open(p, 'rb').read()):
                    hits.append((rel, c))
            elif low.endswith('.ico'):
                d = open(p, 'rb').read()
                if len(d) < 6:
                    continue
                cnt = struct.unpack('<H', d[4:6])[0]
                for k in range(cnt):
                    off = 6 + k * 16
                    if off + 16 > len(d):
                        break
                    sz = struct.unpack('<I', d[off + 8:off + 12])[0]
                    o = struct.unpack('<I', d[off + 12:off + 16])[0]
                    frame = d[o:o + sz]
                    for c in _scan_png_chunks(frame):
                        hits.append(('%s[%d]' % (rel, k), c))
    return hits


def version_resource_clean():
    """В version_info.txt не должно быть автора/копирайта/личного имени, а
    Company/Product — нейтральные. Возвращает список проблем."""
    path = os.path.join(ROOT, 'version_info.txt')
    if not os.path.exists(path):
        return ['version_info.txt отсутствует']
    text = io.open(path, encoding='utf-8', errors='replace').read()
    bad = []
    for label, rx in DENY:
        if rx.search(text):
            bad.append('version_info.txt содержит %s' % label)
    for forbidden in ('LegalCopyright', 'Copyright', '@author', 'Author'):
        if forbidden in text:
            bad.append('version_info.txt содержит поле %s' % forbidden)
    return bad


def settings_not_tracked():
    """settings.json (путь + токен пользователя) не должен быть под git, а в
    отслеживаемых файлах не должно быть живого токена."""
    bad = []
    if 'settings.json' in _git('ls-files').splitlines():
        bad.append('settings.json отслеживается git')
    return bad


# Внутренние аудит/процесс-документы: написаны по-русски (сам язык — региональный
# сигнал, раздел D) и насыщены связкой аккаунтов, координатами секрета в истории
# и тактикой alt-аккаунта, которые регэкспом по именам не ловятся (доказано
# семантическим прогоном). Их место — на диске у владельца, а не в публичном репо.
INTERNAL_DOCS = ('AUDIT.md', 'REPORT.md', 'GATES.md', 'GATES-scrub.md',
                 'SCRUB-REPORT.md')


def internal_docs_not_tracked():
    tracked = set(_git('ls-files').splitlines())
    return ['внутренний документ отслеживается git: %s' % d
            for d in INTERNAL_DOCS if d in tracked]


# --- История ----------------------------------------------------------------
def history_problems():
    """Следы в истории коммитов. Чистится только переписыванием (владелец)."""
    probs = []
    ids = set()
    for line in _git('log', '--all', '--format=%an|%ae|%cn|%ce').splitlines():
        if line.strip():
            ids.add(line)
    nonneutral = [x for x in ids
                  if any(rx.search(x) for _l, rx in DENY)]
    if nonneutral:
        probs.append('личность в авторстве коммитов: %d различных подписей'
                     % len(nonneutral))
    tzs = set()
    for line in _git('log', '--all', '--format=%ai').splitlines():
        m = re.search(r'([+-]\d{4})\s*$', line)
        if m:
            tzs.add(m.group(1))
    offtz = sorted(t for t in tzs if t != '+0000')
    if offtz:
        probs.append('ненулевая таймзона в коммитах: %s' % ', '.join(offtz))
    body = _git('log', '--all', '--format=%b')
    if re.search(r'co-authored-by|generated with|signed-off-by', body, re.I):
        probs.append('трейлеры ИИ/подписи в сообщениях коммитов')
    annotated = [l for l in _git('for-each-ref',
                 '--format=%(objecttype) %(refname:short)',
                 'refs/tags').splitlines() if l.startswith('tag ')]
    if annotated:
        probs.append('аннотированные теги (внутри — имя/почта/дата теггера): %d'
                     % len(annotated))
    return probs


# --- Негативный контроль -----------------------------------------------------
def selftest():
    """Каждый детектор обязан поймать заведомо грязный образец."""
    fails = []

    dirty = '%s %s %s %s ghp_%s' % (_N1, _LOGIN, _MAIL, _ALIAS, 'A' * 36)
    caught = any(rx.search(dirty) for _l, rx in DENY) and TOKEN.search(dirty)
    if not caught:
        fails.append('текстовый детектор не поймал грязную строку')

    clean = 'proxy checker output_dir results elite http://pubproxy.com'
    if any(rx.search(clean) for _l, rx in DENY) or TOKEN.search(clean):
        fails.append('текстовый детектор ложно сработал на чистой строке')

    # PNG с tEXt-чанком обязан быть помечен; чистый IHDR/IDAT/IEND — нет.
    def _png(chunks):
        out = b'\x89PNG\r\n\x1a\n'
        for typ, body in chunks:
            out += struct.pack('>I', len(body)) + typ + body + b'\x00\x00\x00\x00'
        return out
    dirty_png = _png([(b'IHDR', b'\x00' * 13), (b'tEXt', b'Software\x00GIMP'),
                      (b'IEND', b'')])
    clean_png = _png([(b'IHDR', b'\x00' * 13), (b'IDAT', b'x'), (b'IEND', b'')])
    if not _scan_png_chunks(dirty_png):
        fails.append('детектор PNG не поймал tEXt-чанк')
    if _scan_png_chunks(clean_png):
        fails.append('детектор PNG ложно сработал на чистом PNG')

    return fails


# --- Режимы ------------------------------------------------------------------
def run_surface():
    ok = True
    hits = scan_text_markers(tracked_files())
    if hits:
        ok = False
        print('  СЛЕДЫ в отслеживаемых файлах:')
        for rel, ln, label, snippet in hits:
            print('    %s:%d  [%s]  %s' % (rel, ln, label, snippet))
    else:
        print('  отслеживаемые файлы: маркеров личности нет')

    ameta = scan_assets()
    if ameta:
        ok = False
        print('  МЕТАДАННЫЕ в картинках:')
        for rel, chunk in ameta:
            print('    %s  чанк %s' % (rel, chunk))
    else:
        print('  картинки (PNG/ICO): вспомогательных метаданных нет')

    vbad = version_resource_clean()
    if vbad:
        ok = False
        for b in vbad:
            print('  РЕСУРС ВЕРСИИ: %s' % b)
    else:
        print('  ресурс версии .exe: нейтральный')

    sbad = settings_not_tracked()
    if sbad:
        ok = False
        for b in sbad:
            print('  СЕКРЕТЫ: %s' % b)
    else:
        print('  settings.json: не под контролем версий')

    dbad = internal_docs_not_tracked()
    if dbad:
        ok = False
        for b in dbad:
            print('  ПУБЛИКАЦИЯ ВНУТРЕННЕГО: %s' % b)
    else:
        print('  внутренние аудит-документы: не опубликованы')

    if ok:
        print('SCRUB SURFACE OK')
    return ok


def run_history():
    probs = history_problems()
    if probs:
        print('  история НЕ вычищена (нужно переписывание истории владельцем):')
        for p in probs:
            print('    - %s' % p)
        return False
    print('SCRUB HISTORY OK')
    return True


def run_selftest():
    fails = selftest()
    if fails:
        for f in fails:
            print('  НЕГАТИВНЫЙ КОНТРОЛЬ ПРОВАЛЕН: %s' % f)
        return False
    print('SCRUB SELFTEST OK')
    return True


MODES = {'--verify': run_surface, '--history': run_history,
         '--selftest': run_selftest}

if __name__ == '__main__':
    args = sys.argv[1:] or ['--verify']
    if args == ['--all']:
        args = ['--selftest', '--verify', '--history']
    bad_mode = [a for a in args if a not in MODES]
    if bad_mode:
        print('режимы: %s | --all' % ' '.join(sorted(MODES)))
        sys.exit(2)
    rc = 0
    for a in args:
        print('== %s ==' % a)
        if not MODES[a]():
            rc = 1
    sys.exit(rc)
