"""Imágenes de vista previa (1200×630) para WhatsApp y redes: verde Sotomayor, título en Lora y la regla con la columna marcada."""
from PIL import Image, ImageDraw, ImageFont
import datetime as dt
import numpy as np

W, H, M = 1200, 630, 80
GREEN, DEEP, GOLD, WHITE = (29, 114, 86), (18, 63, 49), (240, 199, 102), (255, 255, 255)
FONTS = '/home/claude/fonts'
SANS = '/usr/share/fonts/truetype/google-fonts/ofl/sourcesans3/SourceSans3[wght].ttf'

def sans(size, weight=600):
    f = ImageFont.truetype(SANS, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f

def wrap(draw, text, font, width):
    words, lines, cur = text.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines

def _d(s):
    return dt.date(int(s[:4]), int(s[5:7]), int(s[8:10]))

def ruler(draw, dates, mark, y):
    d0 = dt.date(_d(min(dates)).year, _d(min(dates)).month, 1)
    last = _d(max(dates))
    d1 = dt.date(last.year + (last.month == 12), last.month % 12 + 1, 1)
    span = (d1 - d0).days
    x = lambda d: M + (W - 2 * M) * (d - d0).days / span
    draw.line([(M, y), (W - M, y)], fill=(255, 255, 255, 150), width=2)
    for s in dates:
        if s == mark:
            continue
        xi = x(_d(s))
        draw.line([(xi, y - 2), (xi, y - 46)], fill=(255, 255, 255, 170), width=3)
    if mark:
        xi = x(_d(mark))
        draw.line([(xi, y - 2), (xi, y - 78)], fill=GOLD, width=5)
        draw.ellipse([xi - 7, y - 92, xi + 7, y - 78], fill=GOLD)

_BG = None
def background():
    """Verde con luz arriba a la izquierda, sombra abajo a la derecha, trama de tela y grano: como la web."""
    global _BG
    if _BG is not None:
        return _BG.copy()
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    t = (x / W * 0.55 + y / H * 0.45)[..., None]
    g1, g2, g3 = (np.array(c, np.float32) for c in ((33, 118, 87), (29, 114, 86), (19, 82, 64)))
    col = np.where(t < 0.5, g1 + (g2 - g1) * (t / 0.5), g2 + (g3 - g2) * ((t - 0.5) / 0.5))
    hl = np.clip(1 - np.sqrt((x / W - 0.08) ** 2 + 1.6 * (y / H) ** 2) / 0.6, 0, 1)[..., None] * 0.09
    col = col + (255 - col) * hl
    sh = np.clip(1 - np.sqrt((x / W - 1) ** 2 + 1.4 * (y / H - 1) ** 2) / 0.7, 0, 1)[..., None] * 0.28
    col = col * (1 - sh)
    col[::3, :, :] += (255 - col[::3, :, :]) * 0.035
    col[:, ::3, :] *= 0.94
    col += np.random.default_rng(7).normal(0, 5, (H, W, 1)).astype(np.float32)
    _BG = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), 'RGB').convert('RGBA')
    return _BG.copy()

def card(path, title, dates, mark, foot_right, kicker='Las Reglas del Juego'):
    im = background()
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.text((M, 62), kicker, font=sans(34), fill=GOLD)
    width = W - 2 * M
    for size in (72, 66, 60, 56, 52, 48, 44):
        f = ImageFont.truetype(f'{FONTS}/Lora-Bold.ttf', size)
        lines = wrap(d, title, f, width)
        if len(lines) <= 4:
            break
    lh = int(size * 1.16)
    y = 122
    for ln in lines:
        d.text((M, y), ln, font=f, fill=WHITE)
        y += lh
    ruler(d, dates, mark, H - 128)
    d.text((M, H - 96), 'Manuel Sotomayor de Azambuja', font=ImageFont.truetype(f'{FONTS}/Lora-Regular.ttf', 32), fill=WHITE)
    fr = sans(28, 500)
    d.text((W - M - d.textlength(foot_right, font=fr), H - 92), foot_right, font=fr, fill=(255, 255, 255, 215))
    im = Image.alpha_composite(im, ov).convert('RGB')
    im.save(path, optimize=True)
