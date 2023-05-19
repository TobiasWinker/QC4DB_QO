# Qiskit Circuit imports
from qiskit.circuit.library import TwoLocal

# Qiskit imports
import qiskit as qk

# Qiskit Machine Learning imports


def encoding_circuit(inputs, num_qubits=4, type="singular", gate="rz", *args):

    qc = qk.QuantumCircuit(num_qubits)

    # Encode data with a rotation depending on parameter gate
    for i in range(len(inputs)):
        if gate == "rx" or gate == "x":
            qc.rx(inputs[i], i)
        if gate == "ry" or gate == "y":
            qc.ry(inputs[i], i)
        if gate == "rz" or gate == "z":
            qc.rz(inputs[i], i)

    return qc


def stringToCircuitList(string):
    result = []
    for c in string:
        result.append("r" + c)
    return result


# create a paramterized circuit (VQC)
def parametrized_circuit(num_qubits=4, reuploading=False, reps=2, insert_barriers=True, meas=False, calc="xyz", entangleGate="cz", entangleType="circular", encodingGate="rx", encodingType="singular"):

    qr = qk.QuantumRegister(num_qubits, 'qr')
    qc = qk.QuantumCircuit(qr)

    if meas:
        qr = qk.QuantumRegister(num_qubits, 'qr')
        cr = qk.ClassicalRegister(num_qubits, 'cr')
        qc = qk.QuantumCircuit(qr, cr)

    calcCircuits = stringToCircuitList(calc)

    if not reuploading:
        # we can use the TWoLocal circuit from qiskit machine learning

        # Define a vector containg Inputs as parameters (*not* to be optimized)
        inputs = qk.circuit.ParameterVector('x', num_qubits)

        # Encode classical input data
        qc.compose(encoding_circuit(inputs, num_qubits=num_qubits, gate=encodingGate, type=encodingType), inplace=True)
        if insert_barriers: qc.barrier()

        # Variational circuit
        qc.compose(TwoLocal(num_qubits, calcCircuits, entangleGate, entangleType, reps=reps, insert_barriers=insert_barriers, skip_final_rotation_layer=True), inplace=True)
        if insert_barriers: qc.barrier()

        # Add final measurements
        if meas: qc.measure(qr, cr)

    elif reuploading:
        # We have to build the circuit manual

        # Define a vector containg Inputs as parameters (*not* to be optimized)
        inputs = qk.circuit.ParameterVector('x', num_qubits)

        # Define a vector containng variational parameters
        theta = qk.circuit.ParameterVector('theta', len(calcCircuits) * num_qubits * reps)

        # Iterate for a number of repetitions
        for rep in range(reps):

            # Encode classical input data
            qc.compose(encoding_circuit(inputs, num_qubits=num_qubits), inplace=True)
            if insert_barriers: qc.barrier()

            # Variational circuit (does the same as TwoLocal from Qiskit)
            for qubit in range(num_qubits):
                i = 0
                for gate in calcCircuits:
                    layerOffset = len(calcCircuits) * num_qubits * rep
                    index = qubit + layerOffset + i * num_qubits
                    if gate == "rx":
                        qc.rx(theta[index], qubit)
                    if gate == "ry":
                        qc.ry(theta[index], qubit)
                    if gate == "rz":
                        qc.rz(theta[index], qubit)
                    i += 1
            if insert_barriers: qc.barrier()

            # Add entanglers (this code is for a circular entangler)
            qc.cx(qr[-1], qr[0])
            for qubit in range(num_qubits - 1):
                qc.cx(qubit, qubit + 1)
            if insert_barriers: qc.barrier()

        # Add final measurements
        if meas: qc.measure(qr, cr)

    return qc
