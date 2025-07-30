# tests/test_draw.py
import pytest
from pyqcircuit import QuantumCircuit  # your new primitive‑based package
from .conftest import assert_fig_equal


@pytest.mark.parametrize("face", ["#ffe680", "#dddddd"])
def test_three_qubit_demo(face):
    qc = QuantumCircuit(3)
    gstyle = {"facecolor": face}

    qc.h(0, style=gstyle)  # step 1  (auto)
    qc.x(2, step=1, style=gstyle)  # share column 1
    qc.custom([0, 2], "Foo", style=gstyle)  # auto column 2
    qc.cx(0, 1, step=3, style=gstyle)  # explicit column 3

    fig, _ = qc.draw()  # no extra kwargs now
    assert_fig_equal(fig, f"demo_{face.strip('#')}")


def test_measure_symbol():
    """
    Single‑qubit circuit with a measurement symbol – signature unchanged.
    """
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure(0)
    fig, _ = qc.draw()
    # allow 1pixel tolerance for anti‑aliasing
    assert_fig_equal(fig, "measure_symbol", tol=1.0)
