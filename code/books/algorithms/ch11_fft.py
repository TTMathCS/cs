"""Chapter 11: the fast Fourier transform and fast polynomial multiplication."""
import cmath
import random


def fft(a, invert=False):
    """Recursive Cooley-Tukey FFT; len(a) must be a power of two."""
    n = len(a)
    if n == 1:
        return list(a)
    even = fft(a[0::2], invert)
    odd = fft(a[1::2], invert)
    sign = 1 if invert else -1
    out = [0] * n
    for k in range(n // 2):
        w = cmath.exp(sign * 2j * cmath.pi * k / n)   # k-th power of a primitive n-th root
        t = w * odd[k]
        out[k] = even[k] + t                          # the butterfly
        out[k + n // 2] = even[k] - t
    return out


def poly_mul(p, q):
    """Coefficients of p*q (lists, lowest degree first) via the FFT."""
    need = len(p) + len(q) - 1
    n = 1
    while n < need:
        n *= 2
    fp = fft(p + [0] * (n - len(p)))
    fq = fft(q + [0] * (n - len(q)))
    values = [x * y for x, y in zip(fp, fq)]          # multiply point values
    coeffs = fft(values, invert=True)                 # interpolate back
    return [round((c / n).real) for c in coeffs[:need]]


def naive_mul(p, q):
    r = [0] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            r[i + j] += x * y
    return r


def big_multiply(x, y):
    """Multiply integers by treating their decimal digits as polynomial coefficients."""
    dx = [int(c) for c in reversed(str(x))]
    dy = [int(c) for c in reversed(str(y))]
    prod = poly_mul(dx, dy)
    carry, digits = 0, []
    for c in prod:
        carry += c
        digits.append(carry % 10)
        carry //= 10
    while carry:
        digits.append(carry % 10)
        carry //= 10
    return int("".join(map(str, reversed(digits))))


if __name__ == "__main__":
    a = [1, 2, 3, 4]
    print("FFT of", a, "=", [complex(round(z.real, 6), round(z.imag, 6)) for z in fft(a)])
    p, q = [1, 2, 3], [4, 5]           # (1 + 2x + 3x^2)(4 + 5x)
    print("(1 + 2x + 3x^2)(4 + 5x) coefficients:", poly_mul(p, q), " naive:", naive_mul(p, q))
    print("1234 * 5678 =", big_multiply(1234, 5678))

    random.seed(1965)
    ok = True
    for _ in range(50):
        p = [random.randint(-50, 50) for _ in range(random.randint(1, 60))]
        q = [random.randint(-50, 50) for _ in range(random.randint(1, 60))]
        ok &= poly_mul(p, q) == naive_mul(p, q)
    x = random.getrandbits(3000)
    y = random.getrandbits(3000)
    print("50 random polynomial products agree with the naive method:", ok)
    print("two 3000-bit numbers (about 900 digits) multiplied by FFT correctly:",
          big_multiply(x, y) == x * y)
