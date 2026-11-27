"""Genera los PDF de columnas con la plantilla habitual (Lora, azul marino, 90x160 mm)."""
import json, math, re, sys, html
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
                                PageBreak, KeepTogether, Flowable, CondPageBreak)
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.lib.colors import HexColor, black

F = '/home/claude/fonts/'
for name in ['Lora-Regular', 'Lora-Bold', 'Lora-Italic', 'Lora-BoldItalic']:
    pdfmetrics.registerFont(TTFont(name, F + name + '.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif', '/usr/share/fonts/truetype/freefont/FreeSerif.ttf'))
addMapping('Lora-Regular', 0, 0, 'Lora-Regular')
addMapping('Lora-Regular', 1, 0, 'Lora-Bold')
addMapping('Lora-Regular', 0, 1, 'Lora-Italic')
addMapping('Lora-Regular', 1, 1, 'Lora-BoldItalic')

W, H = 90 * mm, 160 * mm
M = 8 * mm                      # margen del marco (la regla va a esta altura)
import os
NAVY_HEX = os.environ.get('PDF_COLOR', '#24385B')
NAVY = HexColor(NAVY_HEX)
KICKER = 'Las Reglas del Juego'
TOP_PAD = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0

ST = {
    'kicker': ParagraphStyle('kicker', fontName='Lora-Regular', fontSize=9, leading=15, textColor=NAVY),
    'title': ParagraphStyle('title', fontName='Lora-Regular', fontSize=22, leading=28, textColor=NAVY,
                            spaceBefore=4, spaceAfter=6),
    'deck': ParagraphStyle('deck', fontName='Lora-Italic', fontSize=10.5, leading=15, textColor=black,
                           spaceAfter=8),
    'lectura': ParagraphStyle('lectura', fontName='Lora-Regular', fontSize=9, leading=15, textColor=NAVY,
                              spaceAfter=4),
    'body': ParagraphStyle('body', fontName='Lora-Regular', fontSize=12.5, leading=17, alignment=TA_JUSTIFY,
                           spaceAfter=8, textColor=black, allowWidows=0, allowOrphans=0),
    'li': ParagraphStyle('li', fontName='Lora-Regular', fontSize=12.5, leading=17, alignment=TA_JUSTIFY,
                         spaceAfter=8, leftIndent=11, bulletIndent=0, textColor=black, allowWidows=0, allowOrphans=0,
                         bulletFontName='Lora-Regular', bulletColor=NAVY, bulletFontSize=12.5),
    'sub': ParagraphStyle('sub', fontName='Lora-Bold', fontSize=12, leading=16, textColor=NAVY,
                          spaceBefore=6, spaceAfter=5, alignment=TA_LEFT),
    'book': ParagraphStyle('book', fontName='Lora-Regular', fontSize=12.5, leading=17, textColor=NAVY,
                           spaceBefore=6, spaceAfter=4, alignment=TA_LEFT),
    'where': ParagraphStyle('where', fontName='Lora-Italic', fontSize=10.5, leading=15, textColor=black,
                            spaceAfter=8, alignment=TA_LEFT),
    'pq': ParagraphStyle('pq', fontName='Lora-Italic', fontSize=12.5, leading=17, alignment=TA_CENTER,
                         textColor=black, spaceBefore=2, spaceAfter=2),
    'closing': ParagraphStyle('closing', fontName='Lora-Italic', fontSize=14, leading=20, alignment=TA_CENTER,
                              textColor=NAVY),
    'by': ParagraphStyle('by', fontName='Lora-Regular', fontSize=9, leading=13, textColor=black),
}

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre',
         'octubre', 'noviembre', 'diciembre']


def fecha_larga(iso):
    y, m, d = iso.split('-')
    return f'{int(d)} de {MESES[int(m) - 1]} de {y}'


def markup(s):
    """Convierte **negrita** y _cursiva_ a etiquetas de ReportLab."""
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s, flags=re.S)
    s = re.sub(r'_(.+?)_', r'<i>\1</i>', s, flags=re.S)
    return s.replace('\n', '<br/>')


def plain(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s, flags=re.S)
    s = re.sub(r'_(.+?)_', r'\1', s, flags=re.S)
    return s


