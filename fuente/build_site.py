"""Genera la vista previa del sitio (una página con rutas por #nombre) desde data/articles.json.

Salida: /home/claude/preview/index.html + /home/claude/preview/site.json
El mismo renderizador servirá para el sitio estático definitivo (modo 'static').
"""
import json, re, html, os, sys, urllib.parse

ROOT = '/home/claude'
MODE = sys.argv[1] if len(sys.argv) > 1 else 'spa'
BASE = sys.argv[2] if len(sys.argv) > 2 else ''   # '/web' mientras se publica en mfsotomayor-source.github.io/web
OUT = f'{ROOT}/preview' if MODE == 'spa' else f'{ROOT}/dist'
BASE_URL = 'https://www.manuelsotomayor.com'
WA_CHANNEL = 'https://whatsapp.com/channel/0029VbDIPZY3QxS3VSnl8V3x'
os.makedirs(OUT, exist_ok=True)

S = json.load(open(f'{ROOT}/data/articles.json'))
ARTS = S['articles']                      # de la más reciente a la más antigua
BYN = {a['n']: a for a in ARTS}
PIL = {p['key']: p for p in S['pillars']}
PIL_ORDER = ['instituciones', 'economia', 'ideas', 'ia', 'iglesia']
SER = {s['key']: s for s in S['series']}
SHORT = {'instituciones': 'Instituciones', 'economia': 'Economía', 'ideas': 'Historia e ideas',
         'ia': 'Inteligencia artificial', 'iglesia': 'Iglesia'}
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'setiembre',
         'octubre', 'noviembre', 'diciembre']

def esc(s):
    return html.escape(s or '', quote=True)

def md(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t, flags=re.S)
    t = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', t, flags=re.S)
    return t.replace('\n', '<br>')

def fecha(d):
    y, m, dd = d.split('-')
    return f'{int(dd)} de {MESES[int(m) - 1]} de {y}'

def link(name):
    """name: inicio | columnas | c-<slug> | temas | tema-<k> | series | serie-<k> | sobre-mi"""
    if MODE == 'spa':
        return '#' + name
    return BASE + path_of(name)

def path_of(name):
    if name == 'inicio':
        return '/'
    if name.startswith('c-'):
        return f'/columnas/{name[2:]}/'
    if name.startswith('tema-'):
        return f'/temas/{name[5:]}/'
    if name.startswith('serie-'):
        return f'/series/{name[6:]}/'
    return f'/{name}/'

def pillars_of(a):
    return [a['pillar']] + [p for p in a['pillars2'] if p != a['pillar']]

def art_url(a):
    return f'{BASE_URL}/columnas/{a["slug"]}/'

ROMAN = {1: 'I', 2: 'II', 3: 'III'}

def series_tag(a):
    if not a['series']:
        return ''
    s = SER[a['series']]
    part = ''
    if a['part']:
        part = ' (' + a['part'].replace('Artículo ', '') + ')'
    return f'<a class="tag" href="{link("serie-" + s["key"])}">Serie {esc(s["name"])}{esc(part)}</a>'

def item(a, show_pillar=True, extra=''):
    tags = [f'<span>{fecha(a["date"])}</span>', f'<span>{a["minutes"]} min de lectura</span>']
    if show_pillar:
        tags.append(f'<a href="{link("tema-" + a["pillar"])}">{esc(PIL[a["pillar"]]["name"])}</a>')
    if extra:
        tags.insert(0, f'<span>{esc(extra)}</span>')
    return (f'<li data-s="{a["slug"]}" data-p="{" ".join(pillars_of(a))}">'
            f'<h3><a href="{link("c-" + a["slug"])}">{esc(a["title"])}</a></h3>'
            f'<p>{esc(a["excerpt"])}</p><div class="meta">{"".join(tags)}</div></li>')

