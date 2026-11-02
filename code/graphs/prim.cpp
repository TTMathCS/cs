#include <functional>
#include <iostream>
#include <queue>
#include <tuple>
#include <utility>
#include <vector>
using namespace std;

// Minimum spanning tree by growing one tree from start; returns its weight, fills chosen in order.
int prim(int n, const vector<tuple<int, int, int>>& edges, int start, vector<tuple<int, int, int>>& chosen) {
    vector<vector<pair<int, int>>> adj(n);           // (weight, neighbour)
    for (auto [u, v, w] : edges) { adj[u].push_back({w, v}); adj[v].push_back({w, u}); }
    vector<bool> inTree(n, false);
    // (edge weight, vertex, the tree vertex it hangs from), smallest first
    priority_queue<tuple<int, int, int>, vector<tuple<int, int, int>>, greater<>> pq;
    pq.push({0, start, -1});
    int total = 0;
    while (!pq.empty()) {
        auto [w, v, from] = pq.top(); pq.pop();      // the cheapest edge leaving the tree
        if (inTree[v]) continue;                     // both ends already in the tree: skip
        inTree[v] = true;
        total += w;
        if (from != -1) chosen.push_back({from, v, w});
        for (auto [w2, x] : adj[v])
            if (!inTree[x]) pq.push({w2, x, v});
    }
    return total;
}

int main() {
    vector<tuple<int, int, int>> edges = {{0, 1, 4}, {0, 7, 8}, {1, 2, 8}, {1, 7, 11}, {2, 3, 7}, {2, 8, 2}, {2, 5, 4},
        {3, 4, 9}, {3, 5, 14}, {4, 5, 10}, {5, 6, 2}, {6, 7, 1}, {6, 8, 6}, {7, 8, 7}};
    vector<tuple<int, int, int>> chosen;
    cout << prim(9, edges, 0, chosen) << "\n[";
    for (size_t i = 0; i < chosen.size(); i++) {
        auto [u, v, w] = chosen[i];
        cout << (i ? ", " : "") << "(" << u << ", " << v << ", " << w << ")";
    }
    cout << "]\n";
}
