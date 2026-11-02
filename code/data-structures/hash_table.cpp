#include <cstdint>
#include <iostream>
#include <set>
#include <sstream>
#include <string>
#include <utility>
#include <vector>
using namespace std;

// Polynomial string hash, the same as Java's String.hashCode, read as an unsigned 32-bit number.
uint32_t hashStr(const string& s) {
    uint32_t h = 0;
    for (unsigned char ch : s) h = 31 * h + ch;      // unsigned arithmetic wraps at 2^32
    return h;
}

// A hash table with separate chaining: each bucket holds a short list of (key, value) pairs.
struct HashMap {
    vector<vector<pair<string, int>>> buckets = vector<vector<pair<string, int>>>(8);
    size_t size = 0;

    vector<pair<string, int>>& bucket(const string& key) { return buckets[hashStr(key) % buckets.size()]; }

    void put(const string& key, int value) {
        auto& b = bucket(key);
        for (auto& kv : b)
            if (kv.first == key) { kv.second = value; return; }   // key already there: replace its value
        b.emplace_back(key, value);
        size++;
        if (size > 0.75 * buckets.size()) resize(2 * buckets.size());   // too full: double the buckets
    }

    int get(const string& key, int dflt) {
        for (auto& kv : bucket(key)) if (kv.first == key) return kv.second;
        return dflt;
    }

    void resize(size_t n) {
        vector<vector<pair<string, int>>> old(n);
        old.swap(buckets);
        for (auto& b : old)
            for (auto& kv : b) buckets[hashStr(kv.first) % n].push_back(kv);
    }
};

int main() {
    string text = "the quick brown fox jumps over the lazy dog the end", w;
    HashMap m;
    set<string> words;
    istringstream in(text);
    while (in >> w) { m.put(w, m.get(w, 0) + 1); words.insert(w); }
    for (auto& x : words) cout << x << " " << m.get(x, 0) << "\n";
    cout << "buckets: " << m.buckets.size() << " keys: " << m.size << " missing: " << m.get("cat", 0) << "\n";
    cout << hashStr("abc") << "\n";
}
