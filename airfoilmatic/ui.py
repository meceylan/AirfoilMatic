"""Look of the Streamlit app: emerald palette, CSS, small HTML blocks.

Kept apart from app.py so the page code stays about the workflow. Nothing here
calls Streamlit; app.py injects the returned strings with st.markdown.

Light and dark mode: switching the theme in the ⋮ menu does not rerun the
script, so the CSS cannot be picked in Python. Every theme-dependent colour is
a CSS variable defined with light-dark(), which the browser resolves from the
color-scheme Streamlit sets on .stApp. One stylesheet therefore serves both
themes and follows a theme switch immediately.
"""
from html import escape

DEVELOPER = {
    "name": "Muhammet Emin CEYLAN",
    "university": {"tr": "İskenderun Teknik Üniversitesi", "en": "Iskenderun Technical University"},
    "linkedin": "https://www.linkedin.com/in/muhammet-emin-ceylan-b79847334",
    "github": "https://github.com/meceylan",
    "repo": "https://github.com/meceylan/AirfoilMatic",
}

FONT = "AirfoilMatic Serif"   # self-hosted family declared in .streamlit/config.toml

# Emerald shades taken from the reference design: deep, main, light.
EMERALD_DEEP, EMERALD, EMERALD_LIGHT = "#13452C", "#1C6142", "#5EBD91"
CRYSTAL = "linear-gradient(135deg,#0E3B25 0%,#17573A 45%,#258A5A 100%)"

# Plot colours. Plotly figures are drawn once per script run, so they cannot
# follow a theme switch either; these mid tones read well on light and dark.
# line: airfoil, fill: LE -> TE gradient, split: split lines, boundary: domain,
# grid/zero: axes, fit/ext: GCI Richardson curve and extrapolated value.
PLOT = dict(line="#2E8B60", fill=("rgba(28,97,66,0.60)", "rgba(94,189,145,0.18)"), split="#D49A45",
            boundary="#8FA198", grid="rgba(94,160,125,0.16)", zero="rgba(94,160,125,0.35)",
            fit="#D49A45", ext="#D2694F")

MOBILE_MAX = 640   # px; below this, wide tables are shown as cards

