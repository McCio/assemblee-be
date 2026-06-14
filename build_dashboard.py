#!/usr/bin/env python3
# /// script
# dependencies = []
# ///
import json
import urllib.request
from collections import Counter
from pathlib import Path

NORMALIZED = Path("normalized")
OUT = Path("dashboard.html")
VENDOR_DIR = Path("vendor")
CHARTJS_URL = "https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"
CHARTJS_VENDOR = VENDOR_DIR / "chart.umd.min.js"

FLAGS_DIR = VENDOR_DIR / "flags"
OPENMOJI_BASE = "https://github.com/hfg-gmuend/openmoji/raw/master/color/svg/"

FLAG_FILES = {
    "it":      ("1F1EE-1F1F9.svg", "IT"),
    "en":      ("1F1EC-1F1E7.svg", "EN"),
    "es-cast": ("1F1EA-1F1F8.svg", "ES"),
    "es-cat":  ("1F3F4-E0065-E0073-E0063-E0074-E007F.svg", "CA"),
    "es-gal":  ("1F3F4-E0065-E0073-E0067-E0061-E007F.svg", "GL"),
    "eu":      ("1F3F4-E0065-E0073-E0070-E0076-E007F.svg", "EU"),
    "de":      ("1F1E9-1F1EA.svg", "DE"),
}


def ensure_chartjs():
    if not CHARTJS_VENDOR.exists():
        VENDOR_DIR.mkdir(exist_ok=True)
        print(f"Downloading Chart.js from {CHARTJS_URL}...")
        urllib.request.urlretrieve(CHARTJS_URL, CHARTJS_VENDOR)
        print(f"Vendored Chart.js ({CHARTJS_VENDOR.stat().st_size // 1024}KB)")
    return CHARTJS_VENDOR.read_text()


def ensure_flags():
    """Download OpenMoji flag SVGs if not already present. Returns dict lang -> svg_text."""
    import re
    FLAGS_DIR.mkdir(parents=True, exist_ok=True)
    svgs = {}
    for lang, (filename, label) in FLAG_FILES.items():
        dest = FLAGS_DIR / filename
        if not dest.exists():
            url = OPENMOJI_BASE + filename
            print(f"Downloading flag {filename} from OpenMoji...")
            urllib.request.urlretrieve(url, dest)
            print(f"  Saved {dest} ({dest.stat().st_size}B)")
        raw = dest.read_text(encoding="utf-8")
        if raw.startswith("<?xml"):
            raw = raw[raw.index("<svg"):]
        raw = raw.strip()
        if 'width=' not in raw[:100]:
            raw = raw.replace("<svg ", '<svg width="20" height="20" ', 1)
        else:
            raw = re.sub(r'width="[^"]*"', 'width="20"', raw, count=1)
            raw = re.sub(r'height="[^"]*"', 'height="20"', raw, count=1)
        svgs[lang] = raw
    return svgs


TRANSLATIONS = json.loads(Path("translations.json").read_text())

MONTH_IT = {
    "01": "Gen", "02": "Feb", "03": "Mar", "04": "Apr",
    "05": "Mag", "06": "Giu", "07": "Lug", "08": "Ago",
    "09": "Set", "10": "Ott", "11": "Nov", "12": "Dic",
}

PROVINCE_AREA = {
    "Agrigento": "Isole", "Alessandria": "Nord-Ovest", "Ancona": "Centro",
    "Aosta": "Nord-Ovest", "Arezzo": "Centro", "Ascoli Piceno": "Centro",
    "Asti": "Nord-Ovest", "Avellino": "Sud", "Bari": "Sud",
    "Barletta-Andria-Trani": "Sud", "Belluno": "Nord-Est", "Benevento": "Sud",
    "Bergamo": "Nord-Ovest", "Biella": "Nord-Ovest", "Bologna": "Nord-Est",
    "Bolzano/Bozen": "Nord-Est", "Brescia": "Nord-Ovest", "Brindisi": "Sud",
    "Cagliari": "Isole", "Caltanissetta": "Isole", "Campobasso": "Sud",
    "Caserta": "Sud", "Catania": "Isole", "Catanzaro": "Sud",
    "Chieti": "Sud", "Como": "Nord-Ovest", "Cosenza": "Sud",
    "Cremona": "Nord-Ovest", "Crotone": "Sud", "Cuneo": "Nord-Ovest",
    "Enna": "Isole", "Fermo": "Centro", "Ferrara": "Nord-Est",
    "Firenze": "Centro", "Foggia": "Sud", "Forlì-Cesena": "Nord-Est",
    "Frosinone": "Centro", "Genova": "Nord-Ovest", "Gorizia": "Nord-Est",
    "Grosseto": "Centro", "Imperia": "Nord-Ovest", "Isernia": "Sud",
    "La Spezia": "Nord-Ovest", "L'Aquila": "Sud", "Latina": "Centro",
    "Lecce": "Sud", "Lecco": "Nord-Ovest", "Livorno": "Centro",
    "Lodi": "Nord-Ovest", "Lucca": "Centro", "Macerata": "Centro",
    "Mantova": "Nord-Ovest", "Massa-Carrara": "Centro", "Matera": "Sud",
    "Messina": "Isole", "Milano": "Nord-Ovest", "Modena": "Nord-Est",
    "Monza e della Brianza": "Nord-Ovest", "Napoli": "Sud", "Novara": "Nord-Ovest",
    "Nuoro": "Isole", "Oristano": "Isole", "Padova": "Nord-Est",
    "Palermo": "Isole", "Parma": "Nord-Est", "Pavia": "Nord-Ovest",
    "Perugia": "Centro", "Pesaro e Urbino": "Centro", "Pescara": "Sud",
    "Piacenza": "Nord-Est", "Pisa": "Centro", "Pistoia": "Centro",
    "Pordenone": "Nord-Est", "Potenza": "Sud", "Prato": "Centro",
    "Ragusa": "Isole", "Ravenna": "Nord-Est", "Reggio di Calabria": "Sud",
    "Reggio nell'Emilia": "Nord-Est", "Rieti": "Centro", "Rimini": "Nord-Est",
    "Roma": "Centro", "Rovigo": "Nord-Est", "Salerno": "Sud",
    "Sassari": "Isole", "Savona": "Nord-Ovest", "Siena": "Centro",
    "Siracusa": "Isole", "Sondrio": "Nord-Ovest", "Sud Sardegna": "Isole",
    "Taranto": "Sud", "Teramo": "Sud", "Terni": "Centro",
    "Torino": "Nord-Ovest", "Trapani": "Isole", "Trento": "Nord-Est",
    "Treviso": "Nord-Est", "Trieste": "Nord-Est", "Udine": "Nord-Est",
    "Varese": "Nord-Ovest", "Venezia": "Nord-Est", "Verbano-Cusio-Ossola": "Nord-Ovest",
    "Vercelli": "Nord-Ovest", "Verona": "Nord-Est", "Vibo Valentia": "Sud",
    "Vicenza": "Nord-Est", "Viterbo": "Centro",
}
AREA_ORDER = ["Nord-Ovest", "Nord-Est", "Centro", "Sud", "Isole"]

# Each entry: (data_category_id, cat_translation_key, [field_data_and_translation_keys])
# Field keys double as both the JSON data key and the translations.json key.
CATEGORIES = [
    ("participants", "cat_partecipanti", ["votanti_normali", "rappresentanze", "deleghe"]),
    ("mode",         "cat_modalita",     ["a_distanza", "in_presenza"]),
    ("typology",     "cat_tipologia_soci", ["persone_fisiche", "persone_giuridiche"]),
    ("genre",        "cat_genere",       ["donne", "uomini"]),
    ("geography",    "cat_geografia",    ["italia", "spagna", "estero"]),
]


def label_for(stem, multi_month_years):
    year, month = stem.split(".")
    return f"{year} {MONTH_IT[month]}" if year in multi_month_years else year


def load_data():
    return {p.stem: json.loads(p.read_text()) for p in sorted(NORMALIZED.glob("*.json"))}


def build_lang_pills(flag_svgs):
    pills = []
    order = ["it", "en", "es-cast", "es-cat", "es-gal", "eu", "de"]
    for lang in order:
        svg = flag_svgs.get(lang, "")
        _, label = FLAG_FILES[lang]
        active_class = ' on' if lang == 'it' else ''
        pills.append(
            f'    <span class="lang-pill{active_class}" data-lang="{lang}" '
            f'onclick="setLang(\'{lang}\')" title="{lang}">'
            f'{svg} {label}</span>'
        )
    return "\n".join(pills)


