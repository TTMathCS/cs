# Fast exponentiation

*Compute $a^n$ with about $\log_2 n$ multiplications instead of $n - 1$, by squaring: $a, a^2, a^4, a^8, \dots$
and multiplying together the ones that the binary digits of $n$ ask for. With remainders taken at each step,
it computes $a^n \bmod m$ for numbers hundreds of digits long.*

| Time | Extra space | Output |
|---|---|---|
| $O(\log n)$ multiplications | $O(1)$ | $a^n$, $a^n \bmod m$, matrix powers |

## The idea

$3^{13}$ the slow way is $3 \cdot 3 \cdot \ldots \cdot 3$, twelve multiplications. But $13 = 8 + 4 + 1$ (binary
`1101`), so

$$3^{13} = 3^{8} \cdot 3^{4} \cdot 3^{1},$$

and $3^2, 3^4, 3^8$ come from squaring: $3^2 = 3 \cdot 3$, $3^4 = 3^2 \cdot 3^2$, $3^8 = 3^4 \cdot 3^4$. That is 3
squarings and 2 more multiplications: 5 instead of 12. For $n$ around a billion it is about 60 instead of a
billion.

The same idea works for anything you can multiply: numbers **modulo $m$** (reduce after every multiplication so
nothing grows), **matrices** (which gives Fibonacci numbers in $O(\log n)$), even polynomials.

## How it works

1. `result = 1`.
2. While $n > 0$: if the lowest binary digit of $n$ is 1, `result *= a`. Then `a *= a` and $n \leftarrow
   \lfloor n / 2 \rfloor$.
3. For $a^n \bmod m$: take `% m` after each multiplication.

## Code

=== "Python"

    ```python
    --8<-- "number-theory/fast_power.py"
    ```

=== "Java"

    ```java
    --8<-- "number-theory/FastPower.java"
    ```

=== "C++"

    ```cpp
    --8<-- "number-theory/fast_power.cpp"
    ```

Output:

- `1024 1594323 1`: $2^{10}$, $3^{13}$ and $7^0$.
- `235042059 1`: $2^{1{,}000{,}000} \bmod (10^9 + 7)$, a number with 301,030 digits reduced to 9 digits, in about 26 multiplications;
  then $3 \cdot 3^{p-2} \bmod p = 1$, showing that $3^{p-2}$ is the inverse of 3 modulo the prime $p$.
- `1 55 2880067194370816120`: $5^{117} \bmod 19 = 1$, and the Fibonacci numbers $F(10)$ and $F(90)$ from matrix powers.

## When to use it

- **Cryptography:** RSA, Diffie–Hellman and digital signatures all compute $a^n \bmod m$ with numbers of 600 or
  more digits; see [cryptography.akadian.ca](https://cryptography.akadian.ca/).
- **Modular inverses modulo a prime:** $a^{-1} \equiv a^{p-2} \pmod p$ (Fermat).
- **Primality tests** such as Fermat and Miller–Rabin, which check $a^{n-1} \bmod n$.
- **Linear recurrences** (Fibonacci and others) and **counting paths of length $n$** in a graph, through matrix powers.
- **Hashing:** the base powers in [Rabin-Karp](../strings/rabin-karp.md).

## Common mistakes

- **Overflow in `a * a % m`:** with $m$ near $10^9$ the product fits in 64 bits; with $m$ near $10^{18}$ it does
  not; use 128-bit multiplication (`__int128` in C++, `Math.multiplyHigh` or `BigInteger` in Java).
- **`1 % m`:** for $m = 1$ the answer is 0, not 1; starting with `result = 1 % m` handles it.
- **Negative exponents:** they need an inverse, which exists only when $\gcd(a, m) = 1$.
- **Squaring once too many:** without a modulus, the last `a *= a` can overflow even though it is never used; the
  Java and C++ `fib` skip it.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: 3^13"

    $13 = 1101_2$. Reading bits from the lowest:

    | Bit | Value | Current square | Result |
    |---|---|---|---|
    | 0 | 1 | $3^1 = 3$ | $1 \cdot 3 = 3$ |
    | 1 | 0 | $3^2 = 9$ | 3 (skip) |
    | 2 | 1 | $3^4 = 81$ | $3 \cdot 81 = 243$ |
    | 3 | 1 | $3^8 = 6561$ | $243 \cdot 6561 = 1{,}594{,}323$ |

    **Modular example, $5^{117} \bmod 19$:** by Fermat's little theorem $5^{18} \equiv 1$, and $117 = 6 \cdot 18 + 9$,
    so it equals $5^9 \bmod 19$. Squares: $5^2 = 25 \equiv 6$, $5^4 \equiv 36 \equiv 17$,
    $5^8 \equiv 289 \equiv 4$; then $5^9 \equiv 4 \cdot 5 = 20 \equiv 1$.

??? abstract "The math: the number of multiplications, and Fermat"

    **Count.** Let $n$ have $k = \lfloor \log_2 n \rfloor + 1$ binary digits, $s$ of them equal to 1. The loop
    does $k - 1$ useful squarings and $s$ multiplications into the result: at most $2 \lfloor \log_2 n \rfloor + 1$.
    For $n = 1{,}000{,}000$ (20 binary digits, 7 of them 1) that is 19 squarings and 7 multiplications.

    **Invariant.** At the start of each loop, $\text{result} \cdot a^n$ equals the original $a_0^{n_0}$. If $n$ is
    even, $(a^2)^{n/2} = a^n$; if odd, $\text{result} \cdot a \cdot (a^2)^{(n-1)/2} = \text{result} \cdot a^n$.
    When $n = 0$, the result is the answer.

    **Not always optimal.** The fewest multiplications for $a^n$ is the length of the shortest *addition chain*
    for $n$; for $n = 15$, square-and-multiply uses 6 but 5 suffice ($a^2, a^3, a^6, a^{12}, a^{15}$). Finding the
    shortest chain is hard in general, and square-and-multiply is within a factor 2 of it.

    **Fermat's little theorem.** If $p$ is prime and $p \nmid a$, then $a^{p-1} \equiv 1 \pmod p$. So
    $a \cdot a^{p-2} \equiv 1$: the inverse of $a$ is $a^{p-2} \bmod p$. Euler's generalisation:
    $a^{\varphi(m)} \equiv 1 \pmod m$ when $\gcd(a, m) = 1$.

??? tip "Watch it step by step"

    Orange: the bit being read; red: the square that gets multiplied in; faded: a square that is skipped.

    <div class="cs-anim" data-anim="fast-power"></div>

??? info "Variations and related ideas"

    - **Left-to-right binary method:** read bits from the top: square, then multiply by $a$ if the bit is 1; the
      same count, and the multiplier is always the small $a$.
    - **Sliding windows** (precompute $a^1, a^3, \dots, a^{2^w - 1}$) use fewer multiplications for long
      exponents, such as those in RSA.
    - **Montgomery ladder:** the same steps whatever the bits, so the time does not leak the secret exponent
      (a defence against timing attacks).
    - **Montgomery multiplication** and **Barrett reduction** make each `% m` fast for big numbers.

## See also

- [Euclid's GCD](gcd.md): inverses for any modulus
- [Fibonacci](../dp/fibonacci.md): $F(n)$ with matrix powers
- [Rabin-Karp](../strings/rabin-karp.md)

## References

- D. E. Knuth, *The Art of Computer Programming*, Vol. 2, 3rd ed., Section 4.6.3 (evaluation of powers).
- A. J. Menezes, P. C. van Oorschot and S. A. Vanstone, *Handbook of Applied Cryptography*, CRC Press, 1996,
  Chapter 14 (efficient implementation).
