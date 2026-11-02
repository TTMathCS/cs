def gcd(a, b):
    """Euclid's algorithm: gcd(a, b) = gcd(b, a mod b), until the second number is 0."""
    while b:
        a, b = b, a % b
    return a


def ext_gcd(a, b):
    """Extended Euclid: returns (g, x, y) with a*x + b*y = g = gcd(a, b)."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)            # b*x1 + (a mod b)*y1 = g
    return g, y1, x1 - (a // b) * y1         # rewrite a mod b as a - (a // b)*b


def lcm(a, b):
    return a // gcd(a, b) * b                # divide first, so the product does not grow too big


def mod_inverse(a, m):
    """The x with a*x = 1 (mod m), or -1 if there is none (when gcd(a, m) > 1)."""
    g, x, _ = ext_gcd(a, m)
    return x % m if g == 1 else -1


if __name__ == "__main__":
    print(gcd(1071, 462), gcd(462, 1071), gcd(17, 5), gcd(0, 9))
    print(*ext_gcd(240, 46))
    print(lcm(4, 6), lcm(687, 365))
    print(mod_inverse(3, 11), mod_inverse(10, 17), mod_inverse(6, 9))
