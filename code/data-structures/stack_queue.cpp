#include <iostream>
#include <map>
#include <string>
#include <vector>
using namespace std;

// Last in, first out, on a growing array: push and pop at the end are O(1) amortized.
template <typename T>
struct Stack {
    vector<T> items;
    void push(const T& x) { items.push_back(x); }
    T pop() { T x = items.back(); items.pop_back(); return x; }
    T peek() const { return items.back(); }
    bool empty() const { return items.empty(); }
};

// First in, first out, in a ring buffer that doubles when full: every operation is O(1) amortized.
template <typename T>
struct Queue {
    vector<T> buf = vector<T>(4);
    size_t head = 0, size = 0;                       // head: index of the front item

    void enqueue(const T& x) {
        if (size == buf.size()) {                    // full: copy into a buffer twice as big
            vector<T> bigger(2 * buf.size());
            for (size_t i = 0; i < size; i++) bigger[i] = buf[(head + i) % buf.size()];
            buf.swap(bigger);
            head = 0;
        }
        buf[(head + size) % buf.size()] = x;
        size++;
    }

    T dequeue() {
        T x = buf[head];
        head = (head + 1) % buf.size();
        size--;
        return x;
    }

    bool empty() const { return size == 0; }
};

// True if every bracket in s is closed by the right kind, in the right order.
bool balanced(const string& s) {
    map<char, char> pairs = {{')', '('}, {']', '['}, {'}', '{'}};
    Stack<char> st;
    for (char ch : s) {
        if (ch == '(' || ch == '[' || ch == '{') st.push(ch);          // remember the opener
        else if (pairs.count(ch)) {
            if (st.empty() || st.pop() != pairs[ch]) return false;      // nothing to close, or wrong kind
        }
    }
    return st.empty();                               // every opener was closed
}

int main() {
    for (string s : {"([]{})", "([)]", "((", "a[b(c)d]e", ""})
        cout << "'" << s << "' " << (balanced(s) ? "True" : "False") << "\n";
    Queue<int> q;
    for (int x = 1; x <= 6; x++) q.enqueue(x);
    vector<int> out = {q.dequeue(), q.dequeue()};
    q.enqueue(7);
    while (!q.empty()) out.push_back(q.dequeue());
    cout << "[";
    for (size_t i = 0; i < out.size(); i++) cout << (i ? ", " : "") << out[i];
    cout << "]\n";
}
