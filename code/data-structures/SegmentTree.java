public class SegmentTree {
    final int n;
    final int[] t;

    /** Range minimum over a[lo..hi] and point updates, both O(log n). Node 1 covers the whole array. */
    SegmentTree(int[] a) {
        n = a.length;
        t = new int[4 * n];
        build(1, 0, n - 1, a);
    }

    void build(int node, int lo, int hi, int[] a) {
        if (lo == hi) { t[node] = a[lo]; return; }    // a leaf holds one value
        int mid = (lo + hi) / 2;
        build(2 * node, lo, mid, a);
        build(2 * node + 1, mid + 1, hi, a);
        t[node] = Math.min(t[2 * node], t[2 * node + 1]);
    }

    /** a[i] = value. */
    void update(int i, int value) { update(i, value, 1, 0, n - 1); }

    void update(int i, int value, int node, int lo, int hi) {
        if (lo == hi) { t[node] = value; return; }
        int mid = (lo + hi) / 2;
        if (i <= mid) update(i, value, 2 * node, lo, mid);
        else update(i, value, 2 * node + 1, mid + 1, hi);
        t[node] = Math.min(t[2 * node], t[2 * node + 1]);   // repair on the way back up
    }

    /** min(a[l..r]), both ends included. */
    int query(int l, int r) { return query(l, r, 1, 0, n - 1); }

    int query(int l, int r, int node, int lo, int hi) {
        if (r < lo || hi < l) return Integer.MAX_VALUE;     // no overlap
        if (l <= lo && hi <= r) return t[node];       // this node's range is inside [l, r]: use it whole
        int mid = (lo + hi) / 2;
        return Math.min(query(l, r, 2 * node, lo, mid), query(l, r, 2 * node + 1, mid + 1, hi));
    }

    public static void main(String[] args) {
        SegmentTree st = new SegmentTree(new int[]{5, 8, 6, 3, 2, 7, 2, 6});
        System.out.println(st.query(0, 7) + " " + st.query(0, 2) + " " + st.query(1, 3) + " " + st.query(5, 5));
        st.update(4, 9);                              // a[4]: 2 -> 9
        System.out.println(st.query(3, 5) + " " + st.query(4, 5));
        st.update(3, 10);
        System.out.println(st.query(0, 4) + " " + st.t[1]);
    }
}
