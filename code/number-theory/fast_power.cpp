#include <array>
#include <iostream>
using namespace std;

// a to the power n with O(log n) multiplications (square and multiply).
long long power(long long a, long long n) {
    long long result = 1;
    while (n > 0) {
        if (n & 1) result *= a;                      // this binary digit of n is 1: include the current square
        a *= a;                                      // a, a^2, a^4, a^8, ...
        n >>= 1;
    }
    return result;
}

// a^n mod m, keeping every number below m.
long long powerMod(long long a, long long n, long long m) {
    long long result = 1 % m;
    a %= m;
    while (n > 0) {
        if (n & 1) result = result * a % m;
        a = a * a % m;
        n >>= 1;
    }
    return result;
}

using Mat = array<array<long long, 2>, 2>;

Mat matMult(const Mat& X, const Mat& Y) {
    return {{{X[0][0] * Y[0][0] + X[0][1] * Y[1][0], X[0][0] * Y[0][1] + X[0][1] * Y[1][1]},
             {X[1][0] * Y[0][0] + X[1][1] * Y[1][0], X[1][0] * Y[0][1] + X[1][1] * Y[1][1]}}};
}

// The nth Fibonacci number from the matrix [[1, 1], [1, 0]] to the power n.
long long fib(int n) {
    Mat result = {{{1, 0}, {0, 1}}}, M = {{{1, 1}, {1, 0}}};
    while (n > 0) {
        if (n & 1) result = matMult(result, M);
        n >>= 1;
        if (n > 0) M = matMult(M, M);                // skip the last squaring, which would overflow
    }
    return result[0][1];
}

int main() {
    cout << power(2, 10) << " " << power(3, 13) << " " << power(7, 0) << "\n";
    const long long MOD = 1000000007LL;
    cout << powerMod(2, 1000000, MOD) << " " << powerMod(3, MOD - 2, MOD) * 3 % MOD << "\n";
    cout << powerMod(5, 117, 19) << " " << fib(10) << " " << fib(90) << "\n";
}
