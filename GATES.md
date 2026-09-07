# Gates: закрыть хвосты — везде одна актуальная версия

OWNS: .github/**, assets/**, tools/**, gui.py, ProxyPulse.iss, ProxyPulse.spec, build.ps1, VERSION, GATES.md

Scope: обе ветки на обоих удалённых репозиториях содержат последний код; номер
версии живёт в одном месте и совпадает в окне, в свойствах .exe и в
установщике; собранная программа проходит настоящий прогон конвейера;
опубликованный релиз — текущая версия, ставится и работает; битый релиз
удалён.

- [ ] G1: main и рабочая ветка на публичном репозитории совпадают с HEAD
  CHECK: python tools/verify_repo.py --public
  EXPECT: PUBLIC REPO OK
  EVIDENCE: pending

- [ ] G2: приватный репозиторий содержит тот же коммит
  CHECK: python tools/verify_repo.py --private
  EXPECT: PRIVATE REPO OK
  EVIDENCE: pending

- [ ] G3: рабочее дерево чистое, а содержимое сборки совпадает с тегом текущей версии
  CHECK: python tools/verify_repo.py --clean
  EXPECT: WORKTREE OK
  EVIDENCE: pending

- [ ] G4: установщик по постоянной ссылке ставится, запускается, иконка и версия совпадают с репозиторием
  CHECK: python tools/verify_release.py
  EXPECT: RELEASE OK
  EVIDENCE: pending

- [ ] G5: номер версии совпадает в файле, в сборке, в свойствах .exe, в записи деинсталляции и в заголовке окна
  CHECK: python tools/verify_version.py
  EXPECT: VERSION OK
  EVIDENCE: pending

- [ ] G6: установленная программа проходит настоящий прогон конвейера и пишет результаты
  CHECK: python tools/verify_pipeline.py
  EXPECT: PIPELINE OK
  EVIDENCE: pending

- [ ] G7: битого релиза v4.0.1 больше нет, последний релиз совпадает с текущей версией
  CHECK: python tools/verify_repo.py --releases
  EXPECT: RELEASES OK
  EVIDENCE: pending
