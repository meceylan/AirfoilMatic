"""Structured C-grid mesh built by the app itself, written as a Fluent mesh file (.msh).

The six blocks and every edge distribution come from ``mesh.plan_mesh`` (the Edge Sizing
table): the same Number of Divisions and bias that Ansys Meshing would use. The inside of
each block is filled by transfinite interpolation (Coons patch) whose blending follows the
spacing of the block edges, so the first cell at the wall keeps the planned height. On the two
front blocks the grid lines then start along the wall normal (``wall_orthogonal``).

Fluent face convention (checked on a .msh file written by Ansys Meshing 2024 R2): a face is
``n0 n1 c0 c1``; c0 lies to the left of n0 -> n1 and c1 to the right; on a boundary c1 = 0.
"""
from dataclasses import dataclass

import numpy as np

from .topology import C_GRID

# Fluent zone ids and boundary-condition codes (Fluent User's Guide, case file format).
CELL_ZONE, INTERIOR, WALL, INLET, OUTLET = 2, 3, 4, 5, 6
BC_CODE = {INTERIOR: 2, WALL: 3, INLET: 10, OUTLET: 5}      # interior, wall, velocity-inlet, pressure-outlet
ZONE_NAME = {CELL_ZONE: ("fluid", "fluid"), INTERIOR: ("interior", "interior-fluid"), WALL: ("wall", "wall"),
             INLET: ("velocity-inlet", "inlet"), OUTLET: ("pressure-outlet", "outlet")}


@dataclass
class BlockMesh:
    nodes: np.ndarray        # (n_nodes, 2)
    cells: np.ndarray        # (n_cells, 4) node indices, counter-clockwise
    faces: np.ndarray        # (n_faces, 4): n0, n1, c0, c1 (0-based; c1 = -1 on a boundary)
    face_zone: np.ndarray    # (n_faces,) zone id of each face

    @property
    def n_cells(self):
        return len(self.cells)


# ---------------------------------------------------------------- edge distributions
def _fractions(n, ratio):
    """n + 1 fractions 0..1 of a geometric distribution; ``ratio`` = second cell / first cell."""
    k = np.arange(n + 1, dtype=float)
    if abs(ratio - 1.0) < 1e-12:
        t = k / n
    else:
        t = (ratio ** k - 1.0) / (ratio ** n - 1.0)
    t[0], t[-1] = 0.0, 1.0
    return t


