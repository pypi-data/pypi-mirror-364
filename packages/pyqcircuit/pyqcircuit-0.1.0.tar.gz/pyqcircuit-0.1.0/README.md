# pyqcircuit

*A tiny pure‑Python helper for drawing quantum‑circuit diagrams with Matplotlib.*

---

## Why?

Most open‑source quantum SDKs bundle heavyweight drawing stacks or require you
to adopt their full IR just to get a circuit picture. **pyqcircuit**
keeps things… well, *simple*: with ***zero*** dependencies
beyond Matplotlib.

---

## Installation

```bash
pip install pyqcircuit             # if you don’t already have it
```
---

## Quick demo

```python
from simple_quantum_draw import QuantumCircuit

qc = QuantumCircuit(3)
qc.h(0)
qc.x(2, step=1)             # share column 1
qc.custom([0, 2], "Foo")     # tall box spanning q0–q2
qc.cx(0, 1, step=3)

qc.draw(box_facecolor="#ffe680",
        wire_labels=["|0⟩", "|+⟩", "|1⟩"])
```

---

## Features

| Category              | Highlights                                                                                     |
| --------------------- |------------------------------------------------------------------------------------------------|
| **Lightweight**       | Single file; no quantum SDKs; pure Python 3.                                                   |
| **Gate set**          | H, X/Y/Z, S, T, ½‑rotations (`X90` etc.), arbitrary `R_x/y/z(θ)`, CNOT, CZ, SWAP, measurement. |
| **Custom gates**      | `qc.custom(qubits, "LABEL")` draws one‑ or multi‑qubit labelled boxes.                         |
| **Flexible layout**   | Explicit `step=` pinning or automatic sequential placement.                                    |
| **Styling**           | Global box colour (`box_facecolor`), wire labels (pass `wire_labels=[…]`).                     |
| **Matplotlib native** | Full access to `fig, ax` for annotation, export, theming.                                      |

---

## API primer

| Call                    | Effect                                  |
| ----------------------- | --------------------------------------- |
| `qc.h(0)`               | One‑qubit Hadamard in next free column. |
| `qc.x(1, step=2)`       | X gate pinned to column 2.              |
| `qc.cx(0, 1)`           | CNOT; control on q0, target on q1.      |
| `qc.custom([0,2], "U")` | One tall box spanning q0…q2.            |
| `qc.measure([0,1])`     | Standard meter symbol on listed qubits. |

---

## Testing & baselines

The **`tests/`** package uses plain `pytest`, `numpy`, and `Pillow`.
Pixel‑perfect regression tests compare freshly rendered figures against PNG
baselines stored in `tests/baseline/`.

```bash
# create / refresh baseline images
env GENERATE=1 pytest -q tests/test_draw_baselines.py

# run the full test suite
pytest
```
---

## Contributing

1. Fork → hack → PR.
2. Ensure `pytest` passes **without** regenerating baselines.
3. Stick to the existing style.

Bug reports and feature ideas welcome in Issues.
