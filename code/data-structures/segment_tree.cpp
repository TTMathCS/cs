#include <algorithm>
#include <climits>
#include <iostream>
#include <vector>
using namespace std;

// Range minimum over a[lo..hi] and point updates, both O(log n). Node 1 covers the whole array.
struct SegmentTree {
    int n;
    vector<int> t;

    explicit SegmentTree(const vector<int>& a) : n(a.size()), t(4 * a.size()) { build(1, 0, n - 1, a); }

    void build(int node, int lo, int hi, const vector<int>& a) {
        if (lo == hi) { t[node] = a[lo]; return; }   // a leaf holds one value
        int mid = (lo + hi) / 2;
        build(2 * node, lo, mid, a);
        build(2 * node + 1, mid + 1, hi, a);
        t[node] = min(t[2 * node], t[2 * node + 1]);
    }

    // a[i] = value.
    void update(int i, int value, int node = 1, int lo = 0, int hi = -1) {
        if (hi == -1) hi = n - 1;
        if (lo == hi) { t[node] = value; return; }
        int mid = (lo + hi) / 2;
        if (i <= mid) update(i, value, 2 * node, lo, mid);
        else update(i, value, 2 * node + 1, mid + 1, hi);
        t[node] = min(t[2 * node], t[2 * node + 1]); // repair on the way back up
    }

    // min(a[l..r]), both ends included.
    int query(int l, int r, int node = 1, int lo = 0, int hi = -1) const {
        if (hi == -1) hi = n - 1;
        if (r < lo || hi < l) return INT_MAX;        // no overlap
        if (l <= lo && hi <= r) return t[node];      // this node's range is inside [l, r]: use it whole
        int mid = (lo + hi) / 2;
        return min(query(l, r, 2 * node, lo, mid), query(l, r, 2 * node + 1, mid + 1, hi));
    }
};

int main() {
    SegmentTree st({5, 8, 6, 3, 2, 7, 2, 6});
    cout << st.query(0, 7) << " " << st.query(0, 2) << " " << st.query(1, 3) << " " << st.query(5, 5) << "\n";
    st.update(4, 9);                                 // a[4]: 2 -> 9
    cout << st.query(3, 5) << " " << st.query(4, 5) << "\n";
    st.update(3, 10);
    cout << st.query(0, 4) << " " << st.t[1] << "\n";
}
