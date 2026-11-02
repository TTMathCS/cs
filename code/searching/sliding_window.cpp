#include <algorithm>
#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>
using namespace std;

// The largest sum of k consecutive values of a.
int maxSumWindow(const vector<int>& a, int k) {
    int window = 0;
    for (int i = 0; i < k; i++) window += a[i];
    int best = window;
    for (size_t i = k; i < a.size(); i++) {
        window += a[i] - a[i - k];                   // slide right: add the new value, drop the old one
        best = max(best, window);
    }
    return best;
}

// The length of the longest stretch of s with no repeated character.
int longestUnique(const string& s) {
    unordered_map<char, int> last;                   // where each character was last seen
    int left = 0, best = 0;                          // the window is s[left..right]
    for (int right = 0; right < (int)s.size(); right++) {
        auto it = last.find(s[right]);
        if (it != last.end() && it->second >= left) left = it->second + 1;  // repeat: shrink past it
        last[s[right]] = right;
        best = max(best, right - left + 1);
    }
    return best;
}

// The length of the shortest stretch of positive values with sum >= target (0 if none).
int shortestWithSum(const vector<int>& a, int target) {
    int left = 0, total = 0, n = a.size(), best = n + 1;
    for (int right = 0; right < n; right++) {
        total += a[right];                           // grow on the right ...
        while (total >= target) {                    // ... and shrink from the left while it still works
            best = min(best, right - left + 1);
            total -= a[left++];
        }
    }
    return best > n ? 0 : best;
}

int main() {
    cout << maxSumWindow({2, 1, 5, 1, 3, 2}, 3) << "\n";
    cout << longestUnique("abcabcbb") << " " << longestUnique("bbbbb") << " " << longestUnique("pwwkew") << " " << longestUnique("") << "\n";
    cout << shortestWithSum({2, 3, 1, 2, 4, 3}, 7) << " " << shortestWithSum({1, 1, 1}, 5) << "\n";
}
