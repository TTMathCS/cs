#include <algorithm>
#include <iostream>
#include <vector>
using namespace std;

// 0/1 knapsack: the most value that fits in a bag of capacity cap, each item taken at most once.
// Returns the best value; the items (by number) that give it are put in items.
int knapsack(const vector<int>& weights, const vector<int>& values, int cap, vector<int>& items) {
    int n = weights.size();
    // best[i][c] = the most value using only the first i items with capacity c
    vector<vector<int>> best(n + 1, vector<int>(cap + 1, 0));
    for (int i = 1; i <= n; i++) {
        int w = weights[i - 1], v = values[i - 1];
        for (int c = 0; c <= cap; c++) {
            best[i][c] = best[i - 1][c];                         // leave item i-1 out ...
            if (w <= c && best[i - 1][c - w] + v > best[i][c])   // ... or take it, if it fits and is better
                best[i][c] = best[i - 1][c - w] + v;
        }
    }
    items.clear();
    for (int i = n, c = cap; i > 0; i--)             // walk back: a changed value means item i-1 was taken
        if (best[i][c] != best[i - 1][c]) { items.push_back(i - 1); c -= weights[i - 1]; }
    sort(items.begin(), items.end());
    return best[n][cap];
}

// The same answer with one row: go through capacities from high to low so each item is used once.
int knapsack1d(const vector<int>& weights, const vector<int>& values, int cap) {
    vector<int> best(cap + 1, 0);
    for (size_t k = 0; k < weights.size(); k++)
        for (int c = cap; c >= weights[k]; c--)
            best[c] = max(best[c], best[c - weights[k]] + values[k]);
    return best[cap];
}

void show(int b, const vector<int>& v) {
    cout << b << " [";
    for (size_t i = 0; i < v.size(); i++) cout << (i ? ", " : "") << v[i];
    cout << "]\n";
}

int main() {
    vector<int> items;
    show(knapsack({1, 3, 4, 5}, {1, 4, 5, 7}, 7, items), items);
    show(knapsack({10, 20, 30}, {60, 100, 120}, 50, items), items);
    cout << knapsack1d({1, 3, 4, 5}, {1, 4, 5, 7}, 7) << " " << knapsack1d({10, 20, 30}, {60, 100, 120}, 50) << "\n";
}