# ------------------------------------------------------------------ columna
def render_blocks(blocks):
    out, ul = [], []
    def flush():
        if ul:
            out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in ul) + '</ul>')
            ul.clear()
    for k, t in blocks:
        if k == 'li':
            ul.append(md(t)); continue
        flush()
        if k == 'sub':
            out.append(f'<h2>{md(t)}</h2>')
        elif k == 'pq':
            out.append(f'<blockquote class="pq"><p>{md(t.strip("“”\"«»"))}</p></blockquote>')
        elif k == 'book':
            out.append(f'<h3 class="book">{md(t)}</h3>')
        elif k == 'where':
            out.append(f'<p class="where"><b>Dónde:</b> {md(t)}</p>')
        else:
            out.append(f'<p>{md(t)}</p>')
    flush()
    return ''.join(out)

def page_article(i, a):
    meta = [f'<span>{fecha(a["date"])}</span>', f'<span>{a["minutes"]} min de lectura</span>',
            f'<a class="tag" href="{link("tema-" + a["pillar"])}">{esc(PIL[a["pillar"]]["name"])}</a>']
    st = series_tag(a)
    if st:
        meta.append(st)
    h = [f'<article class="art wrap"><h1>{esc(a["title"])}</h1>']
    if a['deck']:
        h.append(f'<p class="deck">{esc(a["deck"])}</p>')
    h.append(f'<div class="meta">{"".join(meta)}</div>')
    h.append(f'<div class="body">{render_blocks(a["blocks"])}</div>')
    if a['closing']:
        h.append(f'<p class="closing">{esc(a["closing"]).replace(chr(10), "<br>")}</p>')
    h.append('<div class="sig"><b>Manuel Sotomayor de Azambuja</b>Empresario. Ex-Presidente de CONFIEP</div>')
    h.append(f'<p class="orig">Publicado en El Reporte el {fecha(a["date"])}. '
             f'<a href="{esc(a["er_url"])}">Ver en El Reporte</a></p>')
    wa = 'https://wa.me/?text=' + html.escape(
        urllib.parse.quote(f'{a["title"]}, por Manuel Sotomayor\n{art_url(a)}'))
    h.append(f'<div class="share"><a class="btn" href="{wa}">Compartir por WhatsApp</a>'
             f'<button class="btn alt" type="button" data-copy="{esc(art_url(a))}">Copiar enlace</button>'
             + (f'<a class="btn alt" href="{BASE}/pdf/{a["slug"]}.pdf">Descargar PDF</a>'
                if MODE == 'static' and os.path.exists(f'{ROOT}/site/pdf/{a["slug"]}.pdf') else '')
             + '</div><p class="copied lbl" aria-live="polite"></p>')
    if a['series']:
        s = SER[a['series']]
        lis = []
        for n in s['items']:
            b = BYN[n]
            cls = ' class="here"' if n == a['n'] else ''
            lis.append(f'<li{cls}><a href="{link("c-" + b["slug"])}">{esc(b["title"])}</a></li>')
        h.append(f'<aside class="box"><div class="lbl">Serie</div><h2><a href="{link("serie-" + s["key"])}">'
                 f'{esc(s["name"])}</a></h2><ol class="toc">{"".join(lis)}</ol></aside>')
    older = ARTS[i + 1] if i + 1 < len(ARTS) else None
    newer = ARTS[i - 1] if i > 0 else None
    pg = '<nav class="pager" aria-label="Más columnas">'
    pg += (f'<div><div class="lbl">← Anterior</div><a href="{link("c-" + older["slug"])}">{esc(older["title"])}</a></div>'
           if older else '<div></div>')
    pg += (f'<div class="next"><div class="lbl">Siguiente →</div><a href="{link("c-" + newer["slug"])}">{esc(newer["title"])}</a></div>'
           if newer else '<div></div>')
    h.append(pg + '</nav>')
    rel = [b for b in ARTS if b['n'] != a['n'] and a['pillar'] in pillars_of(b)
           and not (a['series'] and b['series'] == a['series'])][:3]
    if rel:
        h.append(f'<section class="related"><h2>Más en {esc(PIL[a["pillar"]]["name"])}</h2>'
                 f'<ul class="items">{"".join(item(b, False) for b in rel)}</ul></section>')
    h.append('</article>')
    return ''.join(h)

