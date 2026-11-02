#include <iostream>
#include <tuple>
#include <vector>
using namespace std;

using Move = tuple<int, char, char>;

// Moves n discs from source to target, never putting a disc on a smaller one.
void hanoi(int n, char source, char target, char spare, vector<Move>& moves) {
    if (n == 0) return;                              // base case: nothing to move
    hanoi(n - 1, source, spare, target, moves);      // 1. move the n-1 smaller discs out of the way
    moves.emplace_back(n, source, target);           // 2. move the biggest disc
    hanoi(n - 1, spare, target, source, moves);      // 3. move the n-1 smaller discs on top of it
}

// n! = n * (n-1)!, with 0! = 1.
long long factorial(int n) { return n == 0 ? 1 : n * factorial(n - 1); }

int main() {
    vector<Move> moves;
    hanoi(3, 'A', 'C', 'B', moves);
    for (auto& [disc, a, b] : moves) cout << "disc " << disc << ": " << a << " -> " << b << "\n";
    for (int n : {1, 2, 3, 10, 20}) {
        vector<Move> m;
        hanoi(n, 'A', 'C', 'B', m);
        cout << n << " discs: " << m.size() << " moves\n";
    }
    cout << factorial(10) << "\n";
}
