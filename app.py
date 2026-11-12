import csv
import io

import numpy as np
# Import pandas fully before any Plotly figure is built. Plotly looks pandas up in
# sys.modules without importing it; while another server thread is still importing
# pandas (seen on Streamlit Cloud, Python 3.14), Plotly gets a half-loaded module
# and fails with "AttributeError: ... Series". This import waits until pandas is ready.
import pandas  # noqa: F401  (installed with Streamlit)
import plotly.graph_objects as go
import streamlit as st

from airfoilmatic import __version__ as APP_VERSION, APP_STAGE
from airfoilmatic.geometry import (DEFAULT_SPLIT, AirfoilError, chord_line_angle, close_small_te_gap,
                                   looks_reversed, parse_airfoil_file, split_at)
from airfoilmatic.geometry import as_is_split, parse_outline_as_is
from airfoilmatic.topology import C_GRID, RECT, SPLIT_LINES, build_domain, line_warnings, select_lines
from airfoilmatic.topology import AS_IS_LINES, build_domain_as_is
from airfoilmatic.export import safe_file_stem, to_ansys_txt
from airfoilmatic import library as lib
from airfoilmatic.mesh import DEFAULTS, MAX_GOOD_GROWTH, plan_inflation, plan_mesh, plan_wake_axis, reynolds
from airfoilmatic.fluent import (AIR_DENSITY, AIR_VISCOSITY, alpha_sweep, decayed_tu, freestream, inlet_tu_for,
                                 max_reachable_tu, speed_for_reynolds, speed_of_sound)
from airfoilmatic.quality import (FLUENT_MAX_SKEWNESS, FLUENT_MIN_ORTHO, RATING_LEVEL,
                                  expected_wall_aspect_ratio, rate_orthogonal, rate_skewness)
from airfoilmatic.i18n import LANGS, tr, tr_error
from airfoilmatic import ui

st.set_page_config(page_title=f"AirfoilMatic v{APP_VERSION} {APP_STAGE}", layout="wide",
                   menu_items={"Report a bug": f"{ui.DEVELOPER['repo']}/issues",
                               "About": ui.about_markdown("tr") + "\n\n---\n\n" + ui.about_markdown("en")})

# ---------------------------------------------------------------- language
lang_label = st.sidebar.radio("Dil / Language", list(LANGS.values()), horizontal=True)
L = {v: k for k, v in LANGS.items()}[lang_label]


def t(key, **kw):
    return tr(key, L, **kw)


def te(exc):
    return tr_error(exc, L)


# One stylesheet for light and dark (CSS light-dark()), so a theme switch needs no rerun.
PLOT = ui.PLOT
st.markdown(ui.css(), unsafe_allow_html=True)
st.markdown(ui.header_html(APP_VERSION, APP_STAGE, t("subtitle")), unsafe_allow_html=True)

# ---------------------------------------------------------------- sidebar inputs
# Widgets whose label is translated carry a key: without one, Streamlit treats the
# relabelled widget as a new one after a language switch and resets it to its default.
source = st.sidebar.radio(t("source"), ["search", "file"], key="source",
                          format_func=lambda k: t("source_search") if k == "search" else t("source_file"))


MAX_T_PERCENT = 40   # the thickest section in the selection is 38.8% c


def _filters():
    lo, hi = st.session_state.get("f_thick", (0, MAX_T_PERCENT))
    return dict(t_range=(lo / 100.0, hi / 100.0), camber=st.session_state.get("f_camber", lib.CAMBER_ANY),
                family_keys=st.session_state.get("f_family") or None)


def _go(section_id):
    """Put a section in the search box; the page then adds it to the back/forward history."""
    st.session_state.af_query = section_id


def _dice():
    pick = lib.random_section(np.random.default_rng(), avoid=st.session_state.get("af_current"), **_filters())
    st.session_state.dice_empty = pick is None
    if pick is not None:
        _go(pick.id)


def _step(d):
    st.session_state.af_hist_i += d
    st.session_state.af_query = st.session_state.af_history[st.session_state.af_hist_i]


