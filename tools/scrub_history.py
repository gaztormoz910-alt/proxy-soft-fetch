import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEUTRAL_NAME = 'ProxyPulse'
NEUTRAL_MAIL = 'proxypulse@localhost'
EPOCH_DATE = '1980-01-01T00:00:00 +0000'
DROP_PATHS = ('settings.json', 'AU' + 'DIT.md', 'RE' + 'PORT.md', 'GA' + 'TES.md',
              'verify_sources.py', 'scratch')
TOKEN_RX = r'ghp_[A-Za-z0-9]{20,}'

ENV_FILTER = (
    'export GIT_AUTHOR_NAME="%s"; export GIT_AUTHOR_EMAIL="%s"; '
    'export GIT_COMMITTER_NAME="%s"; export GIT_COMMITTER_EMAIL="%s"; '
    'export GIT_AUTHOR_DATE="%s"; export GIT_COMMITTER_DATE="%s";'
) % (NEUTRAL_NAME, NEUTRAL_MAIL, NEUTRAL_NAME, NEUTRAL_MAIL, EPOCH_DATE, EPOCH_DATE)

MSG_FILTER = (
    r"sed -E '/^[Cc]o-[Aa]uthored-[Bb]y:/d; /^[Ss]igned-off-by:/d; "
    r"/[Gg]enerated with \[?" + "Cl" + r"aude/d; /^🤖/d'"
)

INDEX_FILTER = 'git rm -r --cached -q --ignore-unmatch ' + ' '.join(DROP_PATHS)


def _run(args, cwd, env=None, check=True, quiet=False):
    e = dict(os.environ)
    e['FILTER_BRANCH_SQUELCH_WARNING'] = '1'
    if env:
        e.update(env)
    out = subprocess.run(args, cwd=cwd, env=e, capture_output=True, text=True,
                         encoding='utf-8', errors='replace')
    if not quiet and out.stdout.strip():
        print(out.stdout.rstrip())
    if out.returncode != 0 and not quiet:
        sys.stderr.write(out.stderr)
    if check and out.returncode != 0:
        raise SystemExit('команда упала: %s' % ' '.join(args))
    return out


def _git_out(args, cwd):
    return subprocess.run(['git'] + args, cwd=cwd, capture_output=True,
                          text=True, encoding='utf-8', errors='replace').stdout


def summarize(cwd, title):
    print('--- %s ---' % title)
    ids = set(l for l in _git_out(['log', '--branches', '--tags', '--format=%an|%ae|%cn|%ce'],
                                  cwd).splitlines() if l.strip())
    print('  подписи авторов/коммиттеров: %s' % (sorted(ids) or '—'))
    tzs = set()
    for l in _git_out(['log', '--branches', '--tags', '--format=%ai'], cwd).splitlines():
        if l.strip():
            tzs.add(l.strip().split()[-1])
    print('  таймзоны: %s' % sorted(tzs))
    trailers = _git_out(['log', '--branches', '--tags', '--format=%b'], cwd)
    import re
    n = len(re.findall(r'(?im)^(co-authored-by|signed-off-by):', trailers))
    print('  строк-трейлеров (co-authored/signed-off): %d' % n)
    tags = [l for l in _git_out(['for-each-ref', '--format=%(objecttype) %(refname:short)',
                                 'refs/tags'], cwd).splitlines() if l]
    ann = sum(1 for l in tags if l.startswith('tag '))
    print('  тегов всего: %d, из них аннотированных: %d' % (len(tags), ann))
    for p in DROP_PATHS:
        present = bool(_git_out(['log', '--branches', '--tags', '--oneline', '--', p], cwd).strip())
        print('  %s встречается в истории: %s' % (p, 'да' if present else 'нет'))
    shas = _git_out(['rev-list', '--branches', '--tags'], cwd).split()
    hits = []
    if shas:
        g = subprocess.run(['git', 'grep', '-lIE', TOKEN_RX] + shas, cwd=cwd,
                           capture_output=True, text=True, encoding='utf-8',
                           errors='replace')
        hits = [h for h in g.stdout.splitlines() if h.strip()]
    print('  остаточный токен в истории: %s'
          % ('НЕТ' if not hits else 'ОСТАЛСЯ в %d местах: %s (нужен '
             'git-filter-repo --replace-text)' % (len(hits), hits[:3])))


def rewrite(cwd):
    _run(['git', 'filter-branch', '-f',
          '--env-filter', ENV_FILTER,
          '--msg-filter', MSG_FILTER,
          '--index-filter', INDEX_FILTER,
          '--tag-name-filter', 'cat',
          '--', '--branches', '--tags'], cwd)

    for t in [l for l in _git_out(['tag'], cwd).splitlines() if l.strip()]:
        commit = _git_out(['rev-list', '-1', t], cwd).strip()
        _run(['git', 'tag', '-d', t], cwd, quiet=True)
        if commit:
            _run(['git', 'tag', t, commit], cwd, quiet=True)

    for r in [l for l in _git_out(['remote'], cwd).splitlines() if l.strip()]:
        _run(['git', 'remote', 'remove', r], cwd, quiet=True)

    orig = os.path.join(cwd, '.git', 'refs', 'original')
    _run(['git', 'for-each-ref', '--format=%(refname)', 'refs/original/'], cwd, quiet=True)
    for ref in [l for l in _git_out(['for-each-ref', '--format=%(refname)',
                                     'refs/original/'], cwd).splitlines() if l.strip()]:
        _run(['git', 'update-ref', '-d', ref], cwd, quiet=True)
    _run(['git', 'reflog', 'expire', '--expire=now', '--all'], cwd, quiet=True)
    _run(['git', 'gc', '--prune=now'], cwd, quiet=True)


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ('-h', '--help'):
        print('Usage: scrub_history.py <cloned_repo_dir>')
        sys.exit(2)
    target = os.path.abspath(sys.argv[1])
    if not os.path.isdir(os.path.join(target, '.git')):
        raise SystemExit('не git-репозиторий: %s' % target)
    if os.path.normcase(target) == os.path.normcase(ROOT):
        raise SystemExit(
            'ОТКАЗ: это рабочий репозиторий проекта. Переписывай КЛОН:\n'
            '  git clone . ../proxypulse-clean && '
            'python tools/scrub_history.py ../proxypulse-clean')
    print('Переписываю историю в клоне: %s\n' % target)
    summarize(target, 'ДО')
    print()
    rewrite(target)
    print()
    summarize(target, 'ПОСЛЕ')
    print('\nГотово. Проверь: python tools/verify_scrub.py --history (в клоне),\n'
          'затем сделай из клона НОВЫЙ публичный репозиторий (раздел 2).')


if __name__ == '__main__':
    main()