def build():
    chartjs = ensure_chartjs()
    flag_svgs = ensure_flags()
    data = load_data()
    keys = sorted(data.keys())
    year_counts = Counter(k.split(".")[0] for k in keys)
    multi_month_years = {y for y, c in year_counts.items() if c > 1}
    labels = {k: label_for(k, multi_month_years) for k in keys}

    key_meta = {
        k: {"year": int(k.split(".")[0]), "month": int(k.split(".")[1]),
            "multi": k.split(".")[0] in multi_month_years}
        for k in keys
    }
    data_js     = json.dumps(data, ensure_ascii=False)
    labels_js   = json.dumps(labels, ensure_ascii=False)
    keys_js     = json.dumps(keys, ensure_ascii=False)
    key_meta_js = json.dumps(key_meta, ensure_ascii=False)
    cats_js     = json.dumps([[c, l, f] for c, l, f in CATEGORIES], ensure_ascii=False)
    pa_js       = json.dumps(PROVINCE_AREA, ensure_ascii=False)
    ao_js       = json.dumps(AREA_ORDER, ensure_ascii=False)
    trans_js    = json.dumps(TRANSLATIONS, ensure_ascii=False)

    lang_pills_html = build_lang_pills(flag_svgs)

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Banca Etica – Assemblee (partecipazione)</title>
<script>{chartjs}</script>
<style>
:root {{
  --c-dark:  rgb(0,48,135);
  --c-light: rgb(0,200,255);
  --c-black: rgb(0,38,58);
  --c-mid:   rgb(0,100,180);
  --sticky-filter-h: 0px;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,sans-serif;background:#f5f5f5;color:#222;padding:24px;max-width:1400px;margin:0 auto}}
.title-bar{{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:16px;flex-wrap:wrap}}
h1{{font-size:1.4rem}}
.toolbar{{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-bottom:20px}}
.toolbar label{{font-weight:600;font-size:.9rem}}
.filter-row{{position:sticky;top:0;z-index:100;background:#f5f5f5;padding:10px 0;margin-bottom:12px;box-shadow:0 2px 6px rgba(0,0,0,.09)}}
.year-row{{position:sticky;top:var(--sticky-filter-h);z-index:99;background:#f5f5f5;padding:8px 0;margin-bottom:20px;box-shadow:0 2px 4px rgba(0,0,0,.07);justify-content:center}}
.prog-wrap{{position:relative;overflow:visible}}
#prog-popover{{display:none;position:absolute;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 2px 12px rgba(0,0,0,.15);padding:8px;z-index:200}}
  .arrow-sep{{font-size:.9rem;font-weight:700;color:var(--c-mid);flex-shrink:0;opacity:.7;letter-spacing:.04em}}.clear-badge>span{{transform:translateY(-1px)}}
select{{padding:5px 8px;font-size:.95rem;border-radius:6px;border:1px solid #ccc;background:#fff}}
.pill{{padding:5px 14px;border-radius:20px;border:1px solid #ccc;cursor:pointer;font-size:.83rem;background:#fff;user-select:none}}
.pill.on{{background:var(--c-dark);color:#fff;border-color:var(--c-dark)}}
.lang-pill{{padding:4px 10px;border-radius:20px;border:1px solid #ccc;cursor:pointer;font-size:.78rem;background:#fff;user-select:none;display:inline-flex;align-items:center;gap:4px}}
.lang-pill.on{{background:var(--c-dark);color:#fff;border-color:var(--c-dark)}}
.lang-pill svg{{vertical-align:middle;flex-shrink:0}}
.card{{background:#fff;border-radius:10px;padding:18px;box-shadow:0 1px 4px rgba(0,0,0,.08);margin-bottom:20px}}
.card h2{{font-size:.9rem;font-weight:700;color:#555;text-transform:uppercase;letter-spacing:.05em;margin-bottom:14px}}
.chart-wrap{{position:relative;height:200px}}
table{{width:100%;border-collapse:collapse;font-size:.88rem}}
th{{text-align:left;padding:5px 8px;border-bottom:2px solid #eee;color:#666;font-weight:600}}
td{{padding:5px 8px;border-bottom:1px solid #f0f0f0}}
td.num{{text-align:right;font-variant-numeric:tabular-nums}}
.pos{{color:#2a9d2a;font-weight:600}} .neg{{color:#c0392b;font-weight:600}} .na{{color:#aaa}}
.grp-sep{{border-left:2px solid #ddd}}
.zone-table{{font-size:.82rem}}
.zone-table td,.zone-table th{{padding:4px 8px}}
.zone-table tr.area-total td{{background:color-mix(in srgb,var(--c-dark) 10%,transparent)}}
.zone-table tr.area-total td:first-child{{font-weight:700}}
.zone-table tr.area-row td{{background:color-mix(in srgb,var(--c-light) 12%,transparent)}}
.zone-table tr.area-row td:first-child{{font-weight:700}}
.zone-table tr.province-row td{{padding-left:20px}}
.zone-table.hide-provinces tr.province-row{{display:none}}
.zone-table .grp-sep{{border-left:2px solid #bbb}}
.zone-table td.col-tot{{font-weight:700}}
.zone-table tr.clickable{{cursor:pointer}}
.zone-table tr.clickable:hover td{{background:color-mix(in srgb,var(--c-dark) 6%,transparent)}}
.zone-table tr.sel-row td{{background:color-mix(in srgb,var(--c-dark) 18%,transparent)!important;outline:2px solid var(--c-dark);outline-offset:-2px}}
tr.pie-hover td{{background:color-mix(in srgb,var(--c-dark) 8%,transparent)}}
.clear-badge{{font-size:.7rem;background:#e44;color:#fff;border-radius:10px;padding:1px 6px;margin-left:6px;cursor:pointer;display:inline-flex;align-items:center;vertical-align:middle}}
.zone-controls{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:10px}}

.zone-search{{padding:4px 8px;border:1px solid #ccc;border-radius:6px;font-size:.82rem;width:180px}}
.sel-label{{font-size:.85rem;color:var(--c-dark);font-weight:600;padding:4px 8px;background:color-mix(in srgb,var(--c-dark) 8%,transparent);border-radius:6px;display:inline-flex;align-items:center}}
.cats{{display:flex;flex-wrap:wrap;gap:16px}}.cats>.card{{flex:1 1 460px;min-width:0}}
.zone-unavail{{color:#aaa;font-style:italic;font-size:.85rem;padding:8px}}
.prog-controls{{display:flex;gap:8px;align-items:center;margin-bottom:10px;font-size:.85rem}}
.lang-bar{{display:flex;gap:4px;align-items:center;flex-wrap:wrap}}
.pie-wrap{{display:flex;gap:24px;flex-wrap:nowrap;overflow-x:auto;margin-bottom:4px}}
.pie-item{{flex:1 1 240px;min-width:220px;max-width:380px;text-align:center}}
.pie-canvas-wrap{{position:relative;height:260px}}
.pie-label{{font-size:.78rem;color:#666;margin-bottom:4px}}
footer{{margin-top:32px;padding:16px 0;border-top:1px solid #e0e0e0;font-size:.8rem;color:#888;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}}
footer a{{color:var(--c-mid);text-decoration:none}}footer a:hover{{text-decoration:underline}}
.made-by{{color:#555}}
</style>
</head>
<body>
<!--
  Flag icons: OpenMoji (https://openmoji.org/) — CC BY-SA 4.0
  National flags: Unicode CLDR flag sequences.
  Regional flags (Catalonia, Galicia, Basque Country): OpenMoji extras-unicode subdivision flags.
  Attribution: OpenMoji project by HfG Gmünd (https://github.com/hfg-gmuend/openmoji)
-->
<div class="title-bar">
  <h1 id="page-title">Banca Etica — Assemblee (partecipazione)</h1>
  <div class="lang-bar">
{lang_pills_html}
  </div>
</div>
<div id="filter-row" class="toolbar filter-row">
  <span style="display:inline-flex;gap:8px;flex-wrap:wrap;align-items:center">
    <span id="pill-genre"     class="pill on" onclick="togglePill('genre')">Donne/Uomini</span>
    <span id="pill-tipologia" class="pill on" onclick="togglePill('tipologia')">Pers. fisiche/giuridiche</span>
    <span id="pill-mode"      class="pill on" onclick="togglePill('mode')">Presenza/Distanza</span>
  </span>
  <span id="sel-label" class="sel-label" style="display:none"></span>
</div>
<div class="card" id="prog-card">
  <h2 id="prog-title">Progressione annuale</h2>
  <div class="prog-controls">
    <span class="pill on" data-prog="votanti" onclick="toggleProgMetric('votanti')">Partecipazione</span>
    <span class="pill"    data-prog="soci"    onclick="toggleProgMetric('soci')">Pers. socie</span>
    <span class="pill"    data-prog="mode"    onclick="toggleProgMetric('mode')">Presenza/Distanza</span>
  </div>
  <div class="prog-wrap">
    <div class="chart-wrap" style="height:320px"><canvas id="prog-chart"></canvas></div>
    <div id="prog-popover"></div>
  </div>
</div>
<div id="year-row" class="toolbar year-row">
  <label id="label-anno-a">Anno A <select id="selA"></select></label>
  <span class="arrow-sep">→</span>
  <label id="label-anno-b">Anno B <select id="selB"></select></label>
</div>

<div class="card" id="zone-card">
  <h2 id="zone-card-title">Zone geografiche</h2>
  <div class="zone-controls">
    <span class="pill" id="provinceToggle" onclick="toggleProvinces()">Mostra province</span>
    <input class="zone-search" id="zone-search" type="text" placeholder="Cerca provincia…" oninput="renderZones()" style="display:none">
  </div>
  <div id="zones-content"></div>
</div>

<div style="margin-bottom:12px;display:flex;justify-content:flex-end">
  <span id="pill-chart-mode" class="pill" onclick="toggleChartMode()">⭕ Torte</span>
</div>
<div id="charts-section"></div>

<footer>
  <div style="display:flex;flex-direction:column;gap:3px">
    <span><span id="footer-fonte-label">Fonte</span>: <a href="https://www.bancaetica.it/archivio-assemblee/" target="_blank" rel="noopener">Archivio Assemblee — Banca Etica</a></span>
    <span><span id="footer-dati-label">Dati</span>: <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a></span>
    <span><span id="footer-codice-label">Codice</span>: <a href="https://github.com/McCio/assemblee-be" target="_blank" rel="noopener">GitHub</a> · <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank" rel="noopener">CC0 1.0</a></span>
  </div>
  <span class="made-by" id="footer-made-by">Fatto con ♥️ da Marco Ciotola 🧠 con Claude 🤖</span>
</footer>

<script>
const RAW    = {data_js};
const LABELS = {labels_js};
const KEYS   = {keys_js};
const KEY_META = {key_meta_js};
const CATS   = {cats_js};
const PROVINCE_AREA = {pa_js};
const AREA_ORDER    = {ao_js};
const TRANSLATIONS  = {trans_js};

const CSS = getComputedStyle(document.documentElement);
const C_DARK  = CSS.getPropertyValue('--c-dark').trim();
const C_LIGHT = CSS.getPropertyValue('--c-light').trim();
const C_MID   = CSS.getPropertyValue('--c-mid').trim();
function rgba(c, a) {{ return c.replace('rgb(', 'rgba(').replace(')', `,${{a}})`); }}
const COLOR_A = rgba(C_DARK, .85), COLOR_B = rgba(C_LIGHT, .85);
const BORDER_A = C_DARK, BORDER_B = rgba(C_LIGHT, .9);

let sel = {{type:'none'}};
let provincesHidden = true;
let fieldToggles = {{genre: true, tipologia: true, mode: true}};
let chartMode = 'pie';
let _pieHoverLock = false;
function setPieHover(baseId, idx) {{
  if (_pieHoverLock) return;
  _pieHoverLock = true;
  document.querySelectorAll(`[data-chart-id="${{baseId}}"]`).forEach(tr => {{
    tr.classList.toggle('pie-hover', parseInt(tr.dataset.pieIdx) === idx);
  }});
  for (const sfx of ['-a','-b']) {{
    const c = charts[baseId+sfx];
    if (!c) continue;
    if (idx >= 0) {{
      c.setActiveElements([{{datasetIndex:0,index:idx}}]);
      const sliceEl=c.getDatasetMeta(0).data[idx];
      if (sliceEl) c.tooltip.setActiveElements([{{datasetIndex:0,index:idx}}],sliceEl.getCenterPoint());
    }} else {{
      c.setActiveElements([]);
      c.tooltip.setActiveElements([],{{}});
    }}
    c.update('none');
  }}
  _pieHoverLock = false;
}}
let charts = {{}};
let progMetrics = new Set(['votanti']);
let LANG = 'it';
(function(){{const fr=document.getElementById('filter-row');if(fr&&window.ResizeObserver){{const upd=()=>document.documentElement.style.setProperty('--sticky-filter-h',fr.offsetHeight+'px');new ResizeObserver(upd).observe(fr);upd();}}}})();

const PIE_PALETTE = ['#003087','#00a8cc','#00c87a','#ffb300','#cc2244','#7c3aed','#0e7490','#059669','#d97706','#dc2626','#7c3aed','#0284c7'];
function pieColors(n) {{ return Array.from({{length:n}},(_,i)=>PIE_PALETTE[i%PIE_PALETTE.length]); }}
function makePieChart(id, labels, data, baseId, genderParity=false) {{
  destroyChart(id);
  const el=document.getElementById(`chart-${{id}}`); if (!el) return;
  charts[id]=new Chart(el.getContext('2d'),{{type:'pie',plugins:[genderParityPiePlugin],data:{{labels,datasets:[{{data,backgroundColor:pieColors(labels.length)}}]}},options:{{responsive:true,maintainAspectRatio:false,
    onHover:(evt,els)=>{{if(baseId)setPieHover(baseId,els.length?els[0].index:-1);}},
    plugins:{{
      legend:{{display:false}},
      tooltip:{{callbacks:{{label:ctx=>{{
        const total=(ctx.dataset.data||[]).reduce((s,v)=>s+(v??0),0);
        const pct=total?((ctx.parsed/total)*100).toFixed(1):'–';
        return ` ${{ctx.label}}: ${{ctx.parsed}} (${{pct}}%)`;
      }}}}}},
    }}}}}});
  if (genderParity) charts[id]._genderParityPie=true;
}}
function pieHtml(id, lA, lB) {{
  return `<div class="pie-wrap"><div class="pie-item"><div class="pie-label">${{lA}}</div><div class="pie-canvas-wrap"><canvas id="chart-${{id}}-a"></canvas></div></div><div class="pie-item"><div class="pie-label">${{lB}}</div><div class="pie-canvas-wrap"><canvas id="chart-${{id}}-b"></canvas></div></div></div>`;
}}
function pieSwatch(i) {{
  if (chartMode !== 'pie') return '';
  return `<span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${{PIE_PALETTE[i%PIE_PALETTE.length]}};margin-right:5px;vertical-align:middle"></span>`;
}}
function toggleChartMode() {{
  chartMode = chartMode==='bar' ? 'pie' : 'bar';
  const p=document.getElementById('pill-chart-mode');
  p.classList.toggle('on', chartMode==='pie');
  p.textContent = chartMode==='bar' ? `⭕ ${{t('mostra_torte')}}` : `📊 ${{t('mostra_barre')}}`;
  pushState();
  render();
}}

// ── i18n ────────────────────────────────────────────────────────────────────
function t(k) {{ return (TRANSLATIONS[LANG] || TRANSLATIONS.it)[k] ?? k; }}

function rebuildLabels() {{
  const months = (TRANSLATIONS[LANG] || TRANSLATIONS.it).months || TRANSLATIONS.it.months;
  KEYS.forEach(stem => {{
    const m = KEY_META[stem];
    LABELS[stem] = m.multi ? `${{m.year}} ${{months[m.month - 1]}}` : String(m.year);
  }});
}}

function setLang(lang) {{
  LANG = lang;
  document.documentElement.lang = lang.startsWith('es') ? lang.replace('es-','') : lang;
  rebuildLabels();
  updateSelOptions();
  applyLang();
  pushState();
  render();
}}

function applyLang() {{
  document.title = t('page_title');
  document.getElementById('page-title').textContent = t('page_title');
  const la = document.getElementById('label-anno-a');
  const lb = document.getElementById('label-anno-b');
  la.childNodes[0].textContent = t('anno_a') + ' ';
  lb.childNodes[0].textContent = t('anno_b') + ' ';
  document.getElementById('pill-genre').textContent     = t('toggle_donne_uomini');
  document.getElementById('pill-tipologia').textContent = t('toggle_fisiche_giuridiche');
  document.getElementById('pill-mode').textContent      = t('toggle_presenza_distanza');
  document.getElementById('zone-card-title').textContent = t('zone_geografiche');
  document.getElementById('provinceToggle').textContent  = provincesHidden ? t('mostra_province') : t('nascondi_province');
  document.getElementById('zone-search').placeholder    = t('cerca_provincia');
  document.getElementById('prog-title').textContent     = t('progressione_annuale');
  document.getElementById('footer-fonte-label').textContent = t('footer_fonte');
  document.getElementById('footer-dati-label').textContent    = t('footer_dati');
  document.getElementById('footer-codice-label').textContent  = t('footer_codice');
  document.getElementById('footer-made-by').textContent     = t('footer_fatto_con');
  document.querySelectorAll('[data-prog]').forEach(p => {{
    p.textContent = t('metric_' + p.dataset.prog);
  }});
  document.querySelectorAll('.lang-pill').forEach(p => {{
    p.classList.toggle('on', p.dataset.lang === LANG);
    p.title = t('lang_' + p.dataset.lang.replace(/-/g, '_'));
  }});
  const cmp=document.getElementById('pill-chart-mode');
  if (cmp) {{ cmp.textContent = chartMode==='bar' ? `⭕ ${{t('mostra_torte')}}` : `📊 ${{t('mostra_barre')}}`; cmp.classList.toggle('on', chartMode==='pie'); }}
}}

// ── selectors ──────────────────────────────────────────────────────────────
const selA = document.getElementById('selA');
const selB = document.getElementById('selB');
function populateSel(sel, keys) {{
  const prev = sel.value;
  sel.innerHTML = '';
  keys.forEach(k => {{
    const o = document.createElement('option');
    o.value = k; o.textContent = LABELS[k]; sel.appendChild(o);
  }});
  if (keys.includes(prev)) sel.value = prev;
}}
function updateSelOptions() {{
  const iA = KEYS.indexOf(selA.value), iB = KEYS.indexOf(selB.value);
  populateSel(selA, KEYS.slice(0, iB));
  populateSel(selB, KEYS.slice(iA + 1));
}}
populateSel(selA, KEYS);
populateSel(selB, KEYS);
selA.value = KEYS[KEYS.length - 2] || KEYS[0];
selB.value = KEYS[KEYS.length - 1];
updateSelOptions();
selA.addEventListener('change', () => {{ updateSelOptions(); pushState(); render(); }});
selB.addEventListener('change', () => {{ updateSelOptions(); pushState(); render(); }});

// ── utilities ──────────────────────────────────────────────────────────────
function fmt(v) {{ return v == null ? '–' : v.toLocaleString('it-IT'); }}
function fmtDiff(d) {{ return d == null ? '–' : (d > 0 ? '+' : '') + d.toLocaleString('it-IT'); }}
function fmtPct(p) {{ return p == null ? '–' : (p > 0 ? '+' : '') + p.toFixed(1) + '%'; }}
function diffClass(v) {{ return v == null ? 'na' : v > 0 ? 'pos' : v < 0 ? 'neg' : ''; }}
function uomini(z) {{
  if (!z) return null;
  return z.uomini??null;
}}
function sumZones(zones, names) {{
  const r = {{}};
  (names || []).forEach(n => {{
    const z = (zones || {{}})[n]; if (!z) return;
    Object.entries(z).forEach(([k,v]) => {{ if (v != null) r[k] = (r[k]||0)+v; }});
  }});
  return Object.keys(r).length ? r : null;
}}
function withGeoVot(z, geoVot) {{
  if (z && z.votanti != null) return z;
  if (geoVot == null) return z;
  return {{...(z||{{}}), votanti: geoVot}};
}}
function destroyChart(id) {{ if (charts[id]) {{ charts[id].destroy(); delete charts[id]; }} }}
function hasAnyField(zones, field) {{
  return zones && Object.values(zones).some(z => z && z[field] != null);
}}

// ── URL state encoding ──────────────────────────────────────────────────────
function encodeSelState() {{
  if (sel.type === 'none') return 'none';
  return encodeURIComponent(sel.key || 'none');
}}
function encodeState() {{
  return [
    `lang=${{LANG}}`,
    `annoA=${{selA.value}}`,
    `annoB=${{selB.value}}`,
    `sel=${{encodeSelState()}}`,
    `mode=${{chartMode}}`,
    `genre=${{fieldToggles.genre?1:0}}`,
    `tipologia=${{fieldToggles.tipologia?1:0}}`,
    `modeToggle=${{fieldToggles.mode?1:0}}`,
    `metric=${{Array.from(progMetrics).join(',')}}`,
  ].join('&');
}}
function pushState() {{
  history.replaceState(null, '', '#' + encodeState());
}}
function parseHash() {{
  const raw = window.location.hash.slice(1);
  if (!raw) return null;
  const params = {{}};
  raw.split('&').forEach(pair => {{
    const eq = pair.indexOf('=');
    if (eq < 0) return;
    params[pair.slice(0,eq)] = decodeURIComponent(pair.slice(eq+1));
  }});
  return params;
}}
function restoreSelFromKey(selKey) {{
  if (!selKey || selKey === 'none') {{ sel = {{type:'none'}}; return; }}
  const colon = selKey.indexOf(':');
  if (colon < 0) {{ sel = {{type:'none'}}; return; }}
  const type = selKey.slice(0,colon), key = selKey.slice(colon+1);
  const kA=selA.value, kB=selB.value;
  const itA=((RAW[kA]||{{}}).zones||{{}}).italia||{{}}, itB=((RAW[kB]||{{}}).zones||{{}}).italia||{{}};
  const esA=((RAW[kA]||{{}}).zones||{{}}).spagna||{{}}, esB=((RAW[kB]||{{}}).zones||{{}}).spagna||{{}};
  const allIt=[...new Set([...Object.keys(itA),...Object.keys(itB)])];
  const allEs=[...new Set([...Object.keys(esA),...Object.keys(esB)])].sort();
  if (type==='it-total') {{
    const children=AREA_ORDER.filter(a=>allIt.some(n=>PROVINCE_AREA[n]===a));
    sel={{type:'group',key:selKey,labelKey:'sel_italia',children,childType:'area'}};
  }} else if (type==='area') {{
    const children=allIt.filter(n=>PROVINCE_AREA[n]===key).sort();
    sel={{type:'group',key:selKey,label:key,children,childType:'province'}};
  }} else if (type==='es-total') {{
    sel={{type:'group',key:selKey,labelKey:'sel_spagna',children:allEs,childType:'fiare'}};
  }} else if (type==='province'||type==='fiare') {{
    sel={{type:'leaf',key:selKey,name:key,label:key}};
  }} else {{
    sel={{type:'none'}};
  }}
}}
function applyState(params) {{
  if (!params) return;
  if (params.lang && TRANSLATIONS[params.lang]) {{
    LANG = params.lang;
    document.documentElement.lang = LANG.startsWith('es') ? LANG.replace('es-','') : LANG;
  }}
  rebuildLabels();
  if (params.annoA && KEYS.includes(params.annoA)) selA.value = params.annoA;
  if (params.annoB && KEYS.includes(params.annoB)) selB.value = params.annoB;
  updateSelOptions();
  if (params.annoA && KEYS.includes(params.annoA)) selA.value = params.annoA;
  if (params.annoB && KEYS.includes(params.annoB)) selB.value = params.annoB;
  if (params.mode==='bar'||params.mode==='pie') {{
    chartMode=params.mode;
    const p=document.getElementById('pill-chart-mode');
    if (p) p.classList.toggle('on',chartMode==='pie');
  }}
  if (params.genre!==undefined) {{ fieldToggles.genre=params.genre==='1'; const p=document.getElementById('pill-genre'); if (p) p.classList.toggle('on',fieldToggles.genre); }}
  if (params.tipologia!==undefined) {{ fieldToggles.tipologia=params.tipologia==='1'; const p=document.getElementById('pill-tipologia'); if (p) p.classList.toggle('on',fieldToggles.tipologia); }}
  if (params.modeToggle!==undefined) {{ fieldToggles.mode=params.modeToggle==='1'; const p=document.getElementById('pill-mode'); if (p) p.classList.toggle('on',fieldToggles.mode); }}
  if (params.metric) {{
    const keys=params.metric.split(',').filter(k=>['votanti','soci','mode'].includes(k));
    if (keys.length>0) {{ progMetrics=new Set(keys); document.querySelectorAll('[data-prog]').forEach(p=>{{ p.classList.toggle('on',progMetrics.has(p.dataset.prog)); }}); }}
  }}
  if (params.sel&&params.sel!=='none') restoreSelFromKey(params.sel);
  else sel={{type:'none'}};
  syncProgPills();
}}

// ── selection helpers ───────────────────────────────────────────────────────
function selDisplayLabel() {{ return sel.labelKey ? t(sel.labelKey) : (sel.label || ''); }}

// ── zone data for current selection ────────────────────────────────────────
function selZoneData(stem) {{
  const z = (RAW[stem]||{{}}).zones||{{}};
  const it = z.italia||{{}}, es = z.spagna||{{}};
  if (sel.type === 'none') {{
    const all = {{...it,...es}};
    return sumZones(all, Object.keys(all));
  }}
  if (sel.type === 'leaf') {{ return it[sel.name] || es[sel.name] || null; }}
  if (sel.type === 'group') {{
    if (sel.childType === 'area') {{
      const names = Object.keys(it).filter(n => sel.children.includes(PROVINCE_AREA[n]));
      return sumZones(it, names);
    }}
    return sumZones({{...it,...es}}, sel.children);
  }}
  return null;
}}

// ── selection handling ──────────────────────────────────────────────────────
function handleRowClick(type, key) {{
  if (type === 'clear') {{ sel = {{type:'none'}}; pushState(); render(); return; }}
  const selKey = type + ':' + key;
  if (sel.key === selKey) {{ sel = {{type:'none'}}; pushState(); render(); return; }}

  const kA = selA.value, kB = selB.value;
  const itA = ((RAW[kA]||{{}}).zones||{{}}).italia||{{}};
  const itB = ((RAW[kB]||{{}}).zones||{{}}).italia||{{}};
  const esA = ((RAW[kA]||{{}}).zones||{{}}).spagna||{{}};
  const esB = ((RAW[kB]||{{}}).zones||{{}}).spagna||{{}};
  const allIt = [...new Set([...Object.keys(itA), ...Object.keys(itB)])];
  const allEs = [...new Set([...Object.keys(esA), ...Object.keys(esB)])];

  if (type === 'it-total') {{
    const children = AREA_ORDER.filter(a => allIt.some(n => PROVINCE_AREA[n] === a));
    sel = {{type:'group', key:selKey, labelKey:'sel_italia', children, childType:'area'}};
  }} else if (type === 'area') {{
    const children = allIt.filter(n => PROVINCE_AREA[n] === key).sort();
    sel = {{type:'group', key:selKey, label:key, children, childType:'province'}};
  }} else if (type === 'es-total') {{
    sel = {{type:'group', key:selKey, labelKey:'sel_spagna', children:allEs.sort(), childType:'fiare'}};
  }} else {{
    sel = {{type:'leaf', key:selKey, name:key, label:key}};
  }}
  pushState();
  render();
}}

function clearSel() {{ sel = {{type:'none'}}; pushState(); render(); }}

// ── field toggles ───────────────────────────────────────────────────────────
function togglePill(key) {{
  fieldToggles[key] = !fieldToggles[key];
  document.getElementById('pill-'+key).classList.toggle('on', fieldToggles[key]);
  syncProgPills();
  pushState();
  render();
}}

// ── progression metric toggle ───────────────────────────────────────────────
function toggleProgMetric(key) {{
  if (progMetrics.has(key)) {{
    if (progMetrics.size > 1) progMetrics.delete(key);
  }} else {{
    progMetrics.add(key);
  }}
  document.querySelectorAll('[data-prog]').forEach(p => {{
    p.classList.toggle('on', progMetrics.has(p.dataset.prog));
  }});
  pushState();
  renderProgression();
}}

// ── sync prog metric pills with top filter state ────────────────────────────
function syncProgPills() {{
  const COND = {{
    soci: fieldToggles.genre || fieldToggles.tipologia,
    mode: fieldToggles.mode,
  }};
  let changed = false;
  for (const [metric, active] of Object.entries(COND)) {{
    const pill = document.querySelector(`[data-prog="${{metric}}"]`);
    if (!pill) continue;
    pill.style.display = active ? '' : 'none';
    if (!active && progMetrics.has(metric)) {{
      progMetrics.delete(metric);
      pill.classList.remove('on');
      changed = true;
    }}
  }}
  if (changed && progMetrics.size === 0) {{
    progMetrics.add('votanti');
    const vp = document.querySelector('[data-prog="votanti"]');
    if (vp) vp.classList.add('on');
  }}
}}

// ── province toggle ─────────────────────────────────────────────────────────
function toggleProvinces() {{
  provincesHidden = !provincesHidden;
  document.getElementById('provinceToggle').textContent = provincesHidden ? t('mostra_province') : t('nascondi_province');
  document.getElementById('zone-search').style.display = provincesHidden ? 'none' : '';
  const tbl = document.getElementById('zone-table-main');
  if (tbl) tbl.classList.toggle('hide-provinces', provincesHidden);
}}

// ── zone table ──────────────────────────────────────────────────────────────
function computeShow() {{
  const kA = selA.value, kB = selB.value;
  const zA = (RAW[kA]||{{}}).zones||{{}};
  const zB = (RAW[kB]||{{}}).zones||{{}};
  const allA = {{...(zA.italia||{{}}), ...(zA.spagna||{{}})}};
  const allB = {{...(zB.italia||{{}}), ...(zB.spagna||{{}})}};
  const showA = {{
    fisiche: (fieldToggles.genre||fieldToggles.tipologia) && (hasAnyField(allA,'donne')||hasAnyField(allA,'uomini')||hasAnyField(allA,'persone_fisiche')),
    giuridiche: fieldToggles.tipologia && hasAnyField(allA,'persone_giuridiche'),
  }};
  const showB = {{
    fisiche: (fieldToggles.genre||fieldToggles.tipologia) && (hasAnyField(allB,'donne')||hasAnyField(allB,'uomini')||hasAnyField(allB,'persone_fisiche')),
    giuridiche: fieldToggles.tipologia && hasAnyField(allB,'persone_giuridiche'),
  }};
  return {{showA, showB}};
}}
function colCount(show) {{
  return 1+(show.fisiche?(fieldToggles.genre?2:1):0)+(show.giuridiche?1:0);
}}

function zoneHeaders(lA, lB, showA, showB) {{
  const cA=colCount(showA), cB=colCount(showB);
  const need3=fieldToggles.genre&&((showA.fisiche&&showA.giuridiche)||(showB.fisiche&&showB.giuridiche));
  const zrs=need3?3:2;
  const row1=`<tr>
    <th rowspan="${{zrs}}" style="vertical-align:bottom">${{t('zona')}}</th>
    <th colspan="${{cA}}" style="text-align:center;border-bottom:1px solid #ddd">${{lA}}</th>
    <th colspan="${{cB}}" class="grp-sep" style="text-align:center;border-bottom:1px solid #ddd">${{lB}}</th>
    <th colspan="2" class="grp-sep" style="text-align:center;border-bottom:1px solid #ddd">${{t('differenza')}}</th>
  </tr>`;
  function r2(show,isB) {{
    const cls1=isB?'num grp-sep':'num';
    const v=need3?`<th class="${{cls1}}" rowspan="2">${{t('votanti')}}</th>`:`<th class="${{cls1}}">${{t('votanti')}}</th>`;
    if (!need3) {{
      if (show.fisiche&&show.giuridiche&&fieldToggles.genre) return v+`<th class="num">${{t('donne')}}</th><th class="num">${{t('uomini')}}</th><th class="num">${{t('persone_giuridiche')}}</th>`;
      if (show.fisiche&&show.giuridiche) return v+`<th class="num">${{t('persone_fisiche')}}</th><th class="num">${{t('persone_giuridiche')}}</th>`;
      if (show.fisiche&&fieldToggles.genre) return v+`<th class="num">${{t('donne')}}</th><th class="num">${{t('uomini')}}</th>`;
      if (show.fisiche) return v+`<th class="num">${{t('persone_fisiche')}}</th>`;
      if (show.giuridiche) return v+`<th class="num">${{t('persone_giuridiche')}}</th>`;
      return v;
    }}
    if (show.fisiche&&show.giuridiche) return v+`<th colspan="2" style="text-align:center;border-bottom:1px solid #eee">${{t('persone_fisiche')}}</th><th rowspan="2">${{t('persone_giuridiche')}}</th>`;
    if (show.fisiche) return v+`<th colspan="2" style="text-align:center">${{t('persone_fisiche')}}</th>`;
    if (show.giuridiche) return v+`<th rowspan="2">${{t('persone_giuridiche')}}</th>`;
    return v;
  }}
  const drs=need3?' rowspan="2"':'';
  const row2=`<tr>${{r2(showA,false)}}${{r2(showB,true)}}<th class="num grp-sep"${{drs}}>${{t('assoluta')}}</th><th class="num"${{drs}}>%</th></tr>`;
  let row3='';
  if (need3) {{
    function r3(show) {{
      return show.fisiche?`<th>${{t('donne')}}</th><th>${{t('uomini')}}</th>`:'';
    }}
    row3=`<tr>${{r3(showA)}}${{r3(showB)}}</tr>`;
  }}
  return row1+row2+row3;
}}

function yCols(z,show,isB,totRow) {{
  const s=isB?' grp-sep':'';
  const _pct=(val,tot)=>val!=null&&tot>0?Math.round(val/tot*100):null;
  const _bar=(val,tot)=>{{const p=_pct(val,tot);return p!=null?`<div style="margin-top:2px;height:4px;border-radius:2px;background:rgba(0,48,135,.35);width:${{p}}%;min-width:1px"></div>`:'';}};
  const _td=(cls,val,tot,lbl)=>{{const p=_pct(val,tot);const tip=p!=null?` title="${{p}}% ${{lbl}}"`:'' ;return `<td class="num${{cls}}"${{tip}}>${{fmt(val)}}${{_bar(val,tot)}}</td>`;}};
  const v=z.votanti??null;
  const vot=_td(`${{s}} col-tot`,v,totRow?.votanti,t('totale'));
  let fCells='';
  if (show.fisiche) {{
    if (fieldToggles.genre) {{
      const d=z.donne??null,u=uomini(z);
      fCells=_td('',d,totRow?.donne,t('donne'))+_td('',u,totRow?.uomini,t('uomini'));
    }} else {{
      const pf=z.persone_fisiche??null;
      fCells=_td('',pf,totRow?.persone_fisiche,t('persone_fisiche_abbr'));
    }}
  }}
  const pg=z.persone_giuridiche??null;
  const gCells=show.giuridiche?_td('',pg,totRow?.persone_giuridiche,t('persone_giuridiche_abbr')):'';
  return vot+fCells+gCells;
}}
function zoneRow(n, zA, zB, cls, showA, showB, clickArgs, totA, totB) {{
  const a=zA||{{}}, b=zB||{{}};
  const av=a.votanti??null, bv=b.votanti??null;
  const d=(av!=null&&bv!=null)?bv-av:null;
  const p=(av!=null&&bv!=null&&av)?(bv-av)/av*100:null;
  const isSelected=sel.key===clickArgs;
  const selCls=isSelected?' sel-row':'';
  const onClick=clickArgs?` onclick="handleRowClick('${{clickArgs.split(':')[0]}}','${{clickArgs.split(':').slice(1).join(':')}}')"` :'';
  const clickable=clickArgs?' clickable':'';
  const clearBadge=isSelected?`<span class="clear-badge" onclick="event.stopPropagation();clearSel()"><span>×</span></span>`:'';
  return `<tr class="${{cls}}${{selCls}}${{clickable}}"${{onClick}}><td>${{n}}${{clearBadge}}</td>${{yCols(a,showA,false,totA)}}${{yCols(b,showB,true,totB)}}<td class="num grp-sep ${{diffClass(d)}}">${{fmtDiff(d)}}</td><td class="num ${{diffClass(p)}}">${{fmtPct(p)}}</td></tr>`;
}}
function sectionDataRow(label, zA, zB, showA, showB, clickArgs, bgColor=C_DARK, totA, totB) {{
  const a=zA||{{}}, b=zB||{{}};
  const av=a.votanti??null, bv=b.votanti??null;
  const d=(av!=null&&bv!=null)?bv-av:null;
  const p=(av!=null&&bv!=null&&av)?(bv-av)/av*100:null;
  const isSelected=sel.key===clickArgs;
  const selCls=isSelected?' sel-row':'';
  const onClick=clickArgs?` onclick="handleRowClick('${{clickArgs.split(':')[0]}}','${{clickArgs.split(':').slice(1).join(':')}}')"` :'';
  const clearBadge=isSelected?`<span class="clear-badge" style="background:#adf;color:#003;border-radius:10px;padding:1px 6px;margin-left:6px;cursor:pointer;font-size:.7rem" onclick="event.stopPropagation();clearSel()"><span>×</span></span>`:'';
  const onDark=bgColor===C_DARK;
  const posCol=onDark?'#afd':'#060', negCol=onDark?'#faa':'#900', neuCol=onDark?'#aaa':'#888';
  const dCol=d==null?neuCol:d>0?posCol:negCol;
  const pCol=p==null?neuCol:p>0?posCol:negCol;
  const txtColor=onDark?'#fff':C_DARK;
  return `<tr style="background:${{bgColor}};color:${{txtColor}};font-weight:700;cursor:pointer;font-size:.78rem;text-transform:uppercase;letter-spacing:.06em"${{onClick}}${{selCls?` class="${{selCls}}"`:''}}><td style="padding:5px 8px">${{label}}${{clearBadge}}</td>${{yCols(a,showA,false,totA)}}${{yCols(b,showB,true,totB)}}<td class="num grp-sep" style="color:${{dCol}}">${{fmtDiff(d)}}</td><td class="num" style="color:${{pCol}}">${{fmtPct(p)}}</td></tr>`;
}}

function renderZones() {{
  const kA=selA.value, kB=selB.value;
  const lA=LABELS[kA], lB=LABELS[kB];
  const zA=(RAW[kA]||{{}}).zones||{{}}, zB=(RAW[kB]||{{}}).zones||{{}};
  const itA=zA.italia||null, itB=zB.italia||null;
  const esA=zA.spagna||null, esB=zB.spagna||null;
  const content=document.getElementById('zones-content');
  const geoA=(RAW[kA]||{{}}).geography||{{}}, geoB=(RAW[kB]||{{}}).geography||{{}};
  const hasGeoA=geoA.italia!=null||geoA.spagna!=null, hasGeoB=geoB.italia!=null||geoB.spagna!=null;
  if (!itA&&!itB&&!esA&&!esB&&!hasGeoA&&!hasGeoB) {{
    if (sel.type!=='none') {{ sel={{type:'none'}}; render(); }}
    content.innerHTML=`<p class="zone-unavail">${{t('nessun_dato')}}</p>`; return;
  }}
  const {{showA,showB}}=computeShow();
  const filter=provincesHidden?'':document.getElementById('zone-search').value.toLowerCase();
  const headers=zoneHeaders(lA,lB,showA,showB);
  let rows='';
  const allZonesA={{...(itA||{{}}),...(esA||{{}})}};
  const allZonesB={{...(itB||{{}}),...(esB||{{}})}};
  const geoTotA=(geoA.italia??null)!=null||(geoA.spagna??null)!=null ? (geoA.italia??0)+(geoA.spagna??0) : null;
  const geoTotB=(geoB.italia??null)!=null||(geoB.spagna??null)!=null ? (geoB.italia??0)+(geoB.spagna??0) : null;
  const totA=withGeoVot(sumZones(allZonesA,Object.keys(allZonesA)),geoTotA);
  const totB=withGeoVot(sumZones(allZonesB,Object.keys(allZonesB)),geoTotB);
  rows+=sectionDataRow(t('totale'),totA,totB,showA,showB,'clear:',C_DARK,totA,totB);

  if (itA||itB||geoA.italia!=null||geoB.italia!=null) {{
    const allIt=[...new Set([...Object.keys(itA||{{}}), ...Object.keys(itB||{{}})])];
    rows+=sectionDataRow(t('italia'),withGeoVot(sumZones({{...itA}},allIt.filter(n=>itA&&n in itA)),geoA.italia??null),withGeoVot(sumZones({{...itB}},allIt.filter(n=>itB&&n in itB)),geoB.italia??null),showA,showB,'it-total:',COLOR_B,totA,totB);
    for (const area of AREA_ORDER) {{
      const an=allIt.filter(n=>PROVINCE_AREA[n]===area); if (!an.length) continue;
      const fn=filter?an.filter(n=>n.toLowerCase().includes(filter)):an;
      if (filter&&!fn.length) continue;
      rows+=zoneRow(area,sumZones(itA||{{}},an.filter(n=>itA&&n in itA)),sumZones(itB||{{}},an.filter(n=>itB&&n in itB)),'area-row',showA,showB,`area:${{area}}`,totA,totB);
      for (const n of fn.sort()) rows+=zoneRow(n,(itA||{{}})[n]||null,(itB||{{}})[n]||null,'province-row',showA,showB,`province:${{n}}`,totA,totB);
    }}
  }}
  if (!filter&&(esA||esB||geoA.spagna!=null||geoB.spagna!=null)) {{
    const allEs=[...new Set([...Object.keys(esA||{{}}), ...Object.keys(esB||{{}})])].sort();
    rows+=sectionDataRow(t('spagna_fiare'),withGeoVot(sumZones(esA||{{}},Object.keys(esA||{{}})),geoA.spagna??null),withGeoVot(sumZones(esB||{{}},Object.keys(esB||{{}})),geoB.spagna??null),showA,showB,'es-total:',COLOR_B,totA,totB);
    for (const n of allEs) rows+=zoneRow(n,(esA||{{}})[n]||null,(esB||{{}})[n]||null,'area-row',showA,showB,`fiare:${{n}}`,totA,totB);
  }}
  const estA=(RAW[kA]||{{}}).geography?.estero??null;
  const estB=(RAW[kB]||{{}}).geography?.estero??null;
  if (estA!=null||estB!=null) {{
    rows+=sectionDataRow(t('estero'),{{votanti:estA}},{{votanti:estB}},showA,showB,null,COLOR_B,totA,totB);
  }}

  content.innerHTML=`<div style="overflow-x:auto"><table class="zone-table" id="zone-table-main"><thead>${{headers}}</thead><tbody>${{rows}}</tbody></table></div>`;
  if (provincesHidden) document.getElementById('zone-table-main').classList.add('hide-provinces');
}}

// ── charts ──────────────────────────────────────────────────────────────────
function renderCharts() {{
  const section=document.getElementById('charts-section');
  section.innerHTML='';
  if (sel.type==='none') renderTotal(section);
  else if (sel.type==='group') renderGroup(section);
  else renderLeaf(section);
}}

// --- Total mode ---
function renderTotal(section) {{
  const kA=selA.value, kB=selB.value;
  const lA=LABELS[kA], lB=LABELS[kB];
  const dA=RAW[kA]||{{}}, dB=RAW[kB]||{{}};
  const container=document.createElement('div');
  container.className='cats'; section.appendChild(container);

  CATS.forEach(([catId,catKey,fieldKeys]) => {{
    if (catId==='typology' && !fieldToggles.tipologia) return;
    if (catId==='genre'    && !fieldToggles.genre)     return;
    if (catId==='mode'     && !fieldToggles.mode)      return;
    const catLabel=t(catKey);
    const valsA=fieldKeys.map(k=>dA[catId]?.[k]??null);
    const valsB=fieldKeys.map(k=>dB[catId]?.[k]??null);
    if (valsA.every(v=>v==null)&&valsB.every(v=>v==null)) return;
    const fieldLabels=fieldKeys.map(k=>t(k));
    const card=document.createElement('div'); card.className='card';
    const totA=valsA.reduce((s,v)=>s+(v??0),0);
    const totB=valsB.reduce((s,v)=>s+(v??0),0);
    const rows=fieldKeys.map((k,i)=>{{
      const a=valsA[i],b=valsB[i];
      const diff=(a!=null&&b!=null)?b-a:null;
      const pct=(a!=null&&b!=null&&a!==0)?(b-a)/a*100:null;
      const ph=chartMode==='pie'?` data-chart-id="${{catId}}" data-pie-idx="${{i}}" onmouseenter="setPieHover('${{catId}}',${{i}})"`:'';
      const shA=a!=null&&totA>0?`<div style="font-size:.72em;color:#999;line-height:1">${{(a/totA*100).toFixed(1)}}%</div>`:'';
      const shB=b!=null&&totB>0?`<div style="font-size:.72em;color:#999;line-height:1">${{(b/totB*100).toFixed(1)}}%</div>`:'';
      return `<tr${{ph}}><td>${{pieSwatch(i)}}${{t(k)}}</td><td class="num">${{fmt(a)}}${{shA}}</td><td class="num grp-sep">${{fmt(b)}}${{shB}}</td><td class="num grp-sep ${{diffClass(diff)}}">${{fmtDiff(diff)}}</td><td class="num ${{diffClass(pct)}}">${{fmtPct(pct)}}</td></tr>`;
    }}).join('');
    const many=fieldKeys.length>=5;
    const tbl=`<table${{chartMode==='pie'?` onmouseleave="setPieHover('${{catId}}',-1)"`:''}}><thead><tr><th>${{catLabel}}</th><th class="num">${{lA}}</th><th class="num grp-sep">${{lB}}</th><th class="num grp-sep">${{t('diff_ass')}}</th><th class="num">${{t('diff_pct')}}</th></tr></thead><tbody>${{rows}}</tbody></table>`;
    const isGenre=catId==='genre';
    if (chartMode==='pie') {{
      card.innerHTML=`<h2>${{catLabel}}</h2>${{pieHtml(catId,lA,lB)}}<div style="margin-top:12px;overflow-x:auto">${{tbl}}</div>`;
      container.appendChild(card);
      makePieChart(catId+'-a', fieldLabels, valsA, catId, isGenre);
      makePieChart(catId+'-b', fieldLabels, valsB, catId, isGenre);
    }} else {{
      card.innerHTML=`<h2>${{catLabel}}</h2>${{many
        ?`<div class="chart-wrap"><canvas id="chart-${{catId}}"></canvas></div><div style="margin-top:12px;overflow-x:auto">${{tbl}}</div>`
        :`<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start"><div class="chart-wrap"><canvas id="chart-${{catId}}"></canvas></div>${{tbl}}</div>`
      }}`;
      container.appendChild(card);
      destroyChart(catId);
      const ctx=document.getElementById(`chart-${{catId}}`).getContext('2d');
      charts[catId]=new Chart(ctx,{{type:'bar',plugins:isGenre?[genderParityPlugin]:[],data:{{labels:fieldLabels,datasets:[
        {{label:lA,data:valsA,backgroundColor:COLOR_A,borderColor:BORDER_A,borderWidth:1}},
        {{label:lB,data:valsB,backgroundColor:COLOR_B,borderColor:BORDER_B,borderWidth:1}},
      ]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:true,position:'top'}}}},scales:{{y:{{beginAtZero:true}}}}}}}});
      if (isGenre) charts[catId]._genderParityLines=[
        {{value:totA>0?totA/2:null,color:rgba(C_DARK,.5)}},
        {{value:totB>0?totB/2:null,color:rgba(C_LIGHT,.9)}},
      ].filter(l=>l.value!=null);
    }}
  }});
}}

// --- Group mode: one card per field, x-axis = children ---
function renderGroup(section) {{
  const kA=selA.value, kB=selB.value;
  const lA=LABELS[kA], lB=LABELS[kB];
  const itA=((RAW[kA]||{{}}).zones||{{}}).italia||{{}};
  const itB=((RAW[kB]||{{}}).zones||{{}}).italia||{{}};
  const esA=((RAW[kA]||{{}}).zones||{{}}).spagna||{{}};
  const esB=((RAW[kB]||{{}}).zones||{{}}).spagna||{{}};

  function childData(stem, childName) {{
    const it=((RAW[stem]||{{}}).zones||{{}}).italia||{{}};
    const es=((RAW[stem]||{{}}).zones||{{}}).spagna||{{}};
    if (sel.childType==='area') {{
      const names=Object.keys(it).filter(n=>PROVINCE_AREA[n]===childName);
      return sumZones(it,names);
    }}
    return it[childName]||es[childName]||null;
  }}

  const children=sel.children;
  const container=document.createElement('div'); container.className='cats'; section.appendChild(container);

  function groupFieldCard(fieldKey, fieldLabel, getA, getB) {{
    const valsA=children.map(c=>getA(childData(kA,c)));
    const valsB=children.map(c=>getB(childData(kB,c)));
    if (valsA.every(v=>v==null)&&valsB.every(v=>v==null)) return;
    const card=document.createElement('div'); card.className='card';
    const chartId=`grp-${{fieldKey}}`;
    const totA=valsA.reduce((s,v)=>s+(v??0),0);
    const totB=valsB.reduce((s,v)=>s+(v??0),0);
    const rows=children.map((c,i)=>{{
      const a=valsA[i],b=valsB[i];
      const diff=(a!=null&&b!=null)?b-a:null;
      const pct=(a!=null&&b!=null&&a!==0)?(b-a)/a*100:null;
      const ph=chartMode==='pie'?` data-chart-id="${{chartId}}" data-pie-idx="${{i}}" onmouseenter="setPieHover('${{chartId}}',${{i}})"`:'';
      const shA=a!=null&&totA>0?`<div style="font-size:.72em;color:#999;line-height:1">${{(a/totA*100).toFixed(1)}}%</div>`:'';
      const shB=b!=null&&totB>0?`<div style="font-size:.72em;color:#999;line-height:1">${{(b/totB*100).toFixed(1)}}%</div>`:'';
      return `<tr${{ph}}><td>${{pieSwatch(i)}}${{c}}</td><td class="num">${{fmt(a)}}${{shA}}</td><td class="num grp-sep">${{fmt(b)}}${{shB}}</td><td class="num grp-sep ${{diffClass(diff)}}">${{fmtDiff(diff)}}</td><td class="num ${{diffClass(pct)}}">${{fmtPct(pct)}}</td></tr>`;
    }}).join('');
    const many=children.length>=5;
    const horiz=children.length>5;
    const chartH=horiz?Math.max(200,children.length*28):200;
    const tblGrp=`<table${{chartMode==='pie'?` onmouseleave="setPieHover('${{chartId}}',-1)"`:''}}><thead><tr><th>${{t('zona')}}</th><th class="num">${{lA}}</th><th class="num grp-sep">${{lB}}</th><th class="num grp-sep">${{t('diff_ass')}}</th><th class="num">${{t('diff_pct')}}</th></tr></thead><tbody>${{rows}}</tbody></table>`;
    if (chartMode==='pie') {{
      card.innerHTML=`<h2>${{selDisplayLabel()}} — ${{fieldLabel}}</h2>${{pieHtml(chartId,lA,lB)}}<div style="margin-top:12px;overflow-x:auto">${{tblGrp}}</div>`;
      container.appendChild(card);
      makePieChart(chartId+'-a', children, valsA, chartId);
      makePieChart(chartId+'-b', children, valsB, chartId);
    }} else {{
      card.innerHTML=`<h2>${{selDisplayLabel()}} — ${{fieldLabel}}</h2>
        <div style="display:grid;grid-template-columns:${{many?'1fr':'1fr 1fr'}};gap:20px;align-items:start">
          <div class="chart-wrap" style="height:${{chartH}}px"><canvas id="chart-${{chartId}}"></canvas></div>
          ${{!many?tblGrp:''}}
        </div>
        ${{many?`<div style="margin-top:12px;overflow-x:auto">${{tblGrp}}</div>`:''}}`;
      container.appendChild(card);
      destroyChart(chartId);
      const ctx=document.getElementById(`chart-${{chartId}}`).getContext('2d');
      charts[chartId]=new Chart(ctx,{{type:'bar',data:{{labels:children,datasets:[
        {{label:lA,data:valsA,backgroundColor:COLOR_A,borderColor:BORDER_A,borderWidth:1}},
        {{label:lB,data:valsB,backgroundColor:COLOR_B,borderColor:BORDER_B,borderWidth:1}},
      ]}},options:{{
        indexAxis:horiz?'y':'x',
        responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:true,position:'top'}}}},
        scales:{{[horiz?'x':'y']:{{beginAtZero:true}}}},
      }}}});
    }}
  }}

  function dualFieldCard(cardLabel, f1Label, f2Label, getF1, getF2, chartId) {{
    const f1A=children.map(c=>getF1(childData(kA,c)));
    const f1B=children.map(c=>getF1(childData(kB,c)));
    const f2A=children.map(c=>getF2(childData(kA,c)));
    const f2B=children.map(c=>getF2(childData(kB,c)));
    const hasF1A=!f1A.every(v=>v==null),hasF1B=!f1B.every(v=>v==null);
    const hasF2A=!f2A.every(v=>v==null),hasF2B=!f2B.every(v=>v==null);
    if (!hasF1A&&!hasF1B&&!hasF2A&&!hasF2B) return;
    const card=document.createElement('div'); card.className='card';
    const many=children.length>=5;
    const horiz=children.length>5;
    const chartH=horiz?Math.max(200,children.length*28):200;
    const datasets=[];
    if (hasF1A) datasets.push({{label:`${{f1Label}} ${{lA}}`,data:f1A,backgroundColor:rgba(C_DARK,.9),borderColor:C_DARK,borderWidth:1}});
    if (hasF2A) datasets.push({{label:`${{f2Label}} ${{lA}}`,data:f2A,backgroundColor:rgba(C_DARK,.42),borderColor:C_DARK,borderWidth:1}});
    if (hasF1B) datasets.push({{label:`${{f1Label}} ${{lB}}`,data:f1B,backgroundColor:rgba(C_LIGHT,.9),borderColor:rgba(C_LIGHT,.9),borderWidth:1}});
    if (hasF2B) datasets.push({{label:`${{f2Label}} ${{lB}}`,data:f2B,backgroundColor:rgba(C_LIGHT,.42),borderColor:rgba(C_LIGHT,.5),borderWidth:1}});
    const totF1A=f1A.reduce((s,v)=>s+(v??0),0),totF1B=f1B.reduce((s,v)=>s+(v??0),0);
    const totF2A=f2A.reduce((s,v)=>s+(v??0),0),totF2B=f2B.reduce((s,v)=>s+(v??0),0);
    const diffF1=hasF1A&&hasF1B,diffF2=hasF2A&&hasF2B;
    const colsF1=(hasF1A?1:0)+(hasF1B?1:0)+(diffF1?2:0);
    const colsF2=(hasF2A?1:0)+(hasF2B?1:0)+(diffF2?2:0);
    const h1A=hasF1A?`<th class="num">${{lA}}</th>`:'';
    const h1B=hasF1B?`<th class="num grp-sep">${{lB}}</th>`:'';
    const h1D=diffF1?`<th class="num grp-sep">${{t('diff')}}</th><th class="num">%</th>`:'';
    const h2A=hasF2A?`<th class="num grp-sep">${{lA}}</th>`:'';
    const h2B=hasF2B?`<th class="num grp-sep">${{lB}}</th>`:'';
    const h2D=diffF2?`<th class="num grp-sep">${{t('diff')}}</th><th class="num">%</th>`:'';
    const tHead=`<tr><th>${{t('zona')}}</th>
      ${{colsF1?`<th colspan="${{colsF1}}" style="color:var(--c-dark)">${{f1Label}}</th>`:''}}
      <th class="grp-sep" colspan="${{colsF2}}" style="color:var(--c-dark)">${{f2Label}}</th></tr>
      <tr><th></th>${{h1A}}${{h1B}}${{h1D}}${{h2A}}${{h2B}}${{h2D}}</tr>`;
    const rows=children.map((c,i)=>{{
      const f1a=f1A[i],f1b=f1B[i],f2a=f2A[i],f2b=f2B[i];
      const d1=diffF1?f1b-f1a:null,p1=(diffF1&&f1a)?(f1b-f1a)/f1a*100:null;
      const d2=diffF2?f2b-f2a:null,p2=(diffF2&&f2a)?(f2b-f2a)/f2a*100:null;
      const sh=(v,tot)=>v!=null&&tot>0?`<div style="font-size:.72em;color:#999;line-height:1">${{(v/tot*100).toFixed(1)}}%</div>`:'';
      const c1A=hasF1A?`<td class="num">${{fmt(f1a)}}${{sh(f1a,totF1A)}}</td>`:'';
      const c1B=hasF1B?`<td class="num grp-sep">${{fmt(f1b)}}${{sh(f1b,totF1B)}}</td>`:'';
      const c1D=diffF1?`<td class="num grp-sep ${{diffClass(d1)}}">${{fmtDiff(d1)}}</td><td class="num ${{diffClass(p1)}}">${{fmtPct(p1)}}</td>`:'';
      const c2A=hasF2A?`<td class="num grp-sep">${{fmt(f2a)}}${{sh(f2a,totF2A)}}</td>`:'';
      const c2B=hasF2B?`<td class="num grp-sep">${{fmt(f2b)}}${{sh(f2b,totF2B)}}</td>`:'';
      const c2D=diffF2?`<td class="num grp-sep ${{diffClass(d2)}}">${{fmtDiff(d2)}}</td><td class="num ${{diffClass(p2)}}">${{fmtPct(p2)}}</td>`:'';
      const ph=chartMode==='pie'?` data-chart-id="${{chartId}}" data-pie-idx="${{i}}" onmouseenter="setPieHover('${{chartId}}',${{i}})"`:'';
      return `<tr${{ph}}><td>${{pieSwatch(i)}}${{c}}</td>${{c1A}}${{c1B}}${{c1D}}${{c2A}}${{c2B}}${{c2D}}</tr>`;
    }}).join('');
    const tblDual=`<div style="margin-top:12px;overflow-x:auto"><table${{chartMode==='pie'?` onmouseleave="setPieHover('${{chartId}}',-1)"`:''}}><thead>${{tHead}}</thead><tbody>${{rows}}</tbody></table></div>`;
    if (chartMode==='pie') {{
      const pieSumsA=children.map((_,i)=>((f1A[i]??0)+(f2A[i]??0))||null);
      const pieSumsB=children.map((_,i)=>((f1B[i]??0)+(f2B[i]??0))||null);
      card.innerHTML=`<h2>${{selDisplayLabel()}} — ${{cardLabel}}</h2>${{pieHtml(chartId,lA,lB)}}${{tblDual}}`;
      container.appendChild(card);
      makePieChart(chartId+'-a', children, pieSumsA, chartId);
      makePieChart(chartId+'-b', children, pieSumsB, chartId);
    }} else {{
      card.innerHTML=`<h2>${{selDisplayLabel()}} — ${{cardLabel}}</h2>
        <div class="chart-wrap" style="height:${{chartH}}px"><canvas id="chart-${{chartId}}"></canvas></div>
        ${{tblDual}}`;
      container.appendChild(card);
      destroyChart(chartId);
      const ctx=document.getElementById(`chart-${{chartId}}`).getContext('2d');
      charts[chartId]=new Chart(ctx,{{type:'bar',data:{{labels:children,datasets}},options:{{
        indexAxis:horiz?'y':'x',responsive:true,maintainAspectRatio:false,
        plugins:{{legend:{{display:true,position:'top'}}}},
        scales:{{[horiz?'x':'y']:{{beginAtZero:true}}}},
      }}}});
    }}
  }}

  groupFieldCard('votanti',t('votanti'),z=>z?z.votanti??null:null,z=>z?z.votanti??null:null);

  if (fieldToggles.mode) {{
    dualFieldCard(t('cat_modalita'),t('in_presenza'),t('a_distanza'),
      z=>z?z.in_presenza??null:null, z=>z?z.a_distanza??null:null, 'grp-mode');
  }}
  if (fieldToggles.tipologia) {{
    dualFieldCard(t('cat_tipologia_soci'),t('persone_fisiche_abbr'),t('persone_giuridiche_abbr'),
      z=>z?z.persone_fisiche??null:null, z=>z?z.persone_giuridiche??null:null, 'grp-tipo');
  }}
  if (fieldToggles.genre) {{
    dualFieldCard(t('cat_genere'),t('donne'),t('uomini'),
      z=>z?z.donne??null:null, z=>uomini(z), 'grp-genre');
  }}
}}

// --- Leaf mode: adapted category cards from zone data ---
function renderLeaf(section) {{
  const kA=selA.value, kB=selB.value;
  const lA=LABELS[kA], lB=LABELS[kB];
  const getZ=stem=>{{
    const it=((RAW[stem]||{{}}).zones||{{}}).italia||{{}};
    const es=((RAW[stem]||{{}}).zones||{{}}).spagna||{{}};
    return it[sel.name]||es[sel.name]||null;
  }};
  const zA=getZ(kA)||{{}}, zB=getZ(kB)||{{}};
  const container=document.createElement('div'); container.className='cats'; section.appendChild(container);

  const LEAF_CATS=[
    {{labelKey:'cat_modalita',toggle:'mode',fields:[
      {{key:'in_presenza',labelKey:'in_presenza'}},{{key:'a_distanza',labelKey:'a_distanza'}},
    ]}},
    {{labelKey:'cat_tipologia_soci',toggle:'tipologia',fields:[
      {{key:'persone_fisiche',labelKey:'persone_fisiche_abbr'}},{{key:'persone_giuridiche',labelKey:'persone_giuridiche_abbr'}},
    ]}},
    {{labelKey:'cat_genere',toggle:'genre',fields:[
      {{key:'donne',labelKey:'donne'}},{{key:'uomini',labelKey:'uomini',computed:true}},
    ]}},
  ];

  LEAF_CATS.forEach(cat=>{{
    if (cat.toggle && !fieldToggles[cat.toggle]) return;
    const catLabel=t(cat.labelKey);
    const valsA=cat.fields.map(f=>f.computed?uomini(zA):(zA[f.key]??null));
    const valsB=cat.fields.map(f=>f.computed?uomini(zB):(zB[f.key]??null));
    const totLA=valsA.reduce((s,v)=>s+(v??0),0);
    const totLB=valsB.reduce((s,v)=>s+(v??0),0);
    if (valsA.every(v=>v==null)&&valsB.every(v=>v==null)) return;
    const labels=cat.fields.map(f=>t(f.labelKey));
    const card=document.createElement('div'); card.className='card';
    const chartId=`leaf-${{cat.labelKey}}`;
    const isGenreL=cat.labelKey==='cat_genere';
    const rows=cat.fields.map((f,i)=>{{
      const a=valsA[i],b=valsB[i];
      const diff=(a!=null&&b!=null)?b-a:null;
      const pct=(a!=null&&b!=null&&a!==0)?(b-a)/a*100:null;
      const ph=chartMode==='pie'?` data-chart-id="${{chartId}}" data-pie-idx="${{i}}" onmouseenter="setPieHover('${{chartId}}',${{i}})"`:'';
      const shA=a!=null&&totLA>0?`<div style="font-size:.72em;color:#999;line-height:1">${{(a/totLA*100).toFixed(1)}}%</div>`:'';
      const shB=b!=null&&totLB>0?`<div style="font-size:.72em;color:#999;line-height:1">${{(b/totLB*100).toFixed(1)}}%</div>`:'';
      return `<tr${{ph}}><td>${{pieSwatch(i)}}${{t(f.labelKey)}}</td><td class="num">${{fmt(a)}}${{shA}}</td><td class="num grp-sep">${{fmt(b)}}${{shB}}</td><td class="num grp-sep ${{diffClass(diff)}}">${{fmtDiff(diff)}}</td><td class="num ${{diffClass(pct)}}">${{fmtPct(pct)}}</td></tr>`;
    }}).join('');
    const tblLeaf=`<table${{chartMode==='pie'?` onmouseleave="setPieHover('${{chartId}}',-1)"`:''}}><thead><tr><th>${{catLabel}}</th><th class="num">${{lA}}</th><th class="num grp-sep">${{lB}}</th><th class="num grp-sep">${{t('diff_ass')}}</th><th class="num">${{t('diff_pct')}}</th></tr></thead><tbody>${{rows}}</tbody></table>`;
    if (chartMode==='pie') {{
      card.innerHTML=`<h2>${{selDisplayLabel()}} — ${{catLabel}}</h2>${{pieHtml(chartId,lA,lB)}}<div style="margin-top:12px;overflow-x:auto">${{tblLeaf}}</div>`;
      container.appendChild(card);
      makePieChart(chartId+'-a', labels, valsA, chartId, isGenreL);
      makePieChart(chartId+'-b', labels, valsB, chartId, isGenreL);
    }} else {{
      card.innerHTML=`<h2>${{selDisplayLabel()}} — ${{catLabel}}</h2><div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start">
        <div class="chart-wrap"><canvas id="chart-${{chartId}}"></canvas></div>
        ${{tblLeaf}}
      </div>`;
      container.appendChild(card);
      destroyChart(chartId);
      const ctx=document.getElementById(`chart-${{chartId}}`).getContext('2d');
      charts[chartId]=new Chart(ctx,{{type:'bar',plugins:isGenreL?[genderParityPlugin]:[],data:{{labels,datasets:[
        {{label:lA,data:valsA,backgroundColor:COLOR_A,borderColor:BORDER_A,borderWidth:1}},
        {{label:lB,data:valsB,backgroundColor:COLOR_B,borderColor:BORDER_B,borderWidth:1}},
      ]}},options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:true,position:'top'}}}},scales:{{y:{{beginAtZero:true}}}}}}}});
      if (isGenreL) charts[chartId]._genderParityLines=[
        {{value:totLA>0?totLA/2:null,color:rgba(C_DARK,.5)}},
        {{value:totLB>0?totLB/2:null,color:rgba(C_LIGHT,.9)}},
      ].filter(l=>l.value!=null);
    }}
  }});
}}

// ── progression chart ────────────────────────────────────────────────────────
const progVerticalLinesPlugin={{id:'progVerticalLines',afterDraw(chart){{const iA=KEYS.indexOf(selA.value),iB=KEYS.indexOf(selB.value);if(iA<0&&iB<0)return;const c=chart.ctx,xS=chart.scales.x,yS=chart.scales.y;if(!xS||!yS)return;const top=yS.top,bot=yS.bottom;c.save();c.setLineDash([6,4]);c.lineWidth=2;if(iA>=0){{const px=xS.getPixelForValue(iA);c.strokeStyle=C_DARK;c.beginPath();c.moveTo(px,top);c.lineTo(px,bot);c.stroke();}}if(iB>=0){{const px=xS.getPixelForValue(iB);c.strokeStyle=C_LIGHT;c.beginPath();c.moveTo(px,top);c.lineTo(px,bot);c.stroke();}}c.restore();}}}};
const genderParityPlugin={{id:'genderParity',afterDraw(chart){{const lines=chart._genderParityLines;if(!lines||!lines.length)return;const {{ctx,chartArea}}=chart;const y=chart.scales?.y;if(!y||!chartArea)return;ctx.save();ctx.setLineDash([5,4]);ctx.lineWidth=1.5;lines.forEach(({{value,color}})=>{{if(value==null)return;const py=y.getPixelForValue(value);if(py<chartArea.top||py>chartArea.bottom)return;ctx.strokeStyle=color;ctx.beginPath();ctx.moveTo(chartArea.left,py);ctx.lineTo(chartArea.right,py);ctx.stroke();}});ctx.restore();}}}};
const genderParityPiePlugin={{id:'genderParityPie',afterDraw(chart){{if(!chart._genderParityPie)return;const meta=chart.getDatasetMeta(0);if(!meta||!meta.data||!meta.data[0])return;const {{ctx,chartArea}}=chart;const cx=(chartArea.left+chartArea.right)/2;const cy=meta.data[0].y;const r=meta.data[0].outerRadius;if(!r)return;ctx.save();ctx.strokeStyle='rgba(0,0,0,.3)';ctx.lineWidth=1.5;ctx.setLineDash([4,3]);ctx.beginPath();ctx.moveTo(cx,cy-r);ctx.lineTo(cx,cy+r);ctx.stroke();ctx.restore();}}}};
function hideProgPopover(){{const p=document.getElementById('prog-popover');if(p)p.style.display='none';}}
function showProgPopover(nativeEvt,idx){{const p=document.getElementById('prog-popover');if(!p)return;const wrap=document.querySelector('.prog-wrap');if(!wrap)return;const wr=wrap.getBoundingClientRect();const x=nativeEvt.clientX-wr.left+8,y=nativeEvt.clientY-wr.top+8;p.innerHTML=`<button class="pill" onclick="popoverSetA(${{idx}})">${{t('imposta_anno_a')}}</button><button class="pill" onclick="popoverSetB(${{idx}})">${{t('imposta_anno_b')}}</button>`;p.style.cssText=`display:flex;left:${{x}}px;top:${{y}}px;position:absolute;background:#fff;border:1px solid #ddd;border-radius:8px;box-shadow:0 2px 12px rgba(0,0,0,.15);padding:8px;z-index:200;gap:6px;flex-direction:column`;}}
function popoverSetA(idx){{hideProgPopover();selA.value=KEYS[idx];updateSelOptions();pushState();render();}}
function popoverSetB(idx){{hideProgPopover();selB.value=KEYS[idx];updateSelOptions();pushState();render();}}
document.addEventListener('click',e=>{{const p=document.getElementById('prog-popover');if(p&&p.style.display!=='none'&&!p.contains(e.target))hideProgPopover();}});
let progChart = null;
function progVal(stem, metric) {{
  const z=selZoneData(stem);
  if (z&&z[metric]!=null) return z[metric];
  if (sel.type!=='none') return null;
  const d=RAW[stem]||{{}};
  if (metric==='votanti') {{
    const p=d.participants||{{}};
    const n=p.votanti_normali,r=p.rappresentanze,g=p.deleghe;
    if (n==null&&r==null&&g==null) return null;
    return (n??0)+(r??0)+(g??0);
  }}
  if (metric==='in_presenza') return (d.mode||{{}}).in_presenza??null;
  if (metric==='a_distanza') return (d.mode||{{}}).a_distanza??null;
  return null;
}}
function progSoci(stem) {{
  const z=selZoneData(stem);
  if (z&&z.donne!=null) return {{donne:z.donne,uo:z.uomini??null,pf:z.persone_fisiche??null,pg:z.persone_giuridiche??null}};
  if (sel.type!=='none') return null;
  const d=RAW[stem]||{{}};
  const g=d.genre||{{}};
  const tp=d.typology||{{}};
  if (g.donne!=null) return {{donne:g.donne,uo:g.uomini??null,pf:tp.persone_fisiche??null,pg:tp.persone_giuridiche??null}};
  return null;
}}
const C_GREEN='rgb(30,160,60)';
const C_ORANGE='rgb(200,100,0)';
const C_AMBER='rgb(210,160,0)';
function renderProgression() {{
  const yearLabels=KEYS.map(k=>LABELS[k]);
  if (progChart) {{ progChart.destroy(); progChart=null; }}
  const _pc=document.getElementById('prog-chart');const _ex=Chart.getChart(_pc);if(_ex)_ex.destroy();
  const ctx=_pc.getContext('2d');
  let datasets=[];
  function splitDs(label,data,color) {{
    const n=data.length;
    const nn=[];
    for(let i=0;i<n;i++) if(data[i]!=null) nn.push(i);
    const base={{label,data:[...data],borderColor:color,backgroundColor:rgba(color,.1),tension:0.3,spanGaps:false,pointRadius:5,pointHoverRadius:7}};
    const res=[base];
    for(let i=0;i<nn.length-1;i++) {{
      const f=nn[i],tt=nn[i+1];
      if(tt-f>1) {{
        const bd=new Array(n).fill(null);
        bd[f]=data[f]; bd[tt]=data[tt];
        res.push({{label:'_gap',data:bd,borderColor:color,borderDash:[6,4],borderWidth:1.5,backgroundColor:'transparent',tension:0,spanGaps:true,pointRadius:0,pointHoverRadius:0}});
      }}
    }}
    return res;
  }}
  const multi=progMetrics.size>1;
  if (progMetrics.has('votanti')) {{
    datasets.push(...splitDs(t('votanti'),KEYS.map(stem=>progVal(stem,'votanti')),C_DARK));
  }}
  if (progMetrics.has('soci')) {{
    const sd=KEYS.map(stem=>progSoci(stem));
    const cD=multi?C_ORANGE:C_DARK, cU=multi?C_AMBER:C_LIGHT;
    if (fieldToggles.genre) {{
      datasets.push(...splitDs(t('donne'),sd.map(s=>s?s.donne??null:null),cD));
      datasets.push(...splitDs(t('uomini'),sd.map(s=>s?s.uo??null:null),cU));
    }} else if (fieldToggles.tipologia) {{
      datasets.push(...splitDs(t('persone_fisiche'),sd.map(s=>s?s.pf??null:null),cD));
    }}
    if (fieldToggles.tipologia) {{
      datasets.push(...splitDs(t('persone_giuridiche'),sd.map(s=>s?s.pg??null:null),C_GREEN));
    }}
  }}
  if (progMetrics.has('mode')) {{
    const cP=multi?C_MID:C_DARK, cD2=multi?'rgb(0,150,220)':C_LIGHT;
    datasets.push(...splitDs(t('in_presenza'),KEYS.map(stem=>progVal(stem,'in_presenza')),cP));
    datasets.push(...splitDs(t('a_distanza'),KEYS.map(stem=>progVal(stem,'a_distanza')),cD2));
  }}
  progChart=new Chart(ctx,{{
    type:'line',
    plugins:[progVerticalLinesPlugin],
    data:{{labels:yearLabels,datasets}},
    options:{{responsive:true,maintainAspectRatio:false,
      interaction:{{mode:'index',intersect:false}},
      onClick:(event,activeElements)=>{{
        if(!progChart)return;
        hideProgPopover();
        const xScale=progChart.scales.x;
        const idx=Math.round(xScale.getValueForPixel(event.x));
        if(idx<0||idx>=KEYS.length)return;
        const iA=KEYS.indexOf(selA.value),iB=KEYS.indexOf(selB.value);
        if(idx===iA||idx===iB)return;
        if(idx<iA){{selA.value=KEYS[idx];updateSelOptions();pushState();render();return;}}
        if(idx>iB){{selB.value=KEYS[idx];updateSelOptions();pushState();render();return;}}
        showProgPopover(event.native,idx);
      }},
      plugins:{{legend:{{display:true,position:'top',labels:{{filter:item=>!item.text.startsWith('_')}}}},tooltip:{{mode:'index',intersect:false,filter:item=>!item.dataset.label.startsWith('_'),callbacks:{{label:ctx=>`${{ctx.dataset.label}}: ${{fmt(ctx.raw)}}`}}}}}},
      scales:{{y:{{beginAtZero:false}}}},
    }},
  }});
}}

// ── main render ──────────────────────────────────────────────────────────────
function render() {{
  const lbl=document.getElementById('sel-label');
  lbl.style.display=sel.type==='none'?'none':'';
  lbl.innerHTML=sel.type==='none'?'':`${{selDisplayLabel()}} <span class="clear-badge" onclick="clearSel()"><span>×</span></span>`;
  renderZones();
  renderCharts();
  renderProgression();
}}

(function boot() {{
  rebuildLabels();
  const params = parseHash();
  if (params) applyState(params);
  syncProgPills();
  applyLang();
  render();
  if (!window.location.hash) pushState();
}})();
window.addEventListener('hashchange', () => {{
  const params = parseHash();
  if (params) {{ applyState(params); applyLang(); render(); }}
}});
</script>
</body>
</html>"""
    OUT.write_text(html)
    print(f"Written {OUT} ({OUT.stat().st_size // 1024}KB)")


if __name__ == "__main__":
    build()
