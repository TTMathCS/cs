#include <iostream>
#include <tuple>
using namespace std;

// Euclid's algorithm: gcd(a, b) = gcd(b, a mod b), until the second number is 0.
long long gcd(long long a, long long b) {
    while (b != 0) { long long t = a % b; a = b; b = t; }
    return a;
}

// Extended Euclid: returns {g, x, y} with a*x + b*y = g = gcd(a, b).
tuple<long long, long long, long long> extGcd(long long a, long long b) {
    if (b == 0) return {a, 1, 0};
    auto [g, x1, y1] = extGcd(b, a % b);             // b*x1 + (a mod b)*y1 = g
    return {g, y1, x1 - (a / b) * y1};               // rewrite a mod b as a - (a / b)*b
}

long long lcm(long long a, long long b) {
    return a / gcd(a, b) * b;                        // divide first, so the product does not grow too big
}

// The x with a*x = 1 (mod m), or -1 if there is none (when gcd(a, m) > 1).
long long modInverse(long long a, long long m) {
    auto [g, x, y] = extGcd(a, m);
    (void)y;
    return g == 1 ? ((x % m) + m) % m : -1;
}

int main() {
    cout << gcd(1071, 462) << " " << gcd(462, 1071) << " " << gcd(17, 5) << " " << gcd(0, 9) << "\n";
    auto [g, x, y] = extGcd(240, 46);
    cout << g << " " << x << " " << y << "\n";
    cout << lcm(4, 6) << " " << lcm(687, 365) << "\n";
    cout << modInverse(3, 11) << " " << modInverse(10, 17) << " " << modInverse(6, 9) << "\n";
}