_CSS = """
.stApp{
  --am-top:light-dark(#BCDFCB,#0F2C1F); --am-mid:light-dark(#D3EBDE,#0B1D15); --am-bot:light-dark(#EDF4F3,#070F0B);
  --am-sbt:light-dark(#AFD6C0,#0D2218); --am-sbb:light-dark(#D6EADF,#08120D);
  --am-base:light-dark(#FFFFFF,#09140F); --am-text:light-dark(#111A15,#E6EFEA);
  --am-tint:light-dark(rgba(214,236,224,.95),rgba(37,138,90,.16));
  --am-e1:light-dark(#1C6142,#5EBD91); --am-e2:light-dark(#8FD3B1,#174A31);
  --am-ib:light-dark(rgba(35,128,84,.34),rgba(94,189,145,.30));
  --am-ibg1:light-dark(#FFFFFF,#10211A); --am-ibg2:light-dark(#EEF7F2,#0B1711);
  --am-acc:light-dark(#1C6142,#3FBF85); --am-line:light-dark(rgba(28,97,66,.28),rgba(94,189,145,.28));
  --am-sh:light-dark(rgba(19,69,44,.35),rgba(0,0,0,.55));
  --am-note1:light-dark(#DCEFE5,rgba(37,138,90,.22)); --am-note2:light-dark(#F2F9F5,rgba(15,27,21,.6));
  --am-note-text:light-dark(#174A31,#CDEBDD); --am-head:light-dark(rgba(196,226,209,.72),rgba(12,30,22,.72));
  background:linear-gradient(180deg,var(--am-top) 0px,var(--am-mid) 520px,var(--am-bot) 1400px) !important;
}
[data-testid="stMainBlockContainer"]{container-type:inline-size;}   /* lets plot cards size from the column width */
[data-testid="stHeader"]{background:var(--am-head) !important;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);}
[data-testid="stSidebar"]{background:linear-gradient(180deg,var(--am-sbt),var(--am-sbb)) !important;}

/* inputs: thin emerald frame, soft inner gradient, glow on focus */
[data-testid="stNumberInputContainer"],[data-testid="stTextInputRootElement"],
[data-testid="stSelectbox"] div[role="group"]{border:1px solid var(--am-ib) !important;
  background:linear-gradient(180deg,var(--am-ibg1),var(--am-ibg2)) !important;
  border-radius:.7rem !important;box-shadow:0 2px 8px -4px var(--am-sh);}
[data-testid="stNumberInputContainer"]:focus-within,[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stSelectbox"] div[role="group"]:focus-within{border-color:var(--am-e1) !important;
  box-shadow:0 0 0 3px rgba(63,191,133,.20) !important;}
[data-testid="stNumberInputContainer"] input,[data-testid="stTextInputRootElement"] input,
[data-testid="stSelectbox"] input,[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"]{background:transparent !important;}

/* large cards and plots: gradient emerald frame (containers with key card_* / plot_*) */
[class*="st-key-card_"],[class*="st-key-plot_"]{border:1px solid transparent !important;border-radius:1rem !important;
  padding:1rem 1.1rem !important;box-shadow:0 14px 34px -22px var(--am-sh);
  background:linear-gradient(160deg,var(--am-tint),transparent 70%) padding-box,
    linear-gradient(var(--am-base),var(--am-base)) padding-box,
    linear-gradient(135deg,var(--am-e1),var(--am-e2)) border-box !important;}

/* tables and metrics: emerald accent on the left */
[data-testid="stDataFrame"]{border-left:4px solid var(--am-acc);border-radius:.8rem;overflow:hidden;
  box-shadow:0 10px 26px -20px var(--am-sh);}
[data-testid="stMetric"]{border:1px solid rgba(128,128,128,.22);border-left:4px solid var(--am-acc);border-radius:.8rem;
  padding:.8rem 1rem;background:var(--am-base);}
[data-testid="stExpander"] details{border-color:var(--am-ib) !important;border-radius:.8rem !important;
  background:var(--am-base);}

/* HTML tables (key/value tables): row lines fade from emerald on the left to nothing on the right */
.am-table-wrap{border-left:4px solid var(--am-acc);border-radius:.8rem;overflow:hidden;background:var(--am-base);
  box-shadow:0 10px 26px -20px var(--am-sh);margin:.3rem 0 1rem;}
.am-table{width:100%;border-collapse:separate !important;border-spacing:0;font-size:.92rem;border:none !important;margin:0 !important;}
.am-table th{text-align:left;font-weight:500;opacity:.65;padding:.55rem .8rem;background:var(--am-tint);}
.am-table td{padding:.5rem .8rem;vertical-align:top;overflow-wrap:anywhere;}
.am-table td,.am-table th{border:none !important;}
.am-table tr{background:linear-gradient(90deg,var(--am-line),transparent 85%) left bottom / 100% 1px no-repeat;}
.am-table tbody tr:last-child{background:none;}
.am-table td:first-child{width:45%;}

/* wide tables: dataframe on desktop, one card per row on phones */
.am-rows{display:none;}
.am-row{border:1px solid rgba(128,128,128,.22);border-left:4px solid var(--am-acc);border-radius:.8rem;
  background:var(--am-base);padding:.6rem .8rem;margin:.5rem 0;font-size:.9rem;}
.am-row .h{font-weight:600;margin-bottom:.25rem;}
.am-row .kv{display:flex;justify-content:space-between;gap:.8rem;padding:.15rem 0;border-bottom:1px solid;
  border-image:linear-gradient(90deg,var(--am-line),transparent 85%) 1;}
.am-row .kv:last-child{border-bottom:none;}
.am-row .kv span:first-child{opacity:.65;}
.am-row .kv span:last-child{text-align:right;overflow-wrap:anywhere;}
@media (max-width:MOBILEpx){
  .am-rows{display:block;}
  [class*="st-key-wide_"]{display:none !important;}
}

/* touch screens: a finger on a plot scrolls the page instead of zooming or panning the plot */
@media (pointer:coarse){
  .js-plotly-plot .draglayer,.js-plotly-plot .nsewdrag,.js-plotly-plot [class*="drag"]{pointer-events:none !important;}
  .js-plotly-plot,.js-plotly-plot .plotly,.js-plotly-plot .main-svg{touch-action:pan-y !important;}
  .js-plotly-plot .modebar{display:none !important;}
}

/* crystal: deep-to-light emerald with a glassy highlight */
.am-crystal{position:relative;overflow:hidden;border:1px solid rgba(255,255,255,.14) !important;
  background:CRYSTAL !important;box-shadow:0 10px 28px -8px rgba(19,69,44,.45);}
.am-crystal::before{content:'';position:absolute;inset:0;pointer-events:none;
  background:radial-gradient(120% 80% at 90% -10%,rgba(255,255,255,.28),transparent 55%),
  repeating-linear-gradient(135deg,rgba(255,255,255,.05) 0 2px,transparent 2px 9px);}
.am-crystal,.am-crystal *{color:#fff !important;}
[data-testid="stBaseButton-primary"]{background:CRYSTAL !important;border:none !important;border-radius:999px !important;
  box-shadow:0 6px 16px -6px rgba(19,69,44,.6);}
[data-testid="stBaseButton-primary"] p{color:#fff !important;}
[data-testid="stBaseButton-secondary"]{border-radius:999px !important;}

/* small blocks used by app.py */
.am-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:.75rem;margin:.6rem 0 1.4rem;}
.am-card{border:1px solid rgba(128,128,128,.22);border-left:4px solid var(--am-acc);background:var(--am-base);
  border-radius:.8rem;padding:.8rem 1rem;}
.am-card.am-crystal{border-left:1px solid rgba(255,255,255,.14) !important;}
.am-card .l{font-size:.78rem;opacity:.65;}
.am-card .v{font-size:1.35rem;font-weight:600;line-height:1.35;}
.am-card .s{font-size:.75rem;opacity:.55;}
.am-step{font-size:.8rem;letter-spacing:.04em;text-transform:uppercase;opacity:.6;margin-bottom:.3rem;}
.am-note{background:linear-gradient(160deg,var(--am-note1),var(--am-note2));border:1px solid var(--am-ib);
  border-left:4px solid var(--am-acc);border-radius:.8rem;padding:.75rem .9rem;font-size:.86rem;line-height:1.45;
  color:var(--am-note-text);margin:.4rem 0;}
.am-note b{display:block;margin-bottom:.2rem;}
.am-foot{margin-top:.6rem;padding-top:.8rem;border-top:1px solid rgba(128,128,128,.2);font-size:.85rem;}
.am-foot .who{font-weight:600;}
.am-foot .uni{font-size:.78rem;opacity:.6;margin-bottom:.45rem;}
.am-foot a{display:inline-flex;align-items:center;gap:.35rem;margin-right:.9rem;color:inherit !important;
  text-decoration:none;opacity:.8;}
.am-foot a:hover{opacity:1;color:var(--am-e1) !important;}
.am-head{display:flex;align-items:baseline;gap:.75rem;flex-wrap:wrap;margin-top:-1.5rem;}
.am-head .t{font-family:"FONT",serif;font-size:2.4rem;font-weight:600;letter-spacing:-.01em;}
.am-head .p{font-size:.72rem;padding:.12rem .55rem;border-radius:999px;}
.am-sub{opacity:.55;margin:-.2rem 0 1.2rem 0;font-size:.95rem;}
"""

