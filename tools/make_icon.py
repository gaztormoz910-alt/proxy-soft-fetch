import numpy as np
from PIL import Image, ImageFilter

MASTER = 'assets/ProxyPulse.png'
OUT    = 'assets/ProxyPulse.ico'

SIZES = (256, 128, 96, 64, 48, 40, 32, 24, 20, 16)

SHARPEN = {16: (0.5, 0.45), 20: (0.5, 0.45), 24: (0.55, 0.40),
           32: (0.6, 0.35), 40: (0.6, 0.30), 48: (0.7, 0.25)}


def _srgb_to_linear(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def _linear_to_srgb(a):
    a = np.clip(a, 0.0, 1.0)
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)


def _blur(ch, radius):
    sigma = max(float(radius), 1e-6)
    n = int(np.ceil(3 * sigma))
    x = np.arange(-n, n + 1, dtype=np.float64)
    k = np.exp(-(x * x) / (2 * sigma * sigma))
    k /= k.sum()
    pad = np.pad(ch, n, mode='edge')
    rows = np.apply_along_axis(lambda m: np.convolve(m, k, mode='valid'), 1, pad)
    return np.apply_along_axis(lambda m: np.convolve(m, k, mode='valid'), 0, rows)


def _sharpen_linear(ch, radius, amount):
    return np.clip(ch + amount * (ch - _blur(ch, radius)), 0.0, None)


def resize_linear(img, size, sharpen=None):
    arr = np.asarray(img.convert('RGBA'), dtype=np.float64) / 255.0
    rgb, alpha = arr[..., :3], arr[..., 3]
    lin = _srgb_to_linear(rgb) * alpha[..., None]

    planes = []
    for ch in (lin[..., 0], lin[..., 1], lin[..., 2], alpha):
        f = Image.fromarray(ch.astype(np.float32), mode='F')
        planes.append(np.asarray(f.resize((size, size), Image.LANCZOS),
                                 dtype=np.float64))

    out_a = np.clip(planes[3], 0.0, 1.0)
    safe = np.where(out_a > 1e-6, out_a, 1.0)
    out_rgb = np.stack(planes[:3], axis=-1) / safe[..., None]
    out_rgb = np.where(out_a[..., None] > 1e-6, out_rgb, 0.0)

    if sharpen:
        radius, amount = sharpen
        sharp = np.stack([_sharpen_linear(out_rgb[..., i], radius, amount)
                          for i in range(3)], axis=-1)
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