def _along(x, y, t):
    """Points at arc-length fractions ``t`` along the polyline (x, y); ends kept exactly."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    p = np.column_stack([np.interp(t * s[-1], s, x), np.interp(t * s[-1], s, y)])
    p[0], p[-1] = (x[0], y[0]), (x[-1], y[-1])
    return p


def _line(p0, p1, t):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    p = p0 + t[:, None] * (p1 - p0)
    p[0], p[-1] = p0, p1
    return p


def _arc(center, radius, p0, p1, n):
    """Uniform arc from p0 to p1 around ``center`` (the shorter way); ends kept exactly."""
    a0 = np.arctan2(p0[1] - center[1], p0[0] - center[0])
    a1 = np.arctan2(p1[1] - center[1], p1[0] - center[0])
    while a1 - a0 > np.pi:      # arctan2 jumps at ±pi (the inlet point sits there)
        a1 -= 2 * np.pi
    while a1 - a0 < -np.pi:
        a1 += 2 * np.pi
    th = np.linspace(a0, a1, n + 1)
    p = np.column_stack([center[0] + radius * np.cos(th), center[1] + radius * np.sin(th)])
    p[0], p[-1] = p0, p1
    return p


# ---------------------------------------------------------------- transfinite interpolation
def _arc_fraction(p):
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(p, axis=0).T))])
    return s / s[-1]


def tfi(bottom, top, left, right):
    """Nodes (ni+1, nj+1, 2) of a four-sided block. bottom/top run along i (left -> right),
    left/right along j (bottom -> top); the corners must coincide. The blending parameters
    follow the edge spacing (u from bottom/top, v from left/right), so clustered edges give
    clustered interior lines."""
    B, T, L, R = (np.asarray(a, float) for a in (bottom, top, left, right))
    uB, uT = _arc_fraction(B)[:, None], _arc_fraction(T)[:, None]
    vL, vR = _arc_fraction(L)[None, :], _arc_fraction(R)[None, :]
    du, dv = uT - uB, vR - vL
    den = 1.0 - du * dv
    u = (uB + vL * du) / den
    v = (vL + uB * dv) / den
    u3, v3 = u[..., None], v[..., None]
    P = ((1 - v3) * B[:, None, :] + v3 * T[:, None, :] + (1 - u3) * L[None, :, :] + u3 * R[None, :, :]
         - ((1 - u3) * (1 - v3) * B[0] + u3 * (1 - v3) * B[-1] + (1 - u3) * v3 * T[0] + u3 * v3 * T[-1]))
    P[:, 0], P[:, -1], P[0, :], P[-1, :] = B, T, L, R     # edges exactly as given (shared nodes)
    return P


# Wall-orthogonal start of the grid lines on the front blocks (leading edge -> split line). Plain
# TFI let the lines leave the concave lower surface behind the nose of strongly cambered sections
# almost along the wall (S9104: skewness 0.90, orthogonal quality 0.05; E377: 0.97). Lengths in
# chords: the lines start along the wall normal and join the interpolated line within BLEND
# (exponential weight, rate DECAY; a slower blend left skewness ~0.85 where the lines bend in front
# of the nose); within LE_FADE / SPLIT_FADE of wall length from the side edges (kept as given) the
# start direction turns into the edge's direction.
BLEND = 0.5
DECAY = 5.0
LE_FADE = 0.005
SPLIT_FADE = 0.05


def wall_orthogonal(P, chord, blend=BLEND, fades=None):
    """Block nodes ``P`` (from ``tfi``, wall at j = 0) with each line i starting along the wall
    normal: the node at arc length s from the wall moves towards wall + s * normal with the weight
    (exp(-DECAY x) - exp(-DECAY)) / (1 - exp(-DECAY)), x = s / blend. Near both ends the normal
    turns into the side edge's direction. Wall, top and side edges are kept exactly (shared nodes)."""
    P = np.asarray(P, float)
    B = P[:, 0]
    t = np.gradient(B, axis=0)
    t /= np.linalg.norm(t, axis=1)[:, None]
    n = np.column_stack([-t[:, 1], t[:, 0]])
    if np.mean(np.sum(n * (P[:, 1] - B), 1)) < 0:      # point into the block
        n = -n
    # near each end the direction turns into that of the side edge (which stays as given)
    sw = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(B, axis=0), axis=1))])
    fades = (LE_FADE, SPLIT_FADE) if fades is None else fades
    for end, dist, fade in ((0, sw, fades[0]), (-1, sw[-1] - sw, fades[1])):
        e = P[end, 1] - P[end, 0]
        # A normal leaning past the side edge (away from the block) would run towards it: at a
        # cambered LE (NACA 9940) the lines crossed the front axis. Such a node starts along the
        # edge instead (S9104, rising lower surface before the split line: 0.79 -> 0.64 skewness
        # with this rule on the whole wall rather than near the edge only).
        e_u = e / np.linalg.norm(e)
        inward = B[1] - B[0] if end == 0 else B[-2] - B[-1]
        side = np.sign(e_u[0] * inward[1] - e_u[1] * inward[0])
        n[np.sign(e_u[0] * n[:, 1] - e_u[1] * n[:, 0]) == -side] = e_u
        g = np.clip(1.0 - dist / (fade * chord), 0.0, 1.0)
        g = (g * g * (3.0 - 2.0 * g))[:, None]
        n = (1.0 - g) * n + g * e / np.linalg.norm(e)
        n /= np.linalg.norm(n, axis=1)[:, None]
    s = np.concatenate([np.zeros((len(B), 1)), np.cumsum(np.linalg.norm(np.diff(P, axis=1), axis=2), 1)], 1)
    x = np.clip(s / (blend * chord), 0.0, 1.0)
    w = (np.exp(-DECAY * x) - np.exp(-DECAY)) / (1.0 - np.exp(-DECAY))
    out = P + w[..., None] * (B[:, None, :] + n[:, None, :] * s[..., None] - P)
    out[0], out[-1], out[:, 0], out[:, -1] = P[0], P[-1], P[:, 0], P[:, -1]
    return out


# ---------------------------------------------------------------- C-grid blocks
def _edge(plan, group, key=None):
    for e in plan.edges:
        if e.group == group and (key is None or key in e.edges):
            return e
    raise KeyError((group, key))


def _from(e, small_first):
    """Fractions of edge sizing ``e`` with its first cell at the start of the edge
    (``small_first``) or at its end."""
    t = _fractions(e.n, e.ratio)
    return t if small_first else (1.0 - t[::-1])


