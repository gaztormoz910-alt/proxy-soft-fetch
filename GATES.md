# Gates: одна иконка пользователя на всех размерах, максимальное качество

OWNS: assets/**, tools/**, GATES.md

Scope: в ProxyPulse.ico на каждом размере лежит одна и та же исходная картинка
пользователя, уменьшенная в линейном свете без потери яркости; нарисованной
второй версии не существует; собранная и опубликованная программа показывает
эту иконку и запускается.

- [x] G1: мастер хранится в полном разрешении оригинала, без промежуточного ужатия
  CHECK: python tools/verify_icon.py --master
  EXPECT: MASTER OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=32ea9c017d1d3328745929560d6dc61f1c9fbc94dc77adc505da9d4e0d79d4ae; output-bytes=44

- [x] G2: в .ico десять размеров, и каждый кадр — уменьшенная копия мастера, а не отдельный рисунок
  CHECK: python tools/verify_icon.py --single-source
  EXPECT: SINGLE SOURCE OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=136af8ffa75d7fc3d59b11348986874e1ac085d917fa87e5654970646e8d4086; output-bytes=827

- [x] G3: негативный контроль: та же проверка отвергает нарисованный вариант
  CHECK: python tools/verify_icon.py --negative-control
  EXPECT: NEGATIVE CONTROL OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=3ff89a9305f6dda6a7fc2f523b77f91b8a1556fbc21c314ee538c858a535dd24; output-bytes=381

- [x] G4: уменьшение идёт в линейном свете, потеря яркости на каждом размере ниже 5 процентов
  CHECK: python tools/verify_icon.py --luminance
  EXPECT: LUMINANCE OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=9d06ce33c702fb8ea0721026b0c4ac1859b99841f6ddc314dfe25bd7b72259c5; output-bytes=609

- [x] G5: в коде нет функции рисования мелких иконок
  CHECK: python tools/verify_icon.py --no-drawing
  EXPECT: NO DRAWING OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=26d3cd76ce8ac81b31685dc1e5ff9bcc7b0dc732ccba31be97d4e123e9034825; output-bytes=95

- [x] G6: скачанный из релиза установщик ставится, программа стартует, иконка в сборке совпадает с репозиторием
  CHECK: python tools/verify_release.py
  EXPECT: RELEASE OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=2a6d886fc937232bb39945fbfa055993c6a56452f9433eedffa884c05637e001; output-bytes=329
