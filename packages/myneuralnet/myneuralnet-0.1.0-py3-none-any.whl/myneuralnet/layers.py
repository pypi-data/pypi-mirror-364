import numpy as np
from .activations import activation_functions

class Layer:
    def __init__(self, units, activation_function="linear", input_dim=None):
        self.units = units
        self.activation_name = activation_function
        self.activation, self.activation_derivative = activation_functions[activation_function]
        self.input_dim = input_dim
        self.weight = None
        self.bias = None

    def initialize(self, input_dim):
        self.weight = np.random.randn(input_dim, self.units)
        self.bias = np.zeros((1, self.units))

    def feedforward(self, inputs):
        self.inputs = inputs
        self.weighted_sum = np.dot(inputs, self.weight) + self.bias
        self.output = self.activation(self.weighted_sum)
        return self.output

    def backpropagation(self, grad_output, learning_rate):
        grad_L_wrt_weighted_sum = grad_output * self.activation_derivative(self.weighted_sum)
        grad_L_wrt_weight = np.dot(self.inputs.T, grad_L_wrt_weighted_sum)
        grad_L_wrt_bias = np.sum(grad_L_wrt_weighted_sum, axis=0, keepdims=True)
        grad_L_wrt_input = np.dot(grad_L_wrt_weighted_sum, self.weight.T)

        self.weight -= learning_rate * grad_L_wrt_weight
        self.bias -= learning_rate * grad_L_wrt_bias

        return grad_L_wrt_input
