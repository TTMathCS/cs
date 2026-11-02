#include <iostream>
#include <vector>
using namespace std;

// Sorts a in place, smallest first.
void insertionSort(vector<int>& a) {
    for (int i = 1; i < (int)a.size(); i++) {
        int key = a[i];                              // a[0..i-1] is sorted; insert a[i] into it
        int j = i - 1;
        while (j >= 0 && a[j] > key) {               // shift bigger values one place right
            a[j + 1] = a[j];
            j--;
        }
        a[j + 1] = key;                              // drop the key into the gap
    }
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
}

int main() {
    vector<vector<int>> tests = {{12, 11, 13, 5, 6}, {38, 27, 43, 3, 9, 82, 10}, {}};
    for (auto& a : tests) {
        insertionSort(a);
        print(a);
    }
}
