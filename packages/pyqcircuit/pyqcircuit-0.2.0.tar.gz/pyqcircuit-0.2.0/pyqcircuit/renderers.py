from math import pi
from typing import Dict, Callable, Sequence, Union, Iterable

from pyqcircuit.graphics_target import GraphicsTarget
from pyqcircuit.primitives import Line, Box, Circle, Arc, Text
from pyqcircuit.style import GateStyle, default_gate_style

# Registry that maps gate names to renderer functions.
gate_registry: Dict[str, Callable] = {}

NameArg = Union[str, Sequence[str]]


def gate_renderer(names: NameArg):
    """
    Register one rendering function for one *or several* gate names.

    Examples
    --------
    @gate_renderer("H")
    def render_h(...): ...

    @gate_renderer(["H", "X", "Y", "Z"])
    def render_single_qubit_box(...): ...
    """
    # Normalise to an iterable of upper‑case names
    if isinstance(names, str):
        name_list = [names.upper()]
    elif isinstance(names, Iterable):
        name_list = [n.upper() for n in names]
    else:
        raise TypeError("names must be a string or iterable of strings")

    def decorator(fn: Callable):
        for n in name_list:
            gate_registry[n] = fn
        return fn

    return decorator


def _merge_styles(global_style: GateStyle, local_style: GateStyle) -> GateStyle:
    return default_gate_style.merged(global_style).merged(local_style)


def _pretty(gate):
    # Map gate names to pretty math‑text
    pretty = {"RX": r"$R_x$", "RY": r"$R_y$", "RZ": r"$R_z$", "RXY": r"$R_{xy}$"}

    def _fmt(val: float) -> str:
        close = lambda a, b: abs(a - b) < 1e-4
        if close(val, pi):
            return r"π"
        if close(val, -pi):
            return "-π"
        if close(val, pi / 2):
            return "π/2"
        if close(val, -pi / 2):
            return "-π/2"
        return f"{val:.2f}"

    if gate.label is not None:
        base = gate.label
    else:
        base = pretty.get(gate.name, gate.name)  # default → original

    if gate.params:
        parms = ", ".join(_fmt(p) for p in gate.params)
        text = f"{base}({parms})"
    else:
        text = base
    return text


# ----------------------------------------------------------------------
# Gate‑specific rendering functions
# ----------------------------------------------------------------------


# ------- Single‑qubit gates --------------------------------
@gate_renderer(
    [
        "Z",
        "H",
        "X",
        "Y",
        "S",
        "T",
        "S†",
        "T†",
        "I",
        "X90",
        "Y90",
        "Z90",
    ]
)
def render_single_box(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = _merge_styles(global_style, gate.style_overrides)
    x = gate.step
    y = -gate.qubits[0]
    face = st.facecolor or "#e0e0e0"
    edge = st.edgecolor or "black"
    lw = st.linewidth or 1.0
    fs = st.fontsize or 7
    txt = gate.label or gate.name
    tgt.add(Box(x - 0.4, y - 0.4, 0.8, 0.8, face, edge, lw, layer=1))
    tgt.add(Text(x, y, txt, fs, st.textcolor or "black", layer=3))


@gate_renderer(["RX", "RY", "RZ", "RXY"])
def render_rotation(gate, tgt: GraphicsTarget, global_style: GateStyle):
    """Draw a single‑qubit rotation gate, showing its parameter(s)."""
    # --- style merge ---------------------------------------------------
    st = default_gate_style.merged(global_style).merged(gate.style_overrides)

    # --- label with parameters ----------------------------------------
    text = _pretty(gate)

    # --- primitive box -------------------------------------------------
    x = gate.step
    y = -gate.qubits[0]
    face = st.facecolor or "#e0e0e0"
    edge = st.edgecolor or "black"
    lw = st.linewidth or 1.0
    fs = st.fontsize or 7
    tgt.add(Box(x - 0.4, y - 0.4, 0.8, 0.8, face=face, edge=edge, lw=lw, layer=1))
    tgt.add(Text(x, y, text, size=fs, color=st.textcolor or "black", layer=2))


# ------- Two‑qubit gates --------------------------------


@gate_renderer(["CX", "CNOT"])
def render_cnot(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = _merge_styles(global_style, gate.style_overrides)
    x = gate.step
    ctrl, targ = gate.qubits
    cy, ty = -ctrl, -targ
    col = st.edgecolor or "black"
    lw = st.linewidth or 1.0
    tgt.add(Circle(x, cy, 0.1, True, col, lw, layer=1))
    tgt.add(Line(x, cy, x, ty, lw, col, layer=1))
    tgt.add(Circle(x, ty, 0.18, False, col, lw, layer=1))
    tgt.add(Line(x, ty - 0.18, x, ty + 0.18, lw, col, layer=1))
    tgt.add(Line(x - 0.18, ty, x + 0.18, ty, lw, col, layer=1))


@gate_renderer(["CZ"])
def render_cz(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = _merge_styles(global_style, gate.style_overrides)
    x = gate.step
    ctrl, targ = gate.qubits
    cy, ty = -ctrl, -targ
    col = st.edgecolor or "black"
    lw = st.linewidth or 1.0
    tgt.add(Circle(x, cy, 0.1, True, col, lw, layer=1))
    tgt.add(Line(x, cy, x, ty, lw, col, layer=1))
    tgt.add(Circle(x, ty, 0.1, True, col, lw, layer=1))


@gate_renderer(["SWAP"])
def render_swap(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = _merge_styles(global_style, gate.style_overrides)
    x = gate.step
    ctrl, targ = gate.qubits
    cy, ty = -ctrl, -targ
    col = st.edgecolor or "black"
    lw = st.linewidth or 1.0
    tgt.add(Line(x, cy, x, ty, lw, col, layer=1))
    tgt.add(Line(x - 0.18, ty - 0.18, x + 0.18, ty + 0.18, lw, col, layer=1))
    tgt.add(Line(x + 0.18, ty - 0.18, x - 0.18, ty + 0.18, lw, col, layer=1))
    tgt.add(Line(x - 0.18, cy - 0.18, x + 0.18, cy + 0.18, lw, col, layer=1))
    tgt.add(Line(x + 0.18, cy - 0.18, x - 0.18, cy + 0.18, lw, col, layer=1))


# ------- Other operations --------------------------------
@gate_renderer("MEASURE")
def render_measure(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = _merge_styles(global_style, gate.style_overrides)
    x = gate.step
    face = st.facecolor or "#ffffff"
    edge = st.edgecolor or "black"
    lw = st.linewidth or 1.0
    for q in gate.qubits:
        y = -q
        tgt.add(Box(x - 0.4, y - 0.4, 0.8, 0.8, face, edge, lw, layer=1))
        r = 0.2
        tgt.add(Arc(x, y - r / 2, 2 * r, 2 * r, 0, 180, lw, edge, layer=3))
        tgt.add(Line(x, y - r / 2, x + r, y + r - r / 2, lw, edge, layer=3))


@gate_renderer("CUSTOM")
def render_custom(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = _merge_styles(global_style, gate.style_overrides)
    x = gate.step
    ybot = -max(gate.qubits)
    ytop = -min(gate.qubits)
    face = st.facecolor or "#e0e0e0"
    edge = st.edgecolor or "black"
    lw = st.linewidth or 1.0
    fs = st.fontsize or 7
    txt = gate.label or gate.name
    tgt.add(Box(x - 0.4, ybot - 0.4, 0.8, 0.8 + ytop - ybot, face, edge, lw, layer=1))
    tgt.add(Text(x, (ytop + ybot) / 2, txt, fs, st.textcolor or "black", layer=3))