section = None
custom_file = None
as_is = False   # uploaded outline used as drawn (VG, flap, kinked section): inflation workflow only
if source == "search":
    st.session_state.setdefault("af_query", "4412")
    st.session_state.setdefault("af_history", [])
    st.session_state.setdefault("af_hist_i", -1)
    query = st.sidebar.text_input(t("search_label"), key="af_query", help=t("search_help"),
                                  placeholder=t("search_placeholder"))
    button_row = st.sidebar.container(key="af_buttons")   # filled below, once this run's section is in the history
    found = lib.search(query)
    if found:
        # The key follows the query, so a new search starts at its best match.
        section = st.sidebar.selectbox(t("results", n=len(found)), found, key=f"pick_{query}",
                                       format_func=lambda s: s.title if s.source == lib.NACA_FORMULA
                                       else f"{s.title} · {s.family_name}")
        st.session_state.af_current = section.id
        hist, i = st.session_state.af_history, st.session_state.af_hist_i
        if not hist or hist[i] != section.id:   # a new section (typed, picked or rolled): remember it
            st.session_state.af_history = hist[: i + 1] + [section.id]
            st.session_state.af_hist_i = len(st.session_state.af_history) - 1
        # ".txt" so that safe_file_stem cuts only that: titles are not file names ("HQ 1.0/12", "E169 (14.4%)")
        file_prefix = "AirfoilMatic_" + safe_file_stem(section.title.replace(" ", "") + ".txt")
    else:
        file_prefix = "AirfoilMatic_custom"
    b1, b2, b3 = button_row.columns(3)
    b1.button("🎲", on_click=_dice, use_container_width=True, key="dice")
    back = -1 if section is not None else 0   # no section shown (unknown query): ← returns to the last one
    b2.button("←", on_click=_step, args=(back,), use_container_width=True, key="hist_back",
              disabled=st.session_state.af_hist_i + back < 0)
    b3.button("→", on_click=_step, args=(1,), use_container_width=True, key="hist_fwd",
              disabled=st.session_state.af_hist_i >= len(st.session_state.af_history) - 1)
    with st.sidebar.expander(t("random_filters")):
        st.slider(t("f_thickness"), 0, MAX_T_PERCENT, (0, MAX_T_PERCENT), key="f_thick")
        st.radio(t("f_camber"), [lib.CAMBER_ANY, lib.CAMBER_SYMMETRIC, lib.CAMBER_CAMBERED], key="f_camber",
                 horizontal=True, format_func=lambda k: t({lib.CAMBER_ANY: "cam_any", lib.CAMBER_SYMMETRIC: "cam_sym",
                                                           lib.CAMBER_CAMBERED: "cam_cambered"}[k]))
        fam = dict(lib.families())
        st.multiselect(t("f_family"), list(fam), format_func=fam.get, key="f_family",
                       placeholder=t("f_family_ph"))
        st.caption(t("pool_size", n=len(lib.pool(**_filters()))))
    if st.session_state.get("dice_empty"):
        st.sidebar.warning(t("dice_empty"))
else:
    custom_file = st.sidebar.file_uploader(t("upload"), type=["dat", "txt", "csv"], key="upload")
    mirror_slot = st.sidebar.empty()   # "mirror in x" box, filled once the file has been read
    as_is = st.sidebar.checkbox(t("as_is"), value=False, help=t("as_is_help"), key="as_is")
    file_prefix = "AirfoilMatic_" + (safe_file_stem(custom_file.name) if custom_file else "custom")

domain_kind = st.sidebar.selectbox(t("domain_type"), [C_GRID, RECT],
                                   format_func=lambda k: t("dom_cgrid") if k == C_GRID else t("dom_rect"), key="domain_kind")
chord = st.sidebar.number_input(t("chord"), value=1.0, step=0.1, min_value=0.01, key="chord")
file_prefix += "_CGrid" if domain_kind == C_GRID else "_Rect"

# Domain sizes are entered as multiples of the chord, so a long or a tiny chord keeps the same
# relative domain (in metres the defaults made a 10 m chord's domain only 1.5c across).
if domain_kind == C_GRID:
    r_inlet_c = st.sidebar.number_input(t("r_inlet"), value=15.0, step=1.0, min_value=2.0, key="r_inlet_c")
    l_wake_c = st.sidebar.number_input(t("l_wake"), value=20.0, step=1.0, min_value=1.0, key="l_wake_c")
    l_top_c = l_bottom_c = r_inlet_c
else:
    r_inlet_c = st.sidebar.number_input(t("l_inlet"), value=15.0, step=1.0, min_value=1.0, key="l_inlet_c")
    l_wake_c = st.sidebar.number_input(t("l_wake"), value=20.0, step=1.0, min_value=1.0, key="l_wake_c")
    l_top_c = st.sidebar.number_input(t("l_top"), value=15.0, step=1.0, min_value=1.0, key="l_top_c")
    l_bottom_c = st.sidebar.number_input(t("l_bottom"), value=15.0, step=1.0, min_value=1.0, key="l_bottom_c")
r_inlet, l_wake, l_top, l_bottom = (v * chord for v in (r_inlet_c, l_wake_c, l_top_c, l_bottom_c))
st.sidebar.caption(t("domain_in_m", r=r_inlet, w=l_wake) if domain_kind == C_GRID
                   else t("domain_in_m_rect", r=r_inlet, w=l_wake, top=l_top, bot=l_bottom))

# Six checkboxes are rarely changed, so they sit in a collapsed expander that shows how many are on.
# The label must not change between reruns, otherwise Streamlit treats it as a new
# expander and closes it after every click; the count is shown inside instead.
n_on = sum(st.session_state.get(f"line_{k}", True) for k in SPLIT_LINES)
with st.sidebar.expander(t("split_mode")):
    st.caption(f"{n_on}/{len(SPLIT_LINES)}")
    st.caption(t("split_mode_help"))
    kept_lines = [k for k in SPLIT_LINES if st.checkbox(t(k), value=True, key=f"line_{k}")]
all_lines = len(kept_lines) == len(SPLIT_LINES)

sidebar_download = st.sidebar.empty()
st.sidebar.markdown(ui.note_html(t("beta_warning", stage=APP_STAGE, version=APP_VERSION)), unsafe_allow_html=True)
st.sidebar.markdown(ui.footer_html(L, t("dev_label")), unsafe_allow_html=True)

