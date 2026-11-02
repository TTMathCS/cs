# Euclid's GCD

*The greatest common divisor of two numbers, found by replacing the larger with the remainder of dividing by the
smaller, again and again. The extended version also finds $x, y$ with $ax + by = \gcd(a, b)$, which gives
division in modular arithmetic.*

| Time | Extra space | Output |
|---|---|---|
| $O(\log \min(a, b))$ divisions | $O(1)$ (loop), $O(\log)$ (recursive extended) | $\gcd(a, b)$; $x, y$; inverses; lcm |

## The idea

The **greatest common divisor** $\gcd(a, b)$ is the largest number that divides both $a$ and $b$:
$\gcd(12, 18) = 6$. Listing all divisors is slow. Euclid (about 300 BC) noticed:

$$\gcd(a, b) = \gcd(b,\; a \bmod b), \qquad \gcd(a, 0) = a.$$

Any number dividing $a$ and $b$ also divides $a - qb = a \bmod b$, and the other way around; so both pairs have
the same common divisors. The numbers shrink fast, and when the remainder reaches 0, the other number is the gcd.

**Extended Euclid.** Run the same steps, then work backwards to write the gcd as a combination
$ax + by$. This is **Bézout's identity**. When $\gcd(a, m) = 1$, it gives $ax \equiv 1 \pmod m$: $x$ is the
**inverse** of $a$ modulo $m$, the number that "divides by $a$".

**Least common multiple:** $\text{lcm}(a, b) = a \cdot b / \gcd(a, b)$.

## How it works

1. **gcd:** while $b \ne 0$: $(a, b) \leftarrow (b, a \bmod b)$. Return $a$.
2. **extended:** if $b = 0$, return $(a, 1, 0)$. Otherwise get $(g, x_1, y_1)$ for $(b, a \bmod b)$ and return
   $(g,\; y_1,\; x_1 - \lfloor a/b \rfloor \, y_1)$.
3. **inverse of $a$ mod $m$:** run extended Euclid on $(a, m)$; if the gcd is 1, the answer is $x \bmod m$.

## Code

=== "Python"

    ```python
    --8<-- "number-theory/gcd.py"
    ```

=== "Java"

    ```java
    --8<-- "number-theory/Gcd.java"
    ```

=== "C++"

    ```cpp
    --8<-- "number-theory/gcd.cpp"
    ```

Output:

- `21 21 1 9`: $\gcd(1071, 462) = 21$ in either order; 17 and 5 share nothing; $\gcd(0, 9) = 9$.
- `2 -9 47`: $240 \cdot (-9) + 46 \cdot 47 = 2$.
- `12 250755`: $\text{lcm}(4, 6) = 12$. A Mars year is about 687 Earth days and an Earth year 365 days; as whole
  numbers they share no factor, so the two calendars line up again only after 250,755 days.
- `4 12 -1`: $3 \cdot 4 = 12 \equiv 1 \pmod{11}$; $10 \cdot 12 = 120 \equiv 1 \pmod{17}$; 6 has no inverse modulo 9.

## When to use it

- **Simplifying fractions:** divide top and bottom by their gcd.
- **Modular inverses** for division modulo a prime or any $m$: in RSA key generation, in combinatorics modulo
  $10^9 + 7$, in the Chinese remainder theorem.
- **Solving $ax + by = c$** in whole numbers: possible exactly when $\gcd(a, b)$ divides $c$.
- **Rhythms and gears:** when two cycles line up again (the lcm), how many teeth meet.

## Common mistakes

- **Overflow in lcm:** write `a / gcd * b`, not `a * b / gcd`.
- **Negative numbers:** in Java and C++, `%` can be negative; take absolute values first, and bring an inverse
  into $0..m-1$ with `((x % m) + m) % m`.
- **Inverses that do not exist:** if $\gcd(a, m) > 1$, there is no inverse; check before using it.
- **Recursion depth:** not a real problem here (at most about 90 levels for 64-bit numbers), but the loop version
  is just as easy.

## Going deeper

Each part below starts closed; open the ones you want.

