import math
import torch
from math import pi
import numpy as np
# Qiskit imports
import qiskit as qk
from qiskit.utils import QuantumInstance
from qiskit.providers.aer import AerSimulator

# Qiskit Machine Learning imports
from qiskit_machine_learning.neural_networks import CircuitQNN
from qiskit_machine_learning.connectors import TorchConnector

from ML import layer
from ML import circuits


def classicalNN(settings={}, num_inputs=4, num_outputs=15):
    normLayer = layer.NormLayer()
    model = torch.nn.Sequential(
        torch.nn.Linear(num_inputs, 1000),
        torch.nn.Linear(1000, num_outputs),
        torch.nn.Sigmoid(),
        #torch.nn.ReLU(),
        normLayer)
    return model


# --------------------------------------------------
#                Quantum
# -------------------------------------------------


def vqc(settings={"features": "simple", "encoding": "rx", "reuploading": False, "reps": 5, "calc": "yz", "entangleType": "circular", "entangle": "cx", "reward": "rational"}, num_inputs=4, num_outputs=15):
    # Generate the Parametrized Quantum Circuit
    num_qubits_output = math.ceil(math.log2(num_outputs))
    num_qubits = max(num_inputs, num_qubits_output)
    qc = circuits.parametrized_circuit(num_qubits=num_qubits, reuploading=settings["reuploading"], reps=settings["reps"], calc=settings["calc"], entangleGate=settings["entangle"], entangleType=settings["entangleType"], encodingGate=settings["encoding"])

    # Fetch the parameters from the circuit and divide them in Inputs (X) and Trainable Parameters (params)
    X = list(qc.parameters)[:num_qubits]
    params = list(qc.parameters)[num_qubits:]

    # Select a quantum backend to run the simulation of the quantum circuit
    if settings["noisy"]:
        qk.IBMQ.load_account()
        #provider = qk.IBMQ.get_provider(hub='ibm-q')
        #realDevice = provider.get_backend('ibmq_manila')
        #backend = AerSimulator.from_backend(realDevice)
    else:
        backend = qk.Aer.get_backend('aer_simulator_statevector')
    qi = QuantumInstance(backend, shots=10000)

    # Create a Quantum Neural Network object
    qnn = CircuitQNN(qc, input_params=X, weight_params=params, quantum_instance=qi)

    # Connect to PyTorch
    initial_weights = (2 * pi * np.random.rand(qnn.num_weights) - pi)
    quantum_nn = TorchConnector(qnn, initial_weights)

    # build model
    model = torch.nn.Sequential()

    # pad input with zeros to num qubits
    if (num_qubits_output > num_inputs):
        print("Padding: " + str(num_qubits_output - num_inputs))
        paddingLayer = torch.nn.ConstantPad1d((0, num_qubits_output - num_inputs), 2.5 * math.pi)
        model.append(paddingLayer)

    # add quantum layer
    model.append(quantum_nn)

    # reduce number of states to number of outputs
    model.append(layer.CutOutputLayer(num_outputs))

    # norm layer
    model.append(layer.NormLayer())

    return model
