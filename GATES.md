# Gates: закрыть хвосты — везде одна актуальная версия

OWNS: .github/**, assets/**, tools/**, gui.py, ProxyPulse.iss, ProxyPulse.spec, build.ps1, VERSION, GATES.md

Scope: обе ветки на обоих удалённых репозиториях содержат последний код; номер
версии живёт в одном месте и совпадает в окне, в свойствах .exe и в
установщике; собранная программа проходит настоящий прогон конвейера;
опубликованный релиз — текущая версия, ставится и работает; битый релиз
удалён.

- [x] G1: main в публичном репозитории содержит тот же коммит, что и рабочая ветка
  CHECK: python tools/verify_repo.py --public
  EXPECT: PUBLIC REPO OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=d21272377c32106ba4f2d76d042bb06c4979b291e8d7d63e74bc0966a549a4f3; output-bytes=201

- [x] G2: приватный репозиторий содержит тот же коммит
  CHECK: python tools/verify_repo.py --private
  EXPECT: PRIVATE REPO OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=cd271f0903115208bf1f8db59bc41a4f7ab62be48e75627e8ad6ea32b79f2ac6; output-bytes=202

- [x] G3: номер версии задан в одном месте и совпадает в окне, в свойствах .exe и в установщике
  CHECK: python tools/verify_version.py
  EXPECT: VERSION OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=bf6aeaf33c1ec9b960ec9a84ffb0240dd1df7e3c8bf4f28d5202745eec6ec75d; output-bytes=252

- [x] G4: собранная программа проходит настоящий прогон конвейера и пишет результаты
  CHECK: python tools/verify_pipeline.py
  EXPECT: PIPELINE OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=05e8eaf938d2f1cba79c9a02a5c95cc665fa1444f86fecede0418ca3d57db072; output-bytes=1386

- [x] G5: релиз по постоянной ссылке — текущая версия, ставится, запускается, иконка совпадает с репозиторием
  CHECK: python tools/verify_release.py
  EXPECT: RELEASE OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=8b599c09f18cdcc5ad96535e826011b9050eef9f510d4cd40d170b8cfd404224; output-bytes=449

- [x] G6: рабочее дерево чистое, тег текущей версии есть на публичном репозитории
  CHECK: python tools/verify_repo.py --clean
  EXPECT: WORKTREE OK
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\Bog_1\OneDrive\Desktop\Fetch Free Proxy; path=d0a34a25a4a7/53 entries; EXPECT=matched; output-sha256=72afaf31cafe7ec189ec9a44b4d5853efcbc00e11534b633e1390420dfc07963; output-bytes=99

- [ ] G7: битого релиза v4.0.1 больше нет, последний релиз совпадает с текущей версией
  CHECK: python tools/verify_repo.py --releases
  EXPECT: RELEASES OK
  EVIDENCE: pending
