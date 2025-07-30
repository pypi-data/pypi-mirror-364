import numpy as np
from .loss import mean_squared_error

class NeuralNetwork:
    def __init__(self):
        self.layers = []
        self.learning_rate = 0.1

    def add(self, layer):
        if self.layers:
            prev_units = self.layers[-1].units
            layer.initialize(prev_units)
        elif layer.input_dim is not None:
            layer.initialize(layer.input_dim)
        else:
            raise ValueError("First hidden layer must define input_dim")
        self.layers.append(layer)

    def compile(self, learning_rate=0.1):
        self.learning_rate = learning_rate

    def predict(self, x):
        for layer in self.layers:
            x = layer.feedforward(x)
        return x

    def train(self, X, y, epochs=50):
        y = y.reshape(-1, 1)
        for epoch in range(epochs):
            network_output = self.predict(X)
            loss = mean_squared_error(network_output, y)
            grad = 2 * (network_output - y) / y.shape[0]

            for layer in reversed(self.layers):
                grad = layer.backpropagation(grad, self.learning_rate)

            print(f"Epoch {epoch}, Loss: {loss:.4f}")
