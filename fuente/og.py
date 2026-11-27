"""Imágenes de vista previa (1200×630) para WhatsApp y redes: verde Sotomayor, título en Lora y la regla con la columna marcada."""
from PIL import Image, ImageDraw, ImageFont
import datetime as dt

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

def card(path, title, dates, mark, foot_right, kicker='Las Reglas del Juego'):
    im = Image.new('RGBA', (W, H), GREEN + (255,))
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
