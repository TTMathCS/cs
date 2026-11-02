#include <iostream>
#include <vector>
using namespace std;

// Returns an index of target in the sorted vector a, or -1 if it is not there.
int binarySearch(const vector<int>& a, int target) {
    int lo = 0, hi = (int)a.size() - 1;              // the target, if present, is in a[lo..hi]
    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;                // not (lo + hi) / 2, which can overflow
        if (a[mid] == target) return mid;
        if (a[mid] < target) lo = mid + 1;           // everything up to mid is too small
        else hi = mid - 1;                           // everything from mid on is too big
    }
    return -1;
}

// Returns the first index i with a[i] >= target (a.size() if there is none). Same as std::lower_bound.
int lowerBound(const vector<int>& a, int target) {
    int lo = 0, hi = a.size();                       // the answer is in [lo, hi]
    while (lo < hi) {
        int mid = lo + (hi - lo) / 2;
        if (a[mid] < target) lo = mid + 1;
        else hi = mid;
    }
    return lo;
}

int main() {
    vector<int> a = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};
    cout << binarySearch(a, 23) << " " << binarySearch(a, 2) << " " << binarySearch(a, 91) << " " << binarySearch(a, 7) << "\n";
    vector<int> b = {1, 3, 3, 3, 7, 9};
    cout << lowerBound(b, 3) << " " << lowerBound(b, 4) << " " << lowerBound(b, 0) << " " << lowerBound(b, 10) << "\n";
    cout << lowerBound(b, 4) - lowerBound(b, 3) << "\n";   // how many 3s
}
