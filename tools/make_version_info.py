"""Генерирует version_info.txt — блок метаданных, который Windows показывает
в свойствах .exe.

Запуск:  python tools/make_version_info.py 4.1

Без аргумента берётся версия по умолчанию. CI передаёт сюда версию из тега,
чтобы свойства файла не разъезжались с номером релиза.
"""
import io
import sys

DEFAULT = "4.0"

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


def main(version):
    parts = [int(p) for p in version.strip().lstrip('vV').split('.')]
    parts = (parts + [0, 0, 0, 0])[:4]      # Windows требует ровно четыре числа
    text = TEMPLATE.format(v0=parts[0], v1=parts[1], v2=parts[2], v3=parts[3],
                           dotted='.'.join(str(p) for p in parts))
    io.open('version_info.txt', 'w', encoding='utf-8').write(text)
    print('version_info.txt: %s' % '.'.join(str(p) for p in parts))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT)
