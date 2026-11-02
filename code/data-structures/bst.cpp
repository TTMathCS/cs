#include <algorithm>
#include <iostream>
#include <memory>
#include <vector>
using namespace std;

struct Node {
    int key;
    unique_ptr<Node> left, right;                    // smaller keys on the left, larger on the right
    explicit Node(int k) : key(k) {}
};
using Tree = unique_ptr<Node>;

// Inserts key (if new) into the tree.
void insert(Tree& root, int key) {
    if (!root) { root = make_unique<Node>(key); return; }
    if (key < root->key) insert(root->left, key);
    else if (key > root->key) insert(root->right, key);
}

bool contains(const Node* root, int key) {
    while (root) {                                   // go left or right, like a binary search
        if (key == root->key) return true;
        root = key < root->key ? root->left.get() : root->right.get();
    }
    return false;
}

// Removes key (if present) from the tree.
void erase(Tree& root, int key) {
    if (!root) return;
    if (key < root->key) erase(root->left, key);
    else if (key > root->key) erase(root->right, key);
    else if (!root->left) root = std::move(root->right);     // zero or one child: lift the child up
    else if (!root->right) root = std::move(root->left);
    else {
        Node* succ = root->right.get();              // two children: copy in the next larger key ...
        while (succ->left) succ = succ->left.get();
        root->key = succ->key;
        erase(root->right, succ->key);               // ... and delete it from the right subtree
    }
}

// Left subtree, node, right subtree: visits the keys in sorted order.
void inorder(const Node* root, vector<int>& out) {
    if (!root) return;
    inorder(root->left.get(), out);
    out.push_back(root->key);
    inorder(root->right.get(), out);
}

int height(const Node* root) { return root ? 1 + max(height(root->left.get()), height(root->right.get())) : 0; }

void print(const Tree& root) {
    vector<int> v;
    inorder(root.get(), v);
    cout << "[";
    for (size_t i = 0; i < v.size(); i++) cout << (i ? ", " : "") << v[i];
    cout << "]";
}

int main() {
    Tree root;
    for (int k : {50, 30, 70, 20, 40, 60, 80, 35}) insert(root, k);
    print(root);
    cout << " " << height(root.get()) << "\n";
    cout << (contains(root.get(), 60) ? "True" : "False") << " " << (contains(root.get(), 65) ? "True" : "False") << "\n";
    for (int k : {20, 30, 50}) {                     // a leaf, a node with two children, the root
        erase(root, k);
        print(root);
        cout << " root " << root->key << "\n";
    }
    Tree chain;
    for (int k = 1; k <= 7; k++) insert(chain, k);   // sorted input makes a tall, thin tree
    cout << "height after inserting 1..7 in order: " << height(chain.get()) << "\n";
}
