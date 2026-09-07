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
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=98e235a2adf9c52844c0bc83e4d70bb915c73a97e77a4d2fe83b14db5dab9bd7; output-bytes=201

- [x] G2: приватный репозиторий содержит тот же коммит
  CHECK: python tools/verify_repo.py --private
  EXPECT: PRIVATE REPO OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=8c0046ed4e42f08e62b8586a165cdaf042bf576a276350baad77e6c5776e685c; output-bytes=202

- [ ] G3: рабочее дерево чистое, а содержимое сборки совпадает с тегом текущей версии
  CHECK: python tools/verify_repo.py --clean
  EXPECT: WORKTREE OK
  EVIDENCE: pending

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
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=6ae63a49be0f42227eb45be4d32e2849ad8d38913bd1bbcaea08603633ac7df7; output-bytes=1412

- [ ] G7: битого релиза v4.0.1 больше нет, последний релиз совпадает с текущей версией
  CHECK: python tools/verify_repo.py --releases
  EXPECT: RELEASES OK
  EVIDENCE: pending
