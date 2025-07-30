"""
A tiny pure‑Python helper for drawing quantum‑circuit diagrams.


Quick demo
----------
```python
qc = QuantumCircuit(3)
qc.h(0)
qc.x(2, step=1)           # share column 1
qc.custom([0,2], "Foo")   # tall box spanning q0‑q2 in column 2
qc.cx(0, 1, step=3)

qc.draw()
```
"""

import matplotlib.pyplot as plt

__all__ = [
    "QuantumCircuit",
]

from typing import List, Sequence, Mapping, Any

from pyqcircuit.primitives import Line, Text
from pyqcircuit.graphics_target import GraphicsTarget
from pyqcircuit.style import GateStyle
from pyqcircuit.renderers import gate_registry
from pyqcircuit.matplotlib_backend import MatplotlibTarget


class Gate:
    """Data plus the ability to render itself as primitives."""

    def __init__(
        self,
        name: str,
        qubits: Sequence[int],
        params: Sequence[float] | None = None,
        label: str | None = None,
        step: int = 1,
        style: Mapping[str, Any] | None = None,
    ):
        self.name = name.upper()
        self.qubits = tuple(qubits)  # Store as a tuple for immutability and hashability
        self.params = tuple(params) if params else ()
        self.label = label
        self.step = step
        self.style_overrides = GateStyle(**(style or {}))

    # ------------------------------------------------------------------
    def render(self, tgt: GraphicsTarget, global_style: GateStyle) -> None:
        fn = gate_registry.get(self.name)
        if fn is None:
            raise NotImplementedError(f"No renderer for gate {self.name}")
        fn(self, tgt, global_style)


class QuantumCircuit:
    def __init__(self, n_qubits: int):
        if n_qubits < 1:
            raise ValueError("Circuit must contain at least one qubit.")
        self.n_qubits = n_qubits
        self._gates: List[Gate] = []
        self._current_step = 0

    # ---------- helpers ------------------------------------------------
    def _validate_qubits(self, qubits):
        bad = [q for q in qubits if q < 0 or q >= self.n_qubits]
        if bad:
            raise IndexError(f"Qubit index out of range: {bad}")

    def add_gate(self, name, qubits, *, step=None, label=None, params=None, style=None):
        if isinstance(qubits, int):
            qubits = [qubits]
        self._validate_qubits(qubits)
        if step is None:
            self._current_step += 1
            step = self._current_step
        else:
            self._current_step = max(self._current_step, step)

        self._gates.append(Gate(name, qubits, params, label, step, style=style))

    # --------------------------------------------------------------
    # Convenience wrappers -----------------------------------------
    def h(self, q: int, **kwargs):
        self.add_gate("H", q, **kwargs)

    def x(self, q: int, **kwargs):
        self.add_gate("X", q, **kwargs)

    def y(self, q: int, **kwargs):
        self.add_gate("Y", q, **kwargs)

    def z(self, q: int, **kwargs):
        self.add_gate("Z", q, **kwargs)

    def x90(self, q: int, **kwargs):
        self.add_gate("X90", q, **kwargs)

    def y90(self, q: int, **kwargs):
        self.add_gate("Y90", q, **kwargs)

    def z90(self, q: int, **kwargs):
        self.add_gate("Z90", q, **kwargs)

    def s(self, q: int, **kwargs):
        self.add_gate("S", q, **kwargs)

    def t(self, q: int, **kwargs):
        self.add_gate("T", q, **kwargs)

    def i(self, q: int, **kwargs):
        self.add_gate("I", q, **kwargs)

    def rx(self, q: int, theta: float, **kwargs):
        self.add_gate("RX", q, params=[theta], **kwargs)

    def cx(self, control: int, target: int, **kwargs):
        self.add_gate("CNOT", [control, target], **kwargs)

    def cz(self, control: int, target: int, **kwargs):
        self.add_gate("CZ", [control, target], **kwargs)

    def swap(self, q1: int, q2: int, **kwargs):
        self.add_gate("SWAP", [q1, q2], **kwargs)

    def measure(self, qs, **kwargs):
        self.add_gate("MEASURE", qs, **kwargs)

    def custom(self, qubits: Sequence[int] | int, label: str, **kwargs):
        """Insert a *labelled* one‑ or multi‑qubit gate."""
        self.add_gate("CUSTOM", qubits, label=label, **kwargs)

    # ---------- drawing entry point -----------------------------------
    def draw(self, backend: str = "mpl", **backend_kw):
        if backend == "mpl":
            tgt = MatplotlibTarget(self._current_step, self.n_qubits, **backend_kw)
        else:
            raise ValueError(f"Backend {backend!r} not recognised")
        # Wires
        for q in range(self.n_qubits):
            y = -q
            tgt.add(Line(0, y, self._current_step + 1, y, layer=0))
            tgt.add(Text(-0.2, y, f"q{q} |0>", ha="right", va="center", size=9, layer=1))
        # Gates
        global_style = GateStyle()
        for g in self._gates:
            g.render(tgt, global_style)
        return tgt.finalize()


if __name__ == "__main__":
    c = QuantumCircuit(6)
    c.custom(range(6), "SetV\n(_111)", step=1)
    c.h(0, step=2)
    c.i(3, step=2)
    c.rx(4, 3.1415, step=2)
    c.cz(1, 3, step=3)
    c.cx(4, 5, step=3)
    c.cx(5, 4, step=4)

    # c.z(2, step=3)

    c.z90(0, step=4)
    c.x(2, step=4)
    c.swap(4, 5, step=5)
    c.custom(0, "Custom\nGate", step=5)
    c.measure([0, 1, 2], step=6)
    c.custom([3, 4, 5], "Custom\nGate", step=6)
    c.draw()
    # plt.tight_layout()
    plt.show()