def build_cgrid(domain, af, plan, orthogonal=True):
    """Mapped C-grid of ``domain`` (``topology.build_domain``, all six split lines) with the
    edge distributions of ``plan`` (``mesh.plan_mesh``). ``orthogonal=False`` gives the plain TFI
    mesh of the files tried in Fluent before 2026-11-27 (no ``wall_orthogonal`` start)."""
    if domain.kind != C_GRID:
        raise ValueError("The mesh file is only available for the C-grid domain")
    d = domain
    N = plan.n_normal
    le = np.array(af.le)
    su, sl = np.array(af.split_upper), np.array(af.split_lower)
    tu, tl = np.array(af.te_upper), np.array(af.te_lower)
    wake = d.get("wake_axis")
    tm = np.array([wake.x[0], wake.y[0]])
    if not d.blunt_te:
        # Sharp TE: the two surfaces end a round-off apart; one node, or a slit opens there.
        tu = tl = tm
    y_top, y_bot, x_exit = d.y_top, -d.y_bottom, d.x_exit
    front_axis = d.get("front_axis")
    p_in = np.array([front_axis.x[0], front_axis.y[0]])
    atu, atl = np.array([su[0], y_top]), np.array([sl[0], y_bot])
    ttu, ttl = np.array([tu[0], y_top]), np.array([tl[0], y_bot])
    exu, exl, exm = np.array([x_exit, y_top]), np.array([x_exit, y_bot]), np.array([x_exit, tm[1]])

    front, rear, wk = _edge(plan, "g_af_front"), _edge(plan, "g_af_rear"), _edge(plan, "g_wake")
    t_front = _from(front, front.small_end == "end_le")
    t_rear = _from(rear, rear.small_end == "end_split")          # split -> TE
    t_wake = _from(wk, True)                                     # TE -> outlet
    t_arc = np.linspace(0.0, 1.0, front.n + 1)

    def normal(key, p0, p1):
        e = _edge(plan, "g_normal", key)
        return _line(p0, p1, _from(e, True))

    def outlet(key, p0, p1):
        e = _edge(plan, "g_outlet", key)
        return _line(p0, p1, _from(e, True))

    e_axis = normal("front_axis", le, p_in)
    chord = float(np.hypot(*(tm - le)))
    centre = np.array([d.x_split, 0.0])
    blocks, wall_edges, outlet_edges = [], [], []
    for side, sgn in (("upper", 1), ("lower", -1)):
        f_poly = af.upper_front if side == "upper" else af.lower_front
        r_poly = af.upper_rear if side == "upper" else af.lower_rear
        sp, te, at, tt, ex = (su, tu, atu, ttu, exu) if side == "upper" else (sl, tl, atl, ttl, exl)
        e_af_f = _along(*f_poly, t_front)
        e_af_r = _along(*r_poly, t_rear)
        e_af_r[-1] = te
        e_split = normal("split_up" if side == "upper" else "split_low", sp, at)
        e_te = normal("te_up" if side == "upper" else "te_low", te, tt)
        e_arc = _arc(centre, d.y_top, p_in, at, front.n)
        e_top_mid = _line(at, tt, t_rear)
        e_top_wake = _line(tt, ex, t_wake)
        e_wake = _line(tm, exm, t_wake)
        if not d.blunt_te:
            e_wake_left = e_te
            e_out = outlet("outlet_up" if side == "upper" else "outlet_low", exm, ex)
        else:   # blunt TE: half of the closure below the vertical TE line
            closure = _edge(plan, "g_te_closure")
            n_half = plan.n_closure // 2
            t_half = _fractions(n_half, closure.ratio)          # small at the corner
            e_close = _line(tm, te, 1.0 - t_half[::-1])
            wall_edges.append(e_close)
            e_wake_left = np.vstack([e_close, e_te[1:]])
            # The outlet copies the spacing at the TE (base rows, then the shear layer from the TE
            # corner): with the table's single bias from the axis the rows crossed the wake and
            # the cells at the outlet were badly distorted (orthogonal quality ~0).
            e_out = np.column_stack([np.full(len(e_wake_left), x_exit), e_wake_left[:, 1]])
            e_out[0], e_out[-1] = exm, ex
        front_block = tfi(e_af_f, e_arc, e_axis, e_split)
        blocks += [wall_orthogonal(front_block, chord) if orthogonal else front_block,
                   tfi(e_af_r, e_top_mid, e_split, e_te),
                   tfi(e_wake, e_top_wake, e_wake_left, e_out)]
        wall_edges += [e_af_f, e_af_r]
        outlet_edges.append(e_out)
        del sgn
    return _assemble(blocks, wall_edges, outlet_edges)