class Centered(Flowable):
    """Ocupa la página y dibuja su contenido centrado en la altura de la página."""
    def __init__(self, para):
        super().__init__()
        self.para = para

    def wrap(self, aw, ah):
        self.aw, self.ah = aw, ah
        self.pw, self.ph = self.para.wrap(aw - 16, ah)
        return aw, ah

    def draw(self):
        # coordenadas locales: el marco empieza en y=M; centramos respecto de la página
        page_center_local = H / 2 - M - self.ah * 0 - (TOP_PAD if False else 0)
        frame_bottom = M + 6  # padding inferior por defecto del Frame
        y_local = (H / 2 - frame_bottom) - self.ph / 2
        self.para.drawOn(self.canv, 8, y_local)


def on_page(canv, doc):
    canv.saveState()
    canv.setStrokeColor(NAVY)
    canv.setLineWidth(0.5)
    canv.line(M, H - M, W - M, H - M)
    canv.restoreState()


def build(art, outpath):
    story = []
    words = 0
    blocks = art['blocks']
    deck = art.get('deck')
    closing = art['closing'] or ''
    for t in [deck or '', closing] + [b[1] for b in blocks]:
        words += len(plain(t).split())
    minutes = art.get('minutes') or max(1, math.ceil(words / 200))

    story.append(Paragraph(KICKER, ST['kicker']))
    story.append(Paragraph('OPINIÓN', ST['kicker']))
    story.append(Paragraph(html.escape(art['title']), ST['title']))
    if deck:
        story.append(Paragraph(markup(plain(deck)) if '<br/>' not in deck else deck, ST['deck']))
    story.append(Paragraph(f'Lectura: {minutes} min', ST['lectura']))

    for kind, text in blocks:
        t = text if kind in ('raw',) else markup(text)
        for old, new in art.get('post', []):
            t = t.replace(old, new)
        # espacios de no separación: cifra y %, moneda y cifra
        t = re.sub(r'(\d) %', '\\1\u00a0%', t)
        t = re.sub(r'(S/|US\$|€) (\d)', '\\1\u00a0\\2', t)
        if kind == 'p':
            story.append(Paragraph(t, ST['body']))
        elif kind == 'li':
            story.append(Paragraph(t, ST['li'], bulletText='•'))
        elif kind == 'sub':
            story.append(CondPageBreak(66))
            story.append(Paragraph(t, ST['sub']))
        elif kind == 'book':
            story.append(CondPageBreak(66))
            story.append(Paragraph(t, ST['book']))
        elif kind == 'where':
            story.append(Paragraph(f'<font name="Lora-Regular" color="{NAVY_HEX}">•</font>&nbsp;&nbsp;' + t,
                                   ST['where']))
        elif kind == 'pq':
            story.append(KeepTogether([
                HRFlowable(width='100%', thickness=0.5, color=NAVY, spaceBefore=4, spaceAfter=9),
                Paragraph(t, ST['pq']),
                HRFlowable(width='100%', thickness=0.5, color=NAVY, spaceBefore=9, spaceAfter=12),
            ]))
        else:
            raise ValueError(kind)

    story.append(PageBreak())
    if closing:
        story.append(Centered(Paragraph(html.escape(closing).replace('\n', '<br/>'), ST['closing'])))
        story.append(PageBreak())
    story.append(Paragraph(f'<font color="{NAVY_HEX}">Manuel Sotomayor de Azambuja</font>', ST['by']))
    story.append(Paragraph('Empresario. Ex-Presidente de CONFIEP', ST['by']))
    story.append(Paragraph('www.manuelsotomayor.com', ST['by']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(KICKER, ST['by']))
    story.append(Paragraph(f'<font name="Lora-Italic" color="{NAVY_HEX}">Publicado en El Reporte el '
                           f'{fecha_larga(art["date"])}</font>', ST['by']))

    doc = BaseDocTemplate(outpath, pagesize=(W, H), leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
                          title=art['title'], author='Manuel Sotomayor de Azambuja',
                          subject='Las Reglas del Juego · El Reporte', creator='Las Reglas del Juego')
    frame = Frame(M, M, W - 2 * M, H - 2 * M - TOP_PAD + 6, id='f', topPadding=6)
    doc.addPageTemplates([PageTemplate(id='p', frames=[frame], onPage=on_page)])
    doc.build(story)
    return words, minutes


if __name__ == '__main__':
    cfg = json.load(open(sys.argv[1]))
    only = sys.argv[2] if len(sys.argv) > 2 else 'all'
    for art in cfg:
        if only != 'all' and str(art['n']) not in only.split(','):
            continue
        out = os.path.join(os.environ.get("PDF_OUT", "/home/claude/out"), art["file"])
        w, m = build(art, out)
        print(art['n'], art['file'], 'palabras', w, 'min', m)
