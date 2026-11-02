#include <climits>
#include <iostream>
#include <vector>
using namespace std;

const int INF = INT_MAX / 2;                         // half, so INF + INF does not overflow

// All-pairs shortest distances. d[i][j] is the edge weight (INF if none, 0 on the diagonal).
void floydWarshall(vector<vector<int>>& d) {
    int n = d.size();
    for (int k = 0; k < n; k++)                      // allow k as a stop in the middle of paths
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++)
                if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
}

int main() {
    vector<vector<int>> d = {{0, 3, INF, 7}, {8, 0, 2, INF}, {5, INF, 0, 1}, {2, INF, INF, 0}};
    floydWarshall(d);
    for (auto& row : d) {
        cout << "[";
        for (size_t j = 0; j < row.size(); j++) cout << (j ? ", " : "") << row[j];
        cout << "]\n";
    }
    bool neg = false;
    for (size_t i = 0; i < d.size(); i++) neg |= d[i][i] < 0;   // a negative diagonal: a negative cycle
    cout << (neg ? "True" : "False") << "\n";
}
