"""Free-stream and force-vector settings for a 2D Fluent airfoil case.

The angle of attack is applied by rotating the inlet velocity, with the airfoil
geometry kept at zero incidence (chord along +x). Lift and drag report vectors
must then be rotated by the same angle:

    velocity  U = U_inf (cos a, sin a)
    drag      D =       (cos a, sin a)    (parallel to the free stream)
    lift      L =       (-sin a, cos a)   (perpendicular, pointing "up")
"""
import math
import re
from dataclasses import dataclass

# Fluent default air and the standard sea-level speed of sound (15 deg C).
AIR_DENSITY = 1.225          # kg/m^3
AIR_VISCOSITY = 1.7894e-5    # Pa s
SPEED_OF_SOUND = 340.29      # m/s


@dataclass
class Freestream:
    aoa_deg: float
    speed: float
    ux: float
    uy: float
    drag: tuple
    lift: tuple
    reynolds: float
    mach: float


def freestream(aoa_deg, speed, chord, density=AIR_DENSITY, viscosity=AIR_VISCOSITY,
               speed_of_sound=SPEED_OF_SOUND):
    if speed <= 0 or chord <= 0 or density <= 0 or viscosity <= 0:
        raise ValueError("Speed, chord, density and viscosity must be positive")
    a = math.radians(aoa_deg)
    c, s = math.cos(a), math.sin(a)
    return Freestream(
        aoa_deg=aoa_deg, speed=speed, ux=speed * c, uy=speed * s,
        drag=(c, s), lift=(0.0 - s, c),
        reynolds=density * speed * chord / viscosity,
        mach=speed / speed_of_sound,
    )


def speed_for_reynolds(re, chord, density=AIR_DENSITY, viscosity=AIR_VISCOSITY):
    return re * viscosity / (density * chord)


# ----------------------------------------------------------------------------- speed of sound
GAMMA_AIR = 1.4
R_AIR = 287.05               # J/(kg K)


def air_density(temp_c, pressure=101325.0):
    """Ideal-gas density of air, kg/m3 (R = 287.05 J/(kg K))."""
    return pressure / (287.05 * (temp_c + 273.15))


def sutherland_viscosity(temp_c):
    """Dynamic viscosity of air by Sutherland's law, Pa s (mu0 = 1.716e-5 at 273.15 K, S = 110.4 K)."""
    t = temp_c + 273.15
    return 1.716e-5 * (t / 273.15) ** 1.5 * (273.15 + 110.4) / (t + 110.4)


def mach_state(mach, reynolds, temp_c, chord):
    """Free stream of a Mach number, Reynolds number and temperature (ideal-gas air, Sutherland viscosity).
    The density follows from the Reynolds number, the static pressure from the density:
    ``speed``, ``sound`` (m/s), ``viscosity`` (Pa s), ``density`` (kg/m3), ``pressure`` (Pa), ``temperature`` (K)."""
    if mach <= 0 or reynolds <= 0 or chord <= 0:
        raise ValueError("Mach number, Reynolds number and chord must be positive")
    a = speed_of_sound(temp_c)
    u = mach * a
    mu = sutherland_viscosity(temp_c)
    rho = reynolds * mu / (u * chord)
    t_k = temp_c + 273.15
    return dict(speed=u, sound=a, viscosity=mu, density=rho, pressure=rho * R_AIR * t_k, temperature=t_k)


# Above this Knudsen number (mean free path / chord) the gas starts to slip at the wall and the
# continuum (no-slip Navier-Stokes) model of Fluent's pressure-based solver no longer holds.
KNUDSEN_CONTINUUM = 1e-3


def rarefaction(state, temp_c, chord):
    """Knudsen number of a ``mach_state`` free stream: mean free path mu/p * sqrt(pi R T / 2) over the chord.
    About M / Re * sqrt(gamma pi / 2); 1e-7 at M 0.15, Re 2e6 and 1e-3 at M 0.8, Re 1e3."""
    t_k = temp_c + 273.15
    path = state["viscosity"] / state["pressure"] * math.sqrt(math.pi * R_AIR * t_k / 2.0)
    return path / chord


def speed_of_sound(temp_c):
    """Speed of sound in air (ideal gas) at ``temp_c`` degrees Celsius; 15 degC gives 340.29 m/s."""
    t = temp_c + 273.15
    if t <= 0:
        raise ValueError("Temperature must be above absolute zero")
    return math.sqrt(GAMMA_AIR * R_AIR * t)