# ------------------------------------------------------------------ portada
def page_home():
    a = ARTS[0]
    first, last = ARTS[-1]['date'], ARTS[0]['date']
    h = ['<section class="hero"><div class="wrap hero-grid">']
    h.append('<div class="ht"><h1>Las Reglas del Juego</h1>'
             '<p class="lede">Columnas de Manuel Sotomayor de Azambuja sobre instituciones, libertad y el diseño '
             'de las reglas. Se publican en El Reporte desde octubre de 2025.</p>'
             f'<div class="btns"><a class="btn solid" href="{link("columnas")}">Todas las columnas</a>'
             f'<a class="btn line" href="#empieza" data-jump="empieza">Empieza aquí</a></div></div>')
    h.append(f'<div class="latest"><div class="lbl">Última columna, {fecha(a["date"])}</div>'
             f'<h2><a href="{link("c-" + a["slug"])}">{esc(a["title"])}</a></h2>'
             f'<p>{esc(a["excerpt"])}</p><div class="meta"><span>{a["minutes"]} min de lectura</span>'
             f'<span>{esc(PIL[a["pillar"]]["name"])}</span></div></div>')
    chips = ['<button class="chip" type="button" data-f="" aria-pressed="true">Todas <span>52</span></button>']
    for k in PIL_ORDER:
        c = sum(1 for b in ARTS if k in pillars_of(b))
        chips.append(f'<button class="chip" type="button" data-f="{k}" aria-pressed="false">{esc(SHORT[k])} <span>{c}</span></button>')
    h.append('<div class="ruler" id="ruler"><div class="ruler-head">'
             f'<h2>{len(ARTS)} columnas en {months_between(first, last)} meses</h2>'
             '<span class="lbl">Cada marca es una columna. Tócala para verla.</span></div>'
             '<div class="fig" id="rfig"><svg id="rsvg" role="img" aria-label="Línea de tiempo de las columnas"></svg></div>'
             '<div class="cap" id="rcap" aria-live="polite"></div>'
             f'<div class="chips" id="rchips" role="group" aria-label="Destacar un tema">{"".join(chips)}</div></div>')
    h.append('</div></section>')
    # Empieza aquí
    start = [BYN[n] for n in S['start']]
    h.append('<section class="band" id="empieza"><div class="wrap split"><div class="intro"><h2>Empieza aquí</h2>'
             '<p>Cinco columnas que resumen la tesis: el destino de un país no depende de quién gobierna, '
             'sino de las reglas que limitan a quien gobierna.</p></div>'
             f'<ul class="items">{"".join(item(b) for b in start)}</ul></div></section>')
    # Cita
    q = BYN[5]
    h.append('<section class="band quote"><div class="wrap"><blockquote>No se trata de encontrar un buen presidente. '
             'Se trata de que no importe quién sea.</blockquote>'
             f'<p class="lbl">De <a href="{link("c-" + q["slug"])}">{esc(q["title"])}</a></p></div></section>')
    # Series
    cols = []
    for s in S['series']:
        lis = ''.join(f'<li><a href="{link("c-" + BYN[n]["slug"])}">{esc(BYN[n]["title"])}</a></li>' for n in s['items'][:4])
        more = ''
        if len(s['items']) > 4:
            more = f'<a class="more" href="{link("serie-" + s["key"])}">Ver las {len(s["items"])} columnas de la serie</a>'
        cols.append(f'<div class="serie"><h3><a href="{link("serie-" + s["key"])}">{esc(s["name"])}</a></h3>'
                    f'<p>{esc(s["desc"])}</p><ol class="toc">{lis}</ol>{more}</div>')
    h.append('<section class="band" style="padding-top:0"><div class="wrap"><h2>Series</h2>'
             f'<div class="cols3">{"".join(cols)}</div></div></section>')
    # Temas
    h.append(f'<section class="band" style="padding-top:0"><div class="wrap"><h2>Temas</h2>{themes_grid(3)}</div></section>')
    h.append(wa_band())
    return ''.join(h)

def months_between(d1, d2):
    y1, m1 = int(d1[:4]), int(d1[5:7])
    y2, m2 = int(d2[:4]), int(d2[5:7])
    return (y2 - y1) * 12 + (m2 - m1) + 1

