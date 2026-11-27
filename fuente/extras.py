"""Contenido que viene del sitio de Google Sites: entrevistas, Perú 2021, Fundación Perú, archivo, fotos y CV."""
import json

YT = 'https://www.youtube.com/watch?v='
DRIVE = 'https://drive.google.com/file/d/{}/view'

# (id, título, medio o detalle, segundo de inicio)
VIDEOS = {
    'medios': [
        ('LSb69rqCQvw', 'No hay diferencia entre un comunista y un fascista', 'El Reporte', None, 'no-hay-diferencia'),
        ('YAXHewkvh80', 'La amenaza comunista, la libertad y el empresariado', 'El Montonero', None, None),
        ('x6dy79_E_FU', 'Cara a Cara', 'TV Perú Noticias. Entrevista al expresidente de la CONFIEP', None, None),
        ('QmxmUCbQ6rE', 'La política en la economía', 'Reflexiones, con Alfonso Baella. 8 de setiembre de 2021, junto a Jaime Reusche', None, None),
        ('PT0gXDNhvIc', 'Las consecuencias del fallo de La Haya', 'Con Luis Icochea', None, None),
    ],
    'conferencias': [
        ('gkytZMuG2Ek', 'Thought for Action', 'Presentación en Grecia', None, None),
    ],
    'fundacion': [
        ('XHgC7dTL8vc', 'Lanzamiento de la Fundación Perú', 'Primera parte', None, None),
        ('mWOy5wdF4Ok', 'Lanzamiento de la Fundación Perú', 'Segunda parte', None, None),
        ('DVOhLx6JadI', 'Lanzamiento de la Fundación Perú', 'Tercera parte', None, None),
        ('SsD4jh6NpAc', 'Manuel Sotomayor, presidente de la Fundación Perú', 'Primera parte', None, None),
        ('EEaP__xIfI8', 'Manuel Sotomayor, presidente de la Fundación Perú', 'Segunda parte', None, None),
    ],
    'peru2021': [
        ('iXPNTLo1xyI', 'Convocatoria inicial', '1992', None, None),
        ('CNpsl7iGbMQ', 'Lanzamiento de Perú 2021', 'Agosto de 1994', None, None),
        ('W0Zh3SsX2EU', 'Perú 2021 a los nueve años', '', None, None),
    ],
}
LINKS_MEDIOS = [
    (DRIVE.format('1pPcUg5AzGpJVUiw79CBPu37i2mzqivK4'), 'Con Milagros Leiva, primera parte', '11 de agosto de 2021'),
    (DRIVE.format('17yz2PjK1wPmO9XBaqlOd3eyHBo_QM2AK'), 'Con Milagros Leiva, segunda parte', '11 de agosto de 2021'),
    (YT + 'P0foyocN9y4&t=660s', 'Los empresarios con cabeza de avestruz', 'Desde el minuto 11'),
]
PRENSA = [
    (DRIVE.format('1Yd8vBkvP0uCLtPI85mP7aZaIm7ExD-Qe'), 'Hay que desmontar la narrativa de la izquierda', 'Diario Gestión, 2021'),
]
CV = [
    ('https://docs.google.com/document/d/1yB7HLHILiU1Yb7bY91J-LIScAS2JtQXJhkyWptJwn_A/preview', 'Currículum (español)'),
    ('https://docs.google.com/document/d/1oBcbA5WG0axbNtIru86HEbu7KSxhHWCZuZGlyTsQ7b8/preview', 'Curriculum vitae (English)'),
]
RESOLUCION_PDF = DRIVE.format('1EK6eUNVsJOUoSc3GsWT3KOgUWuIi03o5')

DECLARACION = [
    ('p', 'En atención a versiones y referencias mediáticas pasadas, corresponde aclarar con precisión legal y sin '
          'ambigüedades lo siguiente:'),
    ('h3', '1. Situación de Santiago Calle Quirós'),
    ('p', 'El ciudadano Luis Santiago Calle Quirós fue incluido por la Oficina de Control de Activos Extranjeros (OFAC) '
          'de Estados Unidos en octubre de 2013. No obstante, el 14 de junio de 2017, mediante publicación en el Federal '
          'Register, OFAC dispuso su retiro definitivo de la denominada lista de Nacionales Especialmente Designados '
          '(conocida como “Lista Clinton”). Desde entonces, Calle Quirós no mantiene sanciones internacionales vigentes '
          'relacionadas con ese caso.'),
    ('h3', '2. Situación de Manuel F. Sotomayor de Azambuja'),
    ('p', 'El suscrito, Manuel Fernando Sotomayor de Azambuja, economista peruano, fui mencionado en el marco de una '
          'investigación vinculada a una operación inmobiliaria (venta de oficinas en Altavista, San Isidro). Dicha '
          'investigación fue conducida por la Fiscalía Supraprovincial Especializada en Lavado de Activos. El resultado '
          'fue categórico: mediante resolución fiscal se dispuso el Archivamiento Definitivo del caso, confirmando que no '
          'existió participación ilícita ni responsabilidad penal alguna de mi parte.'),
    ('h3', '3. Conclusión'),
    ('li', 'Santiago Calle Quirós no mantiene sanciones internacionales vigentes desde 2017.'),
    ('li', 'Manuel F. Sotomayor no tiene ni ha tenido responsabilidad alguna en dicho caso, quedando acreditada su '
           'inocencia mediante archivamiento definitivo en el Perú.'),
    ('p', 'Este pronunciamiento deja constancia pública, en aras de la transparencia y de la preservación de la verdad.'),
    ('p', 'Lima, 20 de setiembre de 2025'),
]
RESOLUCION = [
    ('Asunto', 'Archivamiento Definitivo de Investigación Fiscal por presunto Lavado de Activos.'),
    ('Interesado', 'Manuel Fernando Sotomayor de Azambuja.'),
    ('Autoridad', '1ª Fiscalía Supraprovincial Corporativa Especializada en Delitos de Lavado de Activos y Pérdida de '
                  'Dominio – Segundo Despacho.'),
    ('Resolución', 'Se resolvió NO HA LUGAR A FORMALIZAR DENUNCIA PENAL por falta de elementos reveladores de delito. '
                   'Se dispone el ARCHIVAMIENTO DEFINITIVO.'),
    ('Efecto jurídico', 'El caso queda definitivamente archivado, sin indicios que vinculen al Sr. Sotomayor con los '
                        'hechos investigados.'),
]

FIX_CAP = {
    'Taj Majal': 'Taj Mahal', 'Raúl, Castro': 'Raúl Castro', 'Monge Tibetano': 'un monje tibetano',
    'Sultan de': 'Sultán de', 'Mahatir': 'Mahathir', 'Tung Chee Wa': 'Tung Chee-hwa', 'Vice Presidente': 'vicepresidente',
    'Tibet': 'Tíbet', 'Alvaro': 'Álvaro',
}
FOTO_BASE = 'https://lh7-us.googleusercontent.com/sitesv-images-rt/'

def fotos():
    out = []
    for fid, cap in json.load(open('/home/claude/data/fotos.json')):
        for a, b in FIX_CAP.items():
            cap = cap.replace(a, b)
        out.append((FOTO_BASE + fid, cap))
    return out
