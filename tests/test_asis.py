"""Outline used as drawn ("Dosyadaki çizgiyi olduğu gibi kullan"): vortex generators,
kinked sections and other outlines whose surfaces do not advance in x."""
import re
import string

import numpy as np
import pytest
from streamlit.runtime.memory_media_file_storage import MemoryMediaFileStorage

from airfoilmatic.export import to_ansys_txt
from airfoilmatic.geometry import (AirfoilError, as_is_split, close_small_te_gap, naca,
                                   parse_airfoil_file, parse_outline_as_is)
from airfoilmatic.i18n import ERRORS_TR, STRINGS, tr_error
from airfoilmatic.mesh import plan_mesh, plan_wake_axis
from airfoilmatic.topology import C_GRID, RECT, Curve, Domain, build_domain_as_is
from test_app import tr, upload, widget
from test_database_findings import crossings

X_VG, H_VG, W_VG = 0.2, 0.01, 0.002


def vg_loop(lean=0.0, blunt=False):
    """NACA 0012 Selig loop (TE -> upper -> LE -> lower -> TE) with a rectangular fin on the
    upper surface at x = 0.2c: walls 0.01c high, 0.002c apart. ``lean`` < 0 tilts the fin
    forward (its top is ahead of its foot)."""
    a = naca("0012", n_points=81, blunt_te=blunt)
    top = lambda x: float(np.interp(x, a.xu, a.yu))  # noqa: E731
    x1 = X_VG + W_VG
    up = ([(x, y) for x, y in zip(a.xu, a.yu) if x < X_VG]
          + [(X_VG, top(X_VG)), (X_VG + lean, top(X_VG) + H_VG), (x1 + lean, top(x1) + H_VG), (x1, top(x1))]
          + [(x, y) for x, y in zip(a.xu, a.yu) if x > x1])
    return np.vstack([np.array(up)[::-1], np.column_stack([a.xl, a.yl])[1:]])


def text(loop):
    return "\n".join(f"{p:.12f} {q:.12f}" for p, q in loop).encode()


def as_loop(af):
    """The outline back in Selig order (TE -> upper -> LE -> lower -> TE)."""
    return np.vstack([np.column_stack([af.xu, af.yu])[::-1], np.column_stack([af.xl, af.yl])[1:]])


def domain_for(af, kind):
    return build_domain_as_is(as_is_split(close_small_te_gap(af)), kind,
                              r_inlet=10, l_wake=20, l_top=10, l_bottom=10)


def fin_top(lean):
    return np.array([[X_VG + lean, 0.0], [X_VG + W_VG + lean, 0.0]])


# ------------------------------------------------------------------ the normal reader loses the fin

@pytest.mark.parametrize("lean", [0.0, -0.004], ids=["vertical", "forward"])
def test_normal_reader_loses_the_fin(lean):
    loop = vg_loop(lean)
    try:
        af = parse_airfoil_file(text(loop))
    except AirfoilError:
        return   # rejected: lost as well
    pts = np.vstack([np.column_stack([af.xu, af.yu]), np.column_stack([af.xl, af.yl])])
    kept = [np.min(np.hypot(*(pts - p).T)) < 1e-9 for p in loop]
    assert not all(kept)
    assert len(pts) < 2 * len(loop) - 2


@pytest.mark.parametrize("lean", [0.0, -0.004], ids=["vertical", "forward"])
def test_as_is_keeps_every_point(lean):
    loop = vg_loop(lean)
    af = parse_outline_as_is(text(loop))
    assert af.xu[0] == af.xl[0] == 0.0 and af.yu[0] == af.yl[0] == 0.0
    assert np.allclose(as_loop(af), loop, rtol=0, atol=1e-9)
    assert np.max(af.yu) > 0.05 + 0.009     # the fin is on the upper path