# ---------------------------------------------------------------- geometry
MIN_NOTE_OVERLAP = 1e-5   # smaller overlaps are repaired without a remark
MIN_SURFACE_POINTS = 12   # below this DesignModeler's curve through the points is too coarse
file_notes = []           # (kind, text) remarks about an uploaded file, shown on the geometry tab
try:
    if source == "search":
        if section is None:
            if query.strip():
                st.error(t("not_found", q=query.strip()))
            else:
                st.info(t("search_empty"))
            st.stop()
        airfoil = section.airfoil(chord)
    else:
        if custom_file is None:
            st.info(t("upload_info"))
            st.stop()
        data = custom_file.getvalue()
        read_file = parse_outline_as_is if as_is else parse_airfoil_file
        airfoil = read_file(data, chord, name=custom_file.name)
        # A file drawn with its nose at the right would meet the flow tail first. The box is
        # ticked when the outline looks reversed and can be changed by hand either way.
        reversed_file = looks_reversed(airfoil)
        mirrored = mirror_slot.checkbox(t("mirror_x"), value=reversed_file, help=t("mirror_x_help"),
                                        key=f"mirror_{custom_file.file_id}")   # a new upload is checked afresh
        if mirrored:
            airfoil = read_file(data, chord, name=custom_file.name, mirror=True)
        if reversed_file and mirrored:
            file_notes.append(("info", t("note_mirrored")))
        elif looks_reversed(airfoil):
            file_notes.append(("warning", t("note_reversed")))
        n_min = min(len(airfoil.xu), len(airfoil.xl))
        if n_min < MIN_SURFACE_POINTS:
            file_notes.append(("warning", t("note_few_points", n=n_min, need=MIN_SURFACE_POINTS)))
        if airfoil.overlap >= MIN_NOTE_OVERLAP:
            file_notes.append(("warning", t("note_overlap", amount=airfoil.overlap)))
        tilt = chord_line_angle(airfoil)
        if abs(tilt) >= 1.0:
            file_notes.append(("info", t("note_tilt", angle=tilt)))
    airfoil = close_small_te_gap(airfoil)
    split_af = as_is_split(airfoil, DEFAULT_SPLIT) if as_is else split_at(airfoil, DEFAULT_SPLIT)
except AirfoilError as e:
    st.error(t("err_geometry", msg=te(e)))
    st.stop()

try:
    domain = (build_domain_as_is if as_is else build_domain)(split_af, domain_kind, r_inlet=r_inlet, l_wake=l_wake,
                                                            l_top=l_top, l_bottom=l_bottom)
except ValueError as e:
    st.error(t("err_domain", msg=te(e)))
    st.stop()
if as_is:   # the outline as drawn has only the two axes; the split-line boxes do not apply
    kept_lines, all_lines = list(AS_IS_LINES), False

# `domain` keeps every split line (used for sizing plans); `out_domain` is what is
# drawn and exported for the chosen workflow.
out_domain = select_lines(domain, kept_lines)
txt_data = to_ansys_txt(out_domain)
with sidebar_download:
    st.download_button(t("download"), data=txt_data, file_name=f"{file_prefix}.txt",
                       mime="text/plain", width="stretch", key="dl_sidebar",
                       type="primary")


# ---------------------------------------------------------------- helpers
def airfoil_traces(fig):
    for c in domain.by_kind("airfoil") + [c for c in domain.curves if c.key == "te_closure"]:
        fig.add_trace(go.Scatter(x=c.x, y=c.y, mode="lines", showlegend=False,
                                 line=dict(color=PLOT["line"], width=2.5), hoverinfo="skip"))
    x = np.concatenate([airfoil.xu, airfoil.xl[::-1]])
    y = np.concatenate([airfoil.yu, airfoil.yl[::-1]])
    # emerald fill from the leading edge (deep) to the trailing edge (light); needs plotly >= 5.20
    fig.add_trace(go.Scatter(x=x, y=y, fill="toself",
                             fillgradient=dict(type="horizontal", colorscale=[[0, PLOT["fill"][0]], [1, PLOT["fill"][1]]]),
                             line=dict(color="rgba(0,0,0,0)", width=0), name=airfoil.name))


def style(fig, height, xrange=None, yrange=None, fit_domain=False):
    fig.update_layout(xaxis_title=t("x_axis"), yaxis_title=t("y_axis"), showlegend=True, height=height,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family=ui.FONT),
                      margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.08, x=0),
                      # fit_domain: keep the given ranges and shrink the drawing area to keep 1:1, instead of
                      # widening the y range (on phones that showed far more than the domain)
                      xaxis=dict(range=xrange, constrain="domain" if fit_domain else None),
                      yaxis=dict(scaleanchor="x", scaleratio=1, range=yrange,
                                 constrain="domain" if fit_domain else None))
    for upd in (fig.update_xaxes, fig.update_yaxes):
        upd(gridcolor=PLOT["grid"], zerolinecolor=PLOT["zero"], tickfont=dict(size=12))


def fitted_chart(fig, key, xr, yr, max_h=780):
    """Show exactly xr x yr at 1:1. The card takes that aspect ratio and the chart stretches to fill it,
    so the chart is short on a phone and grows with the domain instead of showing empty space."""
    aspect = (xr[1] - xr[0]) / (yr[1] - yr[0])
    # Card height = drawing width / aspect + room for legend, axes and padding. 100cqw is the width of
    # the main column (a CSS container, see ui.py); ~100 px of it go to padding and the y axis.
    st.markdown(f"<style>.st-key-{key}{{height:calc((100cqw - 100px) / {aspect:.3f} + 170px) !important;flex:0 0 auto !important;"
                f"min-height:230px;max-height:{max_h}px}}"
                f".st-key-{key} [data-testid='stPlotlyChart']{{flex:1 1 auto;min-height:0}}</style>",
                unsafe_allow_html=True)
    style(fig, None, xr, yr, fit_domain=True)
    # legend in its own top margin: on a phone it wraps to two rows and must not cover the drawing
    fig.update_layout(legend=dict(orientation="h", x=0, y=1.03, yanchor="bottom"), margin=dict(t=70, b=10))
    with st.container(key=key):
        st.plotly_chart(fig, width="stretch", height="stretch", config={"scrollZoom": False})


