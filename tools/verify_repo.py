import io
import json
import subprocess
import sys
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

PUBLIC_API = 'https://api.github.com/repos/gaztormoz910-alt/proxy-soft-fetch'
BRANCH = ''
BROKEN_RELEASES = ()

SHIPPED = ('gui.py', 'fetch_proxy.py', 'assets', 'VERSION',
           'ProxyPulse.spec', 'ProxyPulse.iss', 'version_info.txt',
           'requirements.txt', '.github/workflows/release.yml')


def git(*args):
    out = subprocess.run(('git',) + args, capture_output=True, text=True,
                         encoding='utf-8', errors='replace')
    assert out.returncode == 0, 'git %s -> %d: %s' % (
        ' '.join(args), out.returncode, out.stderr.strip())
    return out.stdout.strip()


def head():
    return git('rev-parse', 'HEAD')


def remote_ref(remote, ref):
    line = git('ls-remote', remote, ref)
    return line.split('\t')[0] if line else ''


def api(path):
    req = urllib.request.Request(PUBLIC_API + path,
                                 headers={'Accept': 'application/vnd.github+json'})
    return json.load(urllib.request.urlopen(req, timeout=30))


def version():
    return io.open('VERSION', encoding='utf-8').read().strip()


def _check_remote(remote, label, token):
    h = head()
    refs = ['refs/heads/main']
    if BRANCH:
        refs.append('refs/heads/' + BRANCH)
    for ref in refs:
        got = remote_ref(remote, ref)
        print('  %-8s %-26s %s' % (remote, ref, got[:12] or 'НЕТ'))
        assert got == h, '%s на %s = %s, а HEAD = %s' % (
            ref, remote, got[:12] or 'нет', h[:12])
    print('%s: main указывает на %s' % (label, h[:12]))
    print(token)


def check_public():
    remotes = git('remote').splitlines()
    remote = 'origin' if 'origin' in remotes else 'origin1'
    _check_remote(remote, 'публичный', 'PUBLIC REPO OK')


def check_private():
    _check_remote('origin', 'приватный', 'PRIVATE REPO OK')


def check_clean():
    dirty = git('status', '--porcelain')
    assert not dirty, 'незакоммиченные изменения:\n%s' % dirty
    tag = 'v' + version()
    remotes = git('remote').splitlines()
    remote = 'origin' if 'origin' in remotes else 'origin1'
    got = remote_ref(remote, 'refs/tags/' + tag + '^{}') or remote_ref(remote, 'refs/tags/' + tag)
    h = head()
    print('  рабочее дерево чистое; тег %s -> %s, HEAD %s'
          % (tag, got[:12] or 'НЕТ', h[:12]))
    assert got, 'тега %s нет на публичном репозитории' % tag

    diff = git('diff', '--name-only', got, h, '--', *SHIPPED)
    if diff:
        for path in diff.splitlines():
            print('  расходится: %s' % path)
    assert not diff, 'опубликованный релиз собран не из текущего кода'
    print('  содержимое сборки совпадает с тегом (%d путей сверено)' % len(SHIPPED))
    print('WORKTREE OK')


def check_releases():
    tags = [r['tag_name'] for r in api('/releases')]
    print('  релизы: %s' % ', '.join(tags))
    for bad in BROKEN_RELEASES:
        assert bad not in tags, 'битый релиз %s всё ещё опубликован' % bad
    latest = api('/releases/latest')
    want = 'v' + version()
    print('  latest = %s, ожидалось %s' % (latest['tag_name'], want))
    assert latest['tag_name'] == want, 'последний релиз %s, а текущая версия %s' % (
        latest['tag_name'], want)
    names = [a['name'] for a in latest['assets']]
    print('  ассеты latest: %s' % ', '.join(names))
    assert 'ProxyPulse-setup.exe' in names, 'в последнем релизе нет ProxyPulse-setup.exe'
    print('RELEASES OK')


MODES = {'--public': check_public, '--private': check_private,
         '--clean': check_clean, '--releases': check_releases}

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in MODES:
        print('режимы: %s' % ' '.join(sorted(MODES)))
        sys.exit(2)
    MODES[sys.argv[1]]()
