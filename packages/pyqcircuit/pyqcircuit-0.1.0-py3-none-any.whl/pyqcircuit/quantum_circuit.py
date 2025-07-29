"""
A tiny pure‑Python helper for drawing quantum‑circuit diagrams with Matplotlib.


Quick demo
----------
```python
qc = QuantumCircuit(3)
qc.h(0)
qc.x(2, step=1)           # share column 1
qc.custom([0,2], "Foo")   # tall box spanning q0‑q2 in column 2
qc.cx(0, 1, step=3)

qc.draw(box_facecolor="#ffe680",
        wire_labels=["|0>", "|+>", "|1>"])
```
"""

from typing import List, Sequence, Tuple, Optional

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Circle, Arc

__all__ = [
    "QuantumCircuit",
]


# ---------------------------------------------------------------------
# Helper class ----------------------------------------------------
class Gate:
    """Simple container describing a single operation."""

    def __init__(
        self,
        name: str,
        qubits: Sequence[int],
        params: Sequence[float] | None = None,
        label: str | None = None,
        step: int = 1,
    ):
        self.name = name.upper()
        self.qubits = tuple(sorted(qubits))  # keep ascending for drawers
        self.params = tuple(params) if params else ()
        self.label = label  # Optional override for the box text
        self.step = step  # Column index

    def __repr__(self):
        return (
            f"Gate({self.name}, {self.qubits}, params={self.params}, "
            f"label={self.label!r}, step={self.step})"
        )