# ----------------------------------------------------------------------------- turbulence decay
# With no shear in the free stream the SST k-omega equations (also under Transition SST)
# reduce to dk/dt = -beta* k w and dw/dt = -beta w^2, so between the inlet and the airfoil
#     Tu(x) / Tu_in = (1 + 1.5 beta Tu_in^2 Re_x / VR) ** (-beta* / (2 beta))
# with Re_x = rho U x / mu, VR = mu_t / mu at the inlet, beta* = 0.09, beta = 0.0828
# (Spalart & Rumsey, AIAA J. 45(10), 2007; the outer-layer beta of SST).
BETA_STAR = 0.09
BETA_SST = 0.0828
DECAY_EXP = BETA_STAR / (2.0 * BETA_SST)


def _decay_a(re_x, viscosity_ratio):
    if re_x < 0 or viscosity_ratio <= 0:
        raise ValueError("Distance and viscosity ratio must be positive")
    return 1.5 * BETA_SST * re_x / viscosity_ratio


def decayed_tu(tu_inlet, re_x, viscosity_ratio):
    """Turbulence intensity (fraction) left after the free stream has run a distance with Reynolds
    number ``re_x`` from an inlet with ``tu_inlet`` and eddy-viscosity ratio ``viscosity_ratio``."""
    a = _decay_a(re_x, viscosity_ratio)
    return tu_inlet * (1.0 + a * tu_inlet**2) ** -DECAY_EXP


def max_reachable_tu(re_x, viscosity_ratio):
    """Largest intensity that can reach the airfoil with this viscosity ratio, whatever the inlet
    value: a higher inlet intensity also decays faster (more dissipation)."""
    a = _decay_a(re_x, viscosity_ratio)
    if a == 0:
        return math.inf
    tu_peak = math.sqrt(1.0 / (a * (2.0 * DECAY_EXP - 1.0)))
    return decayed_tu(tu_peak, re_x, viscosity_ratio)


def inlet_tu_for(tu_target, re_x, viscosity_ratio):
    """Inlet intensity that decays to ``tu_target`` at the airfoil, or None when the target cannot
    be reached with this viscosity ratio (then a larger ratio is needed)."""
    a = _decay_a(re_x, viscosity_ratio)
    if tu_target <= 0:
        raise ValueError("Target turbulence intensity must be positive")
    if a == 0:
        return tu_target
    hi = math.sqrt(1.0 / (a * (2.0 * DECAY_EXP - 1.0)))   # intensity of the peak
    if decayed_tu(hi, re_x, viscosity_ratio) < tu_target:
        return None
    lo = tu_target
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if decayed_tu(mid, re_x, viscosity_ratio) < tu_target:
            lo = mid
        else:
            hi = mid
    return hi


# ----------------------------------------------------------------------------- alpha sweep
def alpha_sweep(start, stop, step, speed):
    """Inlet components and force vectors for every angle from ``start`` to ``stop`` (both
    included when the step lands on it)."""
    if step <= 0:
        raise ValueError("Angle step must be positive")
    if stop < start:
        raise ValueError("Last angle must not be below the first one")
    if max(abs(start), abs(stop)) > 180:
        raise ValueError("Angles must be between -180 and 180 degrees")
    n = int(math.floor((stop - start) / step + 1e-9)) + 1
    if n > MAX_ANGLES:
        raise ValueError("Too many angles (more than 361)")
    return angle_rows([round(start + i * step, 10) for i in range(n)], speed)


def angle_rows(angles, speed):
    """Inlet components and force vectors for each angle of ``angles`` (degrees), in that order."""
    out = []
    for a in angles:
        r = math.radians(a)
        c, s = math.cos(r), math.sin(r)
        out.append(dict(aoa=a, ux=speed * c, uy=speed * s, drag=(c, s), lift=(0.0 - s, c)))   # 0.0 - s: no "-0" at 0°
    return out


MAX_ANGLES = 361


def parse_angles(text):
    """The user's own angles from text such as "1.3, 2.8, 6.8": sorted, repeats dropped.

    Angles are separated by spaces, ';' or commas; the decimal mark is a dot. A comma between two
    digits ("1,3") is refused, because it may be a Turkish decimal comma or two angles."""
    text = str(text or "")
    if re.search(r"\d,\d", text):
        raise ValueError("Use a dot for decimals (1.5) and separate angles with a space, ; or a comma and a space")
    parts = [p for p in re.split(r"[\s,;]+", text) if p]
    if not parts:
        raise ValueError("Enter at least one angle")
    angles = set()
    for p in parts:
        try:
            a = float(p)
        except ValueError:
            a = math.nan
        if not math.isfinite(a):
            raise ValueError("Angles must be numbers, separated by a space, ; or a comma")
        if abs(a) > 180:
            raise ValueError("Angles must be between -180 and 180 degrees")
        angles.add(round(a, 4) + 0.0)   # as the journal writes it (4 decimals); + 0.0: "-0" becomes 0
    if len(angles) > MAX_ANGLES:
        raise ValueError("Too many angles (more than 361)")
    return sorted(angles)


