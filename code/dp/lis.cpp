#include <algorithm>
#include <iostream>
#include <vector>
using namespace std;

// O(n^2): best[i] = the length of the longest increasing subsequence that ends at a[i].
int lisSlow(const vector<int>& a) {
    vector<int> best(a.size(), 1);
    int ans = 0;
    for (size_t i = 0; i < a.size(); i++) {
        for (size_t j = 0; j < i; j++)
            if (a[j] < a[i] && best[j] + 1 > best[i]) best[i] = best[j] + 1;
        ans = max(ans, best[i]);
    }
    return ans;
}

// O(n log n): tails[k] = the smallest value that can end an increasing subsequence of length k+1.
// Returns the length; one longest increasing subsequence is put in seq.
int lisFast(const vector<int>& a, vector<int>& seq) {
    vector<int> tails, tailAt, prev(a.size(), -1);
    for (int i = 0; i < (int)a.size(); i++) {
        int k = lower_bound(tails.begin(), tails.end(), a[i]) - tails.begin();   // the first tail >= a[i]
        if (k == (int)tails.size()) { tails.push_back(a[i]); tailAt.push_back(i); }   // extends the longest
        else { tails[k] = a[i]; tailAt[k] = i; }     // a smaller ending for length k+1
        prev[i] = k > 0 ? tailAt[k - 1] : -1;
    }
    seq.clear();
    for (int i = tailAt.empty() ? -1 : tailAt.back(); i != -1; i = prev[i]) seq.push_back(a[i]);
    reverse(seq.begin(), seq.end());
    return tails.size();
}

int main() {
    vector<vector<int>> tests = {{10, 9, 2, 5, 3, 7, 101, 18}, {0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15}};
    for (auto& a : tests) {
        vector<int> seq;
        int k = lisFast(a, seq);
        cout << lisSlow(a) << " " << k << " [";
        for (size_t i = 0; i < seq.size(); i++) cout << (i ? ", " : "") << seq[i];
        cout << "]\n";
    }
}
