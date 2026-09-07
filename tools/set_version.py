"""Единственное место, где задаётся номер версии.

  python tools/set_version.py 4.0.4

Пишет файл VERSION и генерирует version_info.txt. Дальше номер читают все,
кто его показывает:
  * заголовок окна   — gui.py, функция app_version(), из VERSION;
  * свойства .exe    — version_info.txt, который делает этот же скрипт;
  * установщик       — ProxyPulse.iss, который читает VERSION.

До этого версия была вписана руками в трёх местах, и после релиза 4.0.3 окно
продолжало показывать 4.0.
"""
import io
import sys

TEMPLATE = """VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({v0}, {v1}, {v2}, {v3}),
    prodvers=({v0}, {v1}, {v2}, {v3}),
    mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'ProxyPulse'),
         StringStruct('FileDescription', 'ProxyPulse - proxy collector and checker'),
         StringStruct('FileVersion', '{dotted}'),
         StringStruct('InternalName', 'ProxyPulse'),
         StringStruct('OriginalFilename', 'ProxyPulse.exe'),
         StringStruct('ProductName', 'ProxyPulse'),
         StringStruct('ProductVersion', '{dotted}')])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def normalize(version):
    parts = [int(p) for p in version.strip().lstrip('vV').split('.')]
    return (parts + [0, 0, 0, 0])[:4]


def main(version):
    parts = normalize(version)
    short = version.strip().lstrip('vV')
    io.open('VERSION', 'w', encoding='utf-8', newline='\n').write(short + '\n')
    io.open('version_info.txt', 'w', encoding='utf-8').write(
        TEMPLATE.format(v0=parts[0], v1=parts[1], v2=parts[2], v3=parts[3],
                        dotted='.'.join(str(p) for p in parts)))
    print('VERSION=%s version_info=%s' % (short, '.'.join(str(p) for p in parts)))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('использование: python tools/set_version.py 4.0.4')
        sys.exit(2)
    main(sys.argv[1])
