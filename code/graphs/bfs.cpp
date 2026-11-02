#include <algorithm>
#include <iostream>
#include <queue>
#include <utility>
#include <vector>
using namespace std;

// Fewest-edges distance from start to every vertex (-1 if unreachable); fills parent.
vector<int> bfs(const vector<vector<int>>& adj, int start, vector<int>& parent) {
    vector<int> dist(adj.size(), -1);
    parent.assign(adj.size(), -1);
    dist[start] = 0;
    queue<int> q;
    q.push(start);
    while (!q.empty()) {
        int u = q.front(); q.pop();                  // the oldest vertex in the queue: nearest first
        for (int v : adj[u]) {
            if (dist[v] == -1) {                     // first time we reach v: this is the shortest way
                dist[v] = dist[u] + 1;
                parent[v] = u;
                q.push(v);
            }
        }
    }
    return dist;
}

// Walks the parents back from target and reverses: the shortest path from the start.
vector<int> path(const vector<int>& parent, int target) {
    vector<int> out;
    for (; target != -1; target = parent[target]) out.push_back(target);
    reverse(out.begin(), out.end());
    return out;
}

vector<vector<int>> build(int n, const vector<pair<int, int>>& edges) {
    vector<vector<int>> adj(n);
    for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }   // undirected
    return adj;
}

void print(const vector<int>& a, const char* end = "\n") {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]" << end;
}

int main() {
    auto adj = build(8, {{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}, {4, 5}, {2, 5}, {6, 7}});
    vector<int> parent;
    vector<int> dist = bfs(adj, 0, parent);
    print(dist);
    print(path(parent, 4), " ");
    print(path(parent, 5));
    vector<int> unreachable;
    for (int v = 0; v < 8; v++) if (dist[v] == -1) unreachable.push_back(v);
    print(unreachable);
}
