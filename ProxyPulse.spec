# -*- mode: python ; coding: utf-8 -*-
# Сборка: pyinstaller --noconfirm ProxyPulse.spec
#
# onedir, а не onefile: onefile при каждом запуске распаковывает ~200 МБ
# во временную папку — это 5-10 секунд ожидания перед появлением окна и
# частая ложная тревога у антивирусов. Установщик всё равно прячет папку
# от пользователя, поэтому смысла в onefile нет.

from PyInstaller.utils.hooks import collect_all

datas = [('assets', 'assets')]
binaries = []
hiddenimports = [
    'aiohttp_socks', 'python_socks', 'python_socks.async_', 'socks',
    'dns.resolver', 'dns.reversename', 'maxminddb', 'nest_asyncio',
]

# customtkinter возит с собой JSON-темы и шрифты; без collect_all
# собранная программа падает на старте, не найдя тему.
for pkg in ('customtkinter',):
    d, b, h = collect_all(pkg)
    datas += d; binaries += b; hiddenimports += h

a = Analysis(
    ['gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    # Тяжёлое и ненужное: тянется как зависимость Pillow/прочего.
    # nest_asyncio опционально дружит с IPython, и PyInstaller тянет за ним
    # весь Jupyter-хвост (jedi, zmq) — ~10 МБ, которые программе не нужны.
    excludes=['matplotlib', 'numpy', 'scipy', 'pandas', 'pytest', 'PyQt5', 'PySide2',
              'IPython', 'jedi', 'zmq', 'jupyter_client', 'jupyter_core', 'tornado'],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='ProxyPulse',
    debug=False,
    strip=False,
    upx=False,
    console=False,          # GUI-программа: без чёрного окна консоли
    icon='assets/ProxyPulse.ico',
    version='version_info.txt',
)
coll = COLLECT(
    exe, a.binaries, a.datas,
    strip=False, upx=False, name='ProxyPulse',
)
