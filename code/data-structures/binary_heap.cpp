#include <algorithm>
#include <functional>
#include <iostream>
#include <utility>
#include <vector>
using namespace std;

// A min-heap in a vector: a[0] is the smallest; the children of i are 2i+1 and 2i+2.
struct MinHeap {
    vector<int> a;

    void push(int x) {
        a.push_back(x);                              // put it at the bottom ...
        size_t i = a.size() - 1;
        while (i > 0) {                              // ... and sift it up while it beats its parent
            size_t parent = (i - 1) / 2;
            if (a[parent] <= a[i]) break;
            swap(a[parent], a[i]);
            i = parent;
        }
    }

    int pop() {
        int top = a[0];
        a[0] = a.back();                             // move the last value to the root ...
        a.pop_back();
        size_t i = 0, n = a.size();
        while (true) {                               // ... and sift it down below smaller children
            size_t small = i, l = 2 * i + 1, r = 2 * i + 2;
            if (l < n && a[l] < a[small]) small = l;
            if (r < n && a[r] < a[small]) small = r;
            if (small == i) break;
            swap(a[i], a[small]);
            i = small;
        }
        return top;
    }

    int peek() const { return a[0]; }
    size_t size() const { return a.size(); }
};

void print(const vector<int>& v) {
    cout << "[";
    for (size_t i = 0; i < v.size(); i++) cout << (i ? ", " : "") << v[i];
    cout << "]\n";
}

int main() {
    MinHeap h;
    for (int x : {5, 3, 8, 1, 9, 2, 7}) h.push(x);
    print(h.a);                                      // the heap as stored
    vector<int> out;
    while (h.size() > 0) out.push_back(h.pop());     // comes out sorted
    print(out);
    MinHeap top;                                     // the 3 largest of a stream, keeping only 3 values
    for (int x : {12, 3, 45, 7, 33, 21, 9, 40}) {
        top.push(x);
        if (top.size() > 3) top.pop();               // drop the smallest of the 4
    }
    vector<int> best = top.a;
    sort(best.begin(), best.end(), greater<int>());
    print(best);
}