_LINKEDIN_SVG = ("<svg width='15' height='15' viewBox='0 0 24 24' fill='currentColor' aria-hidden='true'><path d='M20.45 "
                 "20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.85 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 "
                 "1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 "
                 "4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 "
                 "0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z'/></svg>")
_GITHUB_SVG = ("<svg width='15' height='15' viewBox='0 0 24 24' fill='currentColor' aria-hidden='true'><path d='M12 .3a12 12 0 "
               "0 0-3.8 23.4c.6.1.8-.3.8-.6v-2c-3.3.7-4-1.6-4-1.6-.6-1.4-1.4-1.8-1.4-1.8-1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 "
               "1.8 2.8 1.3 3.5 1 0-.8.4-1.3.7-1.6-2.7-.3-5.5-1.3-5.5-5.9 0-1.3.5-2.4 1.2-3.2 0-.3-.5-1.5.2-3.2 0 0 1-.3 3.3 "
               "1.2a11.5 11.5 0 0 1 6 0C17.3 4.6 18.3 5 18.3 5c.7 1.7.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.5 "
               "5.9.5.4.9 1.1.9 2.2v3.3c0 .3.2.7.8.6A12 12 0 0 0 12 .3'/></svg>")


def css():
    """Page CSS for both themes (wrapped in a <style> tag)."""
    out = (_CSS.replace("CRYSTAL", CRYSTAL).replace("FONT", FONT)
           .replace("MOBILEpx", f"{MOBILE_MAX}px"))
    return f"<style>{out}</style>"