# ----------------------------------------------------------------------------- sweep journal
_NAME_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")      # Fluent zone names ("wall:011")
_FILE_RE = re.compile(r"^[A-Za-z0-9_.-]+$")        # file names: ':' is not allowed on Windows


def _check_name(value, what):
    """``what`` is a fixed label so the error message can be translated."""
    value = str(value).strip()
    if not _NAME_RE.match(value):
        raise ValueError(f"{what} may only contain letters, digits and _ . : -")
    return value


def _check_file_name(value, what):
    value = str(value).strip()
    if not _FILE_RE.match(value):
        raise ValueError(f"{what} may only contain letters, digits and _ . -")
    return value


def _label_angle(aoa):
    """Angle as written in names and markers: 2 decimals, never a negative zero."""
    return round(aoa, 2) + 0.0


def _case_name(prefix, aoa):
    a = _label_angle(aoa)
    tag = ("m" if a < 0 else "") + f"{abs(a):05.2f}".replace(".", "p")
    return f"{prefix.replace('.', '_')}_aoa_{tag}"


_EXPR_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _check_expression(value):
    value = str(value).strip()
    if not _EXPR_RE.match(value):
        raise ValueError("Expression name may only contain letters, digits and _ and must not start with a digit")
    return value


def angle_text(aoa):
    """Compact angle for a Fluent expression: up to 4 decimals, no trailing zeros, never "-0"."""
    s = f"{aoa:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


_angle_text = angle_text


def _positive(value, what):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{what} must be a positive number")
    return float(value)


def expression_setup(expression="aoa", density=1.225, speed=1.0, chord=1.0, depth=1.0, wall="wall"):
    """Strings the Fluent case needs for the named-expression sweep: the two flow-direction
    components of the pressure-far-field zone and the Cl / Cd expression definitions.
    Tried in Ansys Fluent 2024 R2 (2D): the Cl/Cd values matched Fluent's own force reports."""
    expression = _check_expression(expression)
    wall = _check_name(wall, "Wall zone name")
    density = _positive(density, "Density")
    speed = _positive(speed, "Speed")
    area = _positive(chord, "Chord") * _positive(depth, "Depth")
    q = f"(0.5 * {density:.6g} [kg m^-3] * ({speed:.6g} [m s^-1])^2 * {area:.6g} [m^2])"
    force = f"dot(Force(['{wall}']), vector("
    cl = f"{force}-sin({expression}), cos({expression}), 0)) / {q}"
    return dict(
        flow_x=f"cos({expression})",
        flow_y=f"sin({expression})",
        # Velocity inlet set by Components: the components themselves, not a direction (tried in
        # Fluent 2024 R2 as 51.04 [m/s]*cos(aoa), the 11-angle sweep).
        inlet_x=f"{speed:.6g} [m s^-1]*cos({expression})",
        inlet_y=f"{speed:.6g} [m s^-1]*sin({expression})",
        cl=cl,
        cd=f"{force}cos({expression}), sin({expression}), 0)) / {q}",
        # Fluent's Convergence Conditions use a relative change, which never settles when Cl is
        # about 0 (symmetric profile at 0 deg). Cl + 1 stays near 1, so its relative change is
        # about the absolute change of Cl. Tried in Fluent 2024 R2 (0 deg: stopped by itself
        # after 366 iterations with the same Cl/Cd as a 2000-iteration run).
        clconv=f"{cl} + 1",
    )


