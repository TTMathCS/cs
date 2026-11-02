#include <algorithm>
#include <iostream>
#include <optional>
#include <utility>
#include <vector>
using namespace std;

// In the sorted vector a, finds positions i < j with a[i] + a[j] == target, if any.
optional<pair<int, int>> pairWithSum(const vector<int>& a, int target) {
    int i = 0, j = (int)a.size() - 1;
    while (i < j) {
        int s = a[i] + a[j];
        if (s == target) return make_pair(i, j);
        if (s < target) i++;                         // need a bigger sum: move the left pointer right
        else j--;                                    // need a smaller sum: move the right pointer left
    }
    return nullopt;
}

// Removes repeats from the sorted vector a in place; returns the new length.
int removeDuplicates(vector<int>& a) {
    if (a.empty()) return 0;
    int write = 1;                                   // a[0..write-1] holds the distinct values so far
    for (size_t read = 1; read < a.size(); read++)
        if (a[read] != a[write - 1]) a[write++] = a[read];
    a.resize(write);
    return write;
}

// Two walls of heights h[i], h[j] hold (j - i) * min(h[i], h[j]) water; returns the most.
int maxWater(const vector<int>& h) {
    int i = 0, j = (int)h.size() - 1, best = 0;
    while (i < j) {
        best = max(best, (j - i) * min(h[i], h[j]));
        if (h[i] < h[j]) i++;                        // the shorter wall limits us: only moving it can help
        else j--;
    }
    return best;
}

void printPair(const optional<pair<int, int>>& p) {
    if (p) cout << "(" << p->first << ", " << p->second << ")\n";
    else cout << "None\n";
}

int main() {
    printPair(pairWithSum({1, 2, 4, 7, 11, 15}, 15));
    printPair(pairWithSum({1, 2, 4, 7, 11, 15}, 10));
    vector<int> a = {1, 1, 2, 3, 3, 3, 4};
    int n = removeDuplicates(a);
    cout << n << " [";
    for (int i = 0; i < n; i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
    cout << maxWater({1, 8, 6, 2, 5, 4, 8, 3, 7}) << "\n";
}