@pytest.mark.parametrize("lean", [0.0, -0.004], ids=["vertical", "forward"])
@pytest.mark.parametrize("kind", [C_GRID, RECT])
def test_exported_domain_has_no_crossings(lean, kind):
    d = domain_for(parse_outline_as_is(text(vg_loop(lean))), kind)
    keys = [c.key for c in d.curves]
    assert keys[:2] == ["af_upper", "af_lower"]
    assert {"front_axis", "wake_axis"} <= set(keys)
    assert not {"split_up", "split_low", "te_up", "te_low"} & set(keys)
    assert crossings(d) == 0
    assert crossings(txt_domain(to_ansys_txt(d))) == 0
    assert all(k in STRINGS for k in keys)


def txt_domain(txt):
    groups = {}
    for line in txt.splitlines():
        g, _, x, y, _ = line.split()
        groups.setdefault(int(g), []).append((float(x), float(y)))
    return Domain("txt", [Curve(str(g), "", np.array(p)[:, 0], np.array(p)[:, 1]) for g, p in groups.items()])


def test_scaled_and_shifted_file_is_normalised():
    loop = vg_loop()
    af = parse_outline_as_is(text(loop * 250.0 + [40.0, -7.0]), chord=0.5)
    assert np.allclose(as_loop(af), loop * 0.5, atol=1e-9)


def test_lednicer_file_gives_the_same_outline():
    loop = vg_loop()
    le = int(np.argmin(loop[:, 0]))
    up, lo = loop[: le + 1][::-1], loop[le:]
    body = "\n".join(f"{p:.12f} {q:.12f}" for p, q in np.vstack([up, lo]))
    data = f"VG test\n{len(up)}. {len(lo)}.\n{body}".encode()
    assert np.allclose(as_loop(parse_outline_as_is(data)), loop, atol=1e-9)


def test_mirrored_file():
    loop = vg_loop(-0.004)
    flipped = loop * [-1.0, 1.0] + [3.0, 0.0]
    af = parse_outline_as_is(text(flipped), mirror=True)
    assert np.allclose(as_loop(af), loop, atol=1e-9)
    assert crossings(domain_for(af, C_GRID)) == 0


def test_lower_surface_fin_and_clockwise_file():
    """A fin on the lower side, written clockwise (TE -> lower -> LE -> upper)."""
    loop = vg_loop() * [1.0, -1.0]
    af = parse_outline_as_is(text(loop[::-1]))
    assert np.min(af.yl) < -0.059 and np.max(af.yu) < 0.061
    assert crossings(domain_for(af, C_GRID)) == 0


# ------------------------------------------------------------------ blunt trailing edge

def test_blunt_base_drawn_as_points_becomes_the_closure():
    """A flat base drawn as part of the loop: the points at the largest x share the TE; the two
    outermost are the closure ends and the base points between them go (they lie on it)."""
    loop = vg_loop(blunt=True)
    top, bottom = loop[0], loop[-1]
    base = np.column_stack([np.full(5, 1.0), np.linspace(bottom[1], top[1], 7)[1:-1]])
    af = parse_outline_as_is(text(np.vstack([loop, base, loop[:1]])))
    assert np.allclose(as_loop(af), loop, atol=1e-9)
    assert af.te_gap == pytest.approx(top[1] - bottom[1], abs=1e-9)
    d = domain_for(af, C_GRID)
    assert d.blunt_te and "te_closure" in [c.key for c in d.curves]
    wake = d.get("wake_axis")
    assert wake.x[0] == pytest.approx(1.0) and wake.y[0] == pytest.approx(0.0, abs=1e-12)
    assert crossings(d) == 0


def test_open_blunt_file_is_closed_between_its_ends():
    loop = vg_loop(blunt=True)
    af = parse_outline_as_is(text(loop))
    assert np.allclose(as_loop(af), loop, atol=1e-9)
    d = domain_for(af, RECT)
    assert d.blunt_te and crossings(d) == 0
    assert plan_wake_axis(d).n > 1


def test_tiny_te_gap_is_snapped():
    loop = vg_loop()
    loop[0, 1] += 2e-5
    loop[-1, 1] -= 2e-5
    af = close_small_te_gap(parse_outline_as_is(text(loop)))
    assert af.te_gap == 0.0
    assert not domain_for(af, C_GRID).blunt_te


# ------------------------------------------------------------------ rejected outlines

