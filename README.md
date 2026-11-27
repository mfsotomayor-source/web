# manuelsotomayor.com

Sitio de **Manuel Sotomayor de Azambuja**: las columnas de «Las Reglas del Juego», con temas, series y buscador.

- `docs/` es el sitio publicado (GitHub Pages lo sirve tal cual).
- `fuente/articulos.json` contiene el texto de cada columna, su fecha, tema y serie.
- `fuente/build_site.py` genera `docs/` a partir de ese archivo, con `style.css`, `app.js` y `og.py` (imágenes de vista previa para WhatsApp).

Para regenerar: `python3 fuente/build_site.py static /web` y copiar el resultado a `docs/`.
