# Gates: одна иконка пользователя на всех размерах, максимальное качество

OWNS: assets/**, tools/**, GATES.md

Scope: в ProxyPulse.ico на каждом размере лежит одна и та же исходная картинка
пользователя, уменьшенная в линейном свете без потери яркости; нарисованной
второй версии не существует; собранная и опубликованная программа показывает
эту иконку и запускается.

- [ ] G1: мастер хранится в полном разрешении оригинала, без промежуточного ужатия
  CHECK: python tools/verify_icon.py --master
  EXPECT: MASTER OK
  EVIDENCE: pending

- [ ] G2: в .ico десять размеров, и каждый кадр — уменьшенная копия мастера, а не отдельный рисунок
  CHECK: python tools/verify_icon.py --single-source
  EXPECT: SINGLE SOURCE OK
  EVIDENCE: pending

- [ ] G3: негативный контроль: та же проверка отвергает нарисованный вариант
  CHECK: python tools/verify_icon.py --negative-control
  EXPECT: NEGATIVE CONTROL OK
  EVIDENCE: pending

- [ ] G4: уменьшение идёт в линейном свете, потеря яркости на каждом размере ниже 5 процентов
  CHECK: python tools/verify_icon.py --luminance
  EXPECT: LUMINANCE OK
  EVIDENCE: pending

- [ ] G5: в коде нет функции рисования мелких иконок
  CHECK: python tools/verify_icon.py --no-drawing
  EXPECT: NO DRAWING OK
  EVIDENCE: pending

- [ ] G6: скачанный из релиза установщик ставится, программа стартует, иконка в сборке совпадает с репозиторием
  CHECK: python tools/verify_release.py
  EXPECT: RELEASE OK
  EVIDENCE: pending
