#include <iostream>
#include <utility>
#include <vector>
using namespace std;

using Graph = vector<vector<int>>;

void visit(const Graph& adj, int u, vector<bool>& seen, vector<int>& order) {
    seen[u] = true;
    order.push_back(u);
    for (int v : adj[u])
        if (!seen[v]) visit(adj, v, seen, order);   // go as deep as possible before u's next neighbour
}

// The order in which depth-first search first visits the vertices reachable from start.
vector<int> dfsOrder(const Graph& adj, int start) {
    vector<bool> seen(adj.size(), false);
    vector<int> order;
    visit(adj, start, seen, order);
    return order;
}

// The same order without recursion, using an explicit stack (safe for huge graphs).
vector<int> dfsIterative(const Graph& adj, int start) {
    vector<bool> seen(adj.size(), false);
    vector<int> order, stack = {start};
    while (!stack.empty()) {
        int u = stack.back(); stack.pop_back();
        if (seen[u]) continue;
        seen[u] = true;
        order.push_back(u);
        for (int i = (int)adj[u].size() - 1; i >= 0; i--)   // reversed, so the first neighbour is popped first
            if (!seen[adj[u][i]]) stack.push_back(adj[u][i]);
    }
    return order;
}

// Labels each vertex with the number of its connected component; returns the count.
int components(const Graph& adj, vector<int>& comp) {
    comp.assign(adj.size(), -1);
    int count = 0;
    for (int s = 0; s < (int)adj.size(); s++) {
        if (comp[s] != -1) continue;                 // already labelled
        vector<int> stack = {s};
        comp[s] = count;
        while (!stack.empty()) {
            int u = stack.back(); stack.pop_back();
            for (int v : adj[u])
                if (comp[v] == -1) { comp[v] = count; stack.push_back(v); }
        }
        count++;
    }
    return count;
}

// Undirected graph: is there a cycle? (An edge to an already-seen vertex other than our parent.)
bool hasCycle(const Graph& adj) {
    vector<bool> seen(adj.size(), false);
    for (int s = 0; s < (int)adj.size(); s++) {
        if (seen[s]) continue;
        vector<pair<int, int>> stack = {{s, -1}};
        seen[s] = true;
        while (!stack.empty()) {
            auto [u, parent] = stack.back(); stack.pop_back();
            for (int v : adj[u]) {
                if (!seen[v]) { seen[v] = true; stack.push_back({v, u}); }
                else if (v != parent) return true;
            }
        }
    }
    return false;
}

Graph build(int n, const vector<pair<int, int>>& edges) {
    Graph adj(n);
    for (auto [u, v] : edges) { adj[u].push_back(v); adj[v].push_back(u); }
    return adj;
}

void print(const vector<int>& a) {
    cout << "[";
    for (size_t i = 0; i < a.size(); i++) cout << (i ? ", " : "") << a[i];
    cout << "]";
}

int main() {
    Graph g = build(8, {{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}, {4, 5}, {2, 5}, {6, 7}});
    print(dfsOrder(g, 0)); cout << " "; print(dfsIterative(g, 0)); cout << "\n";
    vector<int> comp;
    int count = components(g, comp);
    cout << "(" << count << ", "; print(comp); cout << ")\n";
    Graph tree = build(5, {{0, 1}, {0, 2}, {2, 3}, {2, 4}});
    cout << (hasCycle(g) ? "True" : "False") << " " << (hasCycle(tree) ? "True" : "False") << "\n";
}
