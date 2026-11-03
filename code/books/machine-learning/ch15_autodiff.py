"""Chapter 15: a tiny reverse-mode automatic differentiation engine on scalars, and an MLP built on it."""
import math
import random


class Value:
    """A number that remembers how it was computed, so that gradients can flow back through it."""

    def __init__(self, data, parents=(), op=""):
        self.data = float(data)
        self.grad = 0.0
        self._parents = parents
        self._backward = lambda: None     # pushes self.grad to the parents' grads
        self.op = op

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")
        def backward():
            self.grad += out.grad         # d(a+b)/da = 1
            other.grad += out.grad
        out._backward = backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")
        def backward():
            self.grad += other.data * out.grad   # d(ab)/da = b
            other.grad += self.data * out.grad
        out._backward = backward
        return out

    def __pow__(self, k):                 # k is a plain number
        out = Value(self.data ** k, (self,), f"**{k}")
        def backward():
            self.grad += k * self.data ** (k - 1) * out.grad
        out._backward = backward
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")
        def backward():
            self.grad += (1 - t * t) * out.grad
        out._backward = backward
        return out

    def relu(self):
        out = Value(max(0.0, self.data), (self,), "relu")
        def backward():
            self.grad += (self.data > 0) * out.grad
        out._backward = backward
        return out

    def exp(self):
        e = math.exp(self.data)
        out = Value(e, (self,), "exp")
        def backward():
            self.grad += e * out.grad
        out._backward = backward
        return out

    def log(self):
        out = Value(math.log(self.data), (self,), "log")
        def backward():
            self.grad += out.grad / self.data
        out._backward = backward
        return out

    __radd__ = __add__
    __rmul__ = __mul__
    def __neg__(self): return self * -1
    def __sub__(self, other): return self + (-other)
    def __rsub__(self, other): return (-self) + other
    def __truediv__(self, other): return self * other ** -1

    def backward(self):
        """Visit nodes in reverse topological order and apply the chain rule at each."""
        order, seen = [], set()
        def visit(v):
            if id(v) not in seen:
                seen.add(id(v))
                for p in v._parents:
                    visit(p)
                order.append(v)
        visit(self)
        self.grad = 1.0
        for v in reversed(order):
            v._backward()
        return len(order)


class MLP:
    def __init__(self, sizes, rng):
        self.layers = []
        for fan_in, fan_out in zip(sizes, sizes[1:]):
            W = [[Value(rng.gauss(0, 1 / math.sqrt(fan_in))) for _ in range(fan_in)] for _ in range(fan_out)]
            b = [Value(0.0) for _ in range(fan_out)]
            self.layers.append((W, b))

    def __call__(self, x):
        for li, (W, b) in enumerate(self.layers):
            x = [sum((wi * xi for wi, xi in zip(row, x)), bias) for row, bias in zip(W, b)]
            if li < len(self.layers) - 1:
                x = [v.tanh() for v in x]
        return x[0]

    def parameters(self):
        return [p for W, b in self.layers for row in W for p in row] + [p for W, b in self.layers for p in b]


if __name__ == "__main__":
    print("1. f(a, b) = (a * b + b) * tanh(a) at a = 2, b = -3")
    a, b = Value(2.0), Value(-3.0)
    f = (a * b + b) * a.tanh()
    nodes = f.backward()
    print(f"  f = {f.data:.6f}   df/da = {a.grad:.6f}   df/db = {b.grad:.6f}   ({nodes} nodes in the graph)")
    h = 1e-6
    fa = lambda a_, b_: (a_ * b_ + b_) * math.tanh(a_)
    print(f"  finite differences:   df/da = {(fa(2 + h, -3) - fa(2 - h, -3)) / (2 * h):.6f}"
          f"   df/db = {(fa(2, -3 + h) - fa(2, -3 - h)) / (2 * h):.6f}")

    print("\n2. A 2-6-6-1 MLP on the engine, trained on 40 points of two interleaved half-moons")
    rng = random.Random(0)
    data = []
    for i in range(40):
        t = math.pi * rng.random()
        if i % 2 == 0:
            x, label = (math.cos(t), math.sin(t)), 1.0
        else:
            x, label = (1 - math.cos(t), 0.5 - math.sin(t)), -1.0
        data.append(((x[0] + rng.gauss(0, 0.1), x[1] + rng.gauss(0, 0.1)), label))
    net = MLP([2, 6, 6, 1], rng)
    params = net.parameters()
    print(f"  {len(params)} parameters")
    for epoch in range(1, 51):
        # hinge-like smooth loss: softplus(-y * score) = log(1 + exp(-y * score)), averaged
        loss = sum(((-label * net(x)).exp() + 1).log() for x, label in data) * (1.0 / len(data))
        for p in params:
            p.grad = 0.0
        loss.backward()
        for p in params:
            p.data -= 0.5 * p.grad
        if epoch in (1, 10, 20, 30, 50):
            acc = sum((net(x).data > 0) == (label > 0) for x, label in data) / len(data)
            print(f"  epoch {epoch:3d}: loss {loss.data:.4f}  training accuracy {acc:.2f}")
