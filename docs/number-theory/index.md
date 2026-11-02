# Number theory

Algorithms about whole numbers: divisibility, primes and remainders. They are short, old (some are more than
2,000 years old) and still at the heart of modern computing, above all in cryptography, where they work on
numbers hundreds of digits long.

| Page | Problem | Time |
|---|---|---|
| [Euclid's GCD](gcd.md) | greatest common divisor; solving $ax + by = \gcd$; modular inverses | $O(\log \min(a, b))$ |
| [Sieve of Eratosthenes](sieve.md) | all primes up to $n$; factoring many numbers fast | $O(n \log \log n)$ |
| [Fast exponentiation](fast-power.md) | $a^n$ and $a^n \bmod m$ with few multiplications | $O(\log n)$ multiplications |

## Remainders in one paragraph

$a \bmod m$ is the remainder when $a$ is divided by $m$. Writing $a \equiv b \pmod m$ ("$a$ is congruent to
$b$") means $a$ and $b$ have the same remainder. Sums and products can be reduced at every step:
$(a + b) \bmod m$ and $(a \cdot b) \bmod m$ only depend on $a \bmod m$ and $b \bmod m$. That is why programs
can work "modulo $10^9 + 7$" without ever storing huge numbers, and why a clock (modulo 12) works.

## Size of the input

For number algorithms, the size of the input is the number of **digits**, about $\log n$, not $n$ itself. An
algorithm that loops up to $\sqrt n$ (trial division) looks fast, but for a 600-digit number it would take far
longer than the age of the universe. Euclid and fast exponentiation take a number of steps proportional to the
number of digits, which is why they work for cryptography.

For much more on primes, remainders and their use in codes, see the companion site
[cryptography.akadian.ca](https://cryptography.akadian.ca/).
