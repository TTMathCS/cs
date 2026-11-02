#include <iostream>
#include <random>
#include <utility>
#include <vector>
using namespace std;

// Lomuto partition: uses a[hi] as the pivot, returns where the pivot ends up.
int partition(vector<int>& a, int lo, int hi) {
    int pivot = a[hi];
    int i = lo;                                      // a[lo..i-1] holds values < pivot
    for (int j = lo; j < hi; j++)
        if (a[j] < pivot) swap(a[i++], a[j]);
    swap(a[i], a[hi]);                               // pivot goes between the two parts
    return i;
}

// Sorts a[lo..hi] in place (both ends included), smallest first.
void quicksort(vector<int>& a, int lo, int hi) {
    if (lo >= hi) return;
    int p = partition(a, lo, hi);                    // a[p] is now in its final place
    quicksort(a, lo, p - 1);                         // sort what is smaller ...
    quicksort(a, p + 1, hi);                         // ... and what is larger
}

// The safe version: a random pivot makes the slow O(n^2) case vanishingly unlikely.
mt19937 rng(random_device{}());
void quicksortRandom(vector<int>& a, int lo, int hi) {
    if (lo >= hi) return;
    swap(a[uniform_int_distribution<int>(lo, hi)(rng)], a[hi]);  // a random value into the pivot slot
    int p = partition(a, lo, hi);
    quicksortRandom(a, lo, p - 1);
    quicksortRandom(a, p + 1, hi);
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
}

int main() {
    vector<int> a = {10, 80, 30, 90, 40, 50, 70};
    quicksort(a, 0, a.size() - 1);
    print(a);
    vector<int> b = {38, 27, 43, 3, 9, 82, 10};
    quicksort(b, 0, b.size() - 1);
    print(b);
    vector<int> c = {5, 1, 4, 2, 8, 5, 5};
    quicksortRandom(c, 0, c.size() - 1);
    print(c);
}
