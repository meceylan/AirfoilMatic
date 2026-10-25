"""Mesh-quality ratings for the metrics reported by Ansys Meshing / Fluent.

Spectra: Ansys Meshing training material (skewness and orthogonal quality
bands). Hard limits: Fluent User's Guide, "Mesh Requirements and
Considerations": minimum orthogonal quality > 0.01; maximum skewness < 0.95
(stated for triangular/tetrahedral cells, commonly applied to all cells).
"""

# (upper bound, rating key); skewness: lower is better
SKEWNESS_BANDS = [
    (0.25, "q_excellent"),
    (0.50, "q_very_good"),
    (0.80, "q_good"),
    (0.94, "q_acceptable"),
    (0.97, "q_bad"),
    (1.00, "q_unacceptable"),
]

# (lower bound, rating key); orthogonal quality: higher is better
ORTHO_BANDS = [
    (0.95, "q_excellent"),
    (0.70, "q_very_good"),
    (0.20, "q_good"),
    (0.15, "q_acceptable"),
    (0.001, "q_bad"),
    (0.0, "q_unacceptable"),
]

FLUENT_MAX_SKEWNESS = 0.95
FLUENT_MIN_ORTHO = 0.01

RATING_LEVEL = {"q_excellent": 0, "q_very_good": 0, "q_good": 0,
                "q_acceptable": 1, "q_bad": 2, "q_unacceptable": 3}


def rate_skewness(value):
    if not 0.0 <= value <= 1.0:
        raise ValueError("Skewness must be between 0 and 1")
    for upper, key in SKEWNESS_BANDS:
        if value <= upper:
            return key
    return "q_unacceptable"


def rate_orthogonal(value):
    if not 0.0 <= value <= 1.0:
        raise ValueError("Orthogonal quality must be between 0 and 1")
    for lower, key in ORTHO_BANDS:
        if value >= lower:
            return key
    return "q_unacceptable"


def expected_wall_aspect_ratio(first_layer, surface_size):
    """Aspect ratio of the first wall cell: streamwise size / first layer height."""
    return surface_size / first_layer