def sweep_journal(start, stop, step, iterations=1000, expression="aoa", save_every=0, folder="",
                  prefix="airfoilmatic", version="", angles=None):
    """Return the text of a Fluent TUI journal (.jou) for an angle-of-attack sweep.

    At each angle (smallest to largest) only the named expression ``expression`` changes and the
    solver iterates, continuing from the previous solution. The case must use that expression for
    the pressure-far-field flow direction and for the Cl / Cd expression reports (see
    ``expression_setup``). Tried in Ansys Fluent 2024 R2 (standalone, TUI version 24.2).

    ``save_every`` = k writes case & data after every k-th angle (1 = every angle); the last angle
    is always written. 0 (default) writes only the last angle.

    ``angles``: the user's own list (from ``parse_angles``); then start, stop and step are not used."""
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 1:
        raise ValueError("Iterations must be an integer of at least 1")
    if isinstance(save_every, bool) or not isinstance(save_every, int) or save_every < 0:
        raise ValueError("Save interval must be a whole number of 0 or more")
    expression = _check_expression(expression)
    prefix = _check_file_name(prefix, "File name prefix")
    folder = str(folder or "").strip()
    if not folder.isascii():
        raise ValueError("Folder must contain only ASCII characters (Fluent may not handle others)")
    if '"' in folder:
        raise ValueError("Folder must not contain a double quote")
    folder = folder.replace("\\", "/").rstrip("/")
    if angles is not None:
        rows = angle_rows(sorted(set(float(a) + 0.0 for a in angles)), 1.0)
        if not rows:
            raise ValueError("Enter at least one angle")
        if len(rows) > MAX_ANGLES:
            raise ValueError("Too many angles (more than 361)")
    else:
        rows = alpha_sweep(start, stop, step, 1.0)
    n = len(rows)
    if len({_case_name(prefix, r["aoa"]) for r in rows}) != n:
        if angles is not None:
            raise ValueError("Two angles get the same file name: keep angles at least 0.01° apart")
        raise ValueError("Angle step too small: two angles get the same file name")

    def path(aoa):
        name = _case_name(prefix, aoa)
        return f'"{folder}/{name}"' if folder else f'"{name}"'

    first, last = rows[0]["aoa"], rows[-1]["aoa"]
    e = expression
    if save_every == 1:
        save_text = "after every angle"
    elif save_every > 1:
        save_text = f"every {save_every} angles and after the last angle"
    else:
        save_text = "only after the last angle"
    out = [
        f"; AirfoilMatic {version}".rstrip() + " - angle-of-attack sweep journal for Ansys Fluent (2D)",
        "; The case must contain, before this journal is read:",
        f";   - a named expression {e} (angle, e.g. {_angle_text(first)} [deg]),",
        f";   - the pressure-far-field flow direction X = cos({e}), Y = sin({e}),",
        f";   - Cl and Cd as expression report definitions that use {e}",
        f";     (force direction from cos({e}) and sin({e})),",
        ";   - report files that hold only expression reports (and the moment report): a lift/drag",
        ";     report with a changed force vector may ask a question about its file,",
        ";   - residual convergence checks off (otherwise each angle stops after a few iterations).",
        f"; Set {e} to the first angle ({_angle_text(first)} deg), initialise and run at least one iteration yourself:",
        "; a run that starts at iteration 0 can make Fluent ask \"Ok to overwrite?\" for existing",
        "; report files, and inside a journal the next line would become the answer.",
        f"; At each angle the journal only changes {e} and iterates; every angle continues from the",
        "; previous solution (no initialisation).",
        (f"; Angles: {', '.join(_angle_text(r['aoa']) for r in rows)} (own list), count {n}." if angles is not None
         else f"; Angles: first {first:g}, last {last:g}, step {step:g}, count {n}."),
        f"; Iterations per angle: {iterations} = upper limit. If the case has Convergence Conditions",
        "; (Solution > Report Definitions), Fluent stops an angle early when they are met and the journal",
        "; goes on to the next angle (seen in Fluent 2024 R2, 11-angle sweep).",
        f"; Case & data are written {save_text}.",
        "; To continue a stopped sweep: read the last written case & data and run one iteration by hand",
        "; first. Fluent asks \"Do you want to create new file?\" for every report file (it already holds",
        "; later iterations): answer Yes; the rest goes to <name>_<iteration>.out. Then set the first",
        "; angle in AirfoilMatic to the next angle, download a new journal and read it. Give the polar",
        "; tool both report files. Tried in Fluent 2024 R2 (2026-11-25).",
        "; Tried in Ansys Fluent 2024 R2 (standalone, 2D): the edit command, the Cl/Cd expressions and",
        "; the report files (no questions asked), and a 3-angle sweep (-2, 0, 2 deg, 50 iterations",
        "; each) that ran to the end without a question. An 11-angle sweep (-4 ... 16 deg, up to 2000",
        "; iterations each, Convergence Conditions; velocity-inlet case) also ran to the end, and so",
        "; did a sweep with a pressure-far-field case, M 0.3 (2 ... 8 deg).",
        "; Meant for standalone Fluent (Launcher). Tried inside Workbench: Fluent there asks \"Settings have",
        "; changed\" and asks again at every angle change, so the journal breaks.",
        "; Run: File > Read > Journal.",
        "; It turns off Fluent's overwrite question for this session (existing files with the same",
        "; names are overwritten). Fluent 2024 R2 accepted /file/confirm-overwrite? no without error;",
        "; overwriting a case file with it has not been tried yet.",
        '/file/set-tui-version "24.2"',
        "/file/confirm-overwrite? no",
    ]
    for i, r in enumerate(rows, 1):
        out.append(f'(display "\\n=== AirfoilMatic: alpha {_label_angle(r["aoa"]):.2f} deg ({i}/{n}) ===\\n")')
        out.append(f'/define/named-expressions/edit {e} definition "{_angle_text(r["aoa"])} [deg]" q')
        out.append(f"/solve/iterate {iterations}")
        if i == n or (save_every and i % save_every == 0):
            out.append(f"/file/write-case-data {path(r['aoa'])}")
    out.append('(display "\\n=== AirfoilMatic: sweep done ===\\n")')
    return "\n".join(out) + "\n"