def themes_grid(k):
    out = []
    for key in PIL_ORDER:
        p = PIL[key]
        arts = [b for b in ARTS if key in pillars_of(b)]
        lis = ''.join(f'<li><a href="{link("c-" + b["slug"])}">{esc(b["title"])}</a></li>' for b in arts[:k])
        more = ''
        if len(arts) > k:
            more = f'<li class="more"><a href="{link("tema-" + key)}">Ver las {len(arts)} columnas</a></li>'
        out.append(f'<div class="theme"><div><h3><a href="{link("tema-" + key)}">{esc(p["name"])}</a>'
                   f'<small>{len(arts)} {"columna" if len(arts) == 1 else "columnas"}</small></h3>'
                   f'<p>{esc(p["desc"])}</p></div><ul>{lis}{more}</ul></div>')
    return f'<div class="themes">{"".join(out)}</div>'

def wa_band():
    return ('<section class="band wa"><div class="wrap"><div><h2>Cada columna, en tu WhatsApp</h2>'
            '<p>Sigue el canal y recibe la columna el día en que se publica. Es un canal de difusión: '
            'nadie ve tu número ni recibe mensajes de otros.</p></div>'
            f'<a class="btn solid" href="{WA_CHANNEL}">Seguir el canal</a></div></section>')

# ------------------------------------------------------------------ listados
def page_archive():
    chips = ['<button class="chip" type="button" data-f="" aria-pressed="true">Todas <span>52</span></button>']
    for k in PIL_ORDER:
        c = sum(1 for b in ARTS if k in pillars_of(b))
        chips.append(f'<button class="chip" type="button" data-f="{k}" aria-pressed="false">{esc(SHORT[k])} <span>{c}</span></button>')
    h = ['<div class="wrap"><header class="page-head"><h1>Columnas</h1>'
         '<p>Las columnas de «Las Reglas del Juego» publicadas en El Reporte, de la más reciente a la más antigua.</p>'
         '<div class="tools"><input class="search" id="q" type="search" autocomplete="off" '
         'placeholder="Buscar una palabra, un nombre o una frase" aria-label="Buscar en las columnas">'
         f'<div class="chips" id="fchips" role="group" aria-label="Filtrar por tema">{"".join(chips)}</div></div>'
         '<p class="count" id="count"></p></header>']
    months = {}
    for a in ARTS:
        months.setdefault(a['date'][:7], []).append(a)
    for ym, arts in months.items():
        y, m = ym.split('-')
        h.append(f'<section class="month"><h2>{MESES[int(m) - 1].capitalize()} de {y}</h2>'
                 f'<ul class="items">{"".join(item(a) for a in arts)}</ul></section>')
    h.append('<p class="empty" id="empty" hidden>Ninguna columna coincide. Prueba con otra palabra o quita el filtro.</p>')
    h.append('</div>')
    return ''.join(h)

def page_themes():
    return ('<div class="wrap"><header class="page-head"><h1>Temas</h1>'
            '<p>Cinco grandes temas recorren la columna. Una misma columna puede pertenecer a más de uno.</p></header>'
            f'{themes_grid(5)}</div><div style="height:48px"></div>')

def page_theme(key):
    p = PIL[key]
    arts = [b for b in ARTS if key in pillars_of(b)]
    note = ''
    if len(arts) < 4:
        note = ('<p class="lbl" style="margin-top:12px">Aquí se sumarán los ensayos anteriores a la columna '
                'cuando pasen del sitio actual al nuevo.</p>')
    return (f'<div class="wrap"><header class="page-head"><h1>{esc(p["name"])}</h1><p>{esc(p["desc"])}</p>'
            f'<p class="count">{len(arts)} {"columna" if len(arts) == 1 else "columnas"}</p>{note}</header>'
            f'<ul class="items" style="margin-bottom:48px">{"".join(item(b, False) for b in arts)}</ul></div>')

