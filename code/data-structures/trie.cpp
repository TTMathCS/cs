#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <vector>
using namespace std;

struct Node {
    map<char, unique_ptr<Node>> children;            // letter -> next node, kept in order
    bool end = false;                                // does a word end here?
    int count = 0;                                   // how many words pass through here
};

// A prefix tree of words: insert, look up and count by prefix in O(length of the word).
struct Trie {
    Node root;

    void insert(const string& word) {
        Node* node = &root;
        for (char ch : word) {
            auto& next = node->children[ch];
            if (!next) next = make_unique<Node>();
            node = next.get();
            node->count++;
        }
        node->end = true;
    }

    const Node* walk(const string& s) const {
        const Node* node = &root;
        for (char ch : s) {
            auto it = node->children.find(ch);
            if (it == node->children.end()) return nullptr;
            node = it->second.get();
        }
        return node;
    }

    bool contains(const string& w) const { const Node* n = walk(w); return n && n->end; }
    int countPrefix(const string& p) const { const Node* n = walk(p); return n ? n->count : 0; }

    // All stored words that start with prefix, in alphabetical order.
    vector<string> withPrefix(const string& prefix) const {
        vector<string> out;
        string path = prefix;
        if (const Node* n = walk(prefix)) dfs(n, path, out);
        return out;
    }

    static void dfs(const Node* node, string& path, vector<string>& out) {
        if (node->end) out.push_back(path);
        for (auto& [ch, child] : node->children) {
            path.push_back(ch);
            dfs(child.get(), path, out);
            path.pop_back();
        }
    }
};

const char* py(bool b) { return b ? "True" : "False"; }

void show(const vector<string>& xs) {
    cout << "[";
    for (size_t i = 0; i < xs.size(); i++) cout << (i ? ", " : "") << "'" << xs[i] << "'";
    cout << "]\n";
}

int main() {
    Trie t;
    for (string w : {"mars", "marble", "march", "mare", "moon", "moonlight", "map"}) t.insert(w);
    cout << py(t.contains("mars")) << " " << py(t.contains("mar")) << " " << py(t.contains("moonlit")) << "\n";
    cout << t.countPrefix("mar") << " " << t.countPrefix("moon") << " " << t.countPrefix("x") << "\n";
    show(t.withPrefix("mar"));
    show(t.withPrefix("mo"));
}
