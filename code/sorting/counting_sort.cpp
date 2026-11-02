#include <iostream>
#include <vector>
using namespace std;

// Returns a sorted copy of a, whose values are whole numbers from 0 to k. Stable.
vector<int> countingSort(const vector<int>& a, int k) {
    vector<int> count(k + 1, 0);
    for (int x : a) count[x]++;                      // 1. count each value
    for (int v = 1; v <= k; v++)                     // 2. running totals: count[v] = how many are <= v
        count[v] += count[v - 1];
    vector<int> out(a.size());
    for (int i = (int)a.size() - 1; i >= 0; i--)     // 3. place from the back, so equal values keep order
        out[--count[a[i]]] = a[i];
    return out;
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
}

int main() {
    print(countingSort({2, 5, 3, 0, 2, 3, 0, 3}, 5));
    print(countingSort({4, 1, 3, 4, 3}, 4));
    print(countingSort({0}, 0));
}
