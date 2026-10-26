"""Look of the Streamlit app: emerald palette, CSS, small HTML blocks.

Kept apart from app.py so the page code stays about the workflow. Nothing here
calls Streamlit; app.py injects the returned strings with st.markdown/st.html.
"""
import re
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

THEMES = {
    "light": dict(
        top="#D6ECE0", mid="#EAF4EF", bot="#F3F7FA", sbt="#E4F1EA", sbb="#F5F8F6", base="#FFFFFF",
        tint="linear-gradient(160deg,rgba(222,240,231,.95),rgba(255,255,255,0) 70%)",
        e1=EMERALD, e2="#8FD3B1", ib="rgba(35,128,84,.32)", ibg="linear-gradient(180deg,#FFFFFF,#F0F7F3)",
        acc=EMERALD, sh="rgba(19,69,44,.35)", note="linear-gradient(160deg,#E3F2EA,#F4FAF7)",
        note_text="#174A31",
    ),
    "dark": dict(
        top="#0F2C1F", mid="#0A1A13", bot="#070F0B", sbt="#0C1F16", sbb="#08120D", base="#09140F",
        tint="linear-gradient(160deg,rgba(37,138,90,.16),rgba(9,20,15,0) 70%)",
        e1=EMERALD_LIGHT, e2="#174A31", ib="rgba(94,189,145,.30)", ibg="linear-gradient(180deg,#10211A,#0B1711)",
        acc="#3FBF85", sh="rgba(0,0,0,.55)", note="linear-gradient(160deg,rgba(37,138,90,.22),rgba(15,27,21,.6))",
        note_text="#CDEBDD",
    ),
}

# Plot colours per theme: airfoil line, fill gradient (LE -> TE), split lines,
# domain boundary, grid, zero line, GCI fit, GCI extrapolated value.
PLOT = {
    "light": dict(line=EMERALD, fill=("rgba(19,69,44,0.55)", "rgba(94,189,145,0.18)"), split="#C08A3E",
                  boundary="#A3ABA7", grid="rgba(28,97,66,0.10)", zero="rgba(28,97,66,0.25)",
                  fit="#C08A3E", ext="#B5523B"),
    "dark": dict(line=EMERALD_LIGHT, fill=("rgba(94,189,145,0.45)", "rgba(19,69,44,0.25)"), split="#E3B566",
                 boundary="#4E6157", grid="rgba(94,189,145,0.10)", zero="rgba(94,189,145,0.25)",
                 fit="#E3B566", ext="#E07A5F"),
}

_CSS = """
.stApp{background:linear-gradient(180deg,TOP 0px,MID 340px,BOT 900px) !important;}
[data-testid="stHeader"]{background:transparent !important;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,SBT,SBB) !important;}

/* inputs: thin emerald frame, soft inner gradient, glow on focus */
[data-testid="stNumberInputContainer"],[data-testid="stTextInputRootElement"],
[data-testid="stSelectbox"] div[role="group"]{border:1px solid IB !important;background:IBG !important;
  border-radius:.7rem !important;box-shadow:0 2px 8px -4px SH;}
[data-testid="stNumberInputContainer"]:focus-within,[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stSelectbox"] div[role="group"]:focus-within{border-color:E1 !important;
  box-shadow:0 0 0 3px rgba(63,191,133,.20) !important;}
[data-testid="stNumberInputContainer"] input,[data-testid="stTextInputRootElement"] input,
[data-testid="stSelectbox"] input,[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"]{background:transparent !important;}

/* large cards and plots: gradient emerald frame (containers with key card_* / plot_*) */
[class*="st-key-card_"],[class*="st-key-plot_"]{border:1px solid transparent !important;border-radius:1rem !important;
  padding:1rem 1.1rem !important;box-shadow:0 14px 34px -22px SH;
  background:TINT padding-box,linear-gradient(BASE,BASE) padding-box,linear-gradient(135deg,E1,E2) border-box !important;}

/* tables and metrics: emerald accent on the left */
[data-testid="stDataFrame"]{border-left:4px solid ACC;border-radius:.8rem;overflow:hidden;box-shadow:0 10px 26px -20px SH;}
[data-testid="stMetric"]{border:1px solid rgba(128,128,128,.22);border-left:4px solid ACC;border-radius:.8rem;
  padding:.8rem 1rem;background:BASE;}
[data-testid="stExpander"] details{border-color:IB !important;border-radius:.8rem !important;background:BASE;}

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
.am-card{border:1px solid rgba(128,128,128,.22);border-left:4px solid ACC;background:BASE;border-radius:.8rem;padding:.8rem 1rem;}
.am-card.am-crystal{border-left:1px solid rgba(255,255,255,.14) !important;}
.am-card .l{font-size:.78rem;opacity:.65;}
.am-card .v{font-size:1.35rem;font-weight:600;line-height:1.35;}
.am-card .s{font-size:.75rem;opacity:.55;}
.am-step{font-size:.8rem;letter-spacing:.04em;text-transform:uppercase;opacity:.6;margin-bottom:.3rem;}
.am-note{background:NOTE;border:1px solid IB;border-left:4px solid ACC;border-radius:.8rem;padding:.75rem .9rem;
  font-size:.86rem;line-height:1.45;color:NOTE_TEXT;margin:.4rem 0;}
.am-note b{display:block;margin-bottom:.2rem;}
.am-foot{margin-top:.6rem;padding-top:.8rem;border-top:1px solid rgba(128,128,128,.2);font-size:.85rem;}
.am-foot .who{font-weight:600;}
.am-foot .uni{font-size:.78rem;opacity:.6;margin-bottom:.45rem;}
.am-foot a{display:inline-flex;align-items:center;gap:.35rem;margin-right:.9rem;color:inherit !important;
  text-decoration:none;opacity:.8;}
.am-foot a:hover{opacity:1;color:E1 !important;}
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


def theme_name(dark):
    return "dark" if dark else "light"


def css(dark=False):
    """Page CSS for the light or dark theme (wrapped in a <style> tag)."""
    th = THEMES[theme_name(dark)]
    values = {k.upper(): v for k, v in th.items()}
    values.update(CRYSTAL=CRYSTAL, FONT=FONT)
    # one pass with word boundaries, so inserted values are never re-scanned
    out = re.sub(r"\b(" + "|".join(values) + r")\b", lambda m: values[m.group(1)], _CSS)
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
