#include <iostream>
#include <utility>
#include <vector>
using namespace std;

// Sorts a in place, smallest first.
void bubbleSort(vector<int>& a) {
    int n = a.size();
    for (int end = n - 1; end > 0; end--) {          // after each pass, a[end] is in its final place
        bool swapped = false;
        for (int i = 0; i < end; i++) {
            if (a[i] > a[i + 1]) {                   // neighbours in the wrong order: swap them
                swap(a[i], a[i + 1]);
                swapped = true;
            }
        }
        if (!swapped) break;                         // a whole pass with no swap: already sorted
    }
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
}

int main() {
    vector<vector<int>> tests = {{5, 1, 4, 2, 8}, {38, 27, 43, 3, 9, 82, 10}, {1, 2, 3}};
    for (auto& a : tests) {
        bubbleSort(a);
        print(a);
    }
}
