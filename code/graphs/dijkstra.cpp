#include <algorithm>
#include <climits>
#include <functional>
#include <iostream>
#include <queue>
#include <string>
#include <utility>
#include <vector>
using namespace std;

const vector<string> PLACES = {"Erebus Montes", "Olympus Mons", "Ascraeus Mons", "Valles Marineris",
    "Elysium Mons", "Utopia Planitia", "Gale crater", "Jezero crater", "Hellas Planitia"};
// roads between real places on Mars, with their great-circle lengths in km
const vector<vector<int>> ROADS = {{0, 1, 2369}, {0, 4, 2016}, {0, 5, 2305}, {1, 2, 1740}, {2, 3, 3043},
    {4, 6, 1879}, {5, 4, 1486}, {5, 7, 3214}, {7, 6, 3782}, {7, 8, 3616}, {6, 8, 4122}, {1, 6, 5337}};

// Shortest distances from src when every edge weight is >= 0; fills parent.
vector<long long> dijkstra(const vector<vector<pair<int, int>>>& adj, int src, vector<int>& parent) {
    vector<long long> dist(adj.size(), LLONG_MAX);
    parent.assign(adj.size(), -1);
    dist[src] = 0;
    // (distance found so far, vertex), smallest first
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> pq;
    pq.push({0, src});
    while (!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();            // the closest vertex not yet settled
        if (d > dist[u]) continue;                   // an old, longer entry: skip it
        for (auto [v, w] : adj[u]) {
            if (d + w < dist[v]) {                   // relax: going through u is shorter
                dist[v] = d + w;
                parent[v] = u;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}

vector<int> route(const vector<int>& parent, int t) {
    vector<int> out;
    for (; t != -1; t = parent[t]) out.push_back(t);
    reverse(out.begin(), out.end());
    return out;
}

int main() {
    vector<vector<pair<int, int>>> adj(PLACES.size());
    for (auto& r : ROADS) { adj[r[0]].push_back({r[1], r[2]}); adj[r[1]].push_back({r[0], r[2]}); }
    vector<int> parent;
    auto dist = dijkstra(adj, 0, parent);
    for (size_t v = 0; v < PLACES.size(); v++) {
        cout << PLACES[v] << ": " << dist[v] << " km via ";
        auto r = route(parent, v);
        for (size_t i = 0; i < r.size(); i++) cout << (i ? " > " : "") << PLACES[r[i]];
        cout << "\n";
    }
}
