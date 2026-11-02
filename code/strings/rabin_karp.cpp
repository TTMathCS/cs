#include <iostream>
#include <string>
#include <vector>
using namespace std;

// Every position where p starts in text, comparing rolling hashes first and letters only when the hashes
// agree. The number of false alarms (equal hashes, different letters) is put in falseAlarms.
vector<int> rabinKarp(const string& text, const string& p, long long mod, long long base, int& falseAlarms) {
    int n = text.size(), m = p.size();
    vector<int> found;
    falseAlarms = 0;
    if (m > n) return found;
    long long high = 1;                              // the weight of the window's first letter: base^(m-1) mod
    for (int i = 0; i < m - 1; i++) high = high * base % mod;
    long long hp = 0, ht = 0;
    for (int i = 0; i < m; i++) {                    // hash of p and of the first window
        hp = (hp * base + (unsigned char)p[i]) % mod;
        ht = (ht * base + (unsigned char)text[i]) % mod;
    }
    for (int s = 0; s + m <= n; s++) {
        if (hp == ht) {
            if (text.compare(s, m, p) == 0) found.push_back(s);   // equal hashes do not prove a match
            else falseAlarms++;
        }
        if (s + m < n) {                             // roll: drop text[s], add text[s+m]
            ht = (ht - (unsigned char)text[s] * high % mod + mod) % mod;
            ht = (ht * base + (unsigned char)text[s + m]) % mod;
        }
    }
    return found;
}

void show(const vector<int>& v, int fa) {
    cout << "[";
    for (size_t i = 0; i < v.size(); i++) cout << (i ? ", " : "") << v[i];
    cout << "] " << fa << "\n";
}

int main() {
    string text = "dust storms on mars can cover all of mars for months";
    int fa;
    vector<int> f = rabinKarp(text, "mars", 1000000007LL, 256, fa); show(f, fa);
    f = rabinKarp(text, "mars", 13, 256, fa); show(f, fa);
    f = rabinKarp("abracadabra", "abra", 1000000007LL, 256, fa); show(f, fa);
}
