# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

datas = [('assets', 'assets'), ('VERSION', '.')]
if os.path.exists('GeoLite2-Country.mmdb'):
    datas.append(('GeoLite2-Country.mmdb', '.'))

binaries = []
hiddenimports = [
    'aiohttp_socks', 'python_socks', 'python_socks.async_', 'socks',
    'dns.resolver', 'dns.reversename', 'maxminddb', 'nest_asyncio',
]

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
    console=False,
    icon='assets/ProxyPulse.ico',
    version='version_info.txt',
)
coll = COLLECT(
    exe, a.binaries, a.datas,
    strip=False, upx=False, name='ProxyPulse',
)

exe_standalone = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ProxyPulse-standalone',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon='assets/ProxyPulse.ico',
    version='version_info.txt',
)
