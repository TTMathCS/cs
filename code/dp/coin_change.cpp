#include <climits>
#include <iostream>
#include <vector>
using namespace std;

// The fewest coins that add up to amount (any coin may be used many times), and which coins; -1 if impossible.
int minCoins(const vector<int>& coins, int amount, vector<int>& used) {
    vector<int> best(amount + 1, INT_MAX);           // best[x] = fewest coins for the amount x
    vector<int> last(amount + 1, 0);                 // last[x] = the coin used last in that best way
    best[0] = 0;
    for (int x = 1; x <= amount; x++)
        for (int c : coins)
            if (c <= x && best[x - c] != INT_MAX && best[x - c] + 1 < best[x]) {
                best[x] = best[x - c] + 1;
                last[x] = c;
            }
    used.clear();
    if (best[amount] == INT_MAX) return -1;
    for (int x = amount; x > 0; x -= last[x]) used.push_back(last[x]);   // walk back through the choices
    return best[amount];
}

// How many different sets of coins add up to amount (order does not matter).
long long countWays(const vector<int>& coins, int amount) {
    vector<long long> ways(amount + 1, 0);
    ways[0] = 1;                                     // one way to make 0: no coins
    for (int c : coins)                              // coins in the outer loop, so each set is counted once
        for (int x = c; x <= amount; x++) ways[x] += ways[x - c];
    return ways[amount];
}

void show(int k, const vector<int>& v) {
    cout << k << " [";
    for (size_t i = 0; i < v.size(); i++) cout << (i ? ", " : "") << v[i];
    cout << "]\n";
}

int main() {
    vector<int> used;
    int k = minCoins({1, 3, 4}, 6, used); show(k, used);
    k = minCoins({1, 5, 10, 25}, 63, used); show(k, used);
    k = minCoins({2}, 3, used); show(k, used);
    cout << countWays({1, 2, 5}, 5) << " " << countWays({1, 5, 10, 25}, 100) << "\n";
}
