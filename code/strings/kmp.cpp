#include <iostream>
#include <string>
#include <vector>
using namespace std;

// pi[i] = the length of the longest proper prefix of p[0..i] that is also a suffix of it.
vector<int> prefixFunction(const string& p) {
    vector<int> pi(p.size(), 0);
    int k = 0;                                       // the length of the current matching prefix
    for (size_t i = 1; i < p.size(); i++) {
        while (k > 0 && p[i] != p[k]) k = pi[k - 1];   // mismatch: fall back to the next shorter border
        if (p[i] == p[k]) k++;
        pi[i] = k;
    }
    return pi;
}

// Every position where p starts in text (Knuth-Morris-Pratt), in O(len(text) + len(p)).
vector<int> kmpSearch(const string& text, const string& p) {
    vector<int> found;
    if (p.empty()) { for (size_t i = 0; i <= text.size(); i++) found.push_back(i); return found; }
    vector<int> pi = prefixFunction(p);
    int k = 0, m = p.size();                         // k = how many letters of p match right now
    for (int i = 0; i < (int)text.size(); i++) {
        while (k > 0 && text[i] != p[k]) k = pi[k - 1];   // never move back in text: shift p using pi
        if (text[i] == p[k]) k++;
        if (k == m) {                                // a full match ends at i
            found.push_back(i - m + 1);
            k = pi[k - 1];                           // keep going, to find overlapping matches too
        }
    }
    return found;
}

string show(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) s += (i ? ", " : "") + to_string(v[i]);
    return s + "]";
}

int main() {
    cout << show(prefixFunction("ABABCABAB")) << "\n";
    cout << show(kmpSearch("ABABDABACDABABCABAB", "ABABCABAB")) << "\n";
    cout << show(kmpSearch("AAAAA", "AA")) << " " << show(kmpSearch("olympus mons", "mars")) << "\n";
}
