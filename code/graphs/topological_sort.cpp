#include <algorithm>
#include <iostream>
#include <optional>
#include <queue>
#include <stdexcept>
#include <utility>
#include <vector>
using namespace std;

// Topological order of a directed graph (Kahn's algorithm), or nothing if it has a cycle.
optional<vector<int>> kahn(int n, const vector<pair<int, int>>& edges) {
    vector<vector<int>> adj(n);
    vector<int> indeg(n, 0);                         // how many arrows point into each vertex
    for (auto [u, v] : edges) { adj[u].push_back(v); indeg[v]++; }
    queue<int> q;
    for (int v = 0; v < n; v++) if (indeg[v] == 0) q.push(v);   // nothing has to come before these
    vector<int> order;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        order.push_back(u);
        for (int v : adj[u])                         // "remove" u: its arrows no longer count
            if (--indeg[v] == 0) q.push(v);
    }
    if ((int)order.size() != n) return nullopt;      // leftovers lie on a cycle
    return order;
}

void visit(int u, const vector<vector<int>>& adj, vector<int>& state, vector<int>& finished) {
    state[u] = 1;                                    // 0 = new, 1 = on the current path, 2 = finished
    for (int v : adj[u]) {
        if (state[v] == 1) throw runtime_error("cycle");   // an arrow back into the current path
        if (state[v] == 0) visit(v, adj, state, finished);
    }
    state[u] = 2;
    finished.push_back(u);
}

// Topological order by depth-first search: a vertex is finished after everything it points to.
vector<int> dfsTopo(int n, const vector<pair<int, int>>& edges) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : edges) adj[u].push_back(v);
    vector<int> state(n, 0), finished;
    for (int u = 0; u < n; u++) if (state[u] == 0) visit(u, adj, state, finished);
    reverse(finished.begin(), finished.end());       // reverse finishing order
    return finished;
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]\n";
}

int main() {
    // 0 maths, 1 programming, 2 data structures, 3 algorithms, 4 databases, 5 machine learning
    vector<pair<int, int>> edges = {{0, 3}, {1, 2}, {2, 3}, {2, 4}, {3, 5}, {0, 5}};
    print(*kahn(6, edges));
    print(dfsTopo(6, edges));
    auto cyc = kahn(3, {{0, 1}, {1, 2}, {2, 0}});
    if (cyc) print(*cyc); else cout << "None\n";
}
