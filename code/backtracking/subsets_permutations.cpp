#include <iostream>
#include <string>
#include <vector>
using namespace std;

using List = vector<vector<int>>;

// Every subset: for each item, first leave it out, then put it in.
void subsetsGo(const vector<int>& items, size_t i, vector<int>& chosen, List& out) {
    if (i == items.size()) { out.push_back(chosen); return; }
    subsetsGo(items, i + 1, chosen, out);            // without items[i]
    chosen.push_back(items[i]);                      // choose
    subsetsGo(items, i + 1, chosen, out);            // with items[i]
    chosen.pop_back();                               // un-choose (the "back" in backtracking)
}

// Every ordering: fill the positions one by one with an item not used yet.
void permGo(const vector<int>& items, vector<bool>& used, vector<int>& chosen, List& out) {
    if (chosen.size() == items.size()) { out.push_back(chosen); return; }
    for (size_t i = 0; i < items.size(); i++)
        if (!used[i]) {
            used[i] = true; chosen.push_back(items[i]);
            permGo(items, used, chosen, out);
            chosen.pop_back(); used[i] = false;
        }
}

// Every subset (keeping the items' order) that adds up to target; all items positive.
// Prunes: stop as soon as the running sum is too big.
void sumGo(const vector<int>& items, int target, size_t i, int total, vector<int>& chosen, List& out) {
    if (total == target) { out.push_back(chosen); return; }
    if (i == items.size() || total > target) return;   // nothing left, or already too much
    chosen.push_back(items[i]);
    sumGo(items, target, i + 1, total + items[i], chosen, out);
    chosen.pop_back();
    sumGo(items, target, i + 1, total, chosen, out);
}

string show(const List& L) {
    string s = "[";
    for (size_t k = 0; k < L.size(); k++) {
        s += k ? ", [" : "[";
        for (size_t j = 0; j < L[k].size(); j++) s += (j ? ", " : "") + to_string(L[k][j]);
        s += "]";
    }
    return s + "]";
}

int main() {
    vector<int> chosen;
    List out;
    subsetsGo({1, 2, 3}, 0, chosen, out);
    cout << show(out) << "\n";
    out.clear();
    vector<bool> used(3, false);
    permGo({1, 2, 3}, used, chosen, out);
    cout << show(out) << "\n";
    out.clear();
    sumGo({3, 34, 4, 12, 5, 2}, 9, 0, 0, chosen, out);
    cout << show(out) << "\n";
}
