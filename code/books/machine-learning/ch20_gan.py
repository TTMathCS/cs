"""Chapter 20: a generative adversarial network in one dimension, from scratch.
The optimal discriminator D* = p_data / (p_data + p_g) checked numerically, the
value of the game at D* checked against -log 4 + 2 JSD, then a GAN trained with
alternating gradient steps."""
import numpy as np

rng = np.random.default_rng(2014)
sig = lambda s: 1 / (1 + np.exp(-s))
gauss = lambda x, m, s: np.exp(-0.5 * ((x - m) / s) ** 2) / (s * np.sqrt(2 * np.pi))
MU, SD = 4.0, 1.25                                 # the data: N(4, 1.25^2)


def feats(x):                                      # the log-ratio of two Gaussians is quadratic in x
    return np.stack([np.ones_like(x), x, x * x], 1)


def train_D(w, real, fake, lr, steps):
    for _ in range(steps):
        pr, pf = sig(feats(real) @ w), sig(feats(fake) @ w)
        grad = feats(real).T @ (pr - 1) / len(real) + feats(fake).T @ pf / len(fake)
        w = w - lr * grad
    return w


# ------------------------------------------- 1. the optimal discriminator
print("1. generator fixed at N(0, 1); train a quadratic logistic discriminator, compare with D*")
real, fake = rng.normal(MU, SD, 20000), rng.normal(0, 1, 20000)
w = train_D(np.zeros(3), real, fake, 0.02, 4000)
for x in (0.0, 1.5, 2.0, 2.5, 4.0):
    dstar = gauss(x, MU, SD) / (gauss(x, MU, SD) + gauss(x, 0, 1))
    print(f"   x = {x:3.1f}: trained D {sig(feats(np.array([x])) @ w)[0]:.3f}   D* {dstar:.3f}")

# -------------------------------------- 2. the value of the game at D*
xs = np.linspace(-10, 15, 200001); dx = xs[1] - xs[0]
pd, pg = gauss(xs, MU, SD), gauss(xs, 0, 1)
log_d = np.log(pd) - np.logaddexp(np.log(pd), np.log(pg))        # log D*, computed safely
log_1md = np.log(pg) - np.logaddexp(np.log(pd), np.log(pg))      # log (1 - D*)
V = np.sum(pd * log_d + pg * log_1md) * dx
m = (pd + pg) / 2
kl = lambda p, q: np.sum(p * np.log(p / q)) * dx
jsd = 0.5 * kl(pd, m) + 0.5 * kl(pg, m)
print()
print("2. value of the game at D*, by numerical integration")
print(f"   V(D*, G) = {V:.4f};  -log 4 + 2 JSD = {-np.log(4) + 2 * jsd:.4f};  JSD = {jsd:.4f} (at most log 2 = 0.6931)")

# ------------------------------------------------------------ 3. train a GAN
def train_gan(d_steps, steps=3000, lr_d=0.01, lr_g=0.01):
    a, b, w = 1.0, 0.0, np.zeros(3)
    for step in range(1, steps + 1):
        real = rng.normal(MU, SD, 256)
        z = rng.normal(size=256)
        w = train_D(w, real, a * z + b, lr_d, d_steps)         # discriminator steps
        x = a * z + b                                            # one generator step,
        s1 = w[1] + 2 * w[2] * x                                 # non-saturating loss -log D(G(z))
        gx = -(1 - sig(feats(x) @ w)) * s1                       # d/dx of -log D(x)
        a -= lr_g * np.mean(gx * z)
        b -= lr_g * np.mean(gx)
        if step % 500 == 0:
            print(f"   step {step:4d}: generator mean b = {b:5.2f}, std |a| = {abs(a):4.2f}")


print()
print(f"3. GAN: generator G(z) = a z + b, z ~ N(0, 1), from a = 1, b = 0; target mean {MU}, std {SD}")
for k in (1, 10):
    print(f"   {k} discriminator step(s) per generator step:")
    train_gan(k)
