import getpass
import io
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CI_SAFE_USERS = {
    'runneradmin',
    'runner',
    'actions',
    'vscode',
    'root',
    'system',
    'administrator',
    'defaultuser0',
    'proxypulse',
    'proxypulse@localhost',
}

_WIN_USER_RX = re.compile(
    r'(?<![A-Za-z0-9_])[A-Za-z]:\\' + 'Users' + r'\\[^\\\s"\'`<>|]+',
    re.IGNORECASE,
)
_POSIX_HOME_RX = re.compile(
    r'(?<![A-Za-z0-9_/])/(?:home|' + 'Users)/[A-Za-z0-9_.-]+'
)
TOKEN = re.compile(r'(?:gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{20,})')

_STATIC_RULES = (
    ('Windows user path', _WIN_USER_RX),
    ('POSIX home path', _POSIX_HOME_RX),
    ('AI instruction file marker', re.compile(r'\b' + 'CL' + 'AUDE' + r'\.md\b', re.IGNORECASE)),
    ('Process ledger marker', re.compile(r'\b' + 'GA' + 'TES' + r'\.md\b', re.IGNORECASE)),
    ('Audit doc marker', re.compile(r'\b' + 'AU' + 'DIT' + r'\.md\b', re.IGNORECASE)),
    ('Report doc marker', re.compile(r'\b' + 'RE' + 'PORT' + r'\.md\b', re.IGNORECASE)),
    ('Process dir marker', re.compile(r'(?<![A-Za-z0-9_])\.' + 'un' + 'lazy' + r'(?![A-Za-z0-9_])', re.IGNORECASE)),
    ('AI trailer marker', re.compile(r'co-' + 'authored-' + 'by:', re.IGNORECASE)),
    ('AI attribution marker', re.compile(r'generated\s+with\s+' + 'cl' + 'aude', re.IGNORECASE)),
)

SKIP_EXT = {
    '.png', '.ico', '.jpg', '.gif', '.svg', '.webp',
    '.exe', '.dll', '.pyd', '.so', '.zip', '.mmdb',
}

INTERNAL_DOCS = (
    'AU' + 'DIT.md',
    'REP' + 'ORT.md',
    'GA' + 'TES.md',
    'GA' + 'TES-scrub.md',
    'SCRUB-REP' + 'ORT.md',
)


def _git(*args):
    return subprocess.check_output(
        ['git'] + list(args),
        cwd=ROOT,
        text=True,
        encoding='utf-8',
        errors='replace',
    )


