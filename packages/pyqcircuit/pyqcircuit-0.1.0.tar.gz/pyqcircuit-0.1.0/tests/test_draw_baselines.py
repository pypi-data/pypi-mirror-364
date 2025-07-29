import pytest
from pyqcircuit import QuantumCircuit

from .conftest import assert_fig_equal


@pytest.mark.parametrize("face", ["#ffe680", "#dddddd"])
def test_three_qubit_demo(face):
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.x(2, step=1)
    qc.custom([0, 2], "Foo")
    qc.cx(0, 1, step=3)
    fig, _ = qc.draw(box_facecolor=face, wire_labels=["|0>", "|+>", "|1>"])
    assert_fig_equal(fig, f"demo_{face.strip('#')}")


def test_measure_symbol():
    """Single‑qubit circuit with a measurement symbol."""
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure(0)
    fig, _ = qc.draw()
    assert_fig_equal(fig, "measure_symbol", tol=1.0)  # tiny anti‑aliasing wiggle room
