{
const main = document.getElementById('main');
const MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','setiembre','octubre','noviembre','diciembre'];
const MES = ['ene','feb','mar','abr','may','jun','jul','ago','set','oct','nov','dic'];
const NOMBRE = {instituciones:'Instituciones y reglas del juego', economia:'Economía y libertad', ideas:'Historia e ideas', ia:'Inteligencia artificial', iglesia:'Iglesia y doctrina social'};
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const SITE = window.SITE || {mode: 'spa', base: ''};
let DATA = null;
let SEARCH = null;
let rulerRO = null;
let current = '';

const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const fecha = d => { const [y, m, dd] = d.split('-'); return `${+dd} de ${MESES[m - 1]} de ${y}`; };

function route() {
  if (!DATA) return;
  const name = location.hash.slice(1) || 'inicio';
  if (!DATA.pages[name]) {
    const el = document.getElementById(name);
    if (el) { el.scrollIntoView(); return; }
  }
  const key = DATA.pages[name] ? name : 'inicio';
  if (key === current) { window.scrollTo(0, 0); return; }
  current = key;
  const pg = DATA.pages[key];
  main.innerHTML = pg.h;
  document.title = pg.t;
  const sect = key.startsWith('c-') ? 'columnas' : key.startsWith('tema-') ? 'temas' : key.startsWith('serie-') ? 'series' : key;
  document.querySelectorAll('.top .nav a').forEach(a => {
    if (a.dataset.r === sect) a.setAttribute('aria-current', 'page'); else a.removeAttribute('aria-current');
  });
  window.scrollTo(0, 0);
  if (rulerRO) { rulerRO.disconnect(); rulerRO = null; }
  if (key === 'inicio') initRuler();
  if (key === 'columnas') initArchive();
  initCopy();
}

function initRuler() {
  const fig = document.getElementById('rfig');
  const svg = document.getElementById('rsvg');
  const cap = document.getElementById('rcap');
  const chips = document.getElementById('rchips');
  if (!fig || !svg) return;
  const R = DATA.ruler.slice().reverse();
  const L = R.length - 1;
  const t0 = Date.UTC(+R[0].d.slice(0, 4), +R[0].d.slice(5, 7) - 1, 1);
  const lastY = +R[L].d.slice(0, 4), lastM = +R[L].d.slice(5, 7);
  const t1 = Date.UTC(lastY, lastM, 1);
  let filt = '';
  let hot = -1;

  const show = i => {
    const r = R[i];
    cap.innerHTML = `<span class="lbl">${fecha(r.d)}${i === L ? ', la más reciente' : ''}</span><a href="${esc(r.h)}">${esc(r.t)}</a>`;
  };
  const rest = () => {
    if (filt) {
      const n = R.filter(r => r.p.includes(filt)).length;
      cap.innerHTML = `<span class="lbl">${NOMBRE[filt]}</span>${n} de ${R.length} columnas`;
    } else show(L);
  };
  const paint = () => {
    svg.querySelectorAll('.tick').forEach((t, i) => {
      t.classList.toggle('dim', !!filt && !R[i].p.includes(filt));
      t.classList.toggle('on', i === hot);
    });
  };
  const draw = () => {
    const W = fig.clientWidth, H = fig.clientHeight;
    const pl = 4, pr = 4, base = H - 30;
    const x = t => pl + (W - pl - pr) * (t - t0) / (t1 - t0);
    const narrow = W < 520;
    let s = `<line x1="${pl}" x2="${W - pr}" y1="${base}" y2="${base}" stroke="currentColor" stroke-opacity=".6" stroke-width="1.5"/>`;
    let k = 0;
    for (let y = +R[0].d.slice(0, 4), m = +R[0].d.slice(5, 7) - 1; Date.UTC(y, m, 1) <= t1; m++, k++) {
      if (m === 12) { m = 0; y++; }
      const t = Date.UTC(y, m, 1), xm = x(t), jan = m === 0;
      s += `<line x1="${xm}" x2="${xm}" y1="${base}" y2="${base + (jan || k === 0 ? 14 : 7)}" stroke="currentColor" stroke-opacity=".6"/>`;
      if (t < t1 && (narrow ? k % 3 === 0 : true)) {
        const lab = (jan || k === 0) ? `${MES[m]} ${y}` : MES[m];
        s += `<text x="${xm + 4}" y="${base + 22}"${jan || k === 0 ? ' class="yr"' : ''}>${lab}</text>`;
      }
    }
    const xs = R.map(r => x(Date.UTC(+r.d.slice(0, 4), +r.d.slice(5, 7) - 1, +r.d.slice(8, 10), 12)));
    let ticks = '', hits = '';
    R.forEach((r, i) => {
      const xi = xs[i], last = i === L;
      const top = last ? 18 : base - 62;
      ticks += `<line class="tick${last ? ' last' : ''}" x1="${xi}" x2="${xi}" y1="${base - 3}" y2="${top}" style="animation-delay:${reduce ? 0 : i * 14}ms"/>`;
      const a = i ? (xs[i - 1] + xi) / 2 : xi - 8, b = i < L ? (xi + xs[i + 1]) / 2 : xi + 8;
      hits += `<a href="${esc(r.h)}" data-i="${i}" aria-label="${esc(r.t)}"><rect class="hit" x="${a}" y="10" width="${Math.max(b - a, 4)}" height="${base - 6}"/></a>`;
    });
    const lx = xs[L];
    s += ticks + `<circle cx="${lx}" cy="18" r="5" fill="var(--gold)"/>` + hits;
    svg.innerHTML = s;
    paint();
  };
  svg.addEventListener('pointerover', e => {
    const a = e.target.closest('a[data-i]');
    if (!a) return;
    hot = +a.dataset.i; show(hot); paint();
  });
  svg.addEventListener('focusin', e => {
    const a = e.target.closest('a[data-i]');
    if (a) { hot = +a.dataset.i; show(hot); paint(); }
  });
  svg.addEventListener('pointerleave', () => { hot = -1; rest(); paint(); });
  chips.addEventListener('click', e => {
    const b = e.target.closest('.chip');
    if (!b) return;
    filt = b.dataset.f;
    chips.querySelectorAll('.chip').forEach(c => c.setAttribute('aria-pressed', String(c === b)));
    hot = -1; rest(); paint();
  });
  rulerRO = new ResizeObserver(draw);
  rulerRO.observe(fig);
  rest();
}

function initArchive() {
  const q = document.getElementById('q');
  const chips = document.getElementById('fchips');
  const count = document.getElementById('count');
  const empty = document.getElementById('empty');
  const items = [...main.querySelectorAll('.month .items > li')];
  let filt = '', idx = null;
  const build = () => {
    if (SITE.mode === 'static') {
      if (!SEARCH) {
        SEARCH = fetch(SITE.base + '/search.json').then(r => r.json()).then(d => { idx = {}; for (const k in d) idx[k] = norm(d[k]); apply(); });
      }
      return false;
    }
    idx = {};
    items.forEach(li => { idx[li.dataset.s] = norm(DATA.pages['c-' + li.dataset.s].h.replace(/<[^>]+>/g, ' ')); });
    return true;
  };
  const apply = () => {
    const words = norm(q.value.trim()).split(/\s+/).filter(Boolean);
    if (words.length && !idx && !build()) return;
    let shown = 0;
    items.forEach(li => {
      const ok = (!filt || li.dataset.p.split(' ').includes(filt)) && (!words.length || words.every(w => idx[li.dataset.s].includes(w)));
      li.hidden = !ok;
      if (ok) shown++;
    });
    main.querySelectorAll('.month').forEach(sec => { sec.hidden = !sec.querySelector('.items > li:not([hidden])'); });
    count.textContent = shown === items.length ? `${items.length} columnas` : `${shown} de ${items.length} columnas`;
    empty.hidden = shown > 0;
  };
  q.addEventListener('input', apply);
  chips.addEventListener('click', e => {
    const b = e.target.closest('.chip');
    if (!b) return;
    filt = b.dataset.f;
    chips.querySelectorAll('.chip').forEach(c => c.setAttribute('aria-pressed', String(c === b)));
    apply();
  });
  apply();
}

function initCopy() {
  main.querySelectorAll('[data-copy]').forEach(b => b.addEventListener('click', async () => {
    const out = main.querySelector('.copied');
    try {
      await navigator.clipboard.writeText(b.dataset.copy);
      out.textContent = 'Enlace copiado.';
    } catch (err) {
      out.textContent = 'Copia este enlace: ' + b.dataset.copy;
    }
  }));
}

document.addEventListener('click', e => {
  const v = e.target.closest('a.yt[data-id]');
  if (v && SITE.mode === 'static') {
    e.preventDefault();
    const f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + v.dataset.id + '?autoplay=1&rel=0' + (v.dataset.t ? '&start=' + v.dataset.t : '');
    f.title = v.getAttribute('aria-label') || 'Video';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.allowFullscreen = true;
    v.replaceWith(f);
  }
});
document.addEventListener('click', e => {
  const a = e.target.closest('a[data-jump]');
  if (!a) return;
  const el = document.getElementById(a.dataset.jump);
  if (el) { e.preventDefault(); el.scrollIntoView({behavior: reduce ? 'auto' : 'smooth'}); }
});
if (SITE.mode === 'static') {
  const rd = document.getElementById('ruler-data');
  DATA = {ruler: rd ? JSON.parse(rd.textContent) : []};
  if (document.getElementById('rfig')) initRuler();
  if (document.getElementById('q')) initArchive();
  initCopy();
} else {
  window.addEventListener('hashchange', route);
  fetch('site.json').then(r => r.json()).then(d => { DATA = d; route(); }).catch(() => {
    main.innerHTML = '<div class="wrap"><p class="empty">No se pudo cargar el contenido. Vuelve a abrir la página.</p></div>';
  });
}
}
