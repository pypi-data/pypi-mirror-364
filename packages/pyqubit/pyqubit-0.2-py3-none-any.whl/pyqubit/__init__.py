import numpy as np

class Qubit:
    def __init__(self, state=None):
        # Initialize to |0> state if no state is provided
        if state is None:
            self.state = np.array([[1], [0]], dtype=complex)
        else:
            self.state = np.array(state, dtype=complex).reshape((2, 1))
            self.normalize()

    def normalize(self):
        norm = np.linalg.norm(self.state)
        if norm != 0:
            self.state = self.state / norm

    def apply_gate(self, gate):
        self.state = np.dot(gate, self.state)
        self.normalize()

    def x(self):
        X = np.array([[0, 1], [1, 0]], dtype=complex)
        self.apply_gate(X)

    def y(self):
        Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        self.apply_gate(Y)

    def z(self):
        Z = np.array([[1, 0], [0, -1]], dtype=complex)
        self.apply_gate(Z)

    def measure(self):
        probabilities = np.abs(self.state) ** 2
        probabilities = probabilities / np.sum(probabilities)
        return np.random.choice([0, 1], p=probabilities.flatten()) 