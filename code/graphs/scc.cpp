#include <iostream>
#include <utility>
#include <vector>
using namespace std;

struct Kosaraju {
    vector<vector<int>> adj, radj;                   // radj: every arrow reversed
    vector<bool> seen;
    vector<int> order, comp;

    void dfs1(int u) {                               // pass 1: record finishing order
        seen[u] = true;
        for (int v : adj[u]) if (!seen[v]) dfs1(v);
        order.push_back(u);
    }

    void dfs2(int u, int c) {
        comp[u] = c;
        for (int v : radj[u]) if (comp[v] == -1) dfs2(v, c);
    }

    // Strongly connected components; returns the count and fills comp, numbered in topological order.
    int run(int n, const vector<pair<int, int>>& edges) {
        adj.assign(n, {}); radj.assign(n, {});
        for (auto [u, v] : edges) { adj[u].push_back(v); radj[v].push_back(u); }
        seen.assign(n, false);
        for (int u = 0; u < n; u++) if (!seen[u]) dfs1(u);
        comp.assign(n, -1);
        int c = 0;
        for (int i = n - 1; i >= 0; i--)             // pass 2: latest finisher first, on the reversed graph
            if (comp[order[i]] == -1) dfs2(order[i], c++);
        return c;
    }
};

int main() {
    vector<pair<int, int>> edges = {{0, 1}, {1, 2}, {2, 0}, {2, 3}, {3, 4}, {4, 5}, {5, 3}, {6, 5}, {6, 7}, {7, 6}};
    Kosaraju k;
    int count = k.run(8, edges);
    cout << count << " [";
    for (int v = 0; v < 8; v++) cout << (v ? ", " : "") << k.comp[v];
    cout << "]\n[";
    for (int c = 0; c < count; c++) {
        cout << (c ? ", " : "") << "[";
        bool first = true;
        for (int v = 0; v < 8; v++) if (k.comp[v] == c) { cout << (first ? "" : ", ") << v; first = false; }
        cout << "]";
    }
    cout << "]\n";
}
