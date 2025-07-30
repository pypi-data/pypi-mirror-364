import pytest
from pyqcircuit import QuantumCircuit


def test_gate_counts_and_steps():
    qc = QuantumCircuit(2)
    qc.h(0)  # step 1
    qc.x(1, step=1)  # same column
    qc.cx(0, 1)  # step 2 (auto)
    qc.z(0, step=5)  # jump
    qc.z(1, step=5)

    # Order preserved
    assert len(qc._gates) == 5

    # Steps assigned as expected
    steps = [g.step for g in qc._gates]
    assert steps == [1, 1, 2, 5, 5]

    # Automatic counter kept in sync with manual jumps
    assert qc._current_step == 5


@pytest.mark.parametrize("bad_index", [-1, 3])
def test_validate_qubit_range(bad_index):
    qc = QuantumCircuit(2)
    with pytest.raises(IndexError):
        qc.h(bad_index)