# ---------------------------------------------------------------- assembly into cells and faces
def _assemble(blocks, wall_edges, outlet_edges):
    index, nodes = {}, []

    def node_id(p):
        k = (float(p[0]), float(p[1]))
        i = index.get(k)
        if i is None:
            i = index[k] = len(nodes)
            nodes.append(k)
        return i

    cells = []
    for P in blocks:
        ids = np.array([[node_id(P[i, j]) for j in range(P.shape[1])] for i in range(P.shape[0])])
        q = np.stack([ids[:-1, :-1], ids[1:, :-1], ids[1:, 1:], ids[:-1, 1:]], axis=-1).reshape(-1, 4)
        cells.append(q)
    nodes = np.array(nodes)
    cells = np.vstack(cells)
    xy = nodes[cells]
    area = 0.5 * np.sum(xy[:, :, 0] * np.roll(xy[:, :, 1], -1, 1) - np.roll(xy[:, :, 0], -1, 1) * xy[:, :, 1], 1)
    cells[area < 0] = cells[area < 0][:, ::-1]          # all counter-clockwise

    # each cell lies to the left of its own (counter-clockwise) edges
    a = cells.reshape(-1)
    b = np.roll(cells, -1, axis=1).reshape(-1)
    owner = np.repeat(np.arange(len(cells)), 4)
    key = np.minimum(a, b).astype(np.int64) * len(nodes) + np.maximum(a, b)
    order = np.argsort(key, kind="stable")
    key_s = key[order]
    first = np.concatenate([[True], key_s[1:] != key_s[:-1]])
    starts = np.flatnonzero(first)
    counts = np.diff(np.append(starts, len(key_s)))
    if counts.max() > 2:
        raise ValueError("Mesh topology error: an edge is shared by more than two cells")
    f0 = order[starts]
    faces = np.column_stack([a[f0], b[f0], owner[f0], np.full(len(f0), -1)])
    two = counts == 2
    faces[two, 3] = owner[order[starts[two] + 1]]

    def keys(edges):
        out = set()
        for e in edges:
            ids = [index[(float(p[0]), float(p[1]))] for p in e]
            out.update(min(i, j) * len(nodes) + max(i, j) for i, j in zip(ids[:-1], ids[1:]))
        return out

    zone = np.full(len(faces), INTERIOR)
    fkey = key_s[starts]
    boundary = ~two
    zone[boundary] = INLET
    zone[boundary & np.isin(fkey, list(keys(wall_edges)))] = WALL
    zone[boundary & np.isin(fkey, list(keys(outlet_edges)))] = OUTLET
    return BlockMesh(nodes=nodes, cells=cells, faces=faces, face_zone=zone)


# ---------------------------------------------------------------- quality (Fluent definitions)
def quality(mesh):
    """Equiangle skewness and orthogonal quality of every cell (as Fluent defines them)."""
    xy = mesh.nodes[mesh.cells]                               # (nc, 4, 2)
    e_next = np.roll(xy, -1, 1) - xy
    e_prev = np.roll(xy, 1, 1) - xy
    cosang = np.sum(e_next * e_prev, -1) / (np.linalg.norm(e_next, axis=-1) * np.linalg.norm(e_prev, axis=-1))
    ang = np.degrees(np.arccos(np.clip(cosang, -1, 1)))
    skew = np.maximum((ang.max(1) - 90.0) / 90.0, (90.0 - ang.min(1)) / 90.0)

    # area centroid (as Fluent; the node average gave 0.69 instead of Fluent's 0.49 near the LE)
    x, y = xy[..., 0], xy[..., 1]
    x1, y1 = np.roll(x, -1, 1), np.roll(y, -1, 1)
    cross = x * y1 - x1 * y
    a6 = 3.0 * cross.sum(1)
    centre = np.column_stack([((x + x1) * cross).sum(1) / a6, ((y + y1) * cross).sum(1) / a6])
    f = mesh.faces
    p0, p1 = mesh.nodes[f[:, 0]], mesh.nodes[f[:, 1]]
    fc = 0.5 * (p0 + p1)
    t = p1 - p0
    normal = np.column_stack([t[:, 1], -t[:, 0]])                # points from c0 (left) to c1 (right)
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    oq = np.ones(len(mesh.cells))

    def cos_between(n, v):
        return np.sum(n * v, 1) / np.linalg.norm(v, axis=1)

    for side, sign in ((2, 1.0), (3, -1.0)):
        c = f[:, side]
        ok = c >= 0
        n = sign * normal[ok]
        cc = c[ok]
        val = cos_between(n, fc[ok] - centre[cc])
        inner = ok & (f[:, 5 - side] >= 0)
        nb = f[:, 5 - side]
        val2 = np.ones(ok.sum())
        sel = inner[ok]
        val2[sel] = cos_between(n[sel], centre[nb[ok][sel]] - centre[cc[sel]])
        np.minimum.at(oq, cc, np.minimum(val, val2))
    return skew, oq


