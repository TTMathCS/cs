#include <algorithm>
#include <iostream>
#include <vector>
using namespace std;

// Loads packages in order onto one ship per day; returns how many days that takes.
int daysNeeded(const vector<int>& weights, long long capacity) {
    int days = 1;
    long long load = 0;
    for (int w : weights) {
        if (load + w > capacity) { days++; load = 0; }    // does not fit today: start a new day
        load += w;
    }
    return days;
}

// The smallest ship capacity that moves every package, in order, within d days.
long long minCapacity(const vector<int>& weights, int d) {
    long long lo = 0, hi = 0;
    for (int w : weights) { lo = max<long long>(lo, w); hi += w; }  // lo may be too small; hi works
    while (lo < hi) {
        long long mid = (lo + hi) / 2;
        if (daysNeeded(weights, mid) <= d) hi = mid;       // mid works: the answer is mid or smaller
        else lo = mid + 1;                                 // mid fails: the answer is bigger
    }
    return lo;
}

// The largest whole number r with r * r <= n.
long long isqrt(long long n) {
    long long lo = 0, hi = min(n, 3037000499LL);           // 3037000499^2 still fits in 64 bits
    while (lo < hi) {
        long long mid = lo + (hi - lo + 1) / 2;            // round up, so lo = mid makes progress
        if (mid * mid <= n) lo = mid;
        else hi = mid - 1;
    }
    return lo;
}

int main() {
    cout << minCapacity({1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 5) << "\n";
    cout << minCapacity({3, 2, 2, 4, 1, 4}, 3) << "\n";
    cout << minCapacity({1, 2, 3, 1, 1}, 4) << "\n";
    cout << isqrt(0) << " " << isqrt(15) << " " << isqrt(16) << " " << isqrt(1000000007LL) << "\n";
}