def page_series_index():
    blocks = []
    for s in S['series']:
        lis = ''.join(f'<li><a href="{link("c-" + BYN[n]["slug"])}">{esc(BYN[n]["title"])}</a></li>' for n in s['items'])
        blocks.append(f'<div class="serie"><h3><a href="{link("serie-" + s["key"])}">{esc(s["name"])}</a></h3>'
                      f'<p>{esc(s["desc"])}</p><ol class="toc">{lis}</ol></div>')
    return ('<div class="wrap"><header class="page-head"><h1>Series</h1>'
            '<p>Columnas que se leen juntas, como capítulos de un libro breve.</p></header>'
            f'<div class="cols3" style="margin-bottom:56px">{"".join(blocks)}</div></div>')

def page_series(key):
    s = SER[key]
    arts = [BYN[n] for n in s['items']]
    lis = ''.join(item(b, True, b['part'] or '') for b in arts)
    return (f'<div class="wrap"><header class="page-head"><h1>{esc(s["name"])}</h1><p>{esc(s["desc"])}</p>'
            f'<p class="count">{len(arts)} columnas, en orden de lectura</p></header>'
            f'<ul class="items" style="margin-bottom:48px">{lis}</ul></div>')

def page_about():
    return ('<div class="wrap about"><header class="page-head" style="border:0"><h1>Manuel Sotomayor de Azambuja</h1>'
            '</header><div class="body">'
            '<p>Empresario y economista peruano. Presidió la Confederación Nacional de Instituciones Empresariales '
            'Privadas (CONFIEP) entre 1998 y 1999.</p>'
            '<p>En 1992 fundó Perú 2021, hoy Perú Sostenible, una de las primeras iniciativas de responsabilidad social '
            'empresarial de América Latina. Creó, además, la Fundación Perú: Innovando el Futuro, nacida de una iniciativa '
            'del expresidente Alan García.</p>'
            '<p>Ha integrado redes empresariales internacionales como el Consejo Consultivo '
            'Empresarial del APEC (ABAC), el Consejo Empresarial de América Latina (CEAL) y el Grupo de los Cincuenta (G50), '
            'y participa en organizaciones de la sociedad civil como ANCLA.</p>'
            '<p>Escribe «Las Reglas del Juego», la columna que publica El Reporte desde octubre de 2025. Su tesis es '
            'constante: lo que decide el rumbo de un país no son las personas, sino las instituciones. Escribe desde el '
            'liberalismo clásico, con Hayek y Popper como referencias.</p></div>'
            f'<div class="btns" style="margin:8px 0 56px"><a class="btn solid" style="background:var(--green);color:#fff" '
            f'href="{link("columnas")}">Leer las columnas</a></div></div>')

# ------------------------------------------------------------------ ensamblado
pages = {
    'inicio': ('Las Reglas del Juego · Manuel Sotomayor', page_home()),
    'columnas': ('Columnas · Manuel Sotomayor', page_archive()),
    'temas': ('Temas · Manuel Sotomayor', page_themes()),
    'series': ('Series · Manuel Sotomayor', page_series_index()),
    'sobre-mi': ('Sobre mí · Manuel Sotomayor', page_about()),
}
for k in PIL_ORDER:
    pages['tema-' + k] = (f'{PIL[k]["name"]} · Manuel Sotomayor', page_theme(k))
for s in S['series']:
    pages['serie-' + s['key']] = (f'Serie {s["name"]} · Manuel Sotomayor', page_series(s['key']))
for i, a in enumerate(ARTS):
    pages['c-' + a['slug']] = (f'{a["title"]} · Manuel Sotomayor', page_article(i, a))

ruler = [{'d': a['date'], 't': a['title'], 'h': link('c-' + a['slug']), 'p': pillars_of(a)} for a in ARTS]

