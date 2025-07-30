import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def holobit_to_circuit(holobit):
    """Convierte un ``Holobit`` en un ``QuantumCircuit`` de Qiskit."""
    quarks = holobit.quarks + holobit.antiquarks
    circuit = QuantumCircuit(len(quarks))
    for index, quark in enumerate(quarks):
        state = np.asarray(quark.estado, dtype=complex)
        norm = np.linalg.norm(state)
        if not np.isclose(norm, 1.0):
            state = state / norm
        circuit.initialize(state, index)
    return circuit


def execute_circuit(circuit):
    """Ejecuta el circuito y devuelve el ``Statevector`` resultante."""
    return Statevector.from_instruction(circuit)
