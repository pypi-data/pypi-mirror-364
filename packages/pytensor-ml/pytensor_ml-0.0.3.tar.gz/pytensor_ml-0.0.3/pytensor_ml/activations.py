import pytensor.tensor as pt

from pytensor_ml.layers import Layer


class Activation(Layer): ...


class ReLU(Activation):
    def __call__(self, x: pt.TensorLike) -> pt.TensorVariable:
        out = pt.maximum(0, x)
        out.name = "ReLU"
        return out


class LeakyReLU(Activation):
    def __init__(self, negative_slope: pt.TensorLike = 0.01):
        self.negative_slope = negative_slope

    def __call__(self, x: pt.TensorLike) -> pt.TensorVariable:
        out = pt.switch(x > 0, x, -self.negative_slope * x)
        out.name = "LeakyReLU"
        return out


class Tanh(Activation):
    def __call__(self, x: pt.TensorLike) -> pt.TensorVariable:
        out = pt.tanh(x)
        out.name = "TanH"
        return out


class Sigmoid(Activation):
    def __call__(self, x: pt.TensorLike) -> pt.TensorVariable:
        out = pt.sigmoid(x)
        out.name = "Sigmoid"
        return out


class SoftPlus(Activation):
    def __call__(self, x: pt.TensorLike) -> pt.TensorVariable:
        out = pt.softplus(x)
        out.name = "SoftPlus"
        return out


class Softmax(Activation):
    def __init__(self, axis: int = -1):
        self.axis = axis

    def __call__(self, x: pt.TensorLike) -> pt.TensorVariable:
        out = pt.special.softmax(x, axis=self.axis)
        out.name = "Softmax"
        return out


__all__ = ["LeakyReLU", "ReLU", "Sigmoid", "Softmax", "Tanh"]
