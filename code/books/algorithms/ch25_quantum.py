# Chapter 25: quantum algorithms simulated on a classical computer (small sizes only).
# Grover search as a state vector of N amplitudes; and Shor's period finding for N = 15:
# the quantum Fourier transform's output distribution, then the classical post-processing.
import cmath
import math
from fractions import Fraction


def grover(n_qubits, marked, iterations):
    N = 2 ** n_qubits
    amp = [1 / math.sqrt(N)] * N                    # uniform superposition
    history = []
    for t in range(iterations + 1):
        history.append(amp[marked] ** 2)            # probability of measuring the answer
        amp[marked] = -amp[marked]                  # oracle: flip the sign of the answer
        mean = sum(amp) / N
        amp = [2 * mean - a for a in amp]           # diffusion: reflect about the mean
    return history


for n in (4, 8, 10):
    N = 2 ** n
    best = round(math.pi / 4 * math.sqrt(N))
    h = grover(n, marked=3, iterations=2 * best)
    print(f"N = {N:5d}: best iteration count ~ (pi/4)sqrt(N) = {best:2d}, "
          f"success probability there {h[best]:.4f}; at twice that {h[2 * best]:.4f}; "
          f"classical needs about N/2 = {N // 2} guesses")
print()

# Shor for N = 15 with a = 7.  The quantum part samples k from a distribution peaked
# at multiples of Q/r, where r is the order of a mod N.  We compute that distribution.
N, a, Q = 15, 7, 256                                # Q = 2^8 >= N^2
values = [pow(a, x, N) for x in range(Q)]
c = values[0]                                       # suppose the measurement of f gave a^0 = 1
xs = [x for x in range(Q) if values[x] == c]
prob = []
for k in range(Q):
    s = sum(cmath.exp(2j * math.pi * x * k / Q) for x in xs)
    prob.append(abs(s) ** 2 / (len(xs) * Q))
peaks = [(k, round(p, 4)) for k, p in enumerate(prob) if p > 1e-9]
print(f"Shor, N = {N}, a = {a}: after measuring f(x) = {c}, the register holds x in {xs[:5]}...")
print(f"  QFT output: nonzero probabilities only at {peaks}")
for k, _ in peaks[1:]:
    frac = Fraction(k, Q).limit_denominator(N)      # continued fractions
    r = frac.denominator
    print(f"  measured k = {k}: k/Q = {k}/{Q} ~ {frac}, candidate order r = {r}, "
          f"check {a}^{r} mod {N} = {pow(a, r, N)}")
r = 4
p, q = math.gcd(pow(a, r // 2) - 1, N), math.gcd(pow(a, r // 2) + 1, N)
print(f"  r = {r} is even: gcd({a}^{r // 2} - 1, {N}) = {p}, gcd({a}^{r // 2} + 1, {N}) = {q}  ->  {N} = {p} x {q}")
