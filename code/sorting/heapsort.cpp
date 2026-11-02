#include <iostream>
#include <utility>
#include <vector>
using namespace std;

// Moves a[i] down until both children are smaller (only a[0..n-1] is the heap).
void siftDown(vector<int>& a, int i, int n) {
    while (true) {
        int big = i, left = 2 * i + 1, right = 2 * i + 2;
        if (left < n && a[left] > a[big]) big = left;
        if (right < n && a[right] > a[big]) big = right;
        if (big == i) return;
        swap(a[i], a[big]);
        i = big;
    }
}

// Sorts a in place, smallest first, using a max-heap stored in a itself.
void heapsort(vector<int>& a) {
    int n = a.size();
    for (int i = n / 2 - 1; i >= 0; i--)             // build the heap: sift down every parent, last first
        siftDown(a, i, n);
    for (int end = n - 1; end > 0; end--) {
        swap(a[0], a[end]);                          // the largest goes to the back ...
        siftDown(a, 0, end);                         // ... and the heap shrinks by one
    }
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
}

int main() {
    vector<vector<int>> tests = {{4, 10, 3, 5, 1}, {38, 27, 43, 3, 9, 82, 10}, {7, 7, 1}};
    for (auto& a : tests) {
        heapsort(a);
        print(a);
    }
}