??? example "Sample walkthrough: gcd(1071, 462) and extended Euclid on (240, 46)"

    | Step | $a$ | $b$ | $a = q \cdot b + r$ |
    |---|---|---|---|
    | 1 | 1071 | 462 | $1071 = 2 \cdot 462 + 147$ |
    | 2 | 462 | 147 | $462 = 3 \cdot 147 + 21$ |
    | 3 | 147 | 21 | $147 = 7 \cdot 21 + 0$ |

    The gcd is 21. Check: $1071 = 3 \cdot 3 \cdot 7 \cdot 17$ and $462 = 2 \cdot 3 \cdot 7 \cdot 11$ share
    $3 \cdot 7 = 21$.

    **Extended, on 240 and 46:** $240 = 5 \cdot 46 + 10$, $46 = 4 \cdot 10 + 6$, $10 = 1 \cdot 6 + 4$,
    $6 = 1 \cdot 4 + 2$, $4 = 2 \cdot 2 + 0$. Working back:

    $$2 = 6 - 4 = 6 - (10 - 6) = 2 \cdot 6 - 10 = 2(46 - 4 \cdot 10) - 10 = 2 \cdot 46 - 9 \cdot 10$$
    $$= 2 \cdot 46 - 9(240 - 5 \cdot 46) = 47 \cdot 46 - 9 \cdot 240.$$

??? abstract "The math: why it is correct and how fast it is"

    **Correctness.** If $d \mid a$ and $d \mid b$, then $d \mid a - qb$. If $d \mid b$ and $d \mid a - qb$, then
    $d \mid a$. So $(a, b)$ and $(b, a \bmod b)$ have the same common divisors and the same gcd. The remainders
    strictly decrease, so the loop ends, and $\gcd(g, 0) = g$.

    **Extended.** If $b x_1 + (a \bmod b) y_1 = g$ and $a \bmod b = a - \lfloor a/b \rfloor b$, then
    $a y_1 + b (x_1 - \lfloor a/b \rfloor y_1) = g$.

    **Speed.** After two steps the first number at least halves: if $b \le a/2$ then $a \bmod b < b \le a/2$;
    otherwise $a \bmod b = a - b < a/2$. So at most about $2 \log_2 b$ steps.

    **Lamé's theorem (1844):** the worst case is two consecutive Fibonacci numbers. If Euclid takes $k$ steps, then
    $b \ge F_{k+1}$; since $F_k$ grows like $1.618^k$, the number of steps is at most about
    $\log_{1.618} b \approx 4.785 \log_{10} b$, that is, under five steps per decimal digit.

    **Bézout's identity.** $\gcd(a, b)$ is the smallest positive number of the form $ax + by$; every such number is
    a multiple of it.

??? tip "Watch it step by step"

    Orange is the divisor, red the new remainder. Each row's $b$ and remainder become the next row's $a$ and $b$.

    <div class="cs-anim" data-anim="gcd"></div>

??? info "Variations and related ideas"

    - **Binary GCD** (Stein's algorithm): only halving and subtraction, no division; good for very big numbers
      and simple hardware.
    - **Chinese remainder theorem:** solve $x \equiv r_1 \pmod{m_1}$, $x \equiv r_2 \pmod{m_2}$ with extended
      Euclid when $\gcd(m_1, m_2) = 1$.
    - **Continued fractions:** the quotients $2, 3, 7$ above are the continued fraction of $1071/462$; they give the
      best rational approximations, used in calendars and gear ratios.
    - **Polynomials:** the same algorithm finds the gcd of two polynomials.

## See also

- [Fast exponentiation](fast-power.md): inverses modulo a prime via Fermat
- [Number theory](index.md)
- [Fibonacci](../dp/fibonacci.md): the worst case for Euclid

## References

- Euclid, *Elements*, Book VII, Propositions 1–2 (about 300 BC).
- D. E. Knuth, *The Art of Computer Programming*, Vol. 2, 3rd ed., Section 4.5.2 (the greatest common divisor).
- G. Lamé, "Note sur la limite du nombre des divisions dans la recherche du plus grand commun diviseur entre deux
  nombres entiers", *Comptes rendus de l'Académie des sciences* 19, 1844.
