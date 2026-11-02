#include <algorithm>
#include <iostream>
#include <numeric>
#include <tuple>
#include <vector>
using namespace std;

struct Edge { int u, v, w; };

int find(vector<int>& parent, int x) {               // union-find with path halving
    while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
    return x;
}

// Minimum spanning tree of a connected undirected graph; returns its weight and fills chosen.
int kruskal(int n, vector<Edge> edges, vector<Edge>& chosen) {
    vector<int> parent(n);
    iota(parent.begin(), parent.end(), 0);
    sort(edges.begin(), edges.end(), [](const Edge& a, const Edge& b) {   // cheapest first (ties by u, v)
        return tie(a.w, a.u, a.v) < tie(b.w, b.u, b.v);
    });
    int total = 0;
    for (auto& e : edges) {
        int ru = find(parent, e.u), rv = find(parent, e.v);
        if (ru != rv) {                              // joins two different trees: keep it
            parent[ru] = rv;
            total += e.w;
            chosen.push_back(e);
            if ((int)chosen.size() == n - 1) break;
        }                                            // otherwise it would close a cycle: skip it
    }
    return total;
}

int main() {
    vector<Edge> edges = {{0, 1, 4}, {0, 7, 8}, {1, 2, 8}, {1, 7, 11}, {2, 3, 7}, {2, 8, 2}, {2, 5, 4}, {3, 4, 9},
        {3, 5, 14}, {4, 5, 10}, {5, 6, 2}, {6, 7, 1}, {6, 8, 6}, {7, 8, 7}};
    vector<Edge> chosen;
    cout << kruskal(9, edges, chosen) << "\n[";
    for (size_t i = 0; i < chosen.size(); i++)
        cout << (i ? ", " : "") << "(" << chosen[i].u << ", " << chosen[i].v << ", " << chosen[i].w << ")";
    cout << "]\n";
}
