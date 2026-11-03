"""Chapter 16: vanishing and exploding signals in a deep network, and how the initial weight scale fixes them."""
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")   # small matrices: one thread is faster than many
import numpy as np
from ch16_nn import Linear, ReLU, Tanh, Sigmoid


def probe(act, init, depth=30, width=100, seed=0):
    """Push a batch forward through `depth` layers, then a gradient backward.
    Returns the std of the activations and the norm of the gradient arriving at each layer's input."""
    rng = np.random.default_rng(seed)
    layers = [(Linear(width, width, rng, init), act()) for _ in range(depth)]
    h = rng.normal(size=(256, width))
    stds = []
    for lin, a in layers:
        h = a.forward(lin.forward(h))
        stds.append(h.std())
    g = rng.normal(size=h.shape) / np.sqrt(h.size)        # a random gradient of length about 1 at the top
    norms = []
    for lin, a in reversed(layers):
        g = lin.backward(a.backward(g))
        norms.append(np.linalg.norm(g))
    return stds, norms[::-1]


if __name__ == "__main__":
    width = 100
    configs = [
        ("sigmoid, Xavier", Sigmoid, "xavier"),
        ("tanh, std 0.05 ", Tanh, 0.05),
        ("tanh, std 0.3  ", Tanh, 0.3),
        ("tanh, Xavier   ", Tanh, "xavier"),
        ("ReLU, std 0.2  ", ReLU, 0.2),
        ("ReLU, Xavier   ", ReLU, "xavier"),
        ("ReLU, He       ", ReLU, "he"),
    ]
    print(f"30 layers of width {width}, batch of 256 standard normal inputs")
    print(f"Xavier std = sqrt(2/(n_in+n_out)) = {np.sqrt(2 / (2 * width)):.3f};  He std = sqrt(2/n_in) = {np.sqrt(2 / width):.3f}")
    results = [(name, *probe(act, init)) for name, act, init in configs]
    print("\nForward: standard deviation of the activations after layer")
    print("                          1         10         20         30")
    for name, s, _ in results:
        print(f"  {name} " + "  ".join(f"{s[i]:9.2e}" for i in (0, 9, 19, 29)))
    print("\nBackward: length of the gradient arriving at the input of layer")
    print("                          1         10         20         30")
    for name, _, g in results:
        print(f"  {name} " + "  ".join(f"{g[i]:9.2e}" for i in (0, 9, 19, 29)))
