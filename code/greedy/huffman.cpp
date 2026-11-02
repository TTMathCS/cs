#include <functional>
#include <iostream>
#include <map>
#include <queue>
#include <string>
#include <vector>
using namespace std;

vector<int> leftChild, rightChild;
vector<char> letters;
map<char, string> codes;

// Left edge = 0, right edge = 1.
void walk(int node, const string& path) {
    if (node < (int)letters.size()) codes[letters[node]] = path.empty() ? "0" : path;
    else { walk(leftChild[node], path + "0"); walk(rightChild[node], path + "1"); }
}

// Huffman coding: the prefix-free binary code with the fewest total bits for these letter counts.
// Ties are broken by creation order, so the result is the same in every language.
map<char, string> huffman(const vector<char>& ls, const vector<int>& freq) {
    int n = ls.size();
    letters = ls;
    leftChild.assign(2 * n, 0);
    rightChild.assign(2 * n, 0);
    // entries {count, id}; ids 0..n-1 are the letters
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<pair<long long, int>>> heap;
    for (int i = 0; i < n; i++) heap.push({freq[i], i});
    int nextId = n;
    while (heap.size() > 1) {                        // join the two rarest trees into one
        auto a = heap.top(); heap.pop();
        auto b = heap.top(); heap.pop();
        leftChild[nextId] = a.second;
        rightChild[nextId] = b.second;
        heap.push({a.first + b.first, nextId});
        nextId++;
    }
    codes.clear();
    walk(heap.top().second, "");
    return codes;
}

int main() {
    vector<char> ls = {'a', 'b', 'c', 'd', 'e', 'f'};
    vector<int> freq = {45, 13, 12, 16, 9, 5};
    map<char, string> c = huffman(ls, freq);
    int total = 0, all = 0;
    for (size_t i = 0; i < ls.size(); i++) {
        cout << ls[i] << " " << c[ls[i]] << "\n";
        total += freq[i] * c[ls[i]].size();
        all += freq[i];
    }
    cout << "total bits: " << total << " fixed 3-bit code: " << 3 * all << "\n";
    string out;
    for (char ch : string("face")) out += c[ch];
    cout << "face -> " << out << "\n";
}