if MODE == 'spa':
    payload = {'pages': {k: {'t': t, 'h': h} for k, (t, h) in pages.items()}, 'ruler': ruler}
    with open(f'{OUT}/site.json', 'w') as f:
        json.dump(payload, f, ensure_ascii=False, separators=(',', ':'))
    shell = open(f'{ROOT}/site/shell.html').read()
    css = open(f'{ROOT}/site/style.css').read()
    js = open(f'{ROOT}/site/app.js').read()
    shell = shell.replace('/*CSS*/', css).replace('/*JS*/', js)
    for k, v in {'{{HOME}}': link('inicio'), '{{COLS}}': link('columnas'), '{{TEMAS}}': link('temas'),
                 '{{SERIES}}': link('series'), '{{SOBRE}}': link('sobre-mi')}.items():
        shell = shell.replace(k, v)
    open(f'{OUT}/index.html', 'w').write(shell)
    print('páginas', len(pages), '| site.json', os.path.getsize(f'{OUT}/site.json') // 1024, 'KB',
          '| index.html', os.path.getsize(f'{OUT}/index.html') // 1024, 'KB')

# ------------------------------------------------------------------ sitio estático
if MODE == 'static':
    import shutil
    sys.path.insert(0, f'{ROOT}/site')
    from og import card
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(f'{OUT}/assets', exist_ok=True)
    os.makedirs(f'{OUT}/og', exist_ok=True)
    staging = bool(BASE)
    css = open(f'{ROOT}/site/style.css').read()
    open(f'{OUT}/assets/style.css', 'w').write(css)
    open(f'{OUT}/assets/app.js', 'w').write(open(f'{ROOT}/site/app.js').read())
    open(f'{OUT}/assets/icon.svg', 'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#1d7256"/>'
        '<path d="M12 46h40" stroke="#fff" stroke-width="3"/><path d="M18 46V30M26 46V24M34 46V30M42 46V24" stroke="#fff" '
        'stroke-width="3" stroke-linecap="round"/><path d="M50 46V14" stroke="#f0c766" stroke-width="4" stroke-linecap="round"/>'
        '<circle cx="50" cy="13" r="4" fill="#f0c766"/></svg>')
    open(f'{OUT}/.nojekyll', 'w').write('')
    if os.path.isdir(f'{ROOT}/site/pdf'):
        shutil.copytree(f'{ROOT}/site/pdf', f'{OUT}/pdf')
    dates = [a['date'] for a in ARTS]
    card(f'{OUT}/og/inicio.png', 'Columnas sobre instituciones, libertad y el diseño de las reglas',
         dates, ARTS[0]['date'], 'manuelsotomayor.com')
    for a in ARTS:
        card(f'{OUT}/og/{a["slug"]}.png', a['title'], dates, a['date'], fecha(a['date']))

    NAV = [('columnas', 'Columnas'), ('temas', 'Temas'), ('series', 'Series'), ('sobre-mi', 'Sobre mí')]
    def header(sect):
        links = ''.join(f'<a href="{link(k)}"{" aria-current=\"page\"" if k == sect else ""}>{v}</a>' for k, v in NAV)
        return (f'<header class="top"><div class="wrap"><a class="brand" href="{link("inicio")}">Manuel Sotomayor</a>'
                f'<nav class="nav" aria-label="Principal">{links}</nav></div></header>')
    FOOT = ('<footer class="foot"><div class="wrap"><div><b>Manuel Sotomayor de Azambuja</b>Empresario. Ex-Presidente de CONFIEP'
            '<p class="note">© 2026 Manuel Sotomayor de Azambuja. Las columnas se publicaron originalmente en El Reporte.</p></div>'
            '<nav class="nav" aria-label="Pie de página">'
            + ''.join(f'<a href="{link(k)}">{v}</a>' for k, v in NAV) + '</nav></div></footer>')

    def doc(name, title, desc, body, og='inicio', kind='website', extra=''):
        path = path_of(name)
        canon = BASE_URL + path
        sect = ('columnas' if name.startswith('c-') or name == 'columnas' else 'temas' if name.startswith('tema') else
                'series' if name.startswith('serie') else name)
        img = f'{BASE_URL}/og/{og}.png'
        h = ['<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             f'<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">',
             f'<link rel="canonical" href="{canon}">',
             '<meta name="robots" content="noindex">' if staging else '',
             f'<meta property="og:type" content="{kind}"><meta property="og:site_name" content="Manuel Sotomayor">',
             '<meta property="og:locale" content="es_PE">',
             f'<meta property="og:title" content="{esc(title.split(" · ")[0])}">',
             f'<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{canon}">',
             f'<meta property="og:image" content="{img}"><meta property="og:image:width" content="1200">',
             '<meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">',
             f'<link rel="icon" href="{BASE}/assets/icon.svg" type="image/svg+xml">',
             '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
             '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Source+Sans+3:wght@400;500;600;700&display=swap">',
             f'<link rel="stylesheet" href="{BASE}/assets/style.css">', extra, '</head><body>',
             header(sect), f'<main id="main">{body}</main>', FOOT,
             f'<script>window.SITE={{mode:"static",base:"{BASE}"}}</script>',
             f'<script src="{BASE}/assets/app.js" defer></script></body></html>']
        out = f'{OUT}{path}index.html'
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, 'w').write(''.join(h))
        return canon

    DESC = {
        'inicio': 'Columnas de Manuel Sotomayor de Azambuja sobre instituciones, libertad y el diseño de las reglas.',
        'columnas': 'Todas las columnas de «Las Reglas del Juego», de Manuel Sotomayor de Azambuja, publicadas en El Reporte.',
        'temas': 'Los cinco temas de «Las Reglas del Juego»: instituciones, economía, ideas, inteligencia artificial e Iglesia.',
        'series': 'Columnas de Manuel Sotomayor que se leen juntas, como capítulos de un libro breve.',
        'sobre-mi': 'Manuel Sotomayor de Azambuja, empresario y economista peruano, ex presidente de CONFIEP.',
    }
    urls = []
    ruler_json = json.dumps(ruler, ensure_ascii=False).replace('</', '<\\/')
    for name, (title, body) in pages.items():
        if name.startswith('c-'):
            a = next(x for x in ARTS if 'c-' + x['slug'] == name)
            ld = {'@context': 'https://schema.org', '@type': 'OpinionNewsArticle', 'headline': a['title'],
                  'description': a['excerpt'], 'datePublished': a['date'], 'inLanguage': 'es',
                  'author': {'@type': 'Person', 'name': 'Manuel Sotomayor de Azambuja', 'url': BASE_URL + '/sobre-mi/'},
                  'image': f'{BASE_URL}/og/{a["slug"]}.png', 'mainEntityOfPage': BASE_URL + path_of(name)}
            extra = ('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace('</', '<\\/') + '</script>'
                     f'<meta property="article:published_time" content="{a["date"]}">')
            urls.append(doc(name, title, a['excerpt'], body, a['slug'], 'article', extra))
        elif name.startswith('tema-'):
            urls.append(doc(name, title, PIL[name[5:]]['desc'], body))
        elif name.startswith('serie-'):
            urls.append(doc(name, title, SER[name[6:]]['desc'], body))
        else:
            if name == 'inicio':
                body = body + f'<script type="application/json" id="ruler-data">{ruler_json}</script>'
            urls.append(doc(name, title, DESC[name], body))
    # 404
    doc('404tmp', 'Página no encontrada · Manuel Sotomayor', 'Página no encontrada',
        '<div class="wrap"><header class="page-head" style="border:0"><h1>Esta página no existe</h1>'
        f'<p>Puede que la dirección haya cambiado. <a href="{link("columnas")}">Ver todas las columnas</a>.</p></header></div>')
    shutil.move(f'{OUT}/404tmp/index.html', f'{OUT}/404.html'); os.rmdir(f'{OUT}/404tmp')
    # buscador, mapa del sitio y robots
    idx = {}
    for a in ARTS:
        plain = ' '.join([a['title'], a['deck'] or '', ' '.join(t for k, t in a['blocks']), a['closing'] or ''])
        idx[a['slug']] = re.sub(r'[*_]', '', plain)
    json.dump(idx, open(f'{OUT}/search.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    sm = ['<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f'<url><loc>{u}</loc></url>' for u in urls]
    open(f'{OUT}/sitemap.xml', 'w').write(''.join(sm) + '</urlset>')
    open(f'{OUT}/robots.txt', 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n')
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print('sitio estático:', len(pages), 'páginas,', n, 'archivos en', OUT, '| base', BASE or '/', '| staging', staging)