def _collect_dynamic_markers():
    markers = set()
    candidates = [
        os.environ.get('USERNAME', ''),
        os.environ.get('USER', ''),
        Path.home().name,
    ]
    try:
        candidates.append(getpass.getuser())
    except Exception:
        pass
    try:
        for key in ('user.name', 'user.email'):
            val = subprocess.check_output(
                ['git', 'config', '--get', key],
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            if val:
                candidates.append(val)
                if '@' in val:
                    candidates.append(val.split('@', 1)[0])
    except Exception:
        pass
    for env_key in ('PRIVATE_MARKERS', 'SCRUB_MARKERS'):
        raw = os.environ.get(env_key, '')
        for part in raw.split(','):
            part = part.strip()
            if part:
                candidates.append(part)
    for item in candidates:
        low = item.strip().lower()
        if len(low) >= 3 and low not in _CI_SAFE_USERS:
            markers.add(item.strip())
    return sorted(markers, key=len, reverse=True)


def _build_deny_rules(extra_markers=None):
    rules = list(_STATIC_RULES)
    markers = set(_collect_dynamic_markers())
    if extra_markers:
        markers.update(extra_markers)
    for m in sorted(markers, key=len, reverse=True):
        rx = re.compile(r'(?<![A-Za-z0-9_])' + re.escape(m) + r'(?![A-Za-z0-9_])', re.IGNORECASE)
        rules.append(('Local identity marker', rx))
    return rules


def tracked_files():
    files = [f for f in _git('ls-files').splitlines() if f]
    return [f for f in files if os.path.splitext(f)[1].lower() not in SKIP_EXT]


def scan_text_markers(files, extra_markers=None):
    rules = _build_deny_rules(extra_markers=extra_markers)
    hits = []
    for rel in files:
        path = os.path.join(ROOT, rel)
        try:
            with open(path, 'rb') as fh:
                raw = fh.read()
        except OSError:
            continue
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = raw.decode('latin-1')
        for lineno, line in enumerate(text.split('\n'), 1):
            line = line.rstrip('\r')
            for label, rx in rules:
                if rx.search(line):
                    hits.append((rel, lineno, label, line.strip()[:100]))
            if TOKEN.search(line):
                hits.append((rel, lineno, 'GitHub token', line.strip()[:60]))
    return hits


_CRIT = {
    b'IHDR', b'IDAT', b'IEND', b'PLTE', b'tRNS', b'acTL', b'fcTL', b'fdAT',
    b'bKGD', b'pHYs', b'sRGB', b'gAMA', b'cHRM', b'sBIT',
}


def _scan_png_chunks(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return []
    i, found = 8, []
    while i + 8 <= len(data):
        ln = struct.unpack('>I', data[i:i + 4])[0]
        typ = data[i + 4:i + 8]
        if typ not in _CRIT:
            found.append(typ.decode('latin-1', 'replace'))
        i += 12 + ln
        if typ == b'IEND':
            break
    return found


def scan_assets():
    hits = []
    adir = os.path.join(ROOT, 'assets')
    for base, _dirs, names in os.walk(adir):
        for n in names:
            p = os.path.join(base, n)
            rel = os.path.relpath(p, ROOT).replace('\\', '/')
            low = n.lower()
            if low.endswith('.png'):
                with open(p, 'rb') as fh:
                    data = fh.read()
                for c in _scan_png_chunks(data):
                    hits.append((rel, c))
            elif low.endswith('.ico'):
                with open(p, 'rb') as fh:
                    d = fh.read()
                if len(d) < 6:
                    continue
                cnt = struct.unpack('<H', d[4:6])[0]
                for k in range(cnt):
                    off = 6 + k * 16
                    if off + 16 > len(d):
                        break
                    sz = struct.unpack('<I', d[off + 8:off + 12])[0]
                    o = struct.unpack('<I', d[off + 12:off + 16])[0]
                    frame = d[o:o + sz]
                    for c in _scan_png_chunks(frame):
                        hits.append(('%s[%d]' % (rel, k), c))
    return hits


def version_resource_clean():
    path = os.path.join(ROOT, 'version_info.txt')
    if not os.path.exists(path):
        return ['version_info.txt missing']
    text = io.open(path, encoding='utf-8', errors='replace').read()
    bad = []
    for label, rx in _build_deny_rules():
        if rx.search(text):
            bad.append('version_info.txt contains %s' % label)
    for forbidden in ('LegalCopyright', 'Copyright', '@author', 'Author'):
        if forbidden in text:
            bad.append('version_info.txt contains field %s' % forbidden)
    return bad


def settings_not_tracked():
    bad = []
    if 'settings.json' in _git('ls-files').splitlines():
        bad.append('settings.json is tracked by git')
    return bad


def internal_docs_not_tracked():
    tracked = set(_git('ls-files').splitlines())
    return ['internal document is tracked by git: %s' % d for d in INTERNAL_DOCS if d in tracked]


def history_problems():
    probs = []
    rules = _build_deny_rules()
    ids = set()
    for line in _git('log', '--all', '--format=%an|%ae|%cn|%ce').splitlines():
        if line.strip():
            ids.add(line)
    nonneutral = [x for x in ids if any(rx.search(x) for _l, rx in rules)]
    if nonneutral:
        probs.append('identity leak in commit authors: %d entries' % len(nonneutral))
    tzs = set()
    for line in _git('log', '--all', '--format=%ai').splitlines():
        m = re.search(r'([+-]\d{4})\s*$', line)
        if m:
            tzs.add(m.group(1))
    offtz = sorted(t for t in tzs if t != '+0000')
    if offtz:
        probs.append('non-UTC timezone in commits: %s' % ', '.join(offtz))
    body = _git('log', '--all', '--format=%b')
    ai_tr = re.compile(r'co-' + r'authored-by|generated\s+with|signed-' + r'off-by', re.I)
    if ai_tr.search(body):
        probs.append('AI/sign-off trailers found in commit messages')
    annotated = [
        ln for ln in _git('for-each-ref', '--format=%(objecttype) %(refname:short)', 'refs/tags').splitlines()
        if ln.startswith('tag ')
    ]
    if annotated:
        probs.append('annotated tags found: %d' % len(annotated))
    return probs


def selftest():
    fails = []
    rules = _build_deny_rules(extra_markers=['sample_user'])
    dirty = 'C:' + '\\' + 'Users\\sample_user\\Desktop ghp_' + ('A' * 36)
    caught = any(rx.search(dirty) for _l, rx in rules) and TOKEN.search(dirty)
    if not caught:
        fails.append('text detector failed on synthetic dirty input')

    clean = 'proxy checker output_dir results elite http://pubproxy.com'
    if any(rx.search(clean) for _l, rx in rules) or TOKEN.search(clean):
        fails.append('text detector false positive on clean input')

    def _png(chunks):
        out = b'\x89PNG\r\n\x1a\n'
        for typ, body in chunks:
            out += struct.pack('>I', len(body)) + typ + body + b'\x00\x00\x00\x00'
        return out

    dirty_png = _png([(b'IHDR', b'\x00' * 13), (b'tEXt', b'Software\x00GIMP'), (b'IEND', b'')])
    clean_png = _png([(b'IHDR', b'\x00' * 13), (b'IDAT', b'x'), (b'IEND', b'')])
    if not _scan_png_chunks(dirty_png):
        fails.append('PNG detector missed tEXt chunk')
    if _scan_png_chunks(clean_png):
        fails.append('PNG detector false positive on clean PNG')
    return fails


def run_surface():
    ok = True
    hits = scan_text_markers(tracked_files())
    if hits:
        ok = False
        print('  TRACES in tracked files:')
        for rel, ln, label, snippet in hits:
            print('    %s:%d  [%s]  %s' % (rel, ln, label, snippet))
    else:
        print('  tracked files: clean')

    ameta = scan_assets()
    if ameta:
        ok = False
        print('  IMAGE METADATA:')
        for rel, chunk in ameta:
            print('    %s  chunk %s' % (rel, chunk))
    else:
        print('  images (PNG/ICO): clean')

    vbad = version_resource_clean()
    if vbad:
        ok = False
        for b in vbad:
            print('  VERSION RESOURCE: %s' % b)
    else:
        print('  version resource: neutral')

    sbad = settings_not_tracked()
    if sbad:
        ok = False
        for b in sbad:
            print('  SECRETS: %s' % b)
    else:
        print('  settings.json: untracked')

    dbad = internal_docs_not_tracked()
    if dbad:
        ok = False
        for b in dbad:
            print('  INTERNAL DOCS: %s' % b)
    else:
        print('  internal docs: absent')

    if ok:
        print('SCRUB SURFACE OK')
    return ok


def run_history():
    probs = history_problems()
    if probs:
        print('  history NOT clean:')
        for p in probs:
            print('    - %s' % p)
        return False
    print('SCRUB HISTORY OK')
    return True


def run_selftest():
    fails = selftest()
    if fails:
        for f in fails:
            print('  SELFTEST FAILED: %s' % f)
        return False
    print('SCRUB SELFTEST OK')
    return True


MODES = {'--verify': run_surface, '--history': run_history, '--selftest': run_selftest}

if __name__ == '__main__':
    args = sys.argv[1:] or ['--verify']
    if args == ['--all']:
        args = ['--selftest', '--verify', '--history']
    bad_mode = [a for a in args if a not in MODES]
    if bad_mode:
        print('modes: %s | --all' % ' '.join(sorted(MODES)))
        sys.exit(2)
    rc = 0
    for a in args:
        print('== %s ==' % a)
        if not MODES[a]():
            rc = 1
    sys.exit(rc)
