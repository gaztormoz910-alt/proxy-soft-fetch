"""Сборка assets/ProxyPulse.ico из одной картинки — assets/ProxyPulse.png.

Запуск:  python tools/make_icon.py

Одна и та же исходная картинка на всех размерах. Никакого перерисовывания
мелких размеров: если на 16 px что-то плохо читается, это свойство самого
рисунка, а не пайплайна.

Почему уменьшение идёт через линейный свет
------------------------------------------
sRGB — нелинейная шкала: значение 128 это не половина яркости, а примерно
21 процент. Наивное усреднение соседних пикселей при уменьшении складывает
эти закодированные числа напрямую, и яркие тонкие линии на тёмном фоне
теряют яркость. Замерено на этой картинке до исправления: -33 процента
средней яркости на 16 px, -23 на 24 px. Именно так неоновое кольцо и
превращалось в тусклую грязь.

Правильный порядок: sRGB -> линейный свет -> премультипликация на альфу ->
уменьшение -> обратно. Премультипликация обязательна: без неё полностью
прозрачные пиксели за краем плитки вносят свой чёрный цвет в края.
"""
import numpy as np
from PIL import Image, ImageFilter

MASTER = 'assets/ProxyPulse.png'
OUT    = 'assets/ProxyPulse.ico'

# Размеры, которые реально запрашивает Windows: 16/20/24 — заголовок окна и
# трей при 100/125/150 процентах масштаба, 32/40/48 — панель задач и рабочий
# стол, 64/96 — крупные значки в проводнике, 128/256 — плитки и предпросмотр.
SIZES = (256, 128, 96, 64, 48, 40, 32, 24, 20, 16)

# Лёгкая резкость возвращает контраст границ, съеденный ресемплингом.
# (радиус, сила). Применяется В ЛИНЕЙНОМ СВЕТЕ, до перевода обратно в sRGB:
# та же операция в sRGB несимметрична по энергии — светлый ореол добавляет
# больше, чем тёмный забирает, и средняя яркость уезжала на +14% на 48 px.
SHARPEN = {16: (0.5, 0.45), 20: (0.5, 0.45), 24: (0.55, 0.40),
           32: (0.6, 0.35), 40: (0.6, 0.30), 48: (0.7, 0.25)}


def _srgb_to_linear(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(a):
    a = np.clip(a, 0.0, 1.0)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)


def _blur(ch, radius):
    """Разделимое гауссово размытие.

    Своё, а не из Pillow: его GaussianBlur не работает с режимом 'F', а
    переводить линейные значения в 8 бит ради размытия — терять именно ту
    точность, ради которой всё и затевалось.
    """
    sigma = max(float(radius), 1e-6)
    n = int(np.ceil(3 * sigma))
    x = np.arange(-n, n + 1, dtype=np.float64)
    k = np.exp(-(x * x) / (2 * sigma * sigma))
    k /= k.sum()
    pad = np.pad(ch, n, mode='edge')
    rows = np.apply_along_axis(lambda m: np.convolve(m, k, mode='valid'), 1, pad)
    return np.apply_along_axis(lambda m: np.convolve(m, k, mode='valid'), 0, rows)


def _sharpen_linear(ch, radius, amount):
    """Нерезкое маскирование прямо в линейных значениях."""
    return np.clip(ch + amount * (ch - _blur(ch, radius)), 0.0, None)


def resize_linear(img, size, sharpen=None):
    """Уменьшение в линейном свете с премультиплицированной альфой."""
    arr = np.asarray(img.convert('RGBA'), dtype=np.float64) / 255.0
    rgb, alpha = arr[..., :3], arr[..., 3]
    lin = _srgb_to_linear(rgb) * alpha[..., None]

    planes = []
    for ch in (lin[..., 0], lin[..., 1], lin[..., 2], alpha):
        # mode 'F' — единственный способ отдать Pillow дробные значения без
        # округления до 8 бит: в линейном пространстве тёмные тона занимают
        # такой узкий диапазон, что 8 бит дали бы полосы.
        f = Image.fromarray(ch.astype(np.float32), mode='F')
        planes.append(np.asarray(f.resize((size, size), Image.LANCZOS),
                                 dtype=np.float64))

    out_a = np.clip(planes[3], 0.0, 1.0)
    safe = np.where(out_a > 1e-6, out_a, 1.0)          # деление на ноль в прозрачном
    out_rgb = np.stack(planes[:3], axis=-1) / safe[..., None]
    out_rgb = np.where(out_a[..., None] > 1e-6, out_rgb, 0.0)

    if sharpen:
        radius, amount = sharpen
        sharp = np.stack([_sharpen_linear(out_rgb[..., i], radius, amount)
                          for i in range(3)], axis=-1)
        # Тёмная половина ореола упирается в ноль и обрезается, светлая — нет,
        # поэтому на тёмном фоне резкость молча добавляет яркости (замерено:
        # +6.5% на 32 px). Возвращаем исходную энергию: резкость обязана
        # перераспределять контраст, а не подсвечивать картинку.
        w = out_a[..., None]
        before = float((out_rgb * w).sum())
        after = float((sharp * w).sum())
        if after > 1e-9:
            sharp *= before / after
        out_rgb = np.clip(sharp, 0.0, 1.0)

    srgb = _linear_to_srgb(out_rgb)
    data = np.concatenate([srgb, out_a[..., None]], axis=-1)
    return Image.fromarray(np.round(data * 255).astype(np.uint8), mode='RGBA')


def build(master=MASTER, out=OUT):
    src = Image.open(master).convert('RGBA')
    frames = []
    for s in SIZES:
        frames.append(resize_linear(src, s, SHARPEN.get(s)))
    frames[0].save(out, format='ICO', sizes=[(s, s) for s in SIZES],
                   append_images=frames[1:])
    print('%s <- %s %s' % (out, master, src.size))
    print('размеры: %s' % ', '.join('%d' % s for s in sorted(SIZES)))


if __name__ == '__main__':
    build()
