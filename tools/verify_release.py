"""Проверка того, что реально получает пользователь.

  python tools/verify_release.py     ->  RELEASE OK

Скачивает установщик по постоянной ссылке релиза, ставит его молча, запускает
программу и проверяет четыре вещи: она не падает, заголовок окна правильный,
Windows получает иконки тех размеров, которые просит, и .ico внутри
установленной сборки байт в байт совпадает с тем, что лежит в репозитории.

Последнее и есть главное: без него «иконка исправлена» означало бы лишь
«исправлена у меня в папке», а не «доехала до пользователя».
"""
import ctypes
import ctypes.wintypes as wt
import hashlib
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

# Скрипт запускают из разных оболочек, в том числе из cmd.exe с кодировкой
# cp1252, где обычный print с кириллицей падает на UnicodeEncodeError. Проверка,
# которая зависит от кодировки конкретной консоли, ничего не проверяет.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

URL = ('https://github.com/gaztormoz910-alt/proxy-soft-fetch/releases/'
       'latest/download/ProxyPulse-setup.exe')
INSTALL_DIR = os.path.expandvars(r'%LOCALAPPDATA%\Programs\ProxyPulse')
TITLE_PREFIX = 'ProxyPulse'
REPO_ICO = 'assets/ProxyPulse.ico'
WM_GETICON = 0x007F

u, g = ctypes.windll.user32, ctypes.windll.gdi32
u.FindWindowW.restype = ctypes.c_void_p
u.SendMessageW.restype = ctypes.c_void_p
u.GetIconInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
g.GetObjectW.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]


class _ICONINFO(ctypes.Structure):
    _fields_ = [("fIcon", wt.BOOL), ("xHotspot", wt.DWORD), ("yHotspot", wt.DWORD),
                ("hbmMask", ctypes.c_void_p), ("hbmColor", ctypes.c_void_p)]


class _BITMAP(ctypes.Structure):
    _fields_ = [("bmType", ctypes.c_long), ("bmWidth", ctypes.c_long),
                ("bmHeight", ctypes.c_long), ("bmWidthBytes", ctypes.c_long),
                ("bmPlanes", wt.WORD), ("bmBitsPixel", wt.WORD),
                ("bmBits", ctypes.c_void_p)]


def _icon_side(handle):
    if not handle:
        return 0
    ii = _ICONINFO()
    if not u.GetIconInfo(handle, ctypes.byref(ii)):
        return 0
    bm = _BITMAP()
    g.GetObjectW(ii.hbmColor or ii.hbmMask, ctypes.sizeof(bm), ctypes.byref(bm))
    return bm.bmWidth


def _sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    tmp = os.path.join(tempfile.gettempdir(), 'ProxyPulse-setup-check.exe')
    print('качаю %s' % URL)
    urllib.request.urlretrieve(URL, tmp)
    size_mb = os.path.getsize(tmp) / 1048576.0
    print('скачано: %.1f MB' % size_mb)
    assert size_mb > 15, 'установщик подозрительно мал: %.1f MB' % size_mb

    code = subprocess.call([tmp, '/VERYSILENT', '/SUPPRESSMSGBOXES',
                            '/NORESTART', '/NOCANCEL'])
    assert code == 0, 'установщик вернул код %d' % code
    exe = os.path.join(INSTALL_DIR, 'ProxyPulse.exe')
    assert os.path.exists(exe), 'нет %s' % exe

    shipped = os.path.join(INSTALL_DIR, '_internal', 'assets', 'ProxyPulse.ico')
    assert os.path.exists(shipped), 'в установленной сборке нет иконки'
    a, b = _sha256(shipped), _sha256(REPO_ICO)
    print('sha256 иконки: в сборке %s / в репозитории %s' % (a[:16], b[:16]))
    assert a == b, 'иконка в релизе не совпадает с иконкой в репозитории'

    proc = subprocess.Popen([exe])
    try:
        hwnd = None
        for _ in range(60):
            time.sleep(0.5)
            for title in ('ProxyPulse v4.0', 'Unhandled exception in script'):
                h = u.FindWindowW(None, title)
                if h:
                    hwnd, found = ctypes.c_void_p(h), title
                    break
            if hwnd:
                break
        assert hwnd, 'окно не появилось за 30 секунд'
        assert found.startswith(TITLE_PREFIX), 'окно с заголовком %r' % found
        time.sleep(2)
        small = _icon_side(u.SendMessageW(hwnd, WM_GETICON, 0, 0))
        big = _icon_side(u.SendMessageW(hwnd, WM_GETICON, 1, 0))
        want_small, want_big = u.GetSystemMetrics(49), u.GetSystemMetrics(11)
        print('иконки окна: small %dx / big %dx, система просит %d / %d'
              % (small, big, want_small, want_big))
        assert small == want_small, 'ICON_SMALL %d вместо %d' % (small, want_small)
        assert big == want_big, 'ICON_BIG %d вместо %d' % (big, want_big)
        assert proc.poll() is None, 'программа завершилась сама'
    finally:
        proc.kill()
    print('RELEASE OK')


if __name__ == '__main__':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)   # иначе метрики придут без масштаба
    except Exception:
        pass
    main()
