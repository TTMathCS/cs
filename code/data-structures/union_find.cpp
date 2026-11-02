#include <iostream>
#include <numeric>
#include <utility>
#include <vector>
using namespace std;

// Disjoint sets: which group is each item in? Union by size and path compression.
struct UnionFind {
    vector<int> parent, size;
    int groups;

    explicit UnionFind(int n) : parent(n), size(n, 1), groups(n) {
        iota(parent.begin(), parent.end(), 0);       // each item starts as its own group's leader
    }

    int find(int x) {
        int root = x;
        while (parent[root] != root) root = parent[root];   // walk up to the leader
        while (parent[x] != root) {                  // path compression: point everything on the way at it
            int next = parent[x];
            parent[x] = root;
            x = next;
        }
        return root;
    }

    // Joins the groups of a and b; returns false if they were already together.
    bool unite(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;
        if (size[ra] < size[rb]) swap(ra, rb);       // hang the smaller tree under the bigger one
        parent[rb] = ra;
        size[ra] += size[rb];
        groups--;
        return true;
    }

    bool connected(int a, int b) { return find(a) == find(b); }
};

const char* py(bool b) { return b ? "True" : "False"; }

int main() {
    UnionFind uf(10);
    vector<pair<int, int>> pairs = {{0, 1}, {2, 3}, {1, 3}, {5, 6}, {7, 8}, {8, 9}, {3, 0}};
    for (auto [a, b] : pairs) cout << "union(" << a << ", " << b << ") -> " << py(uf.unite(a, b)) << "\n";
    cout << py(uf.connected(0, 2)) << " " << py(uf.connected(4, 5)) << " " << py(uf.connected(7, 9)) << "\n";
    cout << "groups: " << uf.groups << " size of 0's group: " << uf.size[uf.find(0)] << "\n";
}
