"""Пересборка assets/ProxyPulse.ico из мастер-картинки.

Запуск:  python tools/make_icon.py

Крупные размеры берутся из assets/ProxyPulse.png как есть. Мелкие (16-48)
рисуются здесь заново, и вот почему: у мастер-картинки тонкое кольцо со
свечением и точечная карта мира. На 24 px — а именно этот размер Windows
просит для заголовка окна — тонкая линия со свечением превращается в грязь,
а карта в шум. Поэтому для мелких размеров рисуется тот же символ, но
плотными линиями во всю площадь и без свечения.
"""
from PIL import Image, ImageDraw, ImageFilter

SS      = 12                      # суперсэмплинг: рисуем крупно, ужимаем — края гладкие
RING    = (46, 123, 255, 255)     # синий, ярче брендового #2563EB: на 16 px нужен контраст
PULSE   = (31, 216, 122, 255)     # зелёный «живого» отклика
BIG     = (256, 128, 64)          # эти размеры — из мастер-картинки
SMALL   = (48, 32, 24, 16)        # эти — рисуются кодом


def _draw_small(size):
    """Символ во всю площадь: кольцо у самого края, толстый пульс, без плитки."""
    px = size * SS
    im = Image.new('RGBA', (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r = px / 2, 0.455 * px
    stroke = max(SS, int(0.115 * px))
    d.ellipse([c - r, c - r, c + r, c + r], outline=RING, width=stroke)
    def X(f): return (0.02 + 0.96 * f) * px
    d.line([(X(0.00), X(0.50)), (X(0.30), X(0.50)), (X(0.41), X(0.22)),
            (X(0.54), X(0.80)), (X(0.64), X(0.50)), (X(1.00), X(0.50))],
           fill=PULSE, width=stroke, joint='curve')
    return im.resize((size, size), Image.LANCZOS)


def build(master='assets/ProxyPulse.png', out='assets/ProxyPulse.ico'):
    src = Image.open(master).convert('RGBA')
    frames = []
    for s in BIG:
        f = src.resize((s, s), Image.LANCZOS)
        if s <= 64:                # после сильного уменьшения края надо вернуть
            f = f.filter(ImageFilter.UnsharpMask(radius=1.0, percent=90, threshold=2))
        frames.append(f)
    frames += [_draw_small(s) for s in SMALL]

    sizes = [(f.width, f.height) for f in frames]
    frames[0].save(out, format='ICO', sizes=sizes, append_images=frames[1:])
    print('%s: %s' % (out, ', '.join('%dx%d' % s for s in sizes)))


if __name__ == '__main__':
    build()