def header_html(version, stage, subtitle):
    return (f"<div class='am-head'><span class='t'>AirfoilMatic</span>"
            f"<span class='p am-crystal'>v{escape(version)} {escape(stage)}</span></div>"
            f"<div class='am-sub'>{escape(subtitle)}</div>")


def cards_html(items):
    """items: (label, value, sub, crystal). The first card is usually the crystal one."""
    cells = "".join(
        f"<div class='am-card{' am-crystal' if crystal else ''}'><div class='l'>{escape(label)}</div>"
        f"<div class='v'>{escape(value)}</div><div class='s'>{escape(sub)}</div></div>"
        for label, value, sub, crystal in items)
    return f"<div class='am-cards'>{cells}</div>"


def table_html(rows):
    """Small key/value style table (list of dicts with the same keys); wraps text, so it fits a phone."""
    if not rows:
        return ""
    cols = list(rows[0])
    head = "".join(f"<th>{escape(str(c))}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{escape(str(r[c]))}</td>" for c in cols) + "</tr>" for r in rows)
    return f"<div class='am-table-wrap'><table class='am-table'><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"


def row_cards_html(rows, columns=None):
    """Phone version of a wide table: one card per row, first column as the card title."""
    if not rows:
        return ""
    cols = columns or list(rows[0])
    out = []
    for r in rows:
        kv = "".join(f"<div class='kv'><span>{escape(str(c))}</span><span>{escape(str(r[c]))}</span></div>"
                     for c in cols[1:])
        out.append(f"<div class='am-row'><div class='h'>{escape(str(r[cols[0]]))}</div>{kv}</div>")
    return f"<div class='am-rows'>{''.join(out)}</div>"


def step_html(n, title):
    return f"<div class='am-step'>{n} · {escape(title)}</div>"


def note_html(text):
    """Emerald note box; the first line of `text` is shown in bold."""
    head, _, body = text.partition("\n")
    return f"<div class='am-note'><b>{escape(head)}</b>{escape(body)}</div>"


def footer_html(lang, label):
    d = DEVELOPER
    return (f"<div class='am-foot'><div style='font-size:.72rem;opacity:.55'>{escape(label)}</div>"
            f"<div class='who'>{escape(d['name'])}</div>"
            f"<div class='uni'>{escape(d['university'][lang])}</div>"
            f"<a href='{d['linkedin']}' target='_blank' rel='noopener'>{_LINKEDIN_SVG} LinkedIn</a>"
            f"<a href='{d['github']}' target='_blank' rel='noopener'>{_GITHUB_SVG} GitHub</a></div>")


def about_markdown(lang):
    d = DEVELOPER
    if lang == "tr":
        return (f"**AirfoilMatic**: Ansys için 2B kanat profili CFD akış alanı üreticisi.\n\n"
                f"Geliştirici: {d['name']}, {d['university']['tr']}\n\n"
                f"[GitHub]({d['repo']}) · [LinkedIn]({d['linkedin']})")
    return (f"**AirfoilMatic**: 2D airfoil CFD domain generator for Ansys.\n\n"
            f"Developer: {d['name']}, {d['university']['en']}\n\n"
            f"[GitHub]({d['repo']}) · [LinkedIn]({d['linkedin']})")