def plan_rows(plan):
    rows = []
    for e in plan.edges:
        rows.append({
            t("col_group"): t(e.group),
            t("col_edges"): ", ".join(t(k) for k in e.edges),
            t("col_n"): str(e.n),
            t("col_bias"): f"{e.bias:.6g}",  # text: browser locale would show 2,154 and break pasting into Ansys
            t("col_small"): t(e.small_end),
            t("col_dsmin"): m_mm(e.ds_min),
            t("col_dsmax"): m_mm(e.ds_max),
            t("col_growth"): round(e.growth, 4),
            t("col_length"): round(e.length, 5),
        })
    return rows


def wide_table(rows, key, columns=None):
    """Dataframe on wide screens, one card per row on phones (CSS switches between them)."""
    with st.container(key=f"wide_{key}"):
        st.dataframe(rows, width="stretch", hide_index=True, column_order=columns)
    st.markdown(ui.row_cards_html(rows, columns), unsafe_allow_html=True)


def rows_to_csv(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8-sig")  # BOM so Excel shows Turkish characters


tab_geo, tab_mesh = st.tabs([t("tab_geometry"), t("tab_mesh")])

# ================================================================ geometry tab
with tab_geo:
    n_faces = max(1, len(kept_lines))
    if as_is:
        st.caption(t("asis_geom_info"))
    else:
        st.caption(t("geom_info", split=DEFAULT_SPLIT) if all_lines else (t("geom_info_one") if n_faces == 1 else t("geom_info_partial", n=n_faces)))
    for kind, key in line_warnings(kept_lines):
        st.warning(t("warn_single_line", line=t(key)) if kind == "single_line" else t("warn_wake_no_front"))
    if section is not None:
        if section.source == lib.NACA_FORMULA:
            st.caption(t("info_naca", title=section.title, t=100 * section.t, xt=section.xt))
        else:
            st.caption(t("info_uiuc", title=section.title, family=section.family_name, id=section.id,
                         t=100 * section.t, xt=section.xt, camber=100 * section.camber, xc=section.xc,
                         points=section.points))
    if domain.blunt_te:
        st.info(t("blunt_info", gap=split_af.te_gap))
    for kind, text in file_notes:
        (st.warning if kind == "warning" else st.info)(text)

    st.subheader(t("zoom_title"))
    fig_zoom = go.Figure()
    for i, c in enumerate([c for c in out_domain.by_kind("split") if c.key != "te_closure"]):
        fig_zoom.add_trace(go.Scatter(x=c.x, y=c.y, mode="lines", name=t("split_lines"), legendgroup="split",
                                      showlegend=i == 0, hovertext=t(c.key), hoverinfo="text",
                                      line=dict(color=PLOT["split"], width=1.5, dash="dash")))
    airfoil_traces(fig_zoom)
    # airfoil plus a little margin; thick sections (up to ~30 %) still fit in +-0.3c
    t_half = max(np.max(np.abs(airfoil.yu)), np.max(np.abs(airfoil.yl)))
    y_half = max(0.3 * chord, 1.3 * t_half)
    # capped so the plots do not fill a desktop screen; on phones the width already keeps them short
    fitted_chart(fig_zoom, "plot_zoom", [-0.08 * chord, 1.08 * chord], [-y_half, y_half], max_h=430)

    st.subheader(t("full_title"))
    fig_full = go.Figure()
    # one legend entry for all outer boundaries (the legend fits a phone); hover still names each one
    for i, c in enumerate(out_domain.by_kind("boundary")):
        fig_full.add_trace(go.Scatter(x=c.x, y=c.y, mode="lines", name=t("boundaries"), legendgroup="bnd",
                                      showlegend=i == 0, hovertext=t(c.key), hoverinfo="text",
                                      line=dict(color=PLOT["boundary"], width=1.5)))
    for i, c in enumerate([c for c in out_domain.by_kind("split") if c.key != "te_closure"]):
        fig_full.add_trace(go.Scatter(x=c.x, y=c.y, mode="lines", name=t("split_lines"), legendgroup="split",
                                      showlegend=i == 0, hovertext=t(c.key), hoverinfo="text",
                                      line=dict(color=PLOT["split"], width=1.5, dash="dash")))
    airfoil_traces(fig_full)
    # exactly the domain (+4 %)
    xs = np.concatenate([c.x for c in out_domain.curves])
    ys = np.concatenate([c.y for c in out_domain.curves])
    pad = 0.04 * max(np.ptp(xs), np.ptp(ys))
    fitted_chart(fig_full, "plot_full", [xs.min() - pad, xs.max() + pad], [ys.min() - pad, ys.max() + pad],
                 max_h=520)

    st.download_button(t("download"), data=txt_data, file_name=f"{file_prefix}.txt",
                       mime="text/plain", width="stretch", key="dl_main",
                       type="primary")

# ================================================================ mesh tab
INFLATION, MAPPED = "inflation", "mapped"
FAR_FIELD_SIZE = 0.5  # global element size for quad-dominant meshes, in chords
# With inflation on both the airfoil and the wake axis, Ansys failed or produced
# degenerate cells at the TE with ~1 mm elements there; ~3 mm (0.003c) worked.
INFL_MIN_TE = 0.003
INFL_TE_FACTOR = 1.5   # TE surface element / last inflation layer, at least


def m_mm(v):
    """Length in metres and millimetres, e.g. '1.226e-05 m (0.01226 mm)'."""
    return f"{v:.4g} m ({v * 1000:.4g} mm)"


def short(v, unit=""):
    return f"{v:.3g} {unit}".strip() if 1e-3 <= abs(v) < 1e4 else f"{v:.2e} {unit}".strip()


with tab_mesh:
    st.caption(t("mesh_intro"))

    c1, c2, c3 = st.columns(3)
    with c1.container(key="card_flow"):
        st.markdown(ui.step_html(1, t("step_flow")), unsafe_allow_html=True)
        flow_mode = st.radio(t("flow_input"), ["re", "vel"], horizontal=True, key="flow_mode",
                             format_func=lambda k: t("flow_re") if k == "re" else t("flow_vel"))
        u_inf = rho = mu = None
        if flow_mode == "re":
            re = st.number_input(t("re"), value=2.0e6, min_value=1.0e3, step=1.0e5, format="%.4e", key="re")
        else:
            u_inf = st.number_input(t("velocity"), value=30.0, min_value=0.01, key="velocity")
            rho = st.number_input(t("density"), value=1.225, min_value=1e-6, format="%.4f", key="density")
            mu = st.number_input(t("viscosity"), value=1.7894e-5, min_value=1e-9, format="%.4e", key="viscosity")
            re = reynolds(u_inf, rho, mu, chord)
            st.caption(f"Re = {short(re)}")
    with c2.container(key="card_method"):
        st.markdown(ui.step_html(2, t("step_method")), unsafe_allow_html=True)
        if as_is:
            st.session_state.mesh_mode = INFLATION   # mapped blocks need the vertical split lines
        mesh_mode = st.radio(t("mesh_method"), [INFLATION, MAPPED],
                             format_func=lambda k: t("method_inflation") if k == INFLATION else t("method_mapped"),
                             key="mesh_mode", disabled=as_is)
        if as_is:
            st.caption(t("asis_no_mapped"))
        y_plus = st.number_input(t("y_plus"), value=DEFAULTS["y_plus"], min_value=0.05, step=0.5, key="y_plus")
    with c3.container(key="card_growth"):
        st.markdown(ui.step_html(3, t("step_growth")), unsafe_allow_html=True)
        if mesh_mode == INFLATION:
            growth = st.number_input(t("growth"), value=1.15, min_value=1.01, max_value=1.5,
                                     step=0.01, format="%.3f", key="g_infl")
            coverage = st.number_input(t("coverage"), value=1.5, min_value=0.5, max_value=5.0, step=0.25,
                                       key="coverage")
        else:
            growth = st.number_input(t("growth"), value=DEFAULTS["growth"], min_value=1.01, max_value=1.5,
                                     step=0.01, format="%.3f", key="g_map")
    # Chordwise sizes: full width under the three cards so the inputs are not squeezed.
    with st.expander(t("advanced")):
        st.caption(t("advanced_help" if mesh_mode == MAPPED else "advanced_help_infl"))
        cols = st.columns(4 if mesh_mode == MAPPED else 3)
        ds_le = cols[0].number_input(t("ds_le"), value=DEFAULTS["ds_le"], min_value=1e-5, format="%.4f", step=0.0005,
                                     key="ds_le")
        ds_split = cols[1].number_input(t("ds_split"), value=DEFAULTS["ds_split"], min_value=1e-4, format="%.4f",
                                        step=0.001, key="ds_split")
        ds_te = cols[2].number_input(t("ds_te"), value=DEFAULTS["ds_te"], min_value=1e-5, format="%.4f", step=0.0005,
                                     key="ds_te")
        # Inflation mode ends the wake axis at the far-field element size. First element, last
        # element and edge length then fix the progression, so a growth input would change nothing.
        wake_growth = DEFAULTS["wake_growth"]
        if mesh_mode == MAPPED:
            wake_growth = cols[3].number_input(t("wake_growth"), value=DEFAULTS["wake_growth"], min_value=1.01,
                                               max_value=1.5, step=0.01, format="%.3f", key="wake_growth")

    if re < 5e5:
        st.info(t("low_re_note"))
    sizing = dict(y_plus=y_plus, growth=growth, ds_le=ds_le, ds_split=ds_split, ds_te=ds_te,
                  wake_growth=wake_growth)
    plan = infl = None
    try:
        if mesh_mode == INFLATION:
            infl = plan_inflation(re, chord, y_plus=y_plus, growth=growth, coverage=coverage)
        else:
            plan = plan_mesh(domain, split_af, re, **sizing)
    except (ValueError, OverflowError) as e:
        st.error(te(e))

    if infl is not None:
        # Reynolds is an input, so it only appears as a note under the boundary-layer card.
        st.markdown(ui.cards_html([
            (t("infl_first"), f"{infl.first_layer * 1000:.4g} mm", "First Layer Height", True),
            (t("infl_layers"), f"{infl.layers}", "Maximum Layers", False),
            (t("infl_total"), f"{infl.total * 1000:.3g} mm", f"≈ {infl.total / infl.delta_turb:.2g} δ", False),
            (t("m_delta"), f"{infl.delta_turb * 1000:.3g} mm", f"Re = {short(re)}", False),
        ]), unsafe_allow_html=True)
        st.subheader(t("infl_table_title"))
        # Smallest surface element: LE/TE spacing, or a blunt-TE face element.
        # At the sharp TE the upper and lower inflation stacks meet; Ansys 2024 R2 failed whenever the TE
        # surface element was smaller than the last inflation layer (NACA 0012, Re 2e6: 3 mm TE vs 4.3 mm
        # last layer failed, ~5.8 mm worked). Keep the TE element >= 1.5x the last layer and >= 0.003c.
        ds_te_infl = max(ds_te, INFL_MIN_TE, INFL_TE_FACTOR * infl.last_layer / chord)
        smallest = min(ds_le, ds_te_infl) * chord
        if domain.blunt_te:
            smallest = min(smallest, split_af.te_gap / 4)
        defeature = float(f"{smallest / 50:.0e}")   # well below every specified size
        curv_min = float(f"{smallest / 5:.0e}")     # so curvature sizing never coarsens the edges
        infl_rows = [
            {t("col_setting"): "Inflation Option", t("col_value"): "First Layer Thickness"},
            {t("col_setting"): "First Layer Height", t("col_value"): m_mm(infl.first_layer)},
            {t("col_setting"): "Maximum Layers", t("col_value"): f"{infl.layers}"},
            {t("col_setting"): "Growth Rate", t("col_value"): f"{infl.growth:.6g}"},
            {t("col_setting"): t("infl_total"), t("col_value"): f"{m_mm(infl.total)}  (≈ {infl.total / infl.delta_turb:.2g} δ)"},
            {t("col_setting"): t("infl_last"), t("col_value"): m_mm(infl.last_layer)},
            {t("col_setting"): t("glob_size"), t("col_value"): m_mm(FAR_FIELD_SIZE * chord)},
            {t("col_setting"): t("glob_growth"), t("col_value"): "1.15"},
            {t("col_setting"): "Defeature Size (Mesh → Sizing)", t("col_value"): m_mm(defeature)},
            {t("col_setting"): "Curvature Min Size (Mesh → Sizing)", t("col_value"): m_mm(curv_min)},
        ]
        st.markdown(ui.table_html(infl_rows), unsafe_allow_html=True)
        if domain.blunt_te:
            st.warning(t("warn_blunt_infl"))

        # Edge Sizing for the airfoil and wake-axis edges (same geometric plan as mapped mode)
        st.subheader(t("infl_edges_title") if "wake_axis" in kept_lines else t("infl_edges_title_af"))
        if as_is:
            # The drawn wall has no single chordwise spacing (fin walls, kinks): size it by hand.
            st.info(t("asis_edges_note", ds_le=m_mm(ds_le * chord), ds_te=m_mm(ds_te_infl * chord)))
            try:
                wake = plan_wake_axis(domain, ds_te=ds_te_infl, wake_growth=wake_growth,
                                      max_wake_cell=FAR_FIELD_SIZE * chord)
                wide_table([{t("col_group"): t(wake.group), t("col_n"): str(wake.n), t("col_bias"): f"{wake.bias:.6g}",
                             t("col_small"): t(wake.small_end), t("col_dsmin"): m_mm(wake.ds_min),
                             t("col_dsmax"): m_mm(wake.ds_max), t("col_edges"): t("wake_axis")}], "infl_edges")
            except (ValueError, OverflowError) as e:
                st.error(te(e))
        else:
            try:
                edge_plan = plan_mesh(domain, split_af, re, max_wake_cell=FAR_FIELD_SIZE * chord,
                                      **dict(sizing, ds_te=ds_te_infl))
                keep = ("g_af_front", "g_af_rear") + (("g_wake",) if "wake_axis" in kept_lines else ())
                e_rows = [r for e, r in zip(edge_plan.edges, plan_rows(edge_plan)) if e.group in keep]
                for r, e in zip(e_rows, [e for e in edge_plan.edges if e.group in keep]):
                    if e.group == "g_wake":
                        r[t("col_edges")] = t("wake_axis")
                wide_table(e_rows, "infl_edges", [t(k) for k in ("col_group", "col_n", "col_bias", "col_small",
                                                                 "col_dsmin", "col_dsmax", "col_edges")])
            except (ValueError, OverflowError) as e:
                st.error(te(e))
        if infl.growth > MAX_GOOD_GROWTH:
            st.warning(t("warn_growth", g=infl.growth, lim=MAX_GOOD_GROWTH))
        with st.expander(t("howto_title")):
            st.markdown(t("named_sel"))
            st.markdown(t("howto_infl"))
            st.markdown(t("infl_note"))
            st.markdown(t("infl_edges_note"))
            st.caption(t("delta_note", lam=m_mm(infl.delta_lam)))

    if plan is not None:
        if not all_lines:
            st.warning(t("warn_mapped_lines"))
        st.markdown(ui.cards_html([
            (t("m_dy1"), f"{plan.dy1 * 1000:.4g} mm", f"Re = {short(re)}", True),
            (t("m_nbl"), f"{plan.n_bl}", "", False),
            (t("m_cells"), f"{plan.cells:,}",
             t("m_counts_short", n_normal=plan.n_normal, n_front=plan.n_front, n_rear=plan.n_rear,
               n_wake=plan.n_wake), False),
        ]), unsafe_allow_html=True)
        if plan.max_growth > MAX_GOOD_GROWTH:
            st.warning(t("warn_growth", g=plan.max_growth, lim=MAX_GOOD_GROWTH))
        if plan.n_bl < 20:
            st.warning(t("warn_bl", n=plan.n_bl))
        st.subheader(t("table_title"))
        if domain_kind == RECT:
            st.info(t("rect_note"))
        rows = plan_rows(plan)
        wide_table(rows, "edge_sizing", [t(k) for k in ("col_group", "col_n", "col_bias", "col_small",
                                                        "col_dsmin", "col_edges")])
        st.download_button(t("download_csv"), data=rows_to_csv(rows),
                           file_name=f"{file_prefix}_edge_sizing.csv", mime="text/csv")
        with st.expander(t("howto_title")):
            st.markdown(t("named_sel"))
            st.markdown(t("howto"))
            st.caption(t("delta_note", lam=m_mm(plan.delta_lam)))

    # First cell height of the plan above; None when the plan failed (e.g. Re below the valid range).
    dy_ref = infl.first_layer if infl is not None else (plan.dy1 if plan is not None else None)

    # ---- mesh quality check
    with st.expander(t("quality_title")):
        st.caption(t("quality_help"))
        qc = st.columns(4)
        sk_max = qc[0].number_input(t("q_sk_max"), value=None, min_value=0.0, max_value=1.0, format="%.4f",
                                    placeholder="0.76", key="q_sk_max")
        sk_avg = qc[1].number_input(t("q_sk_avg"), value=None, min_value=0.0, max_value=1.0, format="%.4f",
                                    placeholder="0.016", key="q_sk_avg")
        oq_min = qc[2].number_input(t("q_oq_min"), value=None, min_value=0.0, max_value=1.0, format="%.4f",
                                    placeholder="0.027", key="q_oq_min")
        oq_avg = qc[3].number_input(t("q_oq_avg"), value=None, min_value=0.0, max_value=1.0, format="%.4f",
                                    placeholder="0.995", key="q_oq_avg")
        q_rows = []
        worst = 0
        for label, val, rater, limit_ok in (
                (t("q_sk_max"), sk_max, rate_skewness, lambda v: v < FLUENT_MAX_SKEWNESS),
                (t("q_sk_avg"), sk_avg, rate_skewness, None),
                (t("q_oq_min"), oq_min, rate_orthogonal, lambda v: v > FLUENT_MIN_ORTHO),
                (t("q_oq_avg"), oq_avg, rate_orthogonal, None)):
            if val is None:
                continue
            key = rater(val)
            fluent = "—" if limit_ok is None else (t("q_pass") if limit_ok(val) else t("q_fail"))
            worst = max(worst, RATING_LEVEL[key] if limit_ok is not None else 0)
            if limit_ok is not None and not limit_ok(val):
                worst = 3
            q_rows.append({t("q_metric"): label, t("col_value"): f"{val:.4g}",
                           t("q_rating"): t(key), t("q_fluent"): fluent})
        if q_rows:
            st.markdown(ui.table_html(q_rows), unsafe_allow_html=True)
            msg = ("q_verdict_ok", "q_verdict_check", "q_verdict_bad", "q_verdict_fail")[worst]
            (st.success if worst == 0 else st.warning if worst < 3 else st.error)(t(msg))
        if dy_ref:
            st.markdown(t("q_ar_expected",
                          ar_le=expected_wall_aspect_ratio(dy_ref, ds_le * chord),
                          ar_mid=expected_wall_aspect_ratio(dy_ref, ds_split * chord)))
        st.markdown(t("q_explain"))

    # ---- y+ correction
    if dy_ref:
        with st.expander(t("yplus_fix_title")):
            st.caption(t("yplus_fix_help"))
            dy0 = float(f"{dy_ref:.4e}")   # very high Re or a tiny chord can go below the usual 1e-9 m floor
            used = st.number_input(t("yplus_used_dy"), value=dy0, min_value=min(1e-9, dy0), format="%.4e")
            seen = st.number_input(t("yplus_seen"), value=None, min_value=1e-3, format="%.3f", key="yplus_seen")
            if seen:
                st.success(t("yplus_fix_result", dy=m_mm(used * y_plus / seen), target=y_plus))

    # ---- Fluent setup helper
    with st.expander(t("fluent_title")):
        rho_f = rho if rho is not None else AIR_DENSITY
        mu_f = mu if mu is not None else AIR_VISCOSITY
        u_default = u_inf if u_inf is not None else speed_for_reynolds(re, chord, rho_f, mu_f)
        fc = st.columns(3)
        aoa = fc[0].number_input(t("aoa"), value=4.25, step=0.25, format="%.2f", key="aoa")
        temp_c = fc[2].number_input(t("fl_temp"), value=15.0, step=5.0, min_value=-100.0, max_value=500.0,
                                    format="%.1f", key="fl_temp", help=t("fl_temp_help"))
        a_sound = speed_of_sound(temp_c)
        u0 = float(f"{u_default:.4g}")   # Re = 1000 on a long chord needs less than 1 mm/s
        u_fl = fc[1].number_input(t("fl_speed"), value=u0, min_value=min(0.001, u0),
                                  format="%.3f", help=t("fl_speed_help"))
        try:
            fs = freestream(aoa, u_fl, chord, rho_f, mu_f, speed_of_sound=a_sound)
        except ValueError as e:
            st.error(te(e))
            fs = None
        if fs is not None:
            rows_f = [
                {t("col_setting"): t("fl_vel_comp"),
                 t("col_value"): f"X = {fs.ux:.6g} m/s,  Y = {fs.uy:.6g} m/s"},
                {t("col_setting"): t("fl_vel_dir"),
                 t("col_value"): f"X = {fs.drag[0]:.6f},  Y = {fs.drag[1]:.6f}"},
                {t("col_setting"): t("fl_drag"), t("col_value"): f"X = {fs.drag[0]:.6f},  Y = {fs.drag[1]:.6f}"},
                {t("col_setting"): t("fl_lift"), t("col_value"): f"X = {fs.lift[0]:.6f},  Y = {fs.lift[1]:.6f}"},
                {t("col_setting"): t("fl_ref_vel"), t("col_value"): f"{fs.speed:.6g} m/s"},
                {t("col_setting"): t("fl_ref_rho"), t("col_value"): f"{rho_f:g} kg/m³"},
                {t("col_setting"): t("fl_visc"), t("col_value"): f"{mu_f:g} Pa·s"},
                {t("col_setting"): t("fl_ref_len"), t("col_value"): f"{chord:g} m"},
                {t("col_setting"): t("fl_ref_area"), t("col_value"): f"{chord:g} m² (c × 1 m)"},
                {t("col_setting"): t("fl_re_mach"), t("col_value"): f"Re = {fs.reynolds:.4e},  M = {fs.mach:.3f}"},
                {t("col_setting"): t("fl_sound"), t("col_value"): f"{a_sound:.2f} m/s ({temp_c:g} °C)"},
            ]
            st.markdown(ui.table_html(rows_f), unsafe_allow_html=True)
            if abs(fs.reynolds - re) > 0.01 * re:
                st.warning(t("fl_re_mismatch", re_fl=fs.reynolds, re_mesh=re))
            if fs.mach > 0.3:
                st.warning(t("fl_mach_warn", m=fs.mach))
        st.caption(t("fluent_note"))

        if fs is not None:
            # ---- free-stream turbulence decay between the inlet and the leading edge
            st.markdown(f"**{t('tu_title')}**")
            tc = st.columns(3)
            tu_in = tc[0].number_input(t("tu_inlet"), value=1.0, min_value=0.001, max_value=50.0, step=0.1,
                                       format="%.3f", key="tu_inlet")
            vr = tc[1].number_input(t("tu_vr"), value=100.0, min_value=0.1, max_value=1.0e5, step=1.0,
                                    format="%.4g", key="tu_vr")
            tu_goal = tc[2].number_input(t("tu_goal"), value=None, min_value=0.001, max_value=50.0, step=0.01,
                                         format="%.3f", key="tu_goal", placeholder="0.10")
            dist = abs(domain.x_inlet)                       # inlet to the leading edge at x = 0
            re_x = rho_f * fs.speed * dist / mu_f
            tu_le = decayed_tu(tu_in / 100, re_x, vr)
            rows_t = [
                {t("col_setting"): t("tu_dist"), t("col_value"): f"{dist:.4g} m ({dist / chord:.3g} c)"},
                {t("col_setting"): t("tu_at_le"), t("col_value"): f"{100 * tu_le:.3g} %"},
                {t("col_setting"): t("tu_max"),
                 t("col_value"): f"{100 * max_reachable_tu(re_x, vr):.3g} %"},
            ]
            if tu_goal:
                need = inlet_tu_for(tu_goal / 100, re_x, vr)
                rows_t.append({t("col_setting"): t("tu_need", goal=tu_goal),
                               t("col_value"): f"{100 * need:.3g} %" if need is not None else t("tu_unreachable")})
            st.markdown(ui.table_html(rows_t), unsafe_allow_html=True)
            st.caption(t("tu_note"))

            # ---- angle-of-attack sweep: one row per angle, for a polar
            st.markdown(f"**{t('sweep_title')}**")
            sc = st.columns(3)
            a0 = sc[0].number_input(t("sweep_from"), value=-4.0, step=1.0, format="%.2f", key="sweep_from")
            a1 = sc[1].number_input(t("sweep_to"), value=16.0, step=1.0, format="%.2f", key="sweep_to")
            da = sc[2].number_input(t("sweep_step"), value=2.0, min_value=0.05, step=0.5, format="%.2f",
                                    key="sweep_step")
            try:
                sweep = alpha_sweep(a0, a1, da, fs.speed)
            except ValueError as e:
                st.error(te(e))
                sweep = []
            if sweep:
                rows_s = [{"α [°]": f"{r['aoa']:g}", "X-Velocity [m/s]": f"{r['ux']:.6g}",
                           "Y-Velocity [m/s]": f"{r['uy']:.6g}",
                           "Drag X": f"{r['drag'][0]:.6f}", "Drag Y": f"{r['drag'][1]:.6f}",
                           "Lift X": f"{r['lift'][0]:.6f}", "Lift Y": f"{r['lift'][1]:.6f}"} for r in sweep]
                wide_table(rows_s, "sweep")
                st.download_button(t("sweep_csv"), data=rows_to_csv(rows_s),
                                   file_name=f"{file_prefix}_aoa_sweep.csv", mime="text/csv", key="sweep_csv")
