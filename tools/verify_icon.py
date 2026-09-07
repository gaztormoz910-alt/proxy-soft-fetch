"""Проверки иконки для ledger (GATES.md). Каждый режим печатает свой
success-токен только после того, как все утверждения внутри него прошли.

  python tools/verify_icon.py --master           MASTER OK
  python tools/verify_icon.py --single-source    SINGLE SOURCE OK
  python tools/verify_icon.py --negative-control NEGATIVE CONTROL OK
  python tools/verify_icon.py --luminance        LUMINANCE OK
  python tools/verify_icon.py --no-drawing       NO DRAWING OK
"""
import io
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, 'tools')
from make_icon import SIZES, resize_linear   # noqa: E402

# Скрипт запускают из разных оболочек, в том числе из cmd.exe с кодировкой
# cp1252, где обычный print с кириллицей падает на UnicodeEncodeError. Проверка,
# которая зависит от кодировки конкретной консоли, ничего не проверяет.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

MASTER = 'assets/ProxyPulse.png'
ICO    = 'assets/ProxyPulse.ico'

# Порог расхождения кадра с уменьшенным мастером. Смысл: отличить лёгкую
# резкость (единицы уровней) от другого рисунка (десятки). Значение выбрано
# не на глаз — см. режим --negative-control, который меряет обе величины.
SAME_ART_MAX_MAE = 12.0
LUM_MAX_ERROR    = 5.0     # процентов


def _frame(size):
    im = Image.open(ICO)
    im.size = (size, size)
    return im.convert('RGBA')


def _mae(a, b):
    """Среднее отклонение по видимым пикселям, в уровнях 0-255."""
    x = np.asarray(a.convert('RGBA'), dtype=np.float64)
    y = np.asarray(b.convert('RGBA'), dtype=np.float64)
    w = np.maximum(x[..., 3], y[..., 3]) / 255.0
    if w.sum() == 0:
        return 255.0
    d = np.abs(x[..., :3] - y[..., :3]).mean(axis=2)
    return float((d * w).sum() / w.sum())


def _linear_luma(im):
    a = np.asarray(im.convert('RGBA'), dtype=np.float64) / 255.0
    rgb, alpha = a[..., :3], a[..., 3]
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    lum = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    return float((lum * alpha).mean())


def check_master():
    m = Image.open(MASTER)
    assert m.size == (1147, 1147), 'мастер %s, ожидалось 1147x1147' % (m.size,)
    assert m.mode in ('RGBA', 'LA'), 'мастер без альфа-канала: %s' % m.mode
    print('мастер: %s %s' % (m.size, m.mode))
    print('MASTER OK')


def check_single_source():
    have = sorted(Image.open(ICO).ico.sizes())
    want = sorted((s, s) for s in SIZES)
    assert have == want, 'размеры в .ico: %s, ожидалось %s' % (have, want)
    src = Image.open(MASTER).convert('RGBA')
    worst = 0.0
    for s in SIZES:
        mae = _mae(_frame(s), resize_linear(src, s))
        worst = max(worst, mae)
        print('  %3d px: расхождение с мастером %.2f уровня' % (s, mae))
        assert mae <= SAME_ART_MAX_MAE, \
            '%d px не является уменьшенным мастером (%.2f > %.2f)' % (s, mae, SAME_ART_MAX_MAE)
    print('размеров: %d, худшее расхождение %.2f при пороге %.1f' % (len(SIZES), worst, SAME_ART_MAX_MAE))
    print('SINGLE SOURCE OK')


def check_negative_control():
    """Порог обязан отвергать заведомо другой рисунок.

    Рисуем тот самый упрощённый вариант, который стоял в прошлой версии, и
    убеждаемся, что проверка --single-source его бракует. Без этого контроля
    порог мог бы быть настолько широким, что пропускал бы что угодно.
    """
    from PIL import ImageDraw
    src = Image.open(MASTER).convert('RGBA')
    ss = 12
    fakes = {}
    for s in (16, 24, 32, 48):
        px = s * ss
        im = Image.new('RGBA', (px, px), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        c, r = px / 2, 0.455 * px
        w = max(ss, int(0.115 * px))
        d.ellipse([c - r, c - r, c + r, c + r], outline=(46, 123, 255, 255), width=w)
        X = lambda f: (0.02 + 0.96 * f) * px
        d.line([(X(0), X(.5)), (X(.30), X(.5)), (X(.41), X(.22)),
                (X(.54), X(.80)), (X(.64), X(.5)), (X(1), X(.5))],
               fill=(31, 216, 122, 255), width=w, joint='curve')
        fakes[s] = im.resize((s, s), Image.LANCZOS)

    real_worst, fake_best = 0.0, 1e9
    for s, fake in fakes.items():
        ref = resize_linear(src, s)
        real = _mae(_frame(s), ref)
        bad = _mae(fake, ref)
        real_worst = max(real_worst, real)
        fake_best = min(fake_best, bad)
        print('  %3d px: настоящий %.2f | нарисованный %.2f' % (s, real, bad))
        assert bad > SAME_ART_MAX_MAE, \
            'нарисованный вариант на %d px прошёл бы проверку (%.2f)' % (s, bad)
    assert fake_best > real_worst * 2, \
        'порог не разделяет случаи: настоящий %.2f, чужой %.2f' % (real_worst, fake_best)
    print('разделение: настоящий <= %.2f, чужой >= %.2f, порог %.1f'
          % (real_worst, fake_best, SAME_ART_MAX_MAE))
    print('NEGATIVE CONTROL OK')


def check_luminance():
    """Эталон — средняя яркость самого мастера, посчитанная попиксельно.

    Уменьшать мастер ради эталона нельзя: любой ресемплинг в Pillow считает в
    sRGB и сам занижает яркость, так что эталон получил бы ровно ту ошибку,
    которую проверка ищет. Единственная честная опора — исходник без
    ресемплинга вообще.
    """
    src = Image.open(MASTER).convert('RGBA')
    base = _linear_luma(src)
    worst = 0.0
    for s in SIZES:
        err = (_linear_luma(_frame(s)) / base - 1.0) * 100.0
        worst = max(worst, abs(err))
        print('  %3d px: отклонение яркости %+.1f%%' % (s, err))
        assert abs(err) <= LUM_MAX_ERROR,             '%d px: отклонение яркости %.1f%% при пороге %.1f%%' % (s, err, LUM_MAX_ERROR)
    print('худшее отклонение %.1f%% при пороге %.1f%%' % (worst, LUM_MAX_ERROR))
    print('LUMINANCE OK')


def check_no_drawing():
    """В пайплайне не должно остаться рисования мелких размеров."""
    text = io.open('tools/make_icon.py', encoding='utf-8').read()
    for bad in ('ImageDraw', 'ellipse(', 'def _draw_small'):
        assert bad not in text, 'в make_icon.py осталось рисование: %s' % bad
    assert 'resize_linear' in text, 'в make_icon.py нет линейного ресемплинга'
    print('make_icon.py: рисования нет, ресемплинг линейный')
    print('NO DRAWING OK')


MODES = {'--master': check_master, '--single-source': check_single_source,
         '--negative-control': check_negative_control,
         '--luminance': check_luminance, '--no-drawing': check_no_drawing}

if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] not in MODES:
        print('режимы: %s' % ' '.join(sorted(MODES)))
        sys.exit(2)
    MODES[sys.argv[1]]()
