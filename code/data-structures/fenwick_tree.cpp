#include <iostream>
#include <vector>
using namespace std;

// Prefix sums with updates, both in O(log n). Positions are 1..n inside the tree.
struct Fenwick {
    int n;
    vector<long long> t;                             // t[i] holds the sum of the last lowbit(i) values up to i
    explicit Fenwick(int n) : n(n), t(n + 1, 0) {}

    // a[i] += delta, for i in 0..n-1.
    void add(int i, long long delta) {
        for (i++; i <= n; i += i & -i) t[i] += delta;   // jump to the next range that covers position i
    }

    // a[0] + ... + a[i-1].
    long long prefix(int i) const {
        long long s = 0;
        for (; i > 0; i -= i & -i) s += t[i];        // drop the lowest set bit: the ranges tile [1, i]
        return s;
    }

    // a[lo] + ... + a[hi - 1].
    long long rangeSum(int lo, int hi) const { return prefix(hi) - prefix(lo); }
};

int main() {
    vector<int> a = {5, 2, 9, -3, 5, 20, 10, -7};
    Fenwick f(a.size());
    for (size_t i = 0; i < a.size(); i++) f.add(i, a[i]);
    cout << "[";
    for (size_t i = 0; i <= a.size(); i++) cout << (i ? ", " : "") << f.prefix(i);
    cout << "]\n";
    cout << f.rangeSum(2, 6) << "\n";                // 9 - 3 + 5 + 20
    f.add(3, 10);                                    // a[3] becomes 7
    cout << f.rangeSum(2, 6) << " " << f.prefix(8) << "\n";
    cout << "[";
    for (int i = 1; i <= f.n; i++) cout << (i > 1 ? ", " : "") << f.t[i];
    cout << "]\n";
}
