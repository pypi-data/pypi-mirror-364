import numpy as np

def sigmoid(x):
    return 1/(1+ np.exp(-x))

def derivative_sigmoid(x):
    return sigmoid(x) * (1 - sigmoid(x))

def relu(x):
    return np.maximum(0,x)

def derivative_relu(x):
    return (x>0).astype(float)

def linear(x):
    return x

def derivative_linear(x):
    return np.ones_like(x)

activation_functions = {
    "sigmoid": (sigmoid, derivative_sigmoid),
    "relu": (relu, derivative_relu),
    "linear": (linear, derivative_linear)
}