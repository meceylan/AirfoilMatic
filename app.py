import csv
import io
import math
import re

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from airfoilmatic import __version__ as APP_VERSION, APP_STAGE
from airfoilmatic.geometry import (DEFAULT_SPLIT, AirfoilError, close_small_te_gap, naca,
                                   parse_airfoil_file, split_at)
from airfoilmatic.topology import C_GRID, RECT, SPLIT_LINES, build_domain, line_warnings, select_lines
from airfoilmatic.export import to_ansys_txt
from airfoilmatic.mesh import (DEFAULTS, MAX_GOOD_GROWTH, first_cell_height, plan_inflation,
                               plan_mesh, reynolds)
from airfoilmatic.gci import compute_gci
from airfoilmatic.fluent import AIR_DENSITY, AIR_VISCOSITY, freestream, speed_for_reynolds
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
source = st.sidebar.radio(t("source"), ["naca", "file"],
                          format_func=lambda k: t("source_naca") if k == "naca" else t("source_file"))

if source == "naca":
    naca_code = st.sidebar.text_input(t("naca_code"), value="4412", max_chars=5).strip()
    file_prefix = f"domain_naca{naca_code}"
    custom_file = None
else:
    custom_file = st.sidebar.file_uploader(t("upload"), type=["dat", "txt"])
    file_prefix = ("domain_" + re.sub(r"[^A-Za-z0-9_.-]+", "_", custom_file.name.rsplit('.', 1)[0]).strip("_")
                   if custom_file else "domain_custom")

domain_kind = st.sidebar.selectbox(t("domain_type"), [C_GRID, RECT],
                                   format_func=lambda k: t("dom_cgrid") if k == C_GRID else t("dom_rect"))
chord = st.sidebar.number_input(t("chord"), value=1.0, step=0.1, min_value=0.01)

if domain_kind == C_GRID:
    r_inlet = st.sidebar.number_input(t("r_inlet"), value=10.0, step=1.0, min_value=1.0)
    l_wake = st.sidebar.number_input(t("l_wake"), value=20.0, step=1.0, min_value=1.0)
    l_top = l_bottom = r_inlet
else:
    r_inlet = st.sidebar.number_input(t("l_inlet"), value=10.0, step=1.0, min_value=1.0)
    l_wake = st.sidebar.number_input(t("l_wake"), value=20.0, step=1.0, min_value=1.0)
    l_top = st.sidebar.number_input(t("l_top"), value=10.0, step=1.0, min_value=1.0)
    l_bottom = st.sidebar.number_input(t("l_bottom"), value=10.0, step=1.0, min_value=1.0)

st.sidebar.markdown(f"**{t('split_mode')}**", help=t("split_mode_help"))
kept_lines = [k for k in SPLIT_LINES if st.sidebar.checkbox(t(k), value=True, key=f"line_{k}")]
all_lines = len(kept_lines) == len(SPLIT_LINES)

sidebar_download = st.sidebar.empty()
st.sidebar.markdown(ui.note_html(t("beta_warning", stage=APP_STAGE, version=APP_VERSION)), unsafe_allow_html=True)
st.sidebar.markdown(ui.footer_html(L, t("dev_label")), unsafe_allow_html=True)

# ---------------------------------------------------------------- geometry
try:
    if source == "naca":
        if len(naca_code) not in (4, 5) or not naca_code.isdigit():
            st.error(t("err_naca"))
            st.stop()
        airfoil = naca(naca_code, chord)
    else:
        if custom_file is None:
            st.info(t("upload_info"))
            st.stop()
        airfoil = parse_airfoil_file(custom_file.getvalue(), chord, name=custom_file.name)
    airfoil = close_small_te_gap(airfoil)
    split_af = split_at(airfoil, DEFAULT_SPLIT)
except AirfoilError as e:
    st.error(t("err_geometry", msg=te(e)))
    st.stop()

try:
    domain = build_domain(split_af, domain_kind, r_inlet=r_inlet, l_wake=l_wake,
                          l_top=l_top, l_bottom=l_bottom)
except ValueError as e:
    st.error(t("err_domain", msg=te(e)))
    st.stop()

