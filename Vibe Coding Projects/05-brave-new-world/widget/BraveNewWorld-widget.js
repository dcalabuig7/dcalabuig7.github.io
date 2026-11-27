// Brave New World · widget de titulares para Scriptable (iPhone)
// Titulares en directo de El País y BBC. No están verificados:
// la versión verificada es el diario Brave New World (enlace dentro de la lista desplegable).
//
// Parámetro del widget (opcional): una sección, por ejemplo
//   Reino Unido · España · Internacional · Economía · Tecnología · Ciencia · Cultura · Deportes
// Sin parámetro: la noticia principal de cada sección.

const DIARIO = "https://claude.ai/artifact/EwLgqi7CKUYUrjjDsGAoR2";
const EP = "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/";
const BBC = "https://feeds.bbci.co.uk/";

const SECCIONES = [
  { n: "Reino Unido", k: "reino",  feeds: [[BBC + "news/uk/rss.xml", "BBC"]] },
  { n: "España",      k: "espa",   feeds: [[EP + "espana/portada", "El País"], ["https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "El País"]] },
  { n: "Internacional", k: "inter", feeds: [[EP + "internacional/portada", "El País"], [BBC + "news/world/rss.xml", "BBC"]] },
  { n: "Economía",    k: "econo",  feeds: [[EP + "economia/portada", "El País"], [BBC + "news/business/rss.xml", "BBC"]] },
  { n: "Tecnología",  k: "tecno",  feeds: [[EP + "tecnologia/portada", "El País"], [BBC + "news/technology/rss.xml", "BBC"]] },
  { n: "Ciencia y salud", k: "cienc", feeds: [[EP + "ciencia/portada", "El País"], [BBC + "news/science_and_environment/rss.xml", "BBC"]] },
  { n: "Cultura",     k: "cultu",  feeds: [[EP + "cultura/portada", "El País"], [BBC + "news/entertainment_and_arts/rss.xml", "BBC"]] },
  { n: "Deportes",    k: "depor",  feeds: [[EP + "deportes/portada", "El País"], [BBC + "sport/rss.xml", "BBC"]] },
];

const ROJO = new Color("#d10f1f");
const TINTA = new Color("#0d0d0d");
const PAPEL = new Color("#f1f1ee");
const ACERO = new Color("#5a5f66");
const BLANCO = new Color("#fbfbf9");

// ---------- datos ----------
function limpia(s) {
  return (s || "")
    .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'")
    .replace(/&#(\d+);/g, (m, d) => String.fromCharCode(+d))
    .replace(/\s+/g, " ").trim();
}
function campo(item, tag) {
  const m = item.match(new RegExp("<" + tag + "[^>]*>([\\s\\S]*?)</" + tag + ">", "i"));
  return m ? limpia(m[1]) : "";
}
async function leeFeed(url, medio) {
  const r = new Request(url);
  r.timeoutInterval = 12;
  const xml = await r.loadString();
  const items = xml.match(/<item[\s>][\s\S]*?<\/item>/gi) || [];
  const out = items.slice(0, 5).map(it => ({
    titulo: campo(it, "title"),
    url: campo(it, "link") || campo(it, "guid"),
    img: ((it.match(/<media:(?:content|thumbnail)[^>]*url="([^"]+)"/i) || it.match(/<enclosure[^>]*url="([^"]+)"/i) || [])[1] || "").replace(/&amp;/g, "&"),
    medio,
  })).filter(x => x.titulo && x.url);
  if (!out.length) throw new Error("vacío");
  return out;
}
async function leeSeccion(sec) {
  for (const [u, medio] of sec.feeds) {
    try { return { ...sec, noticias: await leeFeed(u, medio) }; } catch (e) {}
  }
  return { ...sec, noticias: [] };
}

const fm = FileManager.local();
const CACHE = fm.joinPath(fm.documentsDirectory(), "bnw-cache.json");
async function cargaTodo() {
  let datos = await Promise.all(SECCIONES.map(leeSeccion));
  const hay = datos.some(s => s.noticias.length);
  if (hay) {
    fm.writeString(CACHE, JSON.stringify({ hora: Date.now(), datos }));
    return { datos, hora: new Date(), cache: false };
  }
  if (fm.fileExists(CACHE)) {
    const c = JSON.parse(fm.readString(CACHE));
    return { datos: c.datos, hora: new Date(c.hora), cache: true };
  }
  return { datos, hora: new Date(), cache: false };
}

function hora(d) {
  const f = new DateFormatter();
  f.locale = "es_ES";
  f.dateFormat = "HH:mm";
  return f.string(d);
}

// ---------- widget ----------
function anchoWidget() {
  const w = Device.screenSize().width;
  return w >= 428 ? 364 : w >= 414 ? 360 : w >= 390 ? 338 : 329;
}
async function imagen(url) {
  if (!url) return null;
  try { const r = new Request(url); r.timeoutInterval = 8; return await r.loadImage(); } catch (e) { return null; }
}
function cabecera(w, titulo, h, cache) {
  const top = w.addStack();
  top.centerAlignContent();
  top.backgroundColor = TINTA;
  top.setPadding(5, 8, 5, 8);
  top.cornerRadius = 3;
  const marca = top.addText("BRAVE NEW WORLD");
  marca.font = Font.blackSystemFont(11);
  marca.textColor = Color.white();
  top.addSpacer(6);
  const sec = top.addText(titulo.toUpperCase());
  sec.font = Font.boldMonospacedSystemFont(8);
  sec.textColor = new Color("#ff4d5a");
  top.addSpacer();
  const t = top.addText((cache ? "SIN RED · " : "") + hora(h));
  t.font = Font.boldMonospacedSystemFont(9);
  t.textColor = new Color("#cccccc");
}
function etiqueta(st, texto) {
  const e = st.addText(texto.toUpperCase());
  e.font = Font.heavySystemFont(8);
  e.textColor = ROJO;
  e.lineLimit = 1;
}
function titular(st, texto, tam, lineas) {
  const t = st.addText(texto);
  t.font = Font.boldSystemFont(tam);
  t.textColor = TINTA;
  t.lineLimit = lineas;
  t.minimumScaleFactor = 0.85;
}

async function creaWidget({ datos, hora: h, cache }) {
  const fam = config.widgetFamily || "large";
  const param = (args.widgetParameter || "").trim().toLowerCase();
  const sec = param ? datos.find(s => s.n.toLowerCase().includes(param) || param.includes(s.k)) : null;

  // lista de [noticia, etiqueta]
  let lista;
  if (sec) lista = sec.noticias.map(n => [n, sec.n + " · " + n.medio]);
  else {
    const llenas = datos.filter(s => s.noticias.length);
    // rota las secciones cada media hora para que con el tiempo salgan las 8
    const giro = llenas.length ? Math.floor(Date.now() / (30 * 60 * 1000)) % 2 * 4 % llenas.length : 0;
    lista = llenas.slice(giro).concat(llenas.slice(0, giro)).map(s => [s.noticias[0], s.n + " · " + s.noticias[0].medio]);
  }

  const w = new ListWidget();
  w.backgroundColor = PAPEL;
  w.setPadding(12, 12, 10, 12);
  w.refreshAfterDate = new Date(Date.now() + 30 * 60 * 1000);
  cabecera(w, sec ? sec.n : "Titulares", h, cache);
  w.addSpacer(8);

  if (!lista.length) {
    const t = w.addText("No se han podido cargar los titulares. Toca para reintentar.");
    t.font = Font.systemFont(12); t.textColor = TINTA;
    return w;
  }

  if (fam === "small") {
    const [n, etq] = lista[0];
    etiqueta(w, etq); w.addSpacer(2); titular(w, n.titulo, 14, 5);
    w.addSpacer();
    return w;
  }

  // noticia principal: foto + titular
  const [n0, e0] = lista[0];
  const lead = w.addStack();
  lead.url = n0.url;
  lead.centerAlignContent();
  const img = fam === "large" ? await imagen(n0.img) : null;
  if (img) {
    const im = lead.addImage(img);
    im.imageSize = new Size(86, 86);
    im.cornerRadius = 4;
    im.applyFillingContentMode();
    lead.addSpacer(10);
  }
  const lt = lead.addStack();
  lt.layoutVertically();
  etiqueta(lt, e0); lt.addSpacer(3);
  titular(lt, n0.titulo, fam === "large" ? 16 : 14, img ? 4 : 3);
  lead.addSpacer();

  if (fam === "medium") {
    w.addSpacer(8);
    const [n1, e1] = lista[1] || [];
    if (n1) { const s = w.addStack(); s.layoutVertically(); s.url = n1.url; etiqueta(s, e1); s.addSpacer(2); titular(s, n1.titulo, 12.5, 2); }
    w.addSpacer();
    return w;
  }

  // rejilla 2 x 2
  w.addSpacer(9);
  const raya = w.addStack(); raya.size = new Size(0, 1); raya.backgroundColor = new Color("#cfcfca");
  w.addSpacer(9);
  const anchoCelda = Math.floor((anchoWidget() - 24 - 14) / 2);
  const resto = lista.slice(1, 5);
  for (let fila = 0; fila < 2; fila++) {
    const f = w.addStack();
    f.topAlignContent();
    for (let col = 0; col < 2; col++) {
      const item = resto[fila * 2 + col];
      const c = f.addStack();
      c.layoutVertically();
      c.size = new Size(anchoCelda, 0);
      if (item) {
        c.url = item[0].url;
        etiqueta(c, item[1]); c.addSpacer(2);
        titular(c, item[0].titulo, 12.5, 3);
        c.addSpacer();
      }
      if (col === 0) f.addSpacer(14);
    }
    if (fila === 0) w.addSpacer(10);
  }
  w.addSpacer();
  const pie = w.addText(sec ? "Sin verificar · Toca el borde para ver más" : "Sin verificar · Cambia de secciones cada 30 min · Toca el borde para ver las 8");
  pie.font = Font.mediumSystemFont(7.5);
  pie.textColor = ACERO;
  pie.lineLimit = 1;
  pie.minimumScaleFactor = 0.8;
  return w;
}

// ---------- vista desplegable dentro de la app ----------
async function muestraTabla({ datos, hora: h, cache }) {
  const tabla = new UITable();
  tabla.showSeparators = true;
  const abiertas = new Set([datos[0] && datos[0].n]);

  function pinta() {
    tabla.removeAllRows();
    const cab = new UITableRow();
    cab.isHeader = true;
    cab.height = 64;
    cab.backgroundColor = TINTA;
    const c = cab.addText("BRAVE NEW WORLD", "Titulares en directo, sin verificar · " + (cache ? "sin conexión, copia de las " : "actualizado a las ") + hora(h));
    c.titleColor = Color.white(); c.subtitleColor = new Color("#cccccc");
    c.titleFont = Font.blackSystemFont(18); c.subtitleFont = Font.systemFont(11);
    tabla.addRow(cab);

    const ir = new UITableRow();
    ir.height = 48;
    ir.dismissOnSelect = false;
    ir.backgroundColor = ROJO;
    const ci = ir.addText("Abrir el diario verificado ›");
    ci.titleColor = Color.white(); ci.titleFont = Font.boldSystemFont(15);
    ir.onSelect = () => Safari.open(DIARIO);
    tabla.addRow(ir);

    for (const s of datos) {
      const abierta = abiertas.has(s.n);
      const r = new UITableRow();
      r.height = 50;
      r.dismissOnSelect = false;
      r.backgroundColor = abierta ? TINTA : PAPEL;
      const t = r.addText((abierta ? "▾  " : "▸  ") + s.n.toUpperCase(), s.noticias.length ? s.noticias.length + " titulares · " + s.noticias[0].medio : "No disponible ahora");
      t.titleFont = Font.boldSystemFont(15); t.titleColor = abierta ? Color.white() : TINTA;
      t.subtitleFont = Font.mediumMonospacedSystemFont(10); t.subtitleColor = abierta ? new Color("#cccccc") : ACERO;
      r.onSelect = () => { abierta ? abiertas.delete(s.n) : abiertas.add(s.n); pinta(); };
      tabla.addRow(r);
      if (!abierta) continue;
      s.noticias.forEach((n, i) => {
        const fr = new UITableRow();
        const lineas = Math.ceil(((i + 1) + ". " + n.titulo).length / 36);
        fr.height = 34 + lineas * 21;
        fr.dismissOnSelect = false;
        fr.backgroundColor = BLANCO;
        fr.cellSpacing = 4;
        const num = fr.addText(String(i + 1));
        num.widthWeight = 8;
        num.titleFont = Font.boldMonospacedSystemFont(15); num.titleColor = ROJO;
        const ct = fr.addText(n.titulo, n.medio.toUpperCase() + " · TOCA PARA LEER");
        ct.widthWeight = 92;
        ct.titleFont = Font.semiboldSystemFont(15); ct.titleColor = TINTA;
        ct.subtitleFont = Font.mediumMonospacedSystemFont(9); ct.subtitleColor = ACERO;
        fr.onSelect = () => Safari.open(n.url);
        tabla.addRow(fr);
      });
    }
    tabla.reload();
  }
  pinta();
  await tabla.present(false);
}

// ---------- arranque ----------
const datos = await cargaTodo();
if (config.runsInWidget) {
  Script.setWidget(await creaWidget(datos));
} else {
  await muestraTabla(datos);
}
Script.complete();
