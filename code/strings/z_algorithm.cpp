#include <algorithm>
#include <iostream>
#include <string>
#include <vector>
using namespace std;

// z[i] = the length of the longest stretch starting at i that equals the start of s (z[0] = len(s)).
vector<int> zArray(const string& s) {
    int n = s.size();
    vector<int> z(n, 0);
    if (n > 0) z[0] = n;
    int l = 0, r = 0;                                // s[l..r) is the rightmost stretch found that equals a prefix
    for (int i = 1; i < n; i++) {
        if (i < r) z[i] = min(r - i, z[i - l]);      // inside a known stretch: reuse the value from the copy
        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) z[i]++;   // then try to extend by direct comparison
        if (i + z[i] > r) { l = i; r = i + z[i]; }
    }
    return z;
}

// Every position where p starts in text: z-values of p + separator + text that reach len(p).
vector<int> zSearch(const string& text, const string& p) {
    vector<int> z = zArray(p + string(1, '\0') + text);
    int m = p.size();
    vector<int> found;
    for (int i = m + 1; i < (int)z.size(); i++) if (z[i] >= m) found.push_back(i - m - 1);
    return found;
}

string show(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) s += (i ? ", " : "") + to_string(v[i]);
    return s + "]";
}

int main() {
    cout << show(zArray("aabxaab")) << "\n" << show(zArray("aaaaa")) << "\n";
    cout << show(zSearch("the red planet has red dust", "red")) << "\n";
}
