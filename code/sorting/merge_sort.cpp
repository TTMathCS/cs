#include <iostream>
#include <vector>
using namespace std;

void merge(vector<int>& a, vector<int>& tmp, int lo, int mid, int hi) {
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi)
        tmp[k++] = (a[i] <= a[j]) ? a[i++] : a[j++];  // <= keeps equal values in order (stable)
    while (i < mid) tmp[k++] = a[i++];               // one side is used up; copy the rest
    while (j < hi) tmp[k++] = a[j++];
    for (k = lo; k < hi; k++) a[k] = tmp[k];
}

// Sorts a[lo..hi) in place, using tmp as scratch space.
void mergeSort(vector<int>& a, vector<int>& tmp, int lo, int hi) {
    if (hi - lo <= 1) return;                        // 0 or 1 items: already sorted
    int mid = (lo + hi) / 2;
    mergeSort(a, tmp, lo, mid);                      // sort each half ...
    mergeSort(a, tmp, mid, hi);
    merge(a, tmp, lo, mid, hi);                      // ... and merge the two sorted halves
}

void mergeSort(vector<int>& a) {
    vector<int> tmp(a.size());
    mergeSort(a, tmp, 0, a.size());
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
}

int main() {
    vector<vector<int>> tests = {{38, 27, 43, 3, 9, 82, 10}, {5, 1, 4, 2, 8, 5}, {1}};
    for (auto& a : tests) {
        mergeSort(a);
        print(a);
    }
}