def test_self_intersecting_loop_is_rejected():
    loop = vg_loop()
    a, b = int(np.argmin(np.abs(loop[:20, 0] - 0.6))), int(np.argmin(np.abs(loop[:40, 0] - 0.4)))
    loop[min(a, b): max(a, b), 1] = -0.2     # part of the upper side pulled below the lower side
    with pytest.raises(AirfoilError, match="crosses itself") as e:
        parse_outline_as_is(text(loop))
    assert tr_error(e.value, "tr") != str(e.value)


def test_too_few_points_are_rejected():
    with pytest.raises(AirfoilError) as e:
        parse_outline_as_is(b"1 0\n0.5 0.05\n0 0\n0.5 -0.05\n1 0\n")
    assert tr_error(e.value, "tr") != str(e.value)


def test_outline_across_the_wake_axis_is_rejected():
    """A hooked, slanted base: the upper path dips below the middle of the closure, behind it."""
    up = [(0, 0), (0.1, 0.05), (0.5, 0.06), (0.9, 0.02), (1.0, -0.04)]
    lo = [(0, 0), (0.1, -0.05), (0.5, -0.06), (0.9, -0.02), (0.96, -0.02)]
    with pytest.raises(AirfoilError, match="wake axis") as e:
        parse_outline_as_is(text(np.vstack([up[::-1], lo[1:]])))
    assert tr_error(e.value, "tr") != str(e.value)


def test_new_strings_have_matching_placeholders():
    fields = lambda s: sorted(f for _, f, _, _ in string.Formatter().parse(s) if f)  # noqa: E731
    for key in ("as_is", "as_is_help", "asis_geom_info", "asis_no_mapped", "asis_edges_note", "af_upper", "af_lower"):
        assert fields(STRINGS[key]["tr"]) == fields(STRINGS[key]["en"]), key
    for msg in ERRORS_TR:
        assert not re.search(r"\{", msg)


def test_normal_mode_plan_is_unchanged_by_the_wake_helper():
    from airfoilmatic.geometry import split_at
    from airfoilmatic.topology import build_domain
    s = split_at(naca("4412"))
    d = build_domain(s)
    wake = next(e for e in plan_mesh(d, s, 2e6, max_wake_cell=0.5).edges if e.group == "g_wake")
    alone = plan_wake_axis(d, max_wake_cell=0.5)
    assert (alone.n, alone.ratio, alone.small_end) == (wake.n, wake.ratio, wake.small_end)


# ------------------------------------------------------------------ the app

@pytest.fixture
def downloads(monkeypatch):
    got = []
    load = MemoryMediaFileStorage.load_and_get_id

    def spy(self, data, mimetype, kind, filename=None):
        got.append((filename, data))
        return load(self, data, mimetype, kind, filename)

    monkeypatch.setattr(MemoryMediaFileStorage, "load_and_get_id", spy)
    return got


@pytest.mark.parametrize("lang", ["tr", "en"])
def test_app_upload_vg_file_as_drawn(lang, downloads):
    at = upload("vg.dat", text(vg_loop(-0.004)), lang)
    widget(at, "radio", tr("mesh_method", lang)).set_value("mapped")   # chosen before ticking the box
    at = at.run()
    widget(at, "checkbox", tr("as_is", lang)).check()
    at = at.run()
    assert not at.exception and not at.error
    radio = widget(at, "radio", tr("mesh_method", lang))
    assert radio.disabled and radio.value == "inflation"
    assert tr("asis_no_mapped", lang) in [c.value for c in at.caption]
    assert any(tr("asis_edges_note", lang).split(":")[0] in i.value for i in at.info)
    txts = [d for name, d in downloads if name and name.endswith("_CGrid.txt")]
    assert txts
    exported = txts[-1].decode() if isinstance(txts[-1], bytes) else txts[-1]
    d = txt_domain(exported)
    assert len(d.curves) == 8 and crossings(d) == 0


def test_app_checkbox_only_for_uploads():
    from test_app import start
    at = start()
    assert tr("as_is", "tr") not in [c.label for c in at.checkbox]
