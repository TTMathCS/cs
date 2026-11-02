#include <algorithm>
#include <climits>
#include <functional>
#include <iostream>
#include <numeric>
#include <queue>
#include <vector>
using namespace std;

// The most activities that do not overlap (one room): always take the one that finishes first.
// Returns their numbers. An activity [s, f) may start exactly when the previous one finishes.
vector<int> selectActivities(const vector<int>& start, const vector<int>& finish) {
    vector<int> order(start.size());
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(), [&](int x, int y) { return finish[x] != finish[y] ? finish[x] < finish[y] : x < y; });
    vector<int> chosen;
    long long freeAt = LLONG_MIN;
    for (int i : order)
        if (start[i] >= freeAt) {                    // it starts after the last chosen one ends: take it
            chosen.push_back(i);
            freeAt = finish[i];
        }
    return chosen;
}

// The fewest rooms that hold every activity (interval partitioning).
int roomsNeeded(const vector<int>& start, const vector<int>& finish) {
    vector<int> order(start.size());
    iota(order.begin(), order.end(), 0);
    sort(order.begin(), order.end(), [&](int x, int y) { return start[x] != start[y] ? start[x] < start[y] : x < y; });
    priority_queue<int, vector<int>, greater<int>> ends;   // when busy rooms become free
    for (int i : order) {
        if (!ends.empty() && ends.top() <= start[i]) ends.pop();   // reuse the room that frees up first
        ends.push(finish[i]);                        // (otherwise this opens a new room)
    }
    return ends.size();
}

int main() {
    vector<int> s = {1, 3, 0, 5, 3, 5, 6, 7, 8, 2, 12};
    vector<int> f = {4, 5, 6, 7, 9, 9, 10, 11, 12, 14, 16};
    vector<int> chosen = selectActivities(s, f);
    cout << chosen.size() << " [";
    for (size_t i = 0; i < chosen.size(); i++) cout << (i ? ", " : "") << chosen[i];
    cout << "]\n" << roomsNeeded(s, f) << "\n";
}
