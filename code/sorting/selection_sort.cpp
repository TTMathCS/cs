#include <iostream>
#include <utility>
#include <vector>
using namespace std;

// Sorts a in place, smallest first.
void selectionSort(vector<int>& a) {
    int n = a.size();
    for (int i = 0; i < n - 1; i++) {
        int smallest = i;                            // find the smallest value in a[i..n-1]
        for (int j = i + 1; j < n; j++)
            if (a[j] < a[smallest]) smallest = j;
        swap(a[i], a[smallest]);                     // put it at position i
    }
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
}

int main() {
    vector<vector<int>> tests = {{64, 25, 12, 22, 11}, {38, 27, 43, 3, 9, 82, 10}, {2, 1}};
    for (auto& a : tests) {
        selectionSort(a);
        print(a);
    }
}