# `domain` keeps every split line (used for sizing plans); `out_domain` is what is
# drawn and exported for the chosen workflow.
out_domain = select_lines(domain, kept_lines)
txt_data = to_ansys_txt(out_domain)
with sidebar_download:
    st.download_button(t("download"), data=txt_data, file_name=f"{file_prefix}.txt",
                       mime="text/plain", use_container_width=True, key="dl_sidebar",
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


def plan_rows(plan):
    rows = []
    for e in plan.edges:
        rows.append({
            t("col_group"): t(e.group),
            t("col_edges"): ", ".join(t(k) for k in e.edges),
            t("col_n"): e.n,
            t("col_bias"): float(f"{e.bias:.6g}"),
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
        st.dataframe(rows, use_container_width=True, hide_index=True, column_order=columns)
    st.markdown(ui.row_cards_html(rows, columns), unsafe_allow_html=True)


def rows_to_csv(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8-sig")  # BOM so Excel shows Turkish characters


tab_geo, tab_mesh, tab_gci = st.tabs([t("tab_geometry"), t("tab_mesh"), t("tab_gci")])

# ================================================================ geometry tab
with tab_geo:
    n_faces = max(1, len(kept_lines))
    st.caption(t("geom_info", split=DEFAULT_SPLIT) if all_lines else (t("geom_info_one") if n_faces == 1 else t("geom_info_partial", n=n_faces)))
    for kind, key in line_warnings(kept_lines):
        st.warning(t("warn_single_line", line=t(key)))
    if domain.blunt_te:
        st.info(t("blunt_info", gap=split_af.te_gap))

    st.subheader(t("zoom_title"))
    fig_zoom = go.Figure()
    for i, c in enumerate([c for c in out_domain.by_kind("split") if c.key != "te_closure"]):
        fig_zoom.add_trace(go.Scatter(x=c.x, y=c.y, mode="lines", name=t("split_lines"), legendgroup="split",
                                      showlegend=i == 0, hovertext=t(c.key), hoverinfo="text",
                                      line=dict(color=PLOT["split"], width=1.5, dash="dash")))
    airfoil_traces(fig_zoom)
    style(fig_zoom, 440, [-0.1 * chord, 1.1 * chord], [-0.5 * chord, 0.5 * chord])
    with st.container(key="plot_zoom"):
        st.plotly_chart(fig_zoom, use_container_width=True, config={"scrollZoom": False})

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
    # Show exactly the domain (+4 %); the figure height follows its aspect ratio.
    xs = np.concatenate([c.x for c in out_domain.curves])
    ys = np.concatenate([c.y for c in out_domain.curves])
    pad = 0.04 * max(np.ptp(xs), np.ptp(ys))
    xr = [xs.min() - pad, xs.max() + pad]
    yr = [ys.min() - pad, ys.max() + pad]
    # The card takes the domain's aspect ratio (plus room for the legend), and the chart stretches
    # to fill it, so a narrow phone gets a short chart instead of a tall one with empty space.
    aspect = (xr[1] - xr[0]) / (yr[1] - yr[0])
    st.markdown(f"<style>.st-key-plot_full{{aspect-ratio:{aspect:.3f} / 1;min-height:300px;max-height:760px}}"
                f".st-key-plot_full [data-testid='stPlotlyChart']{{flex:1 1 auto;min-height:0}}</style>",
                unsafe_allow_html=True)
    style(fig_full, None, xr, yr, fit_domain=True)
    # legend in its own top margin: on a phone it wraps to two rows and must not cover the drawing
    fig_full.update_layout(legend=dict(orientation="h", x=0, y=1.0, yanchor="bottom"), margin=dict(t=64, b=10))
    with st.container(key="plot_full"):
        st.plotly_chart(fig_full, width="stretch", height="stretch", config={"scrollZoom": False})

    st.download_button(t("download"), data=txt_data, file_name=f"{file_prefix}.txt",
                       mime="text/plain", use_container_width=True, key="dl_main",
                       type="primary")

# ================================================================ mesh tab
INFLATION, MAPPED = "inflation", "mapped"
FAR_FIELD_SIZE = 0.5  # global element size for quad-dominant meshes, in chords
# With inflation on both the airfoil and the wake axis, Ansys failed or produced
# degenerate cells at the TE with ~1 mm elements there; ~3 mm (0.003c) worked.
INFL_MIN_TE = 0.003


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
        flow_mode = st.radio(t("flow_input"), ["re", "vel"], horizontal=True,
                             format_func=lambda k: t("flow_re") if k == "re" else t("flow_vel"))
        u_inf = rho = mu = None
        if flow_mode == "re":
            re = st.number_input(t("re"), value=2.0e6, min_value=1.0e3, step=1.0e5, format="%.4e")
        else:
            u_inf = st.number_input(t("velocity"), value=30.0, min_value=0.01)
            rho = st.number_input(t("density"), value=1.225, min_value=1e-6, format="%.4f")
            mu = st.number_input(t("viscosity"), value=1.7894e-5, min_value=1e-9, format="%.4e")
            re = reynolds(u_inf, rho, mu, chord)
            st.caption(f"Re = {short(re)}")
    with c2.container(key="card_method"):
        st.markdown(ui.step_html(2, t("step_method")), unsafe_allow_html=True)
        mesh_mode = st.radio(t("mesh_method"), [INFLATION, MAPPED],
                             format_func=lambda k: t("method_inflation") if k == INFLATION else t("method_mapped"))
        y_plus = st.number_input(t("y_plus"), value=DEFAULTS["y_plus"], min_value=0.05, step=0.5)
    with c3.container(key="card_growth"):
        st.markdown(ui.step_html(3, t("step_growth")), unsafe_allow_html=True)
        if mesh_mode == INFLATION:
            growth = st.number_input(t("growth"), value=1.15, min_value=1.01, max_value=1.5,
                                     step=0.01, format="%.3f", key="g_infl")
            coverage = st.number_input(t("coverage"), value=1.5, min_value=0.5, max_value=5.0, step=0.25)
        else:
            growth = st.number_input(t("growth"), value=DEFAULTS["growth"], min_value=1.01, max_value=1.5,
                                     step=0.01, format="%.3f", key="g_map")
    # Chordwise sizes: full width under the three cards so the inputs are not squeezed.
    with st.expander(t("advanced")):
        st.caption(t("advanced_help"))
        a1, a2, a3, a4 = st.columns(4)
        ds_le = a1.number_input(t("ds_le"), value=DEFAULTS["ds_le"], min_value=1e-5, format="%.4f", step=0.0005)
        ds_split = a2.number_input(t("ds_split"), value=DEFAULTS["ds_split"], min_value=1e-4, format="%.4f",
                                   step=0.001)
        ds_te = a3.number_input(t("ds_te"), value=DEFAULTS["ds_te"], min_value=1e-5, format="%.4f", step=0.0005)
        wake_growth = a4.number_input(t("wake_growth"), value=DEFAULTS["wake_growth"], min_value=1.01,
                                      max_value=1.5, step=0.01, format="%.3f")

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
        ds_te_infl = max(ds_te, INFL_MIN_TE)
        smallest = min(ds_le, ds_te_infl) * chord
        if domain.blunt_te:
            smallest = min(smallest, split_af.te_gap / 4)
        defeature = float(f"{smallest / 50:.0e}")   # well below every specified size
        curv_min = float(f"{smallest / 5:.0e}")     # so curvature sizing never coarsens the edges
        infl_rows = [
            {t("col_setting"): "Inflation Option", t("col_value"): "First Layer Thickness"},
            {t("col_setting"): "First Layer Height", t("col_value"): m_mm(infl.first_layer)},
            {t("col_setting"): "Maximum Layers", t("col_value"): f"{infl.layers}"},
            {t("col_setting"): "Growth Rate", t("col_value"): f"{infl.growth:.3g}"},
            {t("col_setting"): t("infl_total"), t("col_value"): f"{m_mm(infl.total)}  (≈ {infl.total / infl.delta_turb:.2g} δ)"},
            {t("col_setting"): t("infl_last"), t("col_value"): m_mm(infl.last_layer)},
            {t("col_setting"): t("glob_size"), t("col_value"): m_mm(FAR_FIELD_SIZE * chord)},
            {t("col_setting"): t("glob_growth"), t("col_value"): "1.15"},
            {t("col_setting"): "Defeature Size (Mesh → Sizing)", t("col_value"): m_mm(defeature)},
            {t("col_setting"): "Curvature Min Size (Mesh → Sizing)", t("col_value"): m_mm(curv_min)},
        ]
        st.markdown(ui.table_html(infl_rows), unsafe_allow_html=True)
        st.caption(t("infl_note"))
        if domain.blunt_te:
            st.warning(t("warn_blunt_infl"))

        # Edge Sizing for the airfoil and wake-axis edges (same geometric plan as mapped mode)
        st.subheader(t("infl_edges_title") if "wake_axis" in kept_lines else t("infl_edges_title_af"))
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
            st.caption(t("infl_edges_note"))
        except (ValueError, OverflowError) as e:
            st.error(te(e))
        if infl.growth > MAX_GOOD_GROWTH:
            st.warning(t("warn_growth", g=infl.growth, lim=MAX_GOOD_GROWTH))
        with st.expander(t("howto_title")):
            st.markdown(t("howto_infl"))

    if plan is not None:
        if not all_lines:
            st.warning(t("warn_mapped_lines"))
        st.markdown(ui.cards_html([
            (t("m_dy1"), f"{plan.dy1 * 1000:.4g} mm", f"Re = {short(re)}", True),
            (t("m_nbl"), f"{plan.n_bl}", "", False),
            (t("m_cells"), f"{plan.cells:,}", "", False),
        ]), unsafe_allow_html=True)
        st.markdown(t("m_counts", n_normal=plan.n_normal, n_front=plan.n_front,
                      n_rear=plan.n_rear, n_wake=plan.n_wake))
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
            st.markdown(t("howto"))

    st.caption(t("delta_note", lam=m_mm((infl or plan).delta_lam) if (infl or plan) else "-"))

    # ---- mesh quality check
    with st.expander(t("quality_title")):
        st.caption(t("quality_help"))
        qc = st.columns(4)
        sk_max = qc[0].number_input(t("q_sk_max"), value=None, min_value=0.0, max_value=1.0, format="%.4f",
                                    placeholder="0.76")
        sk_avg = qc[1].number_input(t("q_sk_avg"), value=None, min_value=0.0, max_value=1.0, format="%.4f",
                                    placeholder="0.016")
        oq_min = qc[2].number_input(t("q_oq_min"), value=None, min_value=0.0, max_value=1.0, format="%.4f",
                                    placeholder="0.027")
        oq_avg = qc[3].number_input(t("q_oq_avg"), value=None, min_value=0.0, max_value=1.0, format="%.4f",
                                    placeholder="0.995")
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
        dy_ref = infl.first_layer if infl is not None else (plan.dy1 if plan is not None else None)
        if dy_ref:
            st.markdown(t("q_ar_expected",
                          ar_le=expected_wall_aspect_ratio(dy_ref, ds_le * chord),
                          ar_mid=expected_wall_aspect_ratio(dy_ref, ds_split * chord)))
        st.markdown(t("q_explain"))

    # ---- y+ correction
    with st.expander(t("yplus_fix_title")):
        st.caption(t("yplus_fix_help"))
        used = st.number_input(t("yplus_used_dy"), value=float(f"{first_cell_height(re, y_plus, chord):.4e}"),
                               min_value=1e-9, format="%.4e")
        seen = st.number_input(t("yplus_seen"), value=None, min_value=1e-3, format="%.3f")
        if seen:
            st.success(t("yplus_fix_result", dy=m_mm(used * y_plus / seen), target=y_plus))

    # ---- Fluent setup helper
    with st.expander(t("fluent_title")):
        rho_f = rho if rho is not None else AIR_DENSITY
        mu_f = mu if mu is not None else AIR_VISCOSITY
        u_default = u_inf if u_inf is not None else speed_for_reynolds(re, chord, rho_f, mu_f)
        fc = st.columns(2)
        aoa = fc[0].number_input(t("aoa"), value=4.25, step=0.25, format="%.2f")
        u_fl = fc[1].number_input(t("fl_speed"), value=float(f"{u_default:.4g}"), min_value=0.001,
                                  format="%.3f", help=t("fl_speed_help"))
        try:
            fs = freestream(aoa, u_fl, chord, rho_f, mu_f)
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
                {t("col_setting"): t("fl_ref_len"), t("col_value"): f"{chord:g} m"},
                {t("col_setting"): t("fl_ref_area"), t("col_value"): f"{chord:g} m² (c × 1 m)"},
                {t("col_setting"): t("fl_re_mach"), t("col_value"): f"Re = {fs.reynolds:.4e},  M = {fs.mach:.3f}"},
            ]
            st.markdown(ui.table_html(rows_f), unsafe_allow_html=True)
            if abs(fs.reynolds - re) > 0.01 * re:
                st.warning(t("fl_re_mismatch", re_fl=fs.reynolds, re_mesh=re))
            if fs.mach > 0.3:
                st.warning(t("fl_mach_warn", m=fs.mach))
        st.caption(t("fluent_note"))

# ================================================================ GCI tab
LEVELS = ("fine", "medium", "coarse")

with tab_gci:
    st.markdown(t("gci_intro"))
    st.subheader(t("results_title"))
    st.caption(t("results_help"))
    inputs = {"N": [], "Cl": [], "Cd": []}
    for name in LEVELS:
        cols = st.columns([1, 2, 2, 2])
        cols[0].markdown(f"**{t(name)}**")
        inputs["N"].append(cols[1].number_input(t("col_cells"), min_value=1, step=1, value=None,
                                                placeholder=t("ph_cells"), key=f"gci_n_{name}"))
        inputs["Cl"].append(cols[2].number_input("Cl", value=None, format="%.6f", step=1e-4,
                                                 placeholder=t("ph_value"), key=f"gci_cl_{name}"))
        inputs["Cd"].append(cols[3].number_input("Cd", value=None, format="%.6f", step=1e-5,
                                                 placeholder=t("ph_value_cd"), key=f"gci_cd_{name}"))

    n_vals = inputs["N"]
    st.subheader(t("gci_title"))
    if any(v is None for v in n_vals) or all(any(v is None for v in inputs[q]) for q in ("Cl", "Cd")):
        st.info(t("gci_wait"))
    results = {}
    for qty in ("Cl", "Cd"):
        vals = inputs[qty]
        if any(v is None for v in vals + n_vals):
            continue
        try:
            g = compute_gci(n_vals[0], n_vals[1], n_vals[2], vals[0], vals[1], vals[2])
        except (ValueError, ZeroDivisionError, OverflowError) as e:
            st.error(t("gci_err", name=qty, msg=te(e)))
            results[qty] = (vals, None)
            continue
        results[qty] = (vals, g)
        st.markdown(f"**{qty}**")
        cols = st.columns(4)
        cols[0].metric(t("gci_p"), f"{g.p:.3f}")
        cols[1].metric(t("gci_ext"), f"{g.phi_ext:.5g}")
        cols[2].metric(t("gci_fine"), f"{100 * g.gci_fine:.3f} %")
        cols[3].metric(t("gci_asym"), f"{g.asymptotic:.3f}")
        if not g.diverging:
            st.markdown(t("gci_report", name=qty, phi=vals[0], unc=abs(vals[0]) * g.gci_fine,
                          gci=100 * g.gci_fine))
        if g.oscillatory:
            st.warning(t("gci_osc"))
        elif g.diverging:
            st.warning(t("gci_div"))
        elif not 0.8 <= g.asymptotic <= 1.2:
            st.warning(t("gci_asym_warn"))
        if min(g.r21, g.r32) < 1.3:
            st.warning(t("gci_r_warn", r=min(g.r21, g.r32)))

    # ---- convergence plot
    if results:
        h = [1.0 / math.sqrt(n) for n in n_vals]
        qtys = list(results)
        fig = make_subplots(rows=1, cols=len(qtys), subplot_titles=qtys)
        for j, qty in enumerate(qtys, start=1):
            vals, g = results[qty]
            fig.add_trace(go.Scatter(x=h, y=vals, mode="markers+lines", name=t("plot_grids"),
                                     marker=dict(size=10, color=PLOT["line"]), line=dict(color=PLOT["line"]),
                                     showlegend=j == 1, legendgroup="grids",
                                     error_y=dict(type="data", array=[abs(vals[0]) * g.gci_fine, 0, 0],
                                                  visible=True) if g and not g.diverging else None), row=1, col=j)
            if g is not None and not g.diverging:
                hh = np.linspace(0, max(h), 60)
                c_fit = (vals[0] - g.phi_ext) / h[0] ** g.p
                fig.add_trace(go.Scatter(x=hh, y=g.phi_ext + c_fit * hh ** g.p, mode="lines",
                                         name=t("plot_fit"), line=dict(color=PLOT["fit"], dash="dash"),
                                         showlegend=j == 1, legendgroup="fit"), row=1, col=j)
                fig.add_trace(go.Scatter(x=[0], y=[g.phi_ext], mode="markers", name=t("plot_ext"),
                                         marker=dict(symbol="star", size=14, color=PLOT["ext"]),
                                         showlegend=j == 1, legendgroup="ext"), row=1, col=j)
            fig.update_xaxes(title_text=t("plot_h"), range=[-0.05 * max(h), 1.08 * max(h)], row=1, col=j)
        fig.update_layout(height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(family=ui.FONT), legend=dict(orientation="h", y=-0.25))
        fig.update_xaxes(gridcolor=PLOT["grid"])
        fig.update_yaxes(gridcolor=PLOT["grid"])
        with st.container(key="plot_gci"):
            st.plotly_chart(fig, use_container_width=True,
                            config={"toImageButtonOptions": {"format": "png", "filename": f"{file_prefix}_gci",
                                                             "scale": 3}})
        st.caption(t("plot_note"))

    # ---- optional suggested grid family
    with st.expander(t("family_title")):
        ratio = st.select_slider(t("refine_ratio"), options=[1.3, math.sqrt(2), 1.5, 2.0], value=math.sqrt(2),
                                 format_func=lambda r: "√2 ≈ 1.414" if abs(r - math.sqrt(2)) < 1e-9 else f"{r:g}")
        factors = {"fine": ratio, "medium": 1.0, "coarse": 1.0 / ratio}
        try:
            if mesh_mode == INFLATION:
                fam = {n: plan_inflation(re, chord, y_plus=y_plus, growth=growth, coverage=coverage, refine=k)
                       for n, k in factors.items()}
                fam_rows = [{t("level"): t(n), "First Layer Height": m_mm(fam[n].first_layer),
                             "Growth Rate": round(fam[n].growth, 4), "Maximum Layers": fam[n].layers,
                             t("fam_sizes"): f"÷ {factors[n]:.3g}" if n != "medium" else "× 1"}
                            for n in LEVELS]
                wide_table(fam_rows, "family_infl")
                st.caption(t("family_note_infl"))
            else:
                fam = {n: plan_mesh(domain, split_af, re, refine=k, **sizing) for n, k in factors.items()}
                fam_rows = [{t("level"): t(n), t("m_cells"): f"{fam[n].cells:,}",
                             t("m_dy1"): m_mm(fam[n].dy1), t("fam_n_normal"): fam[n].n_normal, t("fam_n_front"): fam[n].n_front,
                             t("fam_n_rear"): fam[n].n_rear, t("fam_n_wake"): fam[n].n_wake}
                            for n in LEVELS]
                wide_table(fam_rows, "family_mapped")
                st.caption(t("family_note"))
                dl = st.columns(3)
                for col, n in zip(dl, LEVELS):
                    col.download_button(t("download_level", level=t(n)), data=rows_to_csv(plan_rows(fam[n])),
                                        file_name=f"{file_prefix}_edge_sizing_{n}.csv", mime="text/csv",
                                        use_container_width=True, key=f"dl_{n}")
        except (ValueError, OverflowError) as e:
            st.error(te(e))
