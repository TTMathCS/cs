#include <climits>
#include <iostream>
#include <optional>
#include <vector>
using namespace std;

const long long INF = LLONG_MAX;
struct Edge { int u, v, w; };

// Shortest distances from src even with negative edge weights, or nothing if a negative cycle is reachable.
optional<vector<long long>> bellmanFord(int n, const vector<Edge>& edges, int src) {
    vector<long long> dist(n, INF);
    dist[src] = 0;
    for (int round = 0; round < n - 1; round++) {    // a shortest path uses at most n-1 edges
        bool changed = false;
        for (auto& e : edges)
            if (dist[e.u] != INF && dist[e.u] + e.w < dist[e.v]) { dist[e.v] = dist[e.u] + e.w; changed = true; }
        if (!changed) break;                         // nothing improved: we are done early
    }
    for (auto& e : edges)                            // one more round: any improvement means a negative cycle
        if (dist[e.u] != INF && dist[e.u] + e.w < dist[e.v]) return nullopt;
    return dist;
}

void show(const vector<long long>& dist) {
    cout << "[";
    for (size_t i = 0; i < dist.size(); i++) {
        cout << (i ? ", " : "");
        if (dist[i] == INF) cout << "inf"; else cout << dist[i];
    }
    cout << "]\n";
}

int main() {
    vector<Edge> edges = {{0, 1, 6}, {0, 2, 7}, {1, 2, 8}, {1, 3, 5}, {1, 4, -4}, {2, 3, -3}, {2, 4, 9}, {3, 1, -2},
        {4, 0, 2}, {4, 3, 7}};
    show(*bellmanFord(5, edges, 0));
    show(*bellmanFord(6, edges, 0));                 // vertex 5 has no edges: unreachable
    vector<Edge> bad = {{0, 1, 1}, {1, 2, -1}, {2, 1, -1}, {2, 3, 1}};
    cout << (bellmanFord(4, bad, 0) ? "False" : "True") << "\n";
}
