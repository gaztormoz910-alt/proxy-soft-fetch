# Gates: закрыть хвосты — везде одна актуальная версия

OWNS: .github/**, assets/**, tools/**, gui.py, ProxyPulse.iss, ProxyPulse.spec, build.ps1, VERSION, GATES.md

Scope: обе ветки на обоих удалённых репозиториях содержат последний код; номер
версии живёт в одном месте и совпадает в окне, в свойствах .exe и в
установщике; собранная программа проходит настоящий прогон конвейера;
опубликованный релиз — текущая версия, ставится и работает; битый релиз
удалён.

- [x] G1: main и рабочая ветка на публичном репозитории совпадают с HEAD
  CHECK: python tools/verify_repo.py --public
  EXPECT: PUBLIC REPO OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=36fbe042b62133a58cd33f2f04bc2d37f07940e530d5e2a911affe6c8a3135d0; output-bytes=201

- [x] G2: приватный репозиторий содержит тот же коммит
  CHECK: python tools/verify_repo.py --private
  EXPECT: PRIVATE REPO OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=bbb0b578a21242f4e32a5ab8a9afb722ad567deb1554284cba10411e1334a826; output-bytes=202

- [x] G3: рабочее дерево чистое, а содержимое сборки совпадает с тегом текущей версии
  CHECK: python tools/verify_repo.py --clean
  EXPECT: WORKTREE OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=0ee73a1260697d5260802ad7957a7e6e16b707f2a587e3bd0a52b37678ebc020; output-bytes=207

- [x] G4: установщик по постоянной ссылке ставится, запускается, иконка и версия совпадают с репозиторием
  CHECK: python tools/verify_release.py
  EXPECT: RELEASE OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=7b4ab99c48fc48e2daa6e4fe837ccc58d4439d9c85e12c3aa77795e2865a88e1; output-bytes=449

- [x] G5: номер версии совпадает в файле, в сборке, в свойствах .exe, в записи деинсталляции и в заголовке окна
  CHECK: python tools/verify_version.py
  EXPECT: VERSION OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=003ef9923efe458457a61e4b09dc08e5964cdc2b3b8e577c6cb92a8e9a6b6fdd; output-bytes=252

- [x] G6: установленная программа проходит настоящий прогон конвейера и пишет результаты
  CHECK: python tools/verify_pipeline.py
  EXPECT: PIPELINE OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=4fa9e2c2e31fa67c6d55e116206a0ddf00f6e984cb6164ee7c09cd780021dac3; output-bytes=1425

- [ ] G7: битого релиза v4.0.1 больше нет, последний релиз совпадает с текущей версией
  CHECK: python tools/verify_repo.py --releases
  EXPECT: RELEASES OK
  EVIDENCE: pending
ABANDON: G7 Удаление релиза выполняется только владельцем: нужна запись в аккаунт gaztormoz910-alt через GitHub API или веб-интерфейс. gh CLI не установлен и не авторизован, действующего токена нет, а вводить учётные данные я не имею права. Передача владельцу: открыть https://github.com/gaztormoz910-alt/proxy-soft-fetch/releases/tag/v4.0.1 -> Edit -> Delete this release, затем подтвердить закрытие командой python tools/verify_repo.py --releases (проверка уже написана и сейчас честно падает).