# ---------------------------------------------------------------- Fluent .msh writer
def to_fluent_msh(mesh, title="AirfoilMatic"):
    """ASCII Fluent mesh file (2D). Indices in hexadecimal, as Fluent expects."""
    nn, nc = len(mesh.nodes), len(mesh.cells)
    order = np.argsort(mesh.face_zone, kind="stable")
    faces, zones = mesh.faces[order], mesh.face_zone[order]
    nf = len(faces)
    out = [f'(0 "{title}: structured C-grid, quadrilateral cells")', "(2 2)",
           f"(10 (0 1 {nn:x} 0 2))", f"(10 (1 1 {nn:x} 1 2)("]
    out += [f"{x:.15e} {y:.15e}" for x, y in mesh.nodes]
    out += ["))", f"(12 (0 1 {nc:x} 0))", f"(12 ({CELL_ZONE:x} 1 {nc:x} 1 3))", f"(13 (0 1 {nf:x} 0))"]
    start = 1
    for z in (INTERIOR, WALL, INLET, OUTLET):
        sel = faces[zones == z]
        if not len(sel):
            continue
        end = start + len(sel) - 1
        out.append(f"(13 ({z:x} {start:x} {end:x} {BC_CODE[z]:x} 2)(")
        c1 = np.where(sel[:, 3] >= 0, sel[:, 3] + 1, 0)
        out += [f"{a + 1:x} {b + 1:x} {c + 1:x} {d:x}" for a, b, c, d in zip(sel[:, 0], sel[:, 1], sel[:, 2], c1)]
        out.append("))")
        start = end + 1
    for z, (kind, name) in ZONE_NAME.items():
        out.append(f"(45 ({z} {kind} {name})())")
    return "\n".join(out) + "\n"


def read_fluent_msh(text):
    """Minimal reader of the ASCII files written by ``to_fluent_msh`` (used by the tests)."""
    import re
    nodes = re.search(r"\(10 \(1 1 ([0-9a-f]+) 1 2\)\(\n(.*?)\n\)\)", text, re.S)
    xy = np.array([[float(v) for v in line.split()] for line in nodes.group(2).splitlines()])
    faces = {}
    for m in re.finditer(r"\(13 \(([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+) ([0-9a-f]+) 2\)\(\n(.*?)\n\)\)", text, re.S):
        rows = np.array([[int(v, 16) for v in line.split()] for line in m.group(5).splitlines()])
        faces[int(m.group(1), 16)] = (int(m.group(4), 16), rows)
    names = dict((int(i), (k, n)) for i, k, n in re.findall(r"\(45 \((\d+) (\S+) (\S+)\)\(\)\)", text))
    return xy, faces, names


# ---------------------------------------------------------------- grid family (mesh independence)
@dataclass
class FamilyMember:
    label: str          # "coarse" | "medium" | "fine"
    refine: float       # cell sizes / refine, growth ratios ** (1 / refine)
    plan: object
    mesh: BlockMesh


# Cell size ratio sqrt(2) between neighbours: about 2x the cells per step in 2D (Celik et al. 2008
# ask for a ratio above 1.3). The medium mesh is the one the app shows.
FAMILY = (("coarse", 2 ** -0.5), ("medium", 1.0), ("fine", 2 ** 0.5))


def mesh_family(domain, af, re, **sizing):
    """Coarse, medium and fine mapped C-grids from the same inputs (``mesh.plan_mesh`` refine)."""
    from .mesh import plan_mesh
    out = []
    for label, k in FAMILY:
        plan = plan_mesh(domain, af, re, refine=k, **sizing)
        out.append(FamilyMember(label, k, plan, build_cgrid(domain, af, plan)))
    return out


def family_zip(family, prefix, title="AirfoilMatic"):
    """ZIP (bytes) with one Fluent .msh per family member: <prefix>_<label>.msh."""
    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in family:
            z.writestr(f"{prefix}_{f.label}.msh", to_fluent_msh(f.mesh, title=f"{title} ({f.label})"))
    return buf.getvalue()
