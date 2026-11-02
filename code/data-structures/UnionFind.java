public class UnionFind {
    final int[] parent, size;
    int groups;

    /** Disjoint sets: which group is each item in? Union by size and path compression. */
    UnionFind(int n) {
        parent = new int[n];
        size = new int[n];
        for (int i = 0; i < n; i++) { parent[i] = i; size[i] = 1; }   // each item leads its own group
        groups = n;
    }

    int find(int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];   // walk up to the leader
        while (parent[x] != root) {                   // path compression: point everything on the way at it
            int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    }

    /** Joins the groups of a and b; returns false if they were already together. */
    boolean union(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;
        if (size[ra] < size[rb]) { int t = ra; ra = rb; rb = t; }   // hang the smaller tree under the bigger
        parent[rb] = ra;
        size[ra] += size[rb];
        groups--;
        return true;
    }

    boolean connected(int a, int b) { return find(a) == find(b); }

    static String py(boolean b) { return b ? "True" : "False"; }

    public static void main(String[] args) {
        UnionFind uf = new UnionFind(10);
        int[][] pairs = {{0, 1}, {2, 3}, {1, 3}, {5, 6}, {7, 8}, {8, 9}, {3, 0}};
        for (int[] p : pairs) System.out.println("union(" + p[0] + ", " + p[1] + ") -> " + py(uf.union(p[0], p[1])));
        System.out.println(py(uf.connected(0, 2)) + " " + py(uf.connected(4, 5)) + " " + py(uf.connected(7, 9)));
        System.out.println("groups: " + uf.groups + " size of 0's group: " + uf.size[uf.find(0)]);
    }
}
