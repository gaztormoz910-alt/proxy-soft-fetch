"""Настоящий прогон конвейера внутри УСТАНОВЛЕННОЙ собранной программы.

  python tools/verify_pipeline.py   ->  PIPELINE OK

Запуск окна ничего не доказывает про охоту: сеть, сертификаты, asyncio,
socks-библиотеки и запись результатов подключаются только во время прогона.
Ровно так уехал релиз 4.0.1 — окно открывалось, а программы не было.

Скрипт вызывает ProxyPulse.exe --selftest, который проходит тот же путь, что
и кнопка СТАРТ: скачивание базы GeoIP, сбор с источников, проверка,
фильтрация, сохранение. Проверяются код возврата, непустой сбор и реально
созданные файлы результатов.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

EXE = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%\Programs\ProxyPulse'),
                   'ProxyPulse.exe')
TIMEOUT = 900


def main():
    assert os.path.exists(EXE), 'программа не установлена: %s' % EXE
    work = tempfile.mkdtemp(prefix='proxypulse-selftest-')
    log = os.path.join(work, 'selftest.log')
    print('рабочая папка: %s' % work)
    try:
        code = subprocess.call([EXE, '--selftest', log], timeout=TIMEOUT)
        text = io.open(log, encoding='utf-8', errors='replace').read() \
            if os.path.exists(log) else ''
        tail = [ln for ln in text.splitlines() if ln.strip()][-12:]
        for ln in tail:
            print('  | %s' % ln)
        assert code == 0, 'selftest вернул код %d' % code

        m = re.search(r'SELFTEST DONE collected=(\d+) checked=(\d+) live=(\d+)', text)
        assert m, 'в логе нет строки завершения SELFTEST DONE'
        collected, checked, live = (int(g) for g in m.groups())
        print('собрано %d, проверено %d, живых %d' % (collected, checked, live))
        assert collected > 0, 'сбор не дал кандидатов'
        assert checked > 0, 'на проверку не ушло ни одного адреса'

        # Файлы результатов — единственное доказательство, что дошло до записи.
        produced = []
        for root, _dirs, files in os.walk(work):
            for f in files:
                if f != 'selftest.log':
                    produced.append(os.path.relpath(os.path.join(root, f), work))
        print('создано файлов результатов: %d' % len(produced))
        for f in produced[:8]:
            print('  + %s' % f)
        assert produced, 'программа не записала ни одного файла результатов'
        print('PIPELINE OK')
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    main()