# ---------------------------------------------------------------------
# Main circuit container ----------------------------------------------
class QuantumCircuit:
    """Extremely lightweight circuit model that can *draw* itself."""

    def __init__(self, n_qubits: int):
        if n_qubits < 1:
            raise ValueError("Circuit must contain at least one qubit.")
        self.n_qubits: int = n_qubits
        self._gates: List[Gate] = []
        self._current_step: int = 0  # Last auto‑assigned column index

    # --------------------------------------------------------------
    # Generic insertion method -------------------------------------
    def add_gate(
        self,
        name: str,
        qubits: Sequence[int] | int,
        params: Sequence[float] | None = None,
        label: str | None = None,
        *,
        step: int | None = None,
    ):
        """Append a gate to the circuit.

        Use explicit ``step`` to force a column; leave it ``None`` to place the
        gate after the current rightmost *automatic* column.
        """
        if isinstance(qubits, int):
            qubits = [qubits]
        self._validate_qubits(qubits)

        # Determine column index
        if step is None:
            self._current_step += 1
            step = self._current_step
        else:
            if step < 1:
                raise ValueError("step must be ≥ 1")
            self._current_step = max(self._current_step, step)

        self._gates.append(Gate(name, qubits, params, label, step))

    # --------------------------------------------------------------
    # Convenience wrappers -----------------------------------------
    def h(self, q: int, *, step: int | None = None):
        self.add_gate("H", q, step=step)

    def x(self, q: int, *, step: int | None = None):
        self.add_gate("X", q, step=step)

    def y(self, q: int, *, step: int | None = None):
        self.add_gate("Y", q, step=step)

    def z(self, q: int, *, step: int | None = None):
        self.add_gate("Z", q, step=step)

    def x90(self, q: int, *, step: int | None = None):
        self.add_gate("X90", q, step=step)

    def y90(self, q: int, *, step: int | None = None):
        self.add_gate("Y90", q, step=step)

    def z90(self, q: int, *, step: int | None = None):
        self.add_gate("Z90", q, step=step)

    def s(self, q: int, *, step: int | None = None):
        self.add_gate("S", q, step=step)

    def t(self, q: int, *, step: int | None = None):
        self.add_gate("T", q, step=step)

    def rx(self, q: int, theta: float, *, step: int | None = None):
        self.add_gate("$R_x$", q, [theta], step=step)

    def ry(self, q: int, theta: float, *, step: int | None = None):
        self.add_gate("$R_y$", q, [theta], step=step)

    def rz(self, q: int, theta: float, *, step: int | None = None):
        self.add_gate("$R_z$", q, [theta], step=step)

    def cx(self, control: int, target: int, *, step: int | None = None):
        self.add_gate("CNOT", [control, target], step=step)

    def cz(self, control: int, target: int, *, step: int | None = None):
        self.add_gate("CZ", [control, target], step=step)

    def swap(self, q1: int, q2: int, *, step: int | None = None):
        self.add_gate("SWAP", [q1, q2], step=step)

    def measure(self, qubits: Sequence[int] | int, *, step: int | None = None):
        self.add_gate("MEASURE", qubits, step=step)

    def custom(self, qubits: Sequence[int] | int, label: str, *, step: int | None = None):
        """Insert a *labelled* one‑ or multi‑qubit gate."""
        self.add_gate("CUSTOM", qubits, label=label, step=step)

    # --------------------------------------------------------------
    def draw(
        self,
        *,
        figsize: Tuple[int, int] | None = None,
        ax: plt.Axes | None = None,
        box_facecolor: str = "#eeeeee",
        wire_labels: Optional[Sequence[str]] = None,
    ):
        """Render the circuit with Matplotlib.

        Parameters
        ----------
        box_facecolor
            Fill colour for *all* gate boxes (default: very light grey). Use any
            Matplotlib‑compatible spec (named colour, hex, RGBA tuple …).
        wire_labels
            Optional list/tuple of per‑qubit labels shown at the far left. If
            omitted, wires are labelled ``q0``, ``q1`` …
        """
        n_cols = max((g.step for g in self._gates), default=1)
        if ax is None:
            auto_figsize = ((n_cols + 2) * 0.8, (self.n_qubits + 1) * 0.8)
            figsize = figsize or auto_figsize
            fig, ax = plt.subplots(figsize=figsize)
        else:
            fig = ax.figure

        # Wires ------------------------------------------------------
        for q in range(self.n_qubits):
            y = -q
            ax.add_line(Line2D([0, n_cols + 1], [y, y], lw=1, zorder=0))  # behind everything
            label = (
                wire_labels[q] if wire_labels and q < len(wire_labels) else rf"q{q} $\vert0\rangle$"
            )
            ax.text(-0.2, y, label, va="center", ha="right", fontsize=10, zorder=3)

        # Gates ------------------------------------------------------
        for g in self._gates:
            x = g.step
            if g.name in {"CNOT", "CX"}:
                self._draw_cnot(ax, x, g.qubits)
            elif g.name == "CZ":
                self._draw_cz(ax, x, g.qubits)
            elif g.name == "SWAP":
                self._draw_swap(ax, x, g.qubits)
            elif g.name == "MEASURE":
                for q in g.qubits:
                    self._draw_measure(ax, x, -q, box_facecolor)
            else:  # generic labelled gate (single or multi‑qubit)
                label = g.label or g.name
                if g.label is None and g.params:
                    if len(g.params) == 1:
                        label += f"({g.params[0]:.2f})"
                    else:
                        label += str(tuple(g.params))
                if len(g.qubits) == 1:
                    self._draw_box(ax, x, -g.qubits[0], label, box_facecolor)
                else:
                    self._draw_multi_box(ax, x, g.qubits, label, box_facecolor)

        # Final cosmetics -------------------------------------------
        ax.set_axis_off()
        ax.set_xlim(-1, n_cols + 1.5)
        ax.set_ylim(-(self.n_qubits - 1) - 1, 0.5)
        ax.set_aspect("equal")
        plt.tight_layout()
        return fig, ax

    # ------------------------------------------------------------------
    # Validation helper
    def _validate_qubits(self, qubits: Sequence[int]):
        bad = [q for q in qubits if q < 0 or q >= self.n_qubits]
        if bad:
            raise IndexError(f"Qubit index/indices out of range: {bad}")

    # ------------------------------------------------------------------
    # Primitive drawing helpers ----------------------------------------
    @staticmethod
    def _draw_box(ax: plt.Axes, x: float, y: float, text: str, face: str):
        size = 0.4
        rect = Rectangle(
            (x - size, y - size),
            2 * size,
            2 * size,
            edgecolor="black",
            facecolor=face,
            lw=1,
            zorder=2,
        )
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center", fontsize=7, zorder=3)

    @staticmethod
    def _draw_multi_box(ax: plt.Axes, x: float, qubits: Sequence[int], text: str, face: str):
        y_top = -min(qubits)
        y_bot = -max(qubits)
        width = 0.8
        rect = Rectangle(
            (x - width / 2, y_bot - 0.4),
            width,
            y_top - y_bot + 0.8,
            edgecolor="black",
            facecolor=face,
            lw=1,
            zorder=2,
        )
        ax.add_patch(rect)
        ax.text(
            x,
            (y_top + y_bot) / 2,
            text,
            ha="center",
            va="center",
            fontsize=7,
            rotation=90 if len(qubits) > 3 else 0,
            zorder=3,
        )

    @staticmethod
    def _draw_cnot(ax: plt.Axes, x: float, qubits: Tuple[int, int]):
        control, target = qubits
        cy, ty = -control, -target
        ax.add_patch(Circle((x, cy), 0.1, fill=True, color="black"))
        ax.add_line(Line2D([x, x], [cy, ty], lw=1, zorder=0))
        ax.add_patch(Circle((x, ty), 0.18, fill=False, edgecolor="black", lw=1))
        ax.add_line(Line2D([x, x], [ty - 0.18, ty + 0.18], lw=1))
        ax.add_line(Line2D([x - 0.18, x + 0.18], [ty, ty], lw=1))

    @staticmethod
    def _draw_cz(ax: plt.Axes, x: float, qubits: Tuple[int, int]):
        control, target = qubits
        cy, ty = -control, -target
        ax.add_patch(Circle((x, cy), 0.1, fill=True, color="black"))
        ax.add_line(Line2D([x, x], [cy, ty], color="black", lw=1, zorder=0))
        ax.add_patch(Circle((x, ty), 0.1, fill=True, color="black", lw=1))

    @staticmethod
    def _draw_swap(ax: plt.Axes, x: float, qubits: Tuple[int, int]):
        y1, y2 = -qubits[0], -qubits[1]
        cross_size = 0.1
        for y in (y1, y2):
            ax.add_line(
                Line2D([x - cross_size, x + cross_size], [y - cross_size, y + cross_size], lw=1)
            )
            ax.add_line(
                Line2D([x - cross_size, x + cross_size], [y + cross_size, y - cross_size], lw=1)
            )
        ax.add_line(Line2D([x, x], [y1, y2], lw=1, zorder=0))

    @staticmethod
    def _draw_measure(ax, x: float, y: float, face: str = "#ffffff"):
        """
        Draw the standard measurement 'meter' symbol:
        """
        size = 0.4
        r = 0.2  # radius of the semicircle
        rect = Rectangle(
            (x - size, y - size),
            2 * size,
            2 * size,
            edgecolor="black",
            facecolor=face,
            lw=1,
            zorder=2,
        )
        ax.add_patch(rect)
        ax.add_patch(Arc((x, y - r / 2), 2 * r, 2 * r, theta1=0, theta2=180, lw=1, zorder=3))
        # pointer (a simple line at ~45°)
        ax.add_line(
            Line2D(
                [x, x + 1.0 * r], [y - r / 2, y + 1.0 * r - r / 2], color="black", lw=1, zorder=3
            )
        )

    # --------------------------------------------------------------


if __name__ == "__main__":
    c = QuantumCircuit(6)
    c.h(0)
    c.x(2, step=1)
    c.rx(3, 0.5, step=1)

    c.z90(0, step=3)
    c.z(2, step=3)
    c.custom([3, 4, 5], "Custom\nGate", step=3)
    c.cx(4, 5, step=2)
    c.cz(1, 3, step=2)
    c.swap(4, 5, step=4)
    c.custom(0, "Custom\nGate", step=2)
    c.measure([0, 1, 2], step=5)
    c.draw(box_facecolor="#eeeeee")
    plt.show()
