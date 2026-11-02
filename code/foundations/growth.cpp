#include <iostream>
using namespace std;

// Looks at every value once, like finding the largest: n steps.
long long linearSteps(int n) {
    long long steps = 0;
    for (int i = 0; i < n; i++) steps++;
    return steps;
}

// Halves the range until one value is left, like binary search: about log2(n) steps.
long long logSteps(int n) {
    long long steps = 0;
    while (n > 1) { n /= 2; steps++; }
    return steps;
}

// Looks at every pair i < j, like checking for duplicates the slow way: n(n-1)/2 steps.
long long quadraticSteps(int n) {
    long long steps = 0;
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++) steps++;
    return steps;
}

int main() {
    cout << "n halving linear pairs\n";
    for (int n : {10, 100, 1000, 4000})
        cout << n << " " << logSteps(n) << " " << linearSteps(n) << " " << quadraticSteps(n) << "\n";
}
