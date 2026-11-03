"""Chapter 15: XOR. No single neuron can do it; a hidden layer can. A 2-2-1 network by hand,
then the same shape trained with backpropagation written out in matrices, with a gradient check."""
import numpy as np

X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], float)
y = np.array([0, 1, 1, 0], float)


def sigmoid(a):
    return 1.0 / (1.0 + np.exp(-a))


def perceptron(X, y, epochs=100):
    """Rosenblatt's rule; on XOR it never stops making mistakes."""
    w, b = np.zeros(2), 0.0
    for _ in range(epochs):
        errors = 0
        for xi, yi in zip(X, y):
            pred = float(w @ xi + b > 0)
            if pred != yi:
                w += (yi - pred) * xi
                b += yi - pred
                errors += 1
    return errors


def forward(params, X):
    W1, b1, W2, b2 = params
    A1 = X @ W1 + b1            # pre-activations of the hidden layer (n by 2)
    H = sigmoid(A1)             # hidden activations
    A2 = H @ W2 + b2            # output pre-activation (n by 1)
    return A1, H, A2, sigmoid(A2)


def loss_and_grads(params, X, y):
    """Mean binary cross-entropy and its gradients by backpropagation."""
    W1, b1, W2, b2 = params
    n = len(X)
    A1, H, A2, P = forward(params, X)
    p = P[:, 0]
    loss = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
    dA2 = (P - y[:, None]) / n  # sigmoid + cross-entropy: dL/da = p - y
    dW2 = H.T @ dA2
    db2 = dA2.sum(0)
    dH = dA2 @ W2.T
    dA1 = dH * H * (1 - H)      # sigmoid'(a) = s(a)(1 - s(a))
    dW1 = X.T @ dA1
    db1 = dA1.sum(0)
    return loss, [dW1, db1, dW2, db2]


if __name__ == "__main__":
    print("1. The perceptron on XOR: mistakes in the 100th pass over the data =", perceptron(X, y))

    print("\n2. A hand-made network: h1 = step(x1 + x2 - 0.5) (OR), h2 = step(x1 + x2 - 1.5) (AND),"
          " out = step(h1 - h2 - 0.5)")
    step = lambda a: (a > 0).astype(float)
    H = step(X @ np.array([[1, 1], [1, 1]], float) + np.array([-0.5, -1.5]))
    out = step(H @ np.array([1.0, -1.0]) - 0.5)
    for xi, hi, oi in zip(X, H, out):
        print(f"  x = {xi.astype(int).tolist()}  hidden = {hi.astype(int).tolist()}  output = {int(oi)}")

    rng = np.random.default_rng(0)
    params = [rng.normal(size=(2, 2)), np.zeros(2), rng.normal(size=(2, 1)), np.zeros(1)]

    print("\n3. Gradient check: backpropagation against finite differences (h = 1e-6)")
    loss, grads = loss_and_grads(params, X, y)
    worst = 0.0
    for P, G in zip(params, grads):
        for idx in np.ndindex(P.shape):
            old = P[idx]
            P[idx] = old + 1e-6
            up = loss_and_grads(params, X, y)[0]
            P[idx] = old - 1e-6
            down = loss_and_grads(params, X, y)[0]
            P[idx] = old
            worst = max(worst, abs((up - down) / 2e-6 - G[idx]))
    print(f"  largest difference over all 9 parameters: {worst:.1e}")

    print("\n4. Training the 2-2-1 sigmoid network by gradient descent, learning rate 2")
    for step_no in range(1, 5001):
        loss, grads = loss_and_grads(params, X, y)
        for P, G in zip(params, grads):
            P -= 2.0 * G
        if step_no in (1, 10, 100, 500, 1000, 5000):
            print(f"  step {step_no:5d}: loss {loss:.4f}")
    print("  outputs:", np.round(forward(params, X)[3][:, 0], 3).tolist())
