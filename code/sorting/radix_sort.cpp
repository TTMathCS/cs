#include <algorithm>
#include <iostream>
#include <vector>
using namespace std;

// A stable counting sort on one decimal digit.
vector<int> sortByDigit(const vector<int>& a, int place) {
    vector<int> count(10, 0);
    for (int x : a) count[(x / place) % 10]++;
    for (int d = 1; d < 10; d++) count[d] += count[d - 1];
    vector<int> out(a.size());
    for (int i = (int)a.size() - 1; i >= 0; i--)     // from the back keeps it stable, which radix sort needs
        out[--count[(a[i] / place) % 10]] = a[i];
    return out;
}

// Returns a sorted copy of non-negative whole numbers (LSD radix sort, base 10).
vector<int> radixSort(vector<int> a) {
    int biggest = a.empty() ? 0 : *max_element(a.begin(), a.end());
    for (long long place = 1; biggest / place > 0; place *= 10)  // one pass per digit, ones first
        a = sortByDigit(a, (int)place);
    return a;
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
}

int main() {
    print(radixSort({170, 45, 75, 90, 802, 24, 2, 66}));
    print(radixSort({329, 457, 657, 839, 436, 720, 355}));
    print(radixSort({5, 0, 5}));
}
