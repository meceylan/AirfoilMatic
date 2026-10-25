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
        drag=(c, s), lift=(-s, c),
        reynolds=density * speed * chord / viscosity,
        mach=speed / speed_of_sound,
    )


def speed_for_reynolds(re, chord, density=AIR_DENSITY, viscosity=AIR_VISCOSITY):
    return re * viscosity / (density * chord)
