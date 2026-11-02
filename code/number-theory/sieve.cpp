#include <iostream>
#include <string>
#include <vector>
using namespace std;

// Sieve of Eratosthenes: isPrime[k] for every k from 0 to n.
vector<bool> sieve(int n) {
    vector<bool> isPrime(n + 1, true);
    isPrime[0] = false;
    if (n >= 1) isPrime[1] = false;
    for (long long p = 2; p * p <= n; p++)
        if (isPrime[p])
            for (long long k = p * p; k <= n; k += p) isPrime[k] = false;   // smaller multiples are done
    return isPrime;
}

// spf[k] = the smallest prime that divides k (for k >= 2): factor any k <= n in O(log k) steps.
vector<int> smallestFactors(int n) {
    vector<int> spf(n + 1);
    for (int k = 0; k <= n; k++) spf[k] = k;
    for (long long p = 2; p * p <= n; p++)
        if (spf[p] == p)                             // p is prime
            for (long long k = p * p; k <= n; k += p)
                if (spf[k] == k) spf[k] = p;
    return spf;
}

string factorize(int k, const vector<int>& spf) {
    string s = "[";
    for (bool first = true; k > 1; k /= spf[k], first = false) s += (first ? "" : ", ") + to_string(spf[k]);
    return s + "]";
}

int main() {
    vector<bool> isP = sieve(50);
    string s = "[";
    for (int k = 0; k <= 50; k++) if (isP[k]) s += (s.size() > 1 ? ", " : "") + to_string(k);
    cout << s << "]\n";
    int count = 0;
    for (bool b : sieve(1000000)) if (b) count++;
    cout << count << "\n";
    vector<int> spf = smallestFactors(10000);
    cout << factorize(360, spf) << " " << factorize(9973, spf) << " " << factorize(2024, spf) << "\n";
}
