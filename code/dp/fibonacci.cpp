#include <iostream>
#include <vector>
using namespace std;

long long calls = 0;

// Straight from the definition: exponential time, because the same values are worked out again and again.
long long fibNaive(int n) {
    calls++;
    return n < 2 ? n : fibNaive(n - 1) + fibNaive(n - 2);
}

vector<long long> memo(100, 0);

// Top-down: the same recursion, but each answer is remembered the first time (memoization).
long long fibMemo(int n) {
    if (n < 2) return n;
    if (memo[n] != 0) return memo[n];
    return memo[n] = fibMemo(n - 1) + fibMemo(n - 2);
}

// Bottom-up: fill a table from the smallest case upwards (tabulation).
long long fibTable(int n) {
    vector<long long> f(n + 1, 0);
    if (n > 0) f[1] = 1;
    for (int i = 2; i <= n; i++) f[i] = f[i - 1] + f[i - 2];
    return f[n];
}

// Bottom-up with only the last two values kept: O(1) memory.
long long fibTwo(int n) {
    long long a = 0, b = 1;                          // F(i), F(i+1)
    for (int i = 0; i < n; i++) { long long t = a + b; a = b; b = t; }
    return a;
}

int main() {
    long long f20 = fibNaive(20);
    cout << f20 << " " << calls << "\n";
    cout << fibMemo(50) << " " << fibTable(50) << " " << fibTwo(50) << "\n";
    cout << "[";
    for (int i = 0; i <= 10; i++) cout << (i ? ", " : "") << fibTwo(i);
    cout << "]\n";
}
