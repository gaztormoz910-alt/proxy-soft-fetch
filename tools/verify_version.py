"""Номер версии обязан совпадать везде, где его видно.

  python tools/verify_version.py   ->  VERSION OK

Сверяются пять независимых мест: файл VERSION в репозитории, копия VERSION
внутри собранной программы, ресурс версии в .exe (то, что Windows показывает
в свойствах файла), запись деинсталляции, которую сделал установщик, и
заголовок реально запущенного окна.

Проверка идёт по УСТАНОВЛЕННОЙ копии, а не по исходникам: расхождение, которое
видит пользователь, возникает именно на этом конце. До появления файла VERSION
окно показывало 4.0, когда релиз был уже 4.0.3.
"""
import ctypes
import ctypes.wintypes as wt
import io
import os
import subprocess
import sys
import time
import winreg

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

INSTALL_DIR = os.path.expandvars(r'%LOCALAPPDATA%\Programs\ProxyPulse')
EXE = os.path.join(INSTALL_DIR, 'ProxyPulse.exe')
UNINSTALL_KEY = r'Software\Microsoft\Windows\CurrentVersion\Uninstall'

u = ctypes.windll.user32
ENUMPROC = ctypes.WINFUNCTYPE(wt.BOOL, ctypes.c_void_p, ctypes.c_void_p)
u.EnumWindows.argtypes = [ENUMPROC, ctypes.c_void_p]


class _FFI(ctypes.Structure):
    _fields_ = [('dwSignature', wt.DWORD), ('dwStrucVersion', wt.DWORD),
                ('dwFileVersionMS', wt.DWORD), ('dwFileVersionLS', wt.DWORD),
                ('dwProductVersionMS', wt.DWORD), ('dwProductVersionLS', wt.DWORD),
                ('dwFileFlagsMask', wt.DWORD), ('dwFileFlags', wt.DWORD),
                ('dwFileOS', wt.DWORD), ('dwFileType', wt.DWORD),
                ('dwFileSubtype', wt.DWORD), ('dwFileDateMS', wt.DWORD),
                ('dwFileDateLS', wt.DWORD)]


def exe_file_version(path):
    ver = ctypes.windll.version
    size = ver.GetFileVersionInfoSizeW(path, None)
    assert size, 'у %s нет ресурса версии' % path
    buf = ctypes.create_string_buffer(size)
    assert ver.GetFileVersionInfoW(path, 0, size, buf), 'GetFileVersionInfoW failed'
    ptr, length = ctypes.c_void_p(), ctypes.c_uint()
    root = ctypes.create_unicode_buffer(2)
    root.value = '\\'
    assert ver.VerQueryValueW(buf, root, ctypes.byref(ptr), ctypes.byref(length)), \
        'VerQueryValueW failed'
    ffi = ctypes.cast(ptr, ctypes.POINTER(_FFI)).contents
    ms, ls = ffi.dwFileVersionMS, ffi.dwFileVersionLS
    return (ms >> 16, ms & 0xFFFF, ls >> 16, ls & 0xFFFF)


def window_title_of(pid, timeout=30.0):
    """Заголовок первого видимого окна процесса.

    Ищем по идентификатору процесса, а не по известному заголовку: именно
    заголовок здесь и проверяется, поэтому искать окно по нему было бы
    проверкой самой себя.
    """
    titles = []

    @ENUMPROC
    def collect(hwnd, _):
        owner = wt.DWORD()
        u.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and u.IsWindowVisible(hwnd):
            n = u.GetWindowTextLengthW(hwnd)
            if n:
                b = ctypes.create_unicode_buffer(n + 1)
                u.GetWindowTextW(hwnd, b, n + 1)
                titles.append(b.value)
        return True

    deadline = time.time() + timeout
    while time.time() < deadline:
        del titles[:]
        u.EnumWindows(collect, None)
        if titles:
            return titles[0]
        time.sleep(0.5)
    return ''


def uninstall_version():
    for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            key = winreg.OpenKey(root, UNINSTALL_KEY)
        except OSError:
            continue
        for i in range(winreg.QueryInfoKey(key)[0]):
            try:
                sub = winreg.OpenKey(key, winreg.EnumKey(key, i))
                disp = winreg.QueryValueEx(sub, 'DisplayName')[0]
            except OSError:
                continue
            if 'ProxyPulse' in disp:
                try:
                    return winreg.QueryValueEx(sub, 'DisplayVersion')[0]
                except OSError:
                    return ''
    return ''


def main():
    want = io.open('VERSION', encoding='utf-8').read().strip()
    print('  VERSION в репозитории : %s' % want)
    assert os.path.exists(EXE), 'программа не установлена: %s' % EXE

    shipped = io.open(os.path.join(INSTALL_DIR, '_internal', 'VERSION'),
                      encoding='utf-8').read().strip()
    print('  VERSION в сборке      : %s' % shipped)
    assert shipped == want, 'в сборке %s, ожидалось %s' % (shipped, want)

    fv = exe_file_version(EXE)
    dotted = '.'.join(str(x) for x in fv[:3])
    print('  свойства .exe         : %s' % '.'.join(str(x) for x in fv))
    assert dotted == want, 'свойства .exe %s, ожидалось %s' % (dotted, want)

    reg = uninstall_version()
    print('  запись деинсталляции  : %s' % (reg or 'НЕТ'))
    assert reg == want, 'установщик записал %r, ожидалось %s' % (reg, want)

    proc = subprocess.Popen([EXE])
    try:
        title = window_title_of(proc.pid)
        print('  заголовок окна        : %r' % title)
        assert title == 'ProxyPulse v%s' % want, \
            'окно показывает %r, ожидалось ProxyPulse v%s' % (title, want)
    finally:
        proc.kill()
    print('VERSION OK')


if __name__ == '__main__':
    main()
