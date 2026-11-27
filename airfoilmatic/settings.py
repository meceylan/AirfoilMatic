"""The user's inputs saved to a JSON file and read back (sidebar "Settings").

Only known input keys are written and read, each with its type (and, for choices, its allowed
values) checked, so a file edited by hand or from another program cannot set anything else.
"""
import json

from . import __version__
from .topology import SPLIT_LINES

APP_NAME = "AirfoilMatic"

_FLOAT = ("re", "mach_in", "mach_temp", "velocity", "density", "viscosity", "aoa", "fl_temp", "chord",
          "r_inlet_c", "l_wake_c", "l_inlet_c", "l_top_c", "l_bottom_c", "y_plus", "g_infl", "coverage",
          "g_map", "ds_le", "ds_split", "ds_te", "wake_growth", "sweep_from", "sweep_to", "sweep_step")
_INT = ("jou_iter", "jou_save_every")
_TEXT = ("af_text", "sweep_list", "jou_expr", "jou_folder")
_BOOL = ("as_is", "msh_family") + tuple(f"line_{k}" for k in SPLIT_LINES)
_CHOICE = {"domain_kind": ("c_grid", "rect"), "out_unit": ("m", "mm"), "flow_mode": ("re", "mach", "vel"),
           "mesh_mode": ("inflation", "mapped"), "sweep_mode": ("range", "list")}
SAVED_KEYS = _FLOAT + _INT + _TEXT + _BOOL + tuple(_CHOICE)


def _clean(key, value):
    """The value in the type the app's widget uses, or None when it does not fit."""
    if key in _BOOL:
        return value if isinstance(value, bool) else None
    if isinstance(value, bool):
        return None
    if key in _FLOAT:
        return float(value) if isinstance(value, (int, float)) else None
    if key in _INT:
        return int(value) if isinstance(value, int) or (isinstance(value, float) and value.is_integer()) else None
    if key in _TEXT:
        return value if isinstance(value, str) else None
    if key in _CHOICE:
        return value if value in _CHOICE[key] else None
    return None


def to_json(state):
    """JSON text of the known inputs found in ``state`` (e.g. st.session_state)."""
    inputs = {}
    for k in SAVED_KEYS:
        if k in state:
            v = _clean(k, state[k])
            if v is not None:
                inputs[k] = v
    return json.dumps({"app": APP_NAME, "version": __version__, "inputs": inputs}, indent=2, ensure_ascii=False)


def from_json(text):
    """Known inputs of a settings file: unknown keys and values of the wrong type are left out."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        raise ValueError("Not an AirfoilMatic settings file") from None
    if not isinstance(data, dict) or data.get("app") != APP_NAME or not isinstance(data.get("inputs"), dict):
        raise ValueError("Not an AirfoilMatic settings file")
    out = {}
    for k, v in data["inputs"].items():
        if k in SAVED_KEYS:
            c = _clean(k, v)
            if c is not None:
                out[k] = c
    return out
