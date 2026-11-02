# Sieve of Eratosthenes

*List every prime up to $n$ by crossing out multiples: start with 2, cross out its multiples, move to the next
number still standing, and repeat. What is never crossed out is prime.*

| Time | Extra space | Output |
|---|---|---|
| $O(n \log \log n)$ | $O(n)$ bits | which numbers up to $n$ are prime; smallest prime factors |

## The idea

A **prime** is a whole number above 1 whose only divisors are 1 and itself: 2, 3, 5, 7, 11, ... Testing each
number by trial division costs up to $\sqrt k$ divisions per number. The sieve, described by Eratosthenes of
Cyrene (about 240 BC, the same man who measured the size of the Earth), does the opposite: instead of asking
"what divides $k$?", each prime **marks its multiples** as not prime.

Two shortcuts make it fast:

- Start crossing out at $p^2$: smaller multiples $2p, 3p, \dots$ already have a smaller prime factor and were
  crossed out earlier.
- Stop when $p^2 > n$: every composite number up to $n$ has a prime factor at most $\sqrt n$.

A small change gives more: store, for each number, the **smallest prime** that crossed it out. Then any number up
to $n$ can be factored by dividing by its smallest prime factor again and again, in $O(\log k)$ steps.

## How it works

1. Make a list `is_prime[0..n]`, all true except 0 and 1.
2. For $p = 2, 3, \dots$ while $p^2 \le n$: if `is_prime[p]`, set `is_prime[k] = false` for
   $k = p^2, p^2 + p, p^2 + 2p, \dots \le n$.
3. The numbers still marked true are the primes.

## Code

=== "Python"

    ```python
    --8<-- "number-theory/sieve.py"
    ```

=== "Java"

    ```java
    --8<-- "number-theory/Sieve.java"
    ```

=== "C++"

    ```cpp
    --8<-- "number-theory/sieve.cpp"
    ```

Output: the 15 primes up to 50; `78498`, the number of primes below one million; then the factorizations
$360 = 2^3 \cdot 3^2 \cdot 5$, $9973$ (prime) and $2024 = 2^3 \cdot 11 \cdot 23$.

## When to use it

- **Many prime questions up to a limit** (say $10^7$ or $10^8$): one sieve, then each answer is a look-up.
- **Factoring many small numbers:** the smallest-prime-factor table.
- **Computing number-theory functions for all $k \le n$** (Euler's $\varphi$, number of divisors, Möbius) with
  the same crossing-out pattern.
- **Not for one huge number:** to test whether a 300-digit number is prime, use a probabilistic test such as
  Miller–Rabin (see [fast exponentiation](fast-power.md)).

## Common mistakes

- **Marking 0 and 1 as prime.**
- **Overflow in $p \cdot p$:** for $n$ near $2^{31}$, compute $p^2$ in 64 bits (the code uses `long`).
- **Memory:** a list of a billion Python booleans does not fit; use a `bytearray`, a bit set, or a segmented sieve.
- **Starting at $2p$ instead of $p^2$:** still correct, just slower.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: up to 50"

    | Prime | Crossed out (starting at $p^2$) |
    |---|---|
    | 2 | 4, 6, 8, 10, ..., 50 (24 numbers) |
    | 3 | 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48 (some already gone) |
    | 5 | 25, 30, 35, 40, 45, 50 |
    | 7 | 49 |
    | 11 | $11^2 = 121 > 50$: stop |

    Left standing: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47.

??? abstract "The math: why it is $O(n \log \log n)$, and how many primes there are"

    **Work.** Each prime $p \le \sqrt n$ crosses out at most $n / p$ numbers, so the total is at most

    $$\sum_{p \le \sqrt n} \frac{n}{p} = n \sum_{p \le \sqrt n} \frac{1}{p} = n \left( \ln \ln \sqrt n + O(1) \right) = O(n \log \log n),$$

    using **Mertens' theorem** (1874): the sum of $1/p$ over primes up to $x$ is $\ln \ln x + 0.2615\ldots + o(1)$.
    $\log \log n$ grows so slowly (about 3 for $n = 10^9$) that the sieve is nearly linear.

    **How many primes?** Euclid proved there are infinitely many: if $p_1, \dots, p_k$ were all of them,
    $p_1 p_2 \cdots p_k + 1$ would have a prime factor not in the list. The **prime number theorem**
    (Hadamard and de la Vallée Poussin, 1896) says the number of primes up to $x$, $\pi(x)$, is about
    $x / \ln x$. For $x = 10^6$: $10^6 / \ln 10^6 \approx 72{,}382$, against the true 78,498 that the program
    counted; the integral $\int_2^x \frac{dt}{\ln t} \approx 78{,}626$ is much closer.

    **Why stopping at $\sqrt n$ is enough.** If $k = ab$ with $1 < a \le b$, then $a^2 \le k$, so $a \le \sqrt k$;
    the smallest prime factor of a composite $k$ is at most $\sqrt k \le \sqrt n$.

??? tip "Watch it step by step"

    Red: the multiples about to be crossed out. Green: primes found. Faded: crossed out.

    <div class="cs-anim" data-anim="sieve"></div>

??? info "Variations and related ideas"

    - **Linear sieve:** crosses each composite out exactly once (by its smallest prime factor), $O(n)$, and builds
      the smallest-factor table at the same time.
    - **Segmented sieve:** sieve a window $[L, R]$ using the primes up to $\sqrt R$; needs only $O(\sqrt R)$ memory
      and finds primes near $10^{12}$.
    - **Odd numbers only / wheel:** skip multiples of 2 (or 2, 3, 5) to halve (or more) the memory and time.
    - **Sieve of Atkin:** $O(n / \log \log n)$ in theory, rarely faster in practice.

## See also

- [Euclid's GCD](gcd.md)
- [Fast exponentiation](fast-power.md): primality tests for big numbers
- [Big-O](../foundations/big-o.md)

## References

- Nicomachus of Gerasa, *Introduction to Arithmetic*, Book I, Chapter 13 (about 100 AD; the oldest surviving
  description, credited to Eratosthenes).
- G. H. Hardy and E. M. Wright, *An Introduction to the Theory of Numbers*, 6th ed., Oxford, 2008, Chapters 1–2 and 22.
- P. Pritchard, "Linear prime-number sieves: a family tree", *Science of Computer Programming* 9(1), 1987.
