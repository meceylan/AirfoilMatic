"""Free-stream and force-vector settings for a 2D Fluent airfoil case.

The angle of attack is applied by rotating the inlet velocity, with the airfoil
geometry kept at zero incidence (chord along +x). Lift and drag report vectors
must then be rotated by the same angle:

    velocity  U = U_inf (cos a, sin a)
    drag      D =       (cos a, sin a)    (parallel to the free stream)
    lift      L =       (-sin a, cos a)   (perpendicular, pointing "up")
"""
import math
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
    n = int(math.floor((stop - start) / step + 1e-9)) + 1
    if n > 361:
        raise ValueError("Too many angles (more than 361)")
    out = []
    for i in range(n):
        a = round(start + i * step, 10)
        r = math.radians(a)
        c, s = math.cos(r), math.sin(r)
        out.append(dict(aoa=a, ux=speed * c, uy=speed * s, drag=(c, s), lift=(0.0 - s, c)))   # 0.0 - s: no "-0" at 0°
    return out
