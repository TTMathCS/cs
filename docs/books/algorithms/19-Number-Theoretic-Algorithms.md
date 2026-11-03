# 19. Number-theoretic and algebraic algorithms

*Every time a browser opens a secure connection, it raises a number with hundreds of digits to a power with hundreds
of digits, modulo a third such number, and it finds large random primes when it makes a key. None of this could be
done by the methods taught at school: multiplying 617-digit numbers is fine, but $a^e$ for a 617-digit $e$ has more
digits than there are atoms in the universe. This chapter is about computing with whole numbers when the numbers are
huge. You will meet the oldest algorithm still in use and prove how fast it is, raise to enormous powers in a few
thousand steps, list primes with sieves, test whether a 100-digit number is prime in a millisecond with a test that
can lie but almost never does, split numbers into their prime factors, solve systems of remainders, and finally
multiply polynomials and big numbers fast with a Fourier transform that uses no complex numbers at all.*

!!! abstract "In this chapter"
    **You will learn:**

    - why the cost of a number algorithm is measured in digits, and why trial division is exponential
    - Euclid's and the extended Euclid algorithm, with Lamé's bound on the number of steps
    - modular arithmetic, fast powering by repeated squaring, and modular inverses
    - the sieve of Eratosthenes in $O(n \log \log n)$ and the linear sieve
    - the Fermat test, Carmichael numbers, and the Miller-Rabin test with a proof of its error bound
    - Pollard's rho factoring method, the Chinese remainder theorem as an algorithm, matrix powers for recurrences, and
      the number-theoretic transform

    **You need:** [Chapter 1](01-What-Is-an-Algorithm.md) (Euclid's algorithm first appears in 1.7),
    [Chapter 3](03-Recursion-and-Induction.md) (induction, recurrences) and [Chapter 11](11-Divide-and-Conquer.md)
    (Karatsuba and the fast Fourier transform). For the algebra behind it all (divisibility, primes, groups):
    https://math.akadian.ca/books/ and in particular https://math.akadian.ca/books/algebra/. The cryptography that uses
    these algorithms is in https://cryptography.akadian.ca/book/.

    **Levels:** 19.1 to 19.3 are beginner to intermediate; 19.4 to 19.6 are intermediate to advanced; 19.7 is advanced.

## 19.1 GCD and extended Euclid

**First, what does "fast" mean for numbers?** For sorting, the input size $n$ was the number of items. For a number
algorithm the input is one or a few numbers, and their *size* is how many digits (or bits) they have. A number $N$ has
about $\log_2 N$ bits. A 2048-bit RSA modulus is about $3.2 \times 10^{616}$, but its size is 2048. So an algorithm that
takes $O(\log N)$ or $O((\log N)^3)$ steps is fast (polynomial in the size), while one that takes $O(\sqrt N)$ steps is
**exponential** in the size: $\sqrt N = 2^{(\log_2 N)/2}$. Trial division up to $\sqrt N$ is fine for a 12-digit
number and hopeless for a 617-digit one. Keep this in mind throughout: we always count in $\log N$.

**The greatest common divisor.** For whole numbers $a$ and $b$, not both 0, $\gcd(a, b)$ is the largest whole number
that divides both. For example $\gcd(240, 46) = 2$. If $\gcd(a, b) = 1$ we say $a$ and $b$ are **coprime**. The school
method, factor both numbers and take the common primes, needs factoring, which we will see is hard. Euclid's method
needs only division with remainder.

**Lemma 19.1.** For $b > 0$, $\gcd(a, b) = \gcd(b, a \bmod b)$.

*Proof.* Write $a = qb + r$ with $r = a \bmod b$, so $0 \le r < b$. Any $d$ that divides $a$ and $b$ divides $r = a - qb$.
Any $d$ that divides $b$ and $r$ divides $a = qb + r$. So the pairs $(a, b)$ and $(b, r)$ have exactly the same common
divisors, hence the same greatest one. $\square$

Since $\gcd(a, 0) = a$, the algorithm is: replace $(a, b)$ by $(b, a \bmod b)$ until $b = 0$, then answer $a$. It stops
because the second number strictly decreases and stays at least 0. Here it is on $(21, 13)$, drawn the way the Greeks
thought of it: cut the largest possible squares off a rectangle, then repeat on what is left.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 290" role="img" aria-label="A 21 by 13 rectangle cut into squares the way Euclid's algorithm divides: one 13 square, one 8, one 5, one 3, one 2 and two 1 squares. The last square side, 1, is the gcd.">
<rect x="20" y="20" width="234" height="234" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="137.0" y="142.0" font-size="14" text-anchor="middle" fill="currentColor">13</text>
<rect x="254" y="20" width="144" height="144" fill="#eea66f" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="326.0" y="97.0" font-size="14" text-anchor="middle" fill="currentColor">8</text>
<rect x="254" y="164" width="90" height="90" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="299.0" y="214.0" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<rect x="344" y="164" width="54" height="54" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="371.0" y="196.0" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<rect x="344" y="218" width="36" height="36" fill="#eea66f" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="362.0" y="241.0" font-size="11" text-anchor="middle" fill="currentColor">2</text>
<rect x="380" y="218" width="18" height="18" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<rect x="380" y="236" width="18" height="18" fill="#7ccf9a" fill-opacity="0.45" stroke="currentColor" stroke-width="1.3"/>
<text x="420" y="48" font-size="14" fill="currentColor" font-family="monospace">21 = 1·13 + 8</text>
<text x="420" y="78" font-size="14" fill="currentColor" font-family="monospace">13 = 1·8 + 5</text>
<text x="420" y="108" font-size="14" fill="currentColor" font-family="monospace">8 = 1·5 + 3</text>
<text x="420" y="138" font-size="14" fill="currentColor" font-family="monospace">5 = 1·3 + 2</text>
<text x="420" y="168" font-size="14" fill="currentColor" font-family="monospace">3 = 1·2 + 1</text>
<text x="420" y="198" font-size="14" fill="currentColor" font-family="monospace">2 = 2·1 + 0</text>
<text x="420" y="240" font-size="13" fill="currentColor">6 steps; gcd = 1</text>
<text x="209.0" y="278" font-size="12" text-anchor="middle" fill="currentColor">21 × 13 rectangle (F8 × F7)</text>
</svg>
<figcaption>Figure 19.1. Euclid's algorithm on 21 and 13 as cutting squares from a rectangle. Each division step removes as many squares of the shorter side as fit; the last square's side is the gcd. Consecutive Fibonacci numbers give one square per step, the slowest possible case.</figcaption>
</figure>

### Lamé's bound

**The question.** How many division steps can Euclid's algorithm take? Each step makes the numbers smaller, but by how
much? The worst case is when every quotient is 1, as in the figure, and then the numbers are consecutive **Fibonacci
numbers** $F_0 = 0$, $F_1 = 1$, $F_{k+2} = F_{k+1} + F_k$ (0, 1, 1, 2, 3, 5, 8, 13, 21, ...).

**Theorem 19.2 (Lamé 1844).** If $a > b \ge 1$ and Euclid's algorithm on $(a, b)$ takes $k \ge 1$ division steps, then
$b \ge F_{k+1}$ and $a \ge F_{k+2}$.

*Proof.* By induction on $k$. For $k = 1$: $b \ge 1 = F_2$ and $a > b$ gives $a \ge 2 = F_3$. For $k \ge 2$: the first step
turns $(a, b)$ into $(b, r)$ with $r = a \bmod b \ge 1$ (it is not 0, since more steps follow), and the algorithm then
takes $k - 1$ steps on $(b, r)$, with $b > r \ge 1$. By induction $r \ge F_k$ and $b \ge F_{k+1}$. And since $a > b$ the
quotient $q = \lfloor a/b \rfloor$ is at least 1, so $a = qb + r \ge b + r \ge F_{k+1} + F_k = F_{k+2}$. $\square$

Since $F_{k+1} \ge \varphi^{k-1}$ where $\varphi = (1 + \sqrt 5)/2 \approx 1.618$ is the golden ratio (another induction:
$\varphi^2 = \varphi + 1$), the number of steps is at most $1 + \log_\varphi b$, which is $O(\log b)$. In decimal terms,
$\log_\varphi 10 \approx 4.785$, so the number of steps is at most about 5 times the number of decimal digits of the
smaller number. That is how Gabriel Lamé stated it in 1844, and his result is often called the first analysis of the
running time of an algorithm. The bound is tight: on $(F_{k+2}, F_{k+1})$ Euclid takes exactly $k$ steps, as the program
below confirms (30 steps for $F_{32} = 2\,178\,309$ and $F_{31}$), and the worst pair below 1000 is $(987, 610)$ with 14
steps.

Counting bit operations: each step is a division of numbers with at most $\log_2 a$ bits. A careful count (the
quotients' lengths add up to about the length of $a$) gives $O((\log a)(\log b))$ bit operations in total, the same as
one schoolbook multiplication. **Binary GCD** (Josef Stein, 1967) replaces division by shifts and subtraction and is
popular in hardware and bignum libraries.

### The extended algorithm

**The question.** Euclid tells us $\gcd(240, 46) = 2$. Can we also write 2 as a combination $240x + 46y$ with whole
numbers $x$ and $y$? The answer is always yes, and the combination is the key to dividing in modular arithmetic.

**Theorem 19.3 (Bézout's identity).** For any $a, b$ not both 0 there are integers $x, y$ with $ax + by = \gcd(a, b)$.

*Proof, as an algorithm.* Run Euclid's algorithm on a sequence $r_0 = a$, $r_1 = b$, $r_{i+1} = r_{i-1} - q_i r_i$, and
carry along, for every remainder, a way of writing it as a combination of $a$ and $b$. Keep the **invariant**
$r_i = a x_i + b y_i$. It holds for $r_0$ with $(x_0, y_0) = (1, 0)$ and for $r_1$ with $(0, 1)$. If it holds for $r_{i-1}$
and $r_i$, then $r_{i+1} = r_{i-1} - q_i r_i = a(x_{i-1} - q_i x_i) + b(y_{i-1} - q_i y_i)$, so it holds for $r_{i+1}$ with
$x_{i+1} = x_{i-1} - q_i x_i$ and $y_{i+1} = y_{i-1} - q_i y_i$. The last nonzero remainder is the gcd, and its pair
$(x, y)$ is the answer. $\square$

**Trace** for $(240, 46)$, each row one remainder:

| $i$ | $q_i$ | $r_i$ | $x_i$ | $y_i$ | check $240x_i + 46y_i$ |
|---|---|---|---|---|---|
| 0 | | 240 | 1 | 0 | 240 |
| 1 | | 46 | 0 | 1 | 46 |
| 2 | 5 | 10 | 1 | $-5$ | $240 - 230 = 10$ |
| 3 | 4 | 6 | $-4$ | 21 | $-960 + 966 = 6$ |
| 4 | 1 | 4 | 5 | $-26$ | $1200 - 1196 = 4$ |
| 5 | 1 | 2 | $-9$ | 47 | $-2160 + 2162 = 2$ |
| 6 | 2 | 0 | 23 | $-120$ | $5520 - 5520 = 0$ |

So $240 \cdot (-9) + 46 \cdot 47 = 2$. The extra work per step is two multiplications and two subtractions, so the extended
algorithm has the same $O(\log b)$ step count. (The last row also says something: $240 \cdot 23 = 46 \cdot 120$ is the
least common multiple $5520$.) The reference page [Euclid's GCD](../../number-theory/gcd.md) has an animation and the
code in three languages.

**History.** The algorithm is in Book VII of Euclid's *Elements*, written around 300 BC, and was probably known before
him. Knuth (TAOCP volume 2) calls it "the granddaddy of all algorithms, because it is the oldest nontrivial algorithm
that has survived to the present day".

## 19.2 Modular arithmetic, fast powering and inverses

**Arithmetic on a clock.** Fix a whole number $m \ge 2$, the **modulus**. We say $a \equiv b \pmod m$, "$a$ is
**congruent** to $b$ mod $m$", when $m$ divides $a - b$, that is, when $a$ and $b$ leave the same remainder on division by
$m$. On a 12-hour clock, $15 \equiv 3 \pmod{12}$. Congruence respects addition and multiplication: if $a \equiv a'$ and
$b \equiv b'$ then $a + b \equiv a' + b'$ and $ab \equiv a'b'$. (Proof of the second: $ab - a'b' = a(b - b') + b'(a - a')$,
a sum of multiples of $m$.) So we may **reduce mod $m$ after every operation**, and numbers never grow beyond $m^2$.
The set $\{0, 1, \ldots, m-1\}$ with these operations is written $\mathbb{Z}_m$ (or $\mathbb{Z}/m\mathbb{Z}$).

### Fast powering

**The problem.** Compute $a^e \bmod m$ for huge $e$. Multiplying by $a$ again and again takes $e - 1$ multiplications:
for a 2048-bit $e$, about $2^{2048}$ of them, which no computer will ever finish. But squaring doubles the exponent:
$a, a^2, a^4, a^8, \ldots$ reaches $a^{2^k}$ in $k$ squarings. Every exponent is a sum of powers of 2 (its binary digits),
so

$$
a^{13} = a^{8 + 4 + 1} = a^8 \cdot a^4 \cdot a^1 .
$$

**Square and multiply (right to left).** Look at the bits of $e$ from the lowest. Keep `base` $= a^{2^i}$; whenever bit $i$
is 1, multiply it into the result:

```python
def power_mod(base, exp, mod):
    result, base = 1 % mod, base % mod
    while exp > 0:
        if exp & 1:
            result = result * base % mod
        base = base * base % mod
        exp >>= 1
    return result
```

**Trace** of $3^{13} \bmod 7$ ($13 = 1101_2$):

| exp | low bit | result after | base after squaring |
|---|---|---|---|
| 13 | 1 | $1 \cdot 3 = 3$ | $3^2 = 9 \equiv 2$ |
| 6 | 0 | 3 | $2^2 = 4$ |
| 3 | 1 | $3 \cdot 4 = 12 \equiv 5$ | $4^2 = 16 \equiv 2$ |
| 1 | 1 | $5 \cdot 2 = 10 \equiv 3$ | (done) |

So $3^{13} \equiv 3 \pmod 7$. (Check with Fermat's little theorem below: $3^6 \equiv 1$, so $3^{13} = (3^6)^2 \cdot 3 \equiv 3$.)

**Theorem 19.4.** `power_mod` computes $a^e \bmod m$ with at most $2\lfloor \log_2 e \rfloor + 2$ multiplications mod $m$.

*Proof.* Invariant: before each pass, $\text{result} \cdot \text{base}^{\text{exp}} \equiv a^e \pmod m$. It holds at the start
(result $= 1$, base $= a$, exp $= e$). If exp is even, the pass replaces base by base$^2$ and exp by exp$/2$, which keeps
$\text{base}^{\text{exp}}$ the same. If exp is odd, it first multiplies result by base and the remaining exponent is
exp $- 1$, which is even, and then does the same. When exp reaches 0 the invariant says result $\equiv a^e$. The loop runs
once per bit of $e$, $\lfloor \log_2 e \rfloor + 1$ times, with at most two multiplications per pass. $\square$

So $2^{10^{18}} \bmod (10^9 + 7)$ takes 60 squarings and 24 multiplications (the exponent has 60 bits, 24 of them ones),
and a 2048-bit exponent about 3000 multiplications on average. The reference
page [Fast exponentiation](../../number-theory/fast-power.md) has the recursive version and an animation. The
left-to-right variant reads the bits from the top: square the result for each bit and multiply by $a$ when the bit is 1.
It uses the same number of operations and multiplies always by the same $a$, which helps when $a$ is small. In
cryptography the *pattern* of multiplications can leak the bits of a secret exponent through timing or power use; real
implementations use constant-time ladders, as the cryptography book explains.

### Inverses

**The question.** In ordinary arithmetic, $3x = 1$ has the solution $x = 1/3$. In $\mathbb{Z}_7$, is there an $x$ with
$3x \equiv 1$? Yes: $3 \cdot 5 = 15 \equiv 1$, so 5 plays the role of $1/3$ mod 7. Such an $x$ is called the **inverse** of
3 mod 7, written $3^{-1} \bmod 7$. In $\mathbb{Z}_{12}$, does 4 have an inverse? $4x$ is always one of $0, 4, 8$, never 1.
The difference is the gcd.

**Theorem 19.5.** $a$ has an inverse mod $m$ if and only if $\gcd(a, m) = 1$, and then the extended Euclid algorithm
finds it in $O(\log m)$ steps.

*Proof.* If $ax \equiv 1 \pmod m$ then $ax - 1 = km$ for some $k$, so any common divisor of $a$ and $m$ divides 1.
Conversely, if $\gcd(a, m) = 1$, Bézout gives $ax + my = 1$, and reducing mod $m$ gives $ax \equiv 1$. $\square$

For example $17^{-1} \bmod 3120$: extended Euclid gives $3120 \cdot 2 + 17 \cdot (-367) = 1$, so the inverse is
$-367 + 3120 = 2753$. This is exactly the private exponent of the toy RSA key in the cryptography book's RSA chapter.
In Python, `pow(17, -1, 3120)` (since Python 3.8) does the same.

**When $m = p$ is prime,** every $a \not\equiv 0$ is coprime to $p$, so every nonzero element has an inverse:
$\mathbb{Z}_p$ is a **field**, a number system where you can add, subtract, multiply and divide (except by 0). This is why
so many algorithms pick a prime modulus, such as $10^9 + 7$ or $998\,244\,353$.

**Theorem 19.6 (Fermat's little theorem).** If $p$ is prime and $p \nmid a$, then $a^{p-1} \equiv 1 \pmod p$.

*Proof.* The numbers $a \cdot 1, a \cdot 2, \ldots, a \cdot (p-1)$ mod $p$ are all nonzero and all different (if $ai \equiv aj$
then multiplying by $a^{-1}$ gives $i \equiv j$). So they are $1, 2, \ldots, p-1$ in some order. Multiply them all:
$a^{p-1} (p-1)! \equiv (p-1)! \pmod p$. Since $(p-1)!$ is a product of invertible numbers, cancel it. $\square$

So a second way to invert mod a prime is $a^{-1} \equiv a^{p-2} \pmod p$, by fast powering. It costs $O(\log p)$
multiplications, like extended Euclid, and is simpler to write, but works only for prime moduli. The same argument with
the $\varphi(m)$ numbers coprime to $m$ gives **Euler's theorem**: $a^{\varphi(m)} \equiv 1 \pmod m$ when $\gcd(a, m) = 1$,
where $\varphi$ is Euler's totient function.

**The other direction is hard.** Given $g$, $h$ and a prime $p$, finding $x$ with $g^x \equiv h \pmod p$ (the **discrete
logarithm**) has no known polynomial-time algorithm on ordinary computers. Fast powering one way, no fast way back: that
asymmetry is the foundation of Diffie-Hellman key exchange.

## 19.3 Sieves: Eratosthenes and the linear sieve

**The problem.** List all primes up to $n$ (a **prime** is a whole number $p \ge 2$ whose only divisors are 1 and $p$).
Testing each number by trial division costs about $\sum_{k \le n} \sqrt k$, roughly $n^{1.5}$. We can do much better by
working the other way round: instead of asking "is $k$ divisible by something?", let each prime announce its multiples.

**The sieve of Eratosthenes.** Write down $2, 3, \ldots, n$. The smallest number not crossed off is prime; cross off all of
its multiples; repeat. Two improvements: when crossing off multiples of $p$, start at $p^2$ (smaller multiples $kp$ with
$k < p$ have a smaller prime factor and are already crossed off), and stop once $p^2 > n$ (every composite $k \le n$ has
a prime factor at most $\sqrt k$, so it has been crossed off by then).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 290" role="img" aria-label="The numbers 1 to 60 in a grid of ten columns. Primes are green. Composites are coloured by the prime that crosses them off first: multiples of 2 blue, multiples of 3 orange, multiples of 5 and 7 grey with a strike.">
<rect x="20" y="20" width="50" height="36" fill="none" stroke="currentColor" stroke-width="0.8"/>
<text x="45.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">1</text>
<rect x="70" y="20" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="95.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<rect x="120" y="20" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="145.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">3</text>
<rect x="170" y="20" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="195.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">4</text>
<rect x="220" y="20" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="245.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<rect x="270" y="20" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="295.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">6</text>
<rect x="320" y="20" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="345.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">7</text>
<rect x="370" y="20" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="395.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">8</text>
<rect x="420" y="20" width="50" height="36" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="445.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">9</text>
<rect x="470" y="20" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="495.0" y="43.0" font-size="14" text-anchor="middle" fill="currentColor">10</text>
<rect x="20" y="56" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="45.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">11</text>
<rect x="70" y="56" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="95.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">12</text>
<rect x="120" y="56" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="145.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">13</text>
<rect x="170" y="56" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="195.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">14</text>
<rect x="220" y="56" width="50" height="36" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="245.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">15</text>
<rect x="270" y="56" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="295.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">16</text>
<rect x="320" y="56" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="345.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">17</text>
<rect x="370" y="56" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="395.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">18</text>
<rect x="420" y="56" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="445.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">19</text>
<rect x="470" y="56" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="495.0" y="79.0" font-size="14" text-anchor="middle" fill="currentColor">20</text>
<rect x="20" y="92" width="50" height="36" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="45.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">21</text>
<rect x="70" y="92" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="95.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">22</text>
<rect x="120" y="92" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="145.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">23</text>
<rect x="170" y="92" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="195.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">24</text>
<rect x="220" y="92" width="50" height="36" fill="none" stroke="currentColor" stroke-width="0.8"/>
<text x="245.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">25</text>
<line x1="228" y1="120" x2="262" y2="100" stroke="currentColor" stroke-width="1"/>
<rect x="270" y="92" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="295.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">26</text>
<rect x="320" y="92" width="50" height="36" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="345.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">27</text>
<rect x="370" y="92" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="395.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">28</text>
<rect x="420" y="92" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="445.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">29</text>
<rect x="470" y="92" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="495.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">30</text>
<rect x="20" y="128" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="45.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">31</text>
<rect x="70" y="128" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="95.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">32</text>
<rect x="120" y="128" width="50" height="36" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="145.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">33</text>
<rect x="170" y="128" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="195.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">34</text>
<rect x="220" y="128" width="50" height="36" fill="none" stroke="currentColor" stroke-width="0.8"/>
<text x="245.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">35</text>
<line x1="228" y1="156" x2="262" y2="136" stroke="currentColor" stroke-width="1"/>
<rect x="270" y="128" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="295.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">36</text>
<rect x="320" y="128" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="345.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">37</text>
<rect x="370" y="128" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="395.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">38</text>
<rect x="420" y="128" width="50" height="36" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="445.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">39</text>
<rect x="470" y="128" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="495.0" y="151.0" font-size="14" text-anchor="middle" fill="currentColor">40</text>
<rect x="20" y="164" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="45.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">41</text>
<rect x="70" y="164" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="95.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">42</text>
<rect x="120" y="164" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="145.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">43</text>
<rect x="170" y="164" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="195.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">44</text>
<rect x="220" y="164" width="50" height="36" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="245.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">45</text>
<rect x="270" y="164" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="295.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">46</text>
<rect x="320" y="164" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="345.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">47</text>
<rect x="370" y="164" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="395.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">48</text>
<rect x="420" y="164" width="50" height="36" fill="none" stroke="currentColor" stroke-width="0.8"/>
<text x="445.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">49</text>
<line x1="428" y1="192" x2="462" y2="172" stroke="currentColor" stroke-width="1"/>
<rect x="470" y="164" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="495.0" y="187.0" font-size="14" text-anchor="middle" fill="currentColor">50</text>
<rect x="20" y="200" width="50" height="36" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="45.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">51</text>
<rect x="70" y="200" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="95.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">52</text>
<rect x="120" y="200" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="145.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">53</text>
<rect x="170" y="200" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="195.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">54</text>
<rect x="220" y="200" width="50" height="36" fill="none" stroke="currentColor" stroke-width="0.8"/>
<text x="245.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">55</text>
<line x1="228" y1="228" x2="262" y2="208" stroke="currentColor" stroke-width="1"/>
<rect x="270" y="200" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="295.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">56</text>
<rect x="320" y="200" width="50" height="36" fill="#eea66f" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="345.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">57</text>
<rect x="370" y="200" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="395.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">58</text>
<rect x="420" y="200" width="50" height="36" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="0.8"/>
<text x="445.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">59</text>
<rect x="470" y="200" width="50" height="36" fill="#9cc9ea" fill-opacity="0.5" stroke="currentColor" stroke-width="0.8"/>
<text x="495.0" y="223.0" font-size="14" text-anchor="middle" fill="currentColor">60</text>
<rect x="20" y="254" width="16" height="16" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="0.8"/>
<text x="42" y="267" font-size="13" fill="currentColor">prime</text>
<rect x="150" y="254" width="16" height="16" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="0.8"/>
<text x="172" y="267" font-size="13" fill="currentColor">crossed by 2</text>
<rect x="280" y="254" width="16" height="16" fill="#eea66f" fill-opacity="0.6" stroke="currentColor" stroke-width="0.8"/>
<text x="302" y="267" font-size="13" fill="currentColor">crossed by 3</text>
<rect x="410" y="254" width="16" height="16" fill="none" stroke="currentColor" stroke-width="0.8"/><line x1="413" y1="267" x2="423" y2="257" stroke="currentColor"/>
<text x="432" y="267" font-size="13" fill="currentColor">crossed by 5 or 7</text>
</svg>
<figcaption>Figure 19.2. The sieve of Eratosthenes up to 60. Each composite is coloured by the prime that crosses it off first (its least prime factor). Crossing off stops after 7, because 11² = 121 > 60; every number left is prime.</figcaption>
</figure>

```python
def sieve(n):
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    p = 2
    while p * p <= n:
        if is_prime[p]:
            is_prime[p * p::p] = bytes(len(range(p * p, n + 1, p)))
        p += 1
    return is_prime
```

The slice assignment crosses off all multiples of $p$ in one fast operation inside Python, which is why this version
handles two million numbers in about a hundredth of a second.

**Theorem 19.7.** The sieve of Eratosthenes takes $O(n \log \log n)$ time.

*Proof.* Crossing off for the prime $p$ touches at most $n/p$ cells. The total is at most

$$
\sum_{p \le \sqrt n} \frac{n}{p} = n \sum_{p \le \sqrt n} \frac{1}{p} .
$$

A first, easy bound: the sum over primes is at most the sum over all $k \le \sqrt n$, the harmonic sum, which is
$O(\log n)$ (Chapter 2), so the sieve is $O(n \log n)$. The sharper bound needs **Mertens' second theorem** (1874):
$\sum_{p \le x} 1/p = \ln \ln x + O(1)$. With $x = \sqrt n$ this is $\ln \ln n + O(1)$, which gives $O(n \log \log n)$.
(Mertens' theorem is proved in number theory books such as Hardy and Wright; it rests on Chebyshev's estimates for how
many primes there are.) $\square$

The function $\log \log n$ grows so slowly that it is below 3 for every $n$ up to $5 \times 10^8$: in practice the sieve
is linear with a small constant. The program counts $4\,347\,778$ crossings for $n = 2 \times 10^6$, about $2.17n$; numbers
like 30 are crossed off three times (by 2, 3 and 5). See also the reference page
[Sieve of Eratosthenes](../../number-theory/sieve.md).

**How many primes are there?** The program finds $148\,933$ primes below two million. The **prime number theorem**
(proved by Hadamard and by de la Vallée Poussin, independently, in 1896) says the number of primes up to $x$, written
$\pi(x)$, satisfies $\pi(x) \sim x / \ln x$; for $x = 2 \times 10^6$ that estimate gives about $137\,800$, about 7 percent low,
as is usual for this simple form at this size (the ratio tends to 1 only slowly). For us the useful consequence is that **primes are common**: a random $k$-digit number
is prime with probability about $1/(2.3k)$. To find a random 300-digit prime, test a few hundred random odd candidates.

### The linear sieve

**The question.** Can we cross off each composite exactly once? Yes, if we let each composite be crossed off only by its
**least prime factor**. Let $\mathrm{lp}(k)$ denote the least prime factor of $k$. Every composite $c$ can be written
uniquely as $c = i \cdot p$ where $p = \mathrm{lp}(c)$ and $i = c / p$; then $p \le \mathrm{lp}(i)$. So: for each $i$ from 2 to $n$,
and for each prime $p \le \mathrm{lp}(i)$ with $ip \le n$, mark $\mathrm{lp}(ip) = p$.

```python
def linear_sieve(n):
    lp = [0] * (n + 1)
    primes = []
    for i in range(2, n + 1):
        if lp[i] == 0:              # nobody crossed i off: it is prime
            lp[i] = i
            primes.append(i)
        for p in primes:
            if p > lp[i] or i * p > n:
                break
            lp[i * p] = p
    return primes, lp
```

**Theorem 19.8 (Gries and Misra 1978).** The linear sieve sets $\mathrm{lp}(c)$ correctly for every $c \le n$ and does $O(n)$
work.

*Proof.* Each composite $c$ is written once as $i \cdot p$ with $p = \mathrm{lp}(c)$, and the inner loop at that $i$ reaches $p$
(because $p \le \mathrm{lp}(i)$ and all smaller primes are already in the list), so $c$ is marked, with the right value. No
composite is marked twice: a marking $\mathrm{lp}(ip) = p$ only happens with $p \le \mathrm{lp}(i)$, which forces $p = \mathrm{lp}(ip)$
and $i = c/p$, so the pair $(i, p)$ is determined by $c$. A number $i$ that is not marked by the time the loop reaches it
has no prime factor below it, so it is prime. The inner loop does one marking per step plus one final test, so the total
work is (number of composites) + $n$ = $O(n)$. $\square$

The linear sieve is not faster than Eratosthenes in practice: the program shows a pure Python linear sieve taking dozens of
times longer than the slice-based Eratosthenes, because constant factors matter more than a $\log \log n$
factor (Chapter 2's lesson). Its real value is the table $\mathrm{lp}$: with it, **any $k \le n$ can be factored in
$O(\log k)$ steps** by dividing by $\mathrm{lp}(k)$ repeatedly, as the program does for $360\,360 = 2^3 \cdot 3^2 \cdot 5 \cdot 7
\cdot 11 \cdot 13$. The same loop computes multiplicative functions such as $\varphi(k)$ for all $k \le n$ at once.

**Segmented sieve.** To list the primes in a window $[L, R]$ with $R$ around $10^{12}$, first sieve the primes up to
$\sqrt R = 10^6$, then cross off their multiples inside an array for the window only. Memory is $O(\sqrt R + (R - L))$
instead of $O(R)$ (exercise 7).

The program for 19.1 to 19.3:

```python
--8<-- "books/algorithms/ch19_arithmetic.py"
```

```
1. Euclid on consecutive Fibonacci numbers (the worst case)
   gcd(F7=13, F6=8) = 1 in 5 steps
   gcd(F12=144, F11=89) = 1 in 10 steps
   gcd(F22=17711, F21=10946) = 1 in 20 steps
   gcd(F32=2178309, F31=1346269) = 1 in 30 steps
   most steps for any 1 <= b <= a < 1000: 14
2. Extended Euclid
   240*(-9) + 46*(47) = 2
   3120*(2) + 17*(-367) = 1
   99*(-11) + 78*(14) = 3
   inverse of 17 mod 3120 = 2753  Python's pow: 2753
3. Fast powers
   3^200 mod 13 = 9  7^560 mod 561 = 1
   2^(10^18) mod (10^9+7) = 719476260  same as pow(): True
4. Sieves
   primes up to 2000000: 148933 (Eratosthenes) and 148933 (linear)
   times: slice-based Eratosthenes 0.01s, pure-Python linear sieve 0.44s
   360360 factored with the lp table: [2, 2, 2, 3, 3, 5, 7, 11, 13]
   Eratosthenes crossings: 4347778 = 2.174 n; linear sieve: 1851066 (one per composite)
```

(The two times will differ on your machine; the ratio between them is the point.)

## 19.4 Primality: Fermat, Miller-Rabin and AKS

*Level: intermediate to advanced.*

**The problem.** Given a number $n$ with hundreds of digits, is it prime? Trial division up to $\sqrt n$ needs about
$10^{150}$ divisions for a 300-digit number. A sieve is worse. We need a test that takes time polynomial in the number
of digits, and the surprise is that such a test can say "composite" without finding any factor.

### The Fermat test

Fermat's little theorem says that if $n$ is prime, then $a^{n-1} \equiv 1 \pmod n$ for every $a$ from 1 to $n-1$. Turn it
around: if we find an $a$ with $a^{n-1} \not\equiv 1$, then $n$ is certainly **composite**, and $a$ is a **Fermat witness**.
Computing $a^{n-1} \bmod n$ costs $O(\log n)$ multiplications. For example $2^{90} \bmod 91 = 64$, so 91 is composite (it is
$7 \times 13$), and we learned that without dividing.

If the test passes, $n$ may still be composite: a base $a$ with $a^{n-1} \equiv 1$ for composite $n$ is a **Fermat liar**.
For $n = 91$, 36 of the 90 bases lie (including the trivial 1 and 90). If some base coprime to $n$ is a witness, then
at least half of the bases coprime to $n$ are witnesses (because the liars coprime to $n$ form a subgroup of the units, and
a proper subgroup has at most half the elements; this argument appears again below). So a few random bases would expose
almost every composite, but not all:

**Carmichael numbers.** A composite $n$ with $a^{n-1} \equiv 1 \pmod n$ for *every* $a$ coprime to $n$ is a **Carmichael
number**. The smallest is $561 = 3 \cdot 11 \cdot 17$, found by Robert Carmichael in 1910. For it, every base coprime to 561
is a liar, and the only witnesses are the bases sharing a factor with 561, which are as hard to find as the factors.

**Theorem 19.9 (Korselt's criterion, 1899).** A composite $n$ is a Carmichael number if and only if $n$ is squarefree and
$p - 1$ divides $n - 1$ for every prime $p$ dividing $n$.

*Proof of the direction we use* ("if"). Let $\gcd(a, n) = 1$ and let $p \mid n$. By Fermat, $a^{p-1} \equiv 1 \pmod p$, and
since $(p-1) \mid (n-1)$, also $a^{n-1} \equiv 1 \pmod p$. This holds for every prime $p$ dividing $n$, and since $n$ is a
product of *distinct* primes, the Chinese remainder theorem (19.6) gives $a^{n-1} \equiv 1 \pmod n$. The "only if"
direction uses the existence of a primitive root mod $p^2$; see Crandall and Pomerance's book. $\square$

Check on 561: $560$ is divisible by $2$, $10$ and $16$. The program finds the 16 Carmichael numbers below $100\,000$, and
Alford, Granville and Pomerance proved in 1994 that there are infinitely many. So the Fermat test alone cannot be made
reliable.

### Miller-Rabin

**The extra idea: square roots of 1.** Mod a prime, the only solutions of $x^2 \equiv 1$ are $x \equiv \pm 1$.

**Lemma 19.10.** If $p$ is prime and $x^2 \equiv 1 \pmod p$, then $x \equiv 1$ or $x \equiv -1 \pmod p$.

*Proof.* $p$ divides $x^2 - 1 = (x - 1)(x + 1)$. A prime that divides a product divides one of the factors. $\square$

Mod a composite there can be more: mod 561, $67^2 = 4489 = 8 \cdot 561 + 1$, so 67 is a square root of 1 other than
$\pm 1$. Such a **nontrivial square root of 1** proves $n$ composite, and even gives a factor: $\gcd(67 - 1, 561) = 33$
and $\gcd(67 + 1, 561) = 17$.

**The test.** Write $n - 1 = 2^s d$ with $d$ odd. For a base $a$, look at the sequence

$$
a^d, \; a^{2d}, \; a^{4d}, \; \ldots, \; a^{2^s d} = a^{n-1} \pmod n ,
$$

where each term is the square of the one before. If $n$ is prime, the last term is 1 (Fermat), and by Lemma 19.10 the
term before the first 1 must be $-1$. So for prime $n$: **either $a^d \equiv 1$, or one of the terms before the last is
$-1$.** If neither happens, $a$ is a **strong witness** and $n$ is composite. Otherwise $a$ is a **strong liar** (if $n$ is
in fact composite).

**Trace** for $n = 561$, $a = 2$: $560 = 2^4 \cdot 35$. The sequence is

$$
2^{35} \equiv 263, \quad 263^2 \equiv 166, \quad 166^2 \equiv 67, \quad 67^2 \equiv 1, \quad 1^2 \equiv 1 \pmod{561} .
$$

The first 1 comes right after 67, which is not $-1 \equiv 560$. So 2 is a strong witness: 561 is composite, even though
$2^{560} \equiv 1$ fools the Fermat test.

**Theorem 19.11.** If $n$ is an odd composite, at most half of the bases $a \in \{1, \ldots, n-1\}$ are strong liars.

*Proof.* Every strong liar is coprime to $n$ (it satisfies $a^{n-1} \equiv 1$, so it is invertible). Let $\mathbb{Z}_n^*$
be the set of the $\varphi(n)$ invertible elements mod $n$; it is a group under multiplication. We find a **proper
subgroup** $B$ of $\mathbb{Z}_n^*$ that contains all strong liars. By Lagrange's theorem (the size of a subgroup divides
the size of the group; https://math.akadian.ca/books/algebra/), $|B| \le \varphi(n)/2 < (n-1)/2$, which proves the claim.

*Case 1: some unit $x$ has $x^{n-1} \not\equiv 1$.* Let $B = \{a \in \mathbb{Z}_n^* : a^{n-1} \equiv 1\}$, the Fermat liars. It is
closed under multiplication, so it is a subgroup, and $x \notin B$, so it is proper. Every strong liar is in $B$.

*Case 2: every unit satisfies $a^{n-1} \equiv 1$,* so $n$ is a Carmichael number, hence squarefree with at least two prime
factors (Theorem 19.9; Carmichael numbers in fact have at least three). Write $n = n_1 n_2$ with $\gcd(n_1, n_2) = 1$ and
$n_1, n_2 > 1$. Among all pairs $(v, j)$ with $v$ a unit and $v^{2^j d} \equiv -1 \pmod n$, choose one with $j$ as large as
possible; call it $t$. Such pairs exist ($v = -1$, $j = 0$, since $d$ is odd) and $t < s$ (because $v^{2^s d} \equiv 1$). Let

$$
B = \{ a \in \mathbb{Z}_n^* : a^{2^t d} \equiv \pm 1 \pmod n \} .
$$

$B$ is closed under multiplication, so it is a subgroup. Every strong liar $a$ is in $B$: either $a^d \equiv 1$, and then
$a^{2^t d} \equiv 1$; or $a^{2^j d} \equiv -1$ for some $j$, then $j \le t$ by the choice of $t$, and squaring $t - j$ more times
gives $\pm 1$. To see that $B$ is proper, use the Chinese remainder theorem to pick $w$ with $w \equiv v \pmod{n_1}$ and $w
\equiv 1 \pmod{n_2}$. Then $w$ is a unit, $w^{2^t d} \equiv -1 \pmod{n_1}$ and $w^{2^t d} \equiv 1 \pmod{n_2}$. If
$w^{2^t d} \equiv 1 \pmod n$ the first fails, and if $w^{2^t d} \equiv -1 \pmod n$ the second fails (as $n_2 > 2$). So
$w \notin B$. $\square$

This proof follows CLRS (section 31.8). With more work the bound improves:

**Theorem 19.12 (Monier 1980; Rabin 1980).** For odd composite $n > 9$, at most $\varphi(n)/4$ bases are strong liars.

The program checks it on a few numbers: $n = 91$ and $n = 8911$ have exactly $\varphi(n)/4$ strong liars (18 of 72, and
1782 of 7128), so the bound is tight, while for the Carmichael numbers 561 and 1105 only 3 to 4 percent of the units lie,
although every unit fools the Fermat test.

**The error after $k$ rounds.** Choose $k$ bases independently at random. If $n$ is prime the test always says "probably
prime". If $n$ is composite, each round independently says "probably prime" with probability at most $1/4$, so all $k$
do with probability at most $4^{-k}$. With $k = 40$ that is below $10^{-24}$. Each round costs $O(\log n)$ multiplications
of $\log n$-bit numbers, so with schoolbook multiplication a round is $O((\log n)^3)$ bit operations. The test never
errs on primes; it can err on composites with tiny probability: a **Monte Carlo** algorithm with one-sided error.

**Deterministic versions.** For numbers of bounded size, a fixed set of bases is enough. Computer searches (Jaeschke
1993; Sorenson and Webster 2015) showed that the first twelve primes $2, 3, \ldots, 37$ as bases give the right answer for
every $n < 2^{64}$; the program's `is_prime` uses them and agrees with the sieve on every number up to a million. Gary
Miller's original 1976 test was deterministic, using all bases up to $O((\log n)^2)$, but its correctness depends on the
unproved generalized Riemann hypothesis; Eric Bach (1990) showed that bases up to $2 (\ln n)^2$ suffice under that
hypothesis. Michael Rabin's 1980 paper turned it into the randomized test with the proven error bound.

**AKS.** In 2002 Manindra Agrawal, Neeraj Kayal and Nitin Saxena, at IIT Kanpur, gave the first primality test that is
deterministic, unconditional and polynomial-time ("PRIMES is in P", *Annals of Mathematics*, 2004). It rests on a
polynomial version of Fermat's theorem: $n$ is prime if and only if $(x + a)^n \equiv x^n + a$ modulo $n$ as polynomials,
checked cleverly modulo $x^r - 1$ for a small $r$. The original running time was about $(\log n)^{12}$, ignoring smaller
factors; Lenstra and Pomerance later reduced it to about $(\log n)^6$. It settled a theoretical question, but Miller-Rabin is much
faster and is what software uses. When a proof of primality is needed, the elliptic-curve primality proving method
(ECPP) is the practical choice.

## 19.5 Factoring: trial division and Pollard's rho

*Level: intermediate to advanced.*

**The problem.** Given a composite $n$, find a nontrivial factor. Unlike primality, no polynomial-time method is known on
ordinary computers, and the security of RSA rests on this. But for numbers up to about 20 digits, or numbers with a
smallish factor, there are good methods.

**Trial division.** Divide by $2, 3, 5, 7, \ldots$ up to $\sqrt n$. If $n$ has a factor at all, it has one at most $\sqrt n$, so
this finds the smallest prime factor $p$ in about $p$ steps and proves primality in about $\sqrt n$ steps. Exponential in
the number of digits, but unbeatable for removing small factors first, which every factoring program does.

### Pollard's rho

**The idea.** Suppose $n$ has an unknown prime factor $p$. Walk through a sequence $x_0, x_1, x_2, \ldots$ mod $n$ given by
$x_{i+1} = f(x_i) = x_i^2 + c \bmod n$. Look at the same sequence mod $p$: since $x_{i+1} \bmod p$ depends only on $x_i
\bmod p$, and there are only $p$ values, the sequence mod $p$ must eventually repeat, and from then on it cycles. Its
picture is a tail leading into a loop, like the Greek letter $\rho$. If $x_i \equiv x_j \pmod p$ but $x_i \neq x_j$ then $p$
divides $x_i - x_j$ but $n$ does not, so $\gcd(x_i - x_j, n)$ is a nontrivial factor. We never need to know $p$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 620 290" role="img" aria-label="The rho shape of Pollard's method for 8051 = 83 times 97. Modulo 97 the sequence 2, 5, 26, 95 enters the cycle 5, 26, 95 after one step. Floyd's two pointers meet at step 3, and the gcd of x3 minus x6 with 8051 is 97.">
<line x1="120.0" y1="237.0" x2="120.0" y2="207.0" stroke="currentColor" stroke-width="1.5"/><polygon points="120.0,198.0 124.0,207.0 116.0,207.0" fill="currentColor"/>
<line x1="129.8" y1="164.9" x2="160.3" y2="117.7" stroke="currentColor" stroke-width="1.5"/><polygon points="165.2,110.1 163.7,119.8 157.0,115.5" fill="currentColor"/>
<line x1="157.0" y1="95.0" x2="92.0" y2="95.0" stroke="currentColor" stroke-width="1.5"/><polygon points="83.0,95.0 92.0,91.0 92.0,99.0" fill="currentColor"/>
<line x1="74.8" y1="110.1" x2="105.3" y2="157.3" stroke="currentColor" stroke-width="1.5"/><polygon points="110.2,164.9 102.0,159.5 108.7,155.2" fill="currentColor"/>
<circle cx="120" cy="255" r="18" fill="#7ccf9a" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="120" y="260" font-size="14" text-anchor="middle" fill="currentColor">2</text>
<circle cx="120" cy="180" r="18" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="120" y="185" font-size="14" text-anchor="middle" fill="currentColor">5</text>
<circle cx="175" cy="95" r="18" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="175" y="100" font-size="14" text-anchor="middle" fill="currentColor">26</text>
<circle cx="65" cy="95" r="18" fill="#9cc9ea" fill-opacity="0.6" stroke="currentColor" stroke-width="1.3"/>
<text x="65" y="100" font-size="14" text-anchor="middle" fill="currentColor">95</text>
<text x="120" y="30" font-size="13" text-anchor="middle" fill="currentColor">x mod 97</text>
<text x="40" y="225" font-size="12" text-anchor="middle" fill="currentColor">tail</text>
<text x="120" y="127" font-size="11" text-anchor="middle" fill="currentColor">cycle of 3</text>
<text x="250" y="40" font-size="13" fill="currentColor">x(i+1) = x(i)² + 1 mod 8051, x(0) = 2</text>
<text x="262" y="82" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">i</text><text x="340" y="82" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">x(i)</text><text x="430" y="82" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">mod 97</text>
<text x="262" y="103" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">0</text><text x="340" y="103" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">2</text><text x="430" y="103" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">2</text>
<text x="262" y="124" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">1</text><text x="340" y="124" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">5</text><text x="430" y="124" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">5</text>
<text x="262" y="145" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">2</text><text x="340" y="145" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">26</text><text x="430" y="145" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">26</text>
<text x="262" y="166" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">3</text><text x="340" y="166" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">677</text><text x="430" y="166" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">95</text>
<text x="262" y="187" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">4</text><text x="340" y="187" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">7474</text><text x="430" y="187" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">5</text>
<text x="262" y="208" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">5</text><text x="340" y="208" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">2839</text><text x="430" y="208" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">26</text>
<text x="262" y="229" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">6</text><text x="340" y="229" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">871</text><text x="430" y="229" font-size="13" text-anchor="end" fill="currentColor" font-family="monospace">95</text>
<text x="250" y="271" font-size="13" fill="currentColor">x(3) ≡ x(6) mod 97, so gcd(871 − 677, 8051) = 97</text>
</svg>
<figcaption>Figure 19.3. Pollard's rho on 8051 = 83 · 97. Modulo the unknown factor 97 the sequence has a tail of length 1 and a cycle of length 3. Floyd's method compares x(i) with x(2i); at i = 3 they agree mod 97 but not mod 8051, and a gcd reveals 97.</figcaption>
</figure>

**How soon does it repeat?** If $f$ behaved like a random function on $p$ values, the **birthday paradox** says a repeat
is expected after about $\sqrt{\pi p / 2}$ steps. (The probability that $k$ random values are all different is
$\prod_{i<k}(1 - i/p) \le e^{-k(k-1)/(2p)}$, which is small once $k$ is a few times $\sqrt p$.) Since $p \le \sqrt n$ for the
smallest factor, that is $O(n^{1/4})$ steps. This is a heuristic: $x^2 + c$ is not truly random, and no proof of the
$O(\sqrt p)$ bound for it is known, but it matches experience very well.

**Finding the repeat without storing the sequence: Floyd's cycle finding.** Run two pointers, a tortoise $x_i$ and a hare
$x_{2i}$, and compare at each step.

**Lemma 19.13 (Floyd).** If a sequence defined by $x_{i+1} = f(x_i)$ has a tail of length $\mu$ and a cycle of length
$\lambda$, then $x_i = x_{2i}$ for some $i \le \mu + \lambda$.

*Proof.* For $i \ge \mu$, $x_i = x_{2i}$ exactly when $\lambda$ divides $2i - i = i$. The multiples of $\lambda$ include one in
every run of $\lambda$ consecutive integers, so there is one in $[\mu, \mu + \lambda)$ (or $i = \lambda$ itself if $\mu = 0$). $\square$

The method is usually credited to Robert Floyd, who did not publish it; Knuth describes it in TAOCP volume 2. In the
example, mod 97 the tail is $\mu = 1$ and the cycle $\lambda = 3$, so the pointers meet at $i = 3$. Mod 83 the sequence
has $\mu = 4$ and $\lambda = 5$, so the other factor would only show up at $i = 5$; the smaller cycle wins.

```python
def pollard_rho(n, c=1, x0=2):
    f = lambda x: (x * x + c) % n
    x = y = x0
    d = 1
    while d == 1:
        x = f(x)
        y = f(f(y))
        d = math.gcd(abs(x - y), n)
    return d          # may be n itself: then retry with another c
```

If both factors' cycles close at the same step, the gcd is $n$ itself and we retry with a different $c$. A complete
factoring routine combines everything: remove small primes by trial division, stop if Miller-Rabin says prime, otherwise
split with rho and recurse on both parts. The program factors $2^{64} + 1 = 274\,177 \times 67\,280\,421\,310\,721$ this way
(that number is the Fermat number $F_6$, first factored by Fortuné Landry in 1880 by hand), and a 28-digit product of
the primes $2^{31} - 1$ and $2^{61} - 1$ in about two seconds.

**Cost and history.** Each step costs three evaluations of $f$ and one gcd. John Pollard published the method in 1975.
Richard Brent's 1980 variant replaces Floyd's comparison by a faster cycle-finder and batches the gcds (multiply many
differences together mod $n$ and take one gcd), and in 1980 Brent and Pollard used it to factor the eighth Fermat number
$F_8 = 2^{256} + 1$. For numbers whose smallest factor is large, rho is too slow, and the methods of choice are the
**elliptic curve method** (Lenstra 1987), whose cost depends on the size of the smallest factor, and for the hardest
case, a product of two primes of equal size, the **quadratic sieve** (Pomerance, early 1980s) and the **general number
field sieve** (developed around 1990 by Pollard, Lenstra, Lenstra, Manasse and others). The number field sieve runs in
time about $\exp\left( (64/9)^{1/3} (\ln n)^{1/3} (\ln \ln n)^{2/3} \right)$: **subexponential**, faster than any power of
$n$ but slower than any polynomial in $\log n$. The largest RSA challenge number factored so far with it, RSA-250 (829
bits), was done in 2020 by Boudot, Gaudry, Guillevic, Heninger, Thomé and Zimmermann. On a large quantum computer, Shor's
algorithm (1994) would factor in polynomial time; [Chapter 25](25-Where-Algorithms-Go.md) says what that does and does
not mean.

## 19.6 The Chinese remainder theorem as an algorithm

**The problem.** A number leaves remainder 2 when divided by 3, remainder 3 when divided by 5, and remainder 2 when
divided by 7. What is it? This puzzle appears in the Chinese text *Sunzi Suanjing*, from somewhere between the 3rd and
5th centuries; the answer given is 23. The general method was written out by Qin Jiushao in 1247.

**Theorem 19.14 (Chinese remainder theorem).** Let $m_1, \ldots, m_k$ be pairwise coprime and $M = m_1 m_2 \cdots m_k$. For any
$r_1, \ldots, r_k$ there is exactly one $x$ with $0 \le x < M$ and $x \equiv r_i \pmod{m_i}$ for all $i$.

*Proof.* **Uniqueness:** if $x$ and $x'$ both work, every $m_i$ divides $x - x'$, and since they are pairwise coprime, so
does their product $M$; with both in $[0, M)$ that forces $x = x'$. **Existence, by an algorithm:** we build $x$ one
congruence at a time. Suppose $x$ satisfies the first $j$ congruences, and let $M_j = m_1 \cdots m_j$. Every number $x + t M_j$
still satisfies them. We want $x + t M_j \equiv r_{j+1} \pmod{m_{j+1}}$, that is,

$$
t \equiv (r_{j+1} - x) \cdot M_j^{-1} \pmod{m_{j+1}} ,
$$

and the inverse exists because $\gcd(M_j, m_{j+1}) = 1$. Starting from $x = 0$, $M_0 = 1$, after $k$ rounds $x$ satisfies all
congruences. $\square$

```python
def crt(residues, moduli):
    x, M = 0, 1
    for r, m in zip(residues, moduli):
        t = (r - x) * inverse(M, m) % m
        x, M = x + M * t, M * m
    return x % M, M
```

**Trace** for Sunzi's puzzle:

| step | congruence | $t$ | $x$ after | $M$ after |
|---|---|---|---|---|
| 1 | $x \equiv 2 \pmod 3$ | $(2 - 0) \cdot 1^{-1} \equiv 2$ | $0 + 1 \cdot 2 = 2$ | 3 |
| 2 | $x \equiv 3 \pmod 5$ | $(3 - 2) \cdot 3^{-1} \equiv 1 \cdot 2 = 2$ | $2 + 3 \cdot 2 = 8$ | 15 |
| 3 | $x \equiv 2 \pmod 7$ | $(2 - 8) \cdot 15^{-1} \equiv (-6) \cdot 1 \equiv 1$ | $8 + 15 \cdot 1 = 23$ | 105 |

($3^{-1} \equiv 2 \pmod 5$ since $3 \cdot 2 = 6 \equiv 1$; $15 \equiv 1 \pmod 7$, so its inverse is 1.) Answer 23, unique mod 105.

**Cost.** Each round is one extended Euclid and a few multiplications, so the whole is $O(k)$ operations on numbers up to
$M$. This incremental form is essentially **Garner's algorithm** (1959), which keeps the answer in a "mixed radix" form so
that most arithmetic stays modulo the small $m_i$.

**What it is for.** The theorem says that $\mathbb{Z}_M$ behaves like the tuple $(\mathbb{Z}_{m_1}, \ldots, \mathbb{Z}_{m_k})$: to
add or multiply numbers mod $M$, you can work mod each $m_i$ separately, in parallel, and combine at the end. Three uses:

- **Big exact results from small primes.** To compute an integer that is known to be less than some bound (a
  determinant, say), compute it modulo several word-sized primes whose product exceeds twice the bound, and combine with
  CRT. Every step is cheap machine arithmetic. The same trick makes the NTT of 19.7 work for big integers: do the
  transform modulo two or three NTT-friendly primes and combine.
- **RSA with CRT.** The owner of an RSA key knows $n = pq$ and decrypts mod $p$ and mod $q$ separately, each with half-size
  numbers, then combines: about four times faster. The cryptography book's RSA chapter covers this, and the fault attack
  that breaks it if one half is computed wrongly.
- **Solving congruences mod composite numbers.** Square roots mod $n = pq$, or $x^2 \equiv 1$ as in Miller-Rabin: four
  solutions, from the combinations of $\pm 1$ mod $p$ and $\pm 1$ mod $q$.

If the moduli are not coprime, a solution exists exactly when the residues agree modulo each $\gcd(m_i, m_j)$, and is
then unique modulo the least common multiple.

The program for 19.4 to 19.6:

```python
--8<-- "books/algorithms/ch19_primes.py"
```

```
1. Carmichael numbers below 100000, by Korselt's criterion
   [561, 1105, 1729, 2465, 2821, 6601, 8911, 10585, 15841, 29341, 41041, 46657, 52633, 62745, 63973, 75361]
   561 =  [3, 11, 17]  2^560 mod 561 = 1
2. Miller-Rabin on 561 with base 2
   560 = 2^4 * 35; 2^(35*2^j) mod 561 for j = 0..4: [263, 166, 67, 1, 1]
3. Share of bases that lie, for some odd composites
   n=   91: phi(n)=   72, Fermat liars   36, strong liars   18 = 0.250 phi(n)
   n=  561: phi(n)=  320, Fermat liars  320, strong liars   10 = 0.031 phi(n)
   n= 1105: phi(n)=  768, Fermat liars  768, strong liars   30 = 0.039 phi(n)
   n= 8911: phi(n)= 7128, Fermat liars 7128, strong liars 1782 = 0.250 phi(n)
   n=   65: phi(n)=   48, Fermat liars   16, strong liars    6 = 0.125 phi(n)
4. Miller-Rabin with 12 bases agrees with the sieve up to 1000000
   agree: True
   2^61 - 1 prime? True   2^61 + 1 prime? False
5. Pollard's rho
   i=1: x=    5 y=   26 gcd=1
   i=2: x=   26 y= 7474 gcd=1
   i=3: x=  677 y=  871 gcd=97
   8051 = 83 * 97
   10403 = 101 * 103
   600851475143 = 71 * 839 * 1471 * 6857
   18446744073709551617 = 274177 * 67280421310721
   4951760154835678088235319297 = 2147483647 * 2305843009213693951
6. Chinese remainder theorem
   x = 2 mod 3, 3 mod 5, 2 mod 7: (23, 105)
   x = 1 mod 4, 2 mod 9, 3 mod 25: (353, 900)
```

## 19.7 Matrix exponentiation and the number-theoretic transform

*Level: advanced.*

### Recurrences by matrix powers

**The question.** The Fibonacci numbers satisfy $F_{k+1} = F_k + F_{k-1}$. Computing $F_n$ by the loop takes $n$ steps,
which is again exponential in the size of $n$. Can fast powering help? Write one step of the recurrence as a matrix
times a vector:

$$
\begin{pmatrix} F_{k+1} \\ F_k \end{pmatrix} = \begin{pmatrix} 1 & 1 \\ 1 & 0 \end{pmatrix} \begin{pmatrix} F_k \\ F_{k-1} \end{pmatrix} .
$$

Applying it $n$ times is multiplying by the $n$-th power of the matrix $Q = \begin{pmatrix} 1 & 1 \\ 1 & 0 \end{pmatrix}$.

**Lemma 19.15.** For $n \ge 1$, $Q^n = \begin{pmatrix} F_{n+1} & F_n \\ F_n & F_{n-1} \end{pmatrix}$.

*Proof.* For $n = 1$ it reads $Q = \begin{pmatrix} F_2 & F_1 \\ F_1 & F_0 \end{pmatrix}$, true. If it holds for $n$, then
$Q^{n+1} = Q^n Q$ has first row $(F_{n+1} + F_n, \; F_{n+1}) = (F_{n+2}, F_{n+1})$ and second row $(F_n + F_{n-1}, \; F_n)
= (F_{n+1}, F_n)$. $\square$

Matrix multiplication is associative, so square-and-multiply works for matrices exactly as for numbers (the proof of
Theorem 19.4 used nothing else). So $F_n \bmod m$ takes $O(\log n)$ multiplications of $2 \times 2$ matrices, each 8
multiplications mod $m$. The program prints $Q^{10}$, whose entries are $F_{11} = 89$, $F_{10} = 55$ and $F_9 = 34$, and computes
$F_{10^{18}} \bmod (10^9 + 7)$ in about 60 squarings.

**In general,** any linear recurrence $a_n = c_1 a_{n-1} + \cdots + c_k a_{n-k}$ becomes a $k \times k$ **companion matrix**
with $c_1, \ldots, c_k$ on the first row and ones just below the diagonal, and $a_n$ costs $O(k^3 \log n)$ operations
(exercise 11). The same trick counts paths: the $(i, j)$ entry of the $n$-th power of a graph's adjacency matrix is the
number of walks of length $n$ from $i$ to $j$. Taking powers in the **(min, +)** algebra instead, where "multiply" is
$+$ and "add" is $\min$, gives shortest paths that use exactly $n$ edges ([Chapter 16](16-Shortest-Paths.md)).

**Fast doubling.** For Fibonacci specifically, Lemma 19.15 with $Q^{2k} = (Q^k)^2$ gives $F_{2k} = F_k (2F_{k+1} - F_k)$ and
$F_{2k+1} = F_k^2 + F_{k+1}^2$, which saves the redundant matrix entries. The program checks that both methods agree. See
also [Fibonacci](../../dp/fibonacci.md) among the reference pages.

### The number-theoretic transform

**The problem.** Multiply two polynomials of degree below $n$, or two numbers of $n$ digits (a number is a polynomial in
10 evaluated at 10, plus carries). The schoolbook method costs $n^2$ multiplications; Karatsuba
([Chapter 11](11-Divide-and-Conquer.md)) gets $O(n^{1.585})$. The fast Fourier transform of 11.7 gets $O(n \log n)$ by
evaluating at the complex roots of unity, but complex numbers in floating point bring rounding errors, which for exact
integer results must be controlled carefully. The **number-theoretic transform** (NTT) does the same thing in
$\mathbb{Z}_p$, where every operation is exact.

**Evaluate, multiply, interpolate.** A polynomial of degree below $n$ is fixed by its values at $n$ distinct points. The
product $c = ab$ has values $c(x) = a(x) b(x)$. So: evaluate $a$ and $b$ at $n$ well-chosen points (with $n$ at least the
number of coefficients of $c$), multiply the values ($n$ multiplications), and convert the values of $c$ back to
coefficients. The FFT idea is that if the points are the powers of a **primitive $n$-th root of unity** $\omega$, both
conversions take $O(n \log n)$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 680 230" role="img" aria-label="Multiplying polynomials with the number-theoretic transform: transform both coefficient lists to values at the n-th roots of unity in O(n log n), multiply the values pointwise in O(n), and transform back in O(n log n).">
<rect x="10" y="20" width="130" height="56" rx="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1.3"/>
<text x="75.0" y="44.5" font-size="13" text-anchor="middle" fill="currentColor">a(x): n</text>
<text x="75.0" y="61.5" font-size="13" text-anchor="middle" fill="currentColor">coefficients</text>
<rect x="10" y="140" width="130" height="56" rx="6" fill="#9cc9ea" fill-opacity="0.35" stroke="currentColor" stroke-width="1.3"/>
<text x="75.0" y="164.5" font-size="13" text-anchor="middle" fill="currentColor">b(x): n</text>
<text x="75.0" y="181.5" font-size="13" text-anchor="middle" fill="currentColor">coefficients</text>
<rect x="220" y="20" width="130" height="56" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor" stroke-width="1.3"/>
<text x="285.0" y="44.5" font-size="13" text-anchor="middle" fill="currentColor">a(ω⁰), …,</text>
<text x="285.0" y="61.5" font-size="13" text-anchor="middle" fill="currentColor">a(ωⁿ⁻¹)</text>
<rect x="220" y="140" width="130" height="56" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor" stroke-width="1.3"/>
<text x="285.0" y="164.5" font-size="13" text-anchor="middle" fill="currentColor">b(ω⁰), …,</text>
<text x="285.0" y="181.5" font-size="13" text-anchor="middle" fill="currentColor">b(ωⁿ⁻¹)</text>
<rect x="400" y="80" width="120" height="56" rx="6" fill="#eea66f" fill-opacity="0.35" stroke="currentColor" stroke-width="1.3"/>
<text x="460.0" y="104.5" font-size="13" text-anchor="middle" fill="currentColor">c(ωᵏ) =</text>
<text x="460.0" y="121.5" font-size="13" text-anchor="middle" fill="currentColor">a(ωᵏ)·b(ωᵏ)</text>
<rect x="570" y="80" width="100" height="56" rx="6" fill="#7ccf9a" fill-opacity="0.35" stroke="currentColor" stroke-width="1.3"/>
<text x="620.0" y="104.5" font-size="13" text-anchor="middle" fill="currentColor">c(x) = a·b:</text>
<text x="620.0" y="121.5" font-size="13" text-anchor="middle" fill="currentColor">coefficients</text>
<line x1="140" y1="48" x2="212" y2="48" stroke="currentColor" stroke-width="1.5"/>
<polygon points="220,48 212,44 212,52" fill="currentColor"/>
<text x="180.0" y="40" font-size="12" text-anchor="middle" fill="currentColor">NTT</text>
<line x1="140" y1="168" x2="212" y2="168" stroke="currentColor" stroke-width="1.5"/>
<polygon points="220,168 212,164 212,172" fill="currentColor"/>
<text x="180.0" y="160" font-size="12" text-anchor="middle" fill="currentColor">NTT</text>
<line x1="350" y1="48" x2="392" y2="94" stroke="currentColor" stroke-width="1.5"/>
<polygon points="400,102 389.6,97.6 395.5,92.2" fill="currentColor"/>
<line x1="350" y1="168" x2="392" y2="122" stroke="currentColor" stroke-width="1.5"/>
<polygon points="400,114 395.5,123.8 389.6,118.4" fill="currentColor"/>
<line x1="520" y1="108" x2="562" y2="108" stroke="currentColor" stroke-width="1.5"/>
<polygon points="570,108 562,104 562,112" fill="currentColor"/>
<text x="545" y="70" font-size="12" text-anchor="middle" fill="currentColor">inverse</text>
<text x="545" y="84" font-size="12" text-anchor="middle" fill="currentColor">NTT</text>
<text x="180" y="110" font-size="12" text-anchor="middle" fill="currentColor">O(n log n) each</text>
<text x="460" y="160" font-size="12" text-anchor="middle" fill="currentColor">O(n) multiplications</text>
<text x="340" y="220" font-size="12" text-anchor="middle" fill="currentColor" font-style="italic">all arithmetic mod p = 998244353, where ω is an element of order n</text>
</svg>
<figcaption>Figure 19.4. Multiplying polynomials with the NTT. Both coefficient lists are transformed to their values at the n powers of ω, the values are multiplied pointwise, and the inverse transform returns the coefficients of the product.</figcaption>
</figure>

**Roots of unity mod $p$.** We need $\omega \in \mathbb{Z}_p$ with $\omega^n = 1$ and $\omega^k \neq 1$ for $0 < k < n$. The nonzero
elements of $\mathbb{Z}_p$ form a cyclic group of order $p - 1$: there is a **primitive root** $g$ whose powers give all of them
(a theorem of Gauss). So an element of order $n$ exists exactly when $n$ divides $p - 1$, namely $\omega = g^{(p-1)/n}$.
For transforms of length $2^k$ we want $p - 1$ divisible by a large power of 2. The favourite is

$$
p = 998\,244\,353 = 119 \cdot 2^{23} + 1 ,
$$

a prime with primitive root 3, which allows lengths up to $2^{23} = 8\,388\,608$. The program checks that
$3^{(p-1)/8}$ has order exactly 8.

**Lemma 19.16 (the two facts the FFT needs).** Let $\omega$ have order $n$ in $\mathbb{Z}_p$, with $n$ even. Then
(a) $\omega^{n/2} = -1$, and (b) $\omega^2$ has order $n/2$.

*Proof.* (a) $(\omega^{n/2})^2 = 1$, so by Lemma 19.10 $\omega^{n/2} = \pm 1$, and it is not 1 because $n/2 < n$ is below the
order. (b) $(\omega^2)^{n/2} = 1$, and $(\omega^2)^k = \omega^{2k} \neq 1$ for $0 < k < n/2$. $\square$

**The recursion (Cooley-Tukey).** Split $a(x)$ into even and odd coefficients: $a(x) = e(x^2) + x \, o(x^2)$, where $e$ and
$o$ have $n/2$ coefficients each. For $0 \le k < n/2$, using $\omega^{k + n/2} = -\omega^k$:

$$
a(\omega^k) = e(\omega^{2k}) + \omega^k o(\omega^{2k}), \qquad a(\omega^{k + n/2}) = e(\omega^{2k}) - \omega^k o(\omega^{2k}) .
$$

The values $e(\omega^{2k})$ for $k < n/2$ are a transform of length $n/2$ with root $\omega^2$ (Lemma 19.16b), and the same for
$o$. So one transform of length $n$ is two of length $n/2$ plus $n/2$ "butterflies" (one multiplication, one addition, one
subtraction each). The cost satisfies $T(n) = 2T(n/2) + O(n)$, which is $O(n \log n)$ by the master theorem of
[Chapter 3](03-Recursion-and-Induction.md). The program's `ntt` does the same computation without recursion: it first
puts the coefficients in **bit-reversed** order (the order in which the recursion would reach them) and then runs the
butterflies for lengths 2, 4, 8, ....

**Theorem 19.17 (inversion).** If $\hat a_j = \sum_{i} a_i \omega^{ij}$ is the transform, then
$a_i = n^{-1} \sum_j \hat a_j \omega^{-ij}$. So the inverse transform is the same algorithm with $\omega^{-1}$ in place of $\omega$,
followed by multiplying by $n^{-1} \bmod p$.

*Proof.* Substitute: $\sum_j \hat a_j \omega^{-ij} = \sum_l a_l \sum_j \omega^{(l - i) j}$. If $l = i$ the inner sum is $n$. If
$l \neq i$, let $u = \omega^{l-i} \neq 1$ (as $0 < |l - i| < n$); the inner sum is a geometric series
$\sum_{j=0}^{n-1} u^j = (u^n - 1)/(u - 1) = 0$, since $u^n = 1$. So the whole is $n a_i$. $\square$

**Worked example.** $(1 + 2x + 3x^2)(4 + 5x)$: the product has 4 coefficients, so $n = 4$, and the program returns
$[4, 13, 22, 15]$, that is $4 + 13x + 22x^2 + 15x^3$. Check: $1 \cdot 4 = 4$; $1 \cdot 5 + 2 \cdot 4 = 13$; $2 \cdot 5 + 3 \cdot 4 = 22$;
$3 \cdot 5 = 15$.

**Limits.** The NTT computes the product **mod $p$**. If the true coefficients can exceed $p$ (for digits of big numbers,
each product coefficient is at most $81n$; for arbitrary coefficients, up to $n p^2$), either keep them small, as the
program does by using decimal digits, or run the transform modulo two or three suitable primes and combine with the CRT
of 19.6. The program multiplies two random 3000-bit numbers through their digits and gets the same answer as Python's
`*`.

**History.** James Cooley and John Tukey published the FFT in 1965 (Gauss had used the idea around 1805, unpublished in
his lifetime). John Pollard described the transform over finite fields in 1971 ("The Fast Fourier Transform in a Finite
Field"), and the same year Arnold Schönhage and Volker Strassen used it to multiply $n$-bit integers in
$O(n \log n \log \log n)$ bit operations. Martin Fürer improved this in 2007, and David Harvey and Joris van der Hoeven
reached $O(n \log n)$ ("Integer multiplication in time $O(n \log n)$", *Annals of Mathematics*, 2021), which is believed
to be optimal, though no matching lower bound is proved.

```python
--8<-- "books/algorithms/ch19_algebra.py"
```

```
1. Fibonacci by matrix powers
   [[1,1],[1,0]]^10 = [[89, 55], [55, 34]]
   F(300) mod 10^9+7 matches the exact value: True
   F(10^18) mod 10^9+7 = 209783453 (fast doubling: 209783453)
2. Number-theoretic transform
   MOD - 1 = 998244352 = 119 * 2^23: True
   order of w8 = 3^((MOD-1)/8): 8
   (1 + 2x + 3x^2)(4 + 5x) = [4, 13, 22, 15]
   random 300 x 200 product equals the naive one: True
   3000-bit integers multiplied via NTT equal x*y: True
```

### In practice

Python's integers have arbitrary size; `math.gcd`, `math.lcm`, `math.isqrt` and three-argument `pow` (including
`pow(a, -1, m)` for inverses) are built in, and CPython multiplies large integers with Karatsuba's method. The GMP
library, used by many languages for big numbers, switches between schoolbook, Toom-Cook and FFT-based multiplication by
size. SymPy provides `isprime`, `factorint` and `crt`; PARI/GP is the standard tool for serious computational number
theory. Cryptographic libraries implement modular arithmetic with Montgomery multiplication (Montgomery 1985), which
avoids division, and in constant time.

## Check yourself

??? question "1. Run the extended Euclid algorithm on $(99, 78)$ by hand. Find $\gcd(99, 78)$ and $x, y$ with $99x + 78y = \gcd$."

    Remainders: $99 = 1 \cdot 78 + 21$, $78 = 3 \cdot 21 + 15$, $21 = 1 \cdot 15 + 6$, $15 = 2 \cdot 6 + 3$, $6 = 2 \cdot 3 + 0$, so the gcd
    is 3. Pairs $(x, y)$: $r = 99$: $(1, 0)$; $78$: $(0, 1)$; $21$: $(1, -1)$; $15$: $(-3, 4)$; $6$: $(4, -5)$; $3$: $(-11, 14)$.
    Check: $99 \cdot (-11) + 78 \cdot 14 = -1089 + 1092 = 3$.

??? question "2. How many division steps does Euclid take on $(987, 610)$, and what does Lamé's bound predict?"

    $987 = F_{16}$ and $610 = F_{15}$, so by the tight case of Theorem 19.2 it takes $16 - 2 = 14$ steps (all quotients 1
    until the last, $2 = 2 \cdot 1 + 0$). Lamé: at most 5 times the 3 digits of 610, so 15. The program confirms that 14 is
    the most for any pair below 1000.

??? question "3. Compute $3^{200} \bmod 13$ in two ways: by Fermat's little theorem and by noticing a smaller order."

    Fermat: $3^{12} \equiv 1$, and $200 = 16 \cdot 12 + 8$, so $3^{200} \equiv 3^8 = 6561 = 504 \cdot 13 + 9 \equiv 9$. Smaller order:
    $3^3 = 27 \equiv 1 \pmod{13}$, and $200 = 66 \cdot 3 + 2$, so $3^{200} \equiv 3^2 = 9$. Both give 9.

??? question "4. Why does the inverse of 4 mod 12 not exist, and which elements of $\mathbb{Z}_{12}$ are invertible?"

    $\gcd(4, 12) = 4 \neq 1$: every $4x$ is a multiple of 4 mod 12, so it is 0, 4 or 8, never 1. The invertible elements are
    those coprime to 12: 1, 5, 7, 11, each its own inverse ($5 \cdot 5 = 25 \equiv 1$, $7 \cdot 7 = 49 \equiv 1$,
    $11 \cdot 11 = 121 \equiv 1$). That is $\varphi(12) = 4$ elements.

??? question "5. Show that 1105 is a Carmichael number using Korselt's criterion."

    $1105 = 5 \cdot 13 \cdot 17$, squarefree. $1104 = 4 \cdot 276 = 12 \cdot 92 = 16 \cdot 69$, so $4$, $12$ and $16$ (that is, $p - 1$ for
    each prime factor) all divide $1104$. By Theorem 19.9, $a^{1104} \equiv 1 \pmod{1105}$ for every $a$ coprime to 1105.

??? question "6. The Miller-Rabin sequence for 561 with base 2 contains 67. Use it to factor 561."

    $67^2 \equiv 1 \pmod{561}$ and $67 \not\equiv \pm 1$, so 561 divides $(67 - 1)(67 + 1)$ without dividing either factor.
    Hence $\gcd(66, 561) = 33$ and $\gcd(68, 561) = 17$ are nontrivial factors: $561 = 33 \cdot 17 = 3 \cdot 11 \cdot 17$.

??? question "7. Write a segmented sieve that lists the primes in $[L, R]$ using $O(\sqrt R + (R - L))$ memory."

    Sieve the small primes up to $\sqrt R$, then cross off their multiples inside the window:

    ```python
    from math import isqrt

    def primes_in_range(L, R):
        r = isqrt(R)
        mark, small = bytearray([1]) * (r + 1), []
        for p in range(2, r + 1):                                 # ordinary sieve up to sqrt(R)
            if mark[p]:
                small.append(p)
                mark[p * p::p] = bytes(len(range(p * p, r + 1, p)))
        is_p = bytearray([1]) * (R - L + 1)
        for p in small:
            start = max(p * p, (L + p - 1) // p * p)               # first multiple >= L, not below p*p
            for m in range(start, R + 1, p):
                is_p[m - L] = 0
        return [L + i for i, f in enumerate(is_p) if f and L + i >= 2]

    print(primes_in_range(10**12, 10**12 + 100))
    # [1000000000039, 1000000000061, 1000000000063, 1000000000091]
    ```

    Starting at $\max(p^2, \lceil L/p \rceil p)$ is the same "start at $p^2$" rule as before, and stops $p$ itself from
    being crossed off when it lies in the window.

??? question "8. Run Pollard's rho with $f(x) = x^2 + 1$ and $x_0 = 2$ on $n = 10403$. At which step does it find a factor?"

    The tortoise and hare values are $(5, 26)$, $(26, 598)$, $(677, 3418)$, $(598, 3531)$, $(3903, 3724)$, $(3418, 9812)$,
    $(156, 9970)$, $(3531, 3682)$, $(5168, 7087)$. At step 9, $\gcd(7087 - 5168, 10403) = \gcd(1919, 10403) = 101$ (as
    $1919 = 19 \cdot 101$), so $10403 = 101 \cdot 103$. Two nearly equal factors near $\sqrt n$ are rho's hardest case for a
    given $n$, but at this size still only 9 steps.

??? question "9. Solve $x \equiv 1 \pmod 4$, $x \equiv 2 \pmod 9$, $x \equiv 3 \pmod{25}$ with the incremental CRT."

    Start $x = 0$, $M = 1$. Mod 4: $t = 1$, $x = 1$, $M = 4$. Mod 9: $t \equiv (2 - 1) \cdot 4^{-1} \equiv 1 \cdot 7 = 7$ (since
    $4 \cdot 7 = 28 \equiv 1$), $x = 1 + 4 \cdot 7 = 29$, $M = 36$. Mod 25: $36 \equiv 11$, $11^{-1} \equiv 16$ ($176 = 7 \cdot 25 + 1$),
    $t \equiv (3 - 29) \cdot 16 = -416 \equiv 9 \pmod{25}$, $x = 29 + 36 \cdot 9 = 353$, $M = 900$. Check: $353 = 88 \cdot 4 + 1 =
    39 \cdot 9 + 2 = 14 \cdot 25 + 3$.

??? question "10. Write code that computes the inverses of $1, 2, \ldots, n$ mod a prime $p > n$ in $O(n)$ total time, and prove it correct."

    Use $\mathrm{inv}[i] \equiv -\lfloor p/i \rfloor \cdot \mathrm{inv}[p \bmod i]$:

    ```python
    def all_inverses(n, p):
        inv = [0, 1]
        for i in range(2, n + 1):
            inv.append(-(p // i) * inv[p % i] % p)
        return inv

    inv = all_inverses(12, 13)
    print(inv, all(i * inv[i] % 13 == 1 for i in range(1, 13)))
    # [0, 1, 7, 9, 10, 8, 11, 2, 5, 3, 4, 6, 12] True
    ```

    Proof: write $p = qi + r$ with $q = \lfloor p/i \rfloor$, $r = p \bmod i$, $0 < r < i$ (as $p$ is prime and $i < p$). Mod $p$,
    $qi + r \equiv 0$, so $qi \equiv -r$. Multiply by $i^{-1} r^{-1}$: $q r^{-1} \equiv -i^{-1}$, so $i^{-1} \equiv -q \cdot r^{-1}$.
    Since $r < i$, $\mathrm{inv}[r]$ is already known.

??? question "11. The tribonacci numbers are $T_0 = 0$, $T_1 = 0$, $T_2 = 1$, $T_{k} = T_{k-1} + T_{k-2} + T_{k-3}$. Give the matrix that computes them and find $T_{12}$ from $M^{10}$."

    With the vector $(T_{k+2}, T_{k+1}, T_k)$, one step is multiplication by
    $M = \begin{pmatrix} 1 & 1 & 1 \\ 1 & 0 & 0 \\ 0 & 1 & 0 \end{pmatrix}$, so $(T_{n+2}, T_{n+1}, T_n) = M^n (1, 0, 0)$, the first column of
    $M^n$. The program's `mat_pow` gives $M^{10}$ with first column $(274, 149, 81)$, so $T_{12} = 274$, $T_{11} = 149$,
    $T_{10} = 81$; check by the list 0, 0, 1, 1, 2, 4, 7, 13, 24, 44, 81, 149, 274. Cost: $O(3^3 \log n)$ operations.

??? question "12. For which powers of two $n$ is there an NTT of length $n$ modulo $p = 97$? And why is $p = 2^{31} - 1$ a bad choice for an NTT?"

    An element of order $n$ exists in $\mathbb{Z}_p$ exactly when $n$ divides $p - 1$. For $p = 97$, $p - 1 = 96 = 2^5 \cdot 3$, so
    the lengths 2, 4, 8, 16 and 32 are possible and 64 is not. For
    $p = 2^{31} - 1$, $p - 1 = 2 \cdot 3^2 \cdot 7 \cdot 11 \cdot 31 \cdot 151 \cdot 331$ has only one factor 2, so no power-of-two length
    above 2 exists: useless for radix-2 NTTs.

## What you learned

- Number algorithms are measured in the number of digits; $O(\sqrt N)$ is exponential, $O((\log N)^k)$ is fast.
- Euclid's algorithm takes $O(\log b)$ steps, with consecutive Fibonacci numbers the worst case (Lamé); the extended
  version gives Bézout coefficients and modular inverses.
- Square-and-multiply computes $a^e \bmod m$ in about $2 \log_2 e$ multiplications; mod a prime, $a^{p-2}$ is $a^{-1}$.
- The sieve of Eratosthenes runs in $O(n \log \log n)$; the linear sieve crosses each composite once and leaves a
  least-prime-factor table for instant factoring.
- Fermat's test is fooled by Carmichael numbers; Miller-Rabin is not, errs with probability at most $1/4$ per round
  (proved $\le 1/2$ here), and with twelve fixed bases is exact below $2^{64}$. AKS is polynomial and deterministic.
- Pollard's rho finds a factor $p$ in about $\sqrt p$ steps by the birthday paradox and Floyd's cycle finding.
- The CRT solves systems of congruences incrementally and splits arithmetic mod $M$ into independent small parts.
- Linear recurrences reduce to matrix powers in $O(k^3 \log n)$; the NTT multiplies polynomials exactly in
  $O(n \log n)$ using roots of unity mod a prime such as $119 \cdot 2^{23} + 1$.

**Next:** [Chapter 20](20-Computational-Geometry.md), algorithms on points, lines and polygons: orientation tests,
convex hulls, sweeps and nearest neighbours.

## Further reading

- D. E. Knuth, *The Art of Computer Programming*, Vol. 2: *Seminumerical Algorithms*, 3rd ed. 1997: Euclid, Lamé, powering, factoring, the FFT, in full depth.
- CLRS (Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms*, 4th ed. 2022), chapter 31 (number-theoretic algorithms) and chapter 30 (polynomials and the FFT).
- R. Crandall and C. Pomerance, *Prime Numbers: A Computational Perspective*, 2nd ed. 2005.
- V. Shoup, *A Computational Introduction to Number Theory and Algebra*, 2nd ed. 2009 (free online from the author).
- G. L. Miller, "Riemann's Hypothesis and Tests for Primality", *Journal of Computer and System Sciences* 13, 1976.
- M. O. Rabin, "Probabilistic Algorithm for Testing Primality", *Journal of Number Theory* 12, 1980.
- L. Monier, "Evaluation and Comparison of Two Efficient Probabilistic Primality Testing Algorithms", *Theoretical Computer Science* 12, 1980.
- W. R. Alford, A. Granville and C. Pomerance, "There Are Infinitely Many Carmichael Numbers", *Annals of Mathematics* 139, 1994.
- M. Agrawal, N. Kayal and N. Saxena, "PRIMES is in P", *Annals of Mathematics* 160, 2004.
- J. M. Pollard, "A Monte Carlo Method for Factorization", *BIT* 15, 1975; R. P. Brent, "An Improved Monte Carlo Factorization Algorithm", *BIT* 20, 1980.
- D. Gries and J. Misra, "A Linear Sieve Algorithm for Finding Prime Numbers", *Communications of the ACM* 21(12), 1978.
- J. M. Pollard, "The Fast Fourier Transform in a Finite Field", *Mathematics of Computation* 25, 1971.
- J. W. Cooley and J. W. Tukey, "An Algorithm for the Machine Calculation of Complex Fourier Series", *Mathematics of Computation* 19, 1965.
- D. Harvey and J. van der Hoeven, "Integer Multiplication in Time $O(n \log n)$", *Annals of Mathematics* 193, 2021.
- G. H. Hardy and E. M. Wright, *An Introduction to the Theory of Numbers* (6th ed. 2008), for Mertens' theorems and the prime number theorem.
- On this site: [Euclid's GCD](../../number-theory/gcd.md), [Fast exponentiation](../../number-theory/fast-power.md),
  [Sieve of Eratosthenes](../../number-theory/sieve.md), [Fibonacci](../../dp/fibonacci.md); [Chapter 11](11-Divide-and-Conquer.md)
  for Karatsuba and the complex FFT; [Chapter 21](21-Randomized-and-Amortized-Analysis.md) for Monte Carlo algorithms.
- The uses in cryptography (Diffie-Hellman, RSA, RSA-CRT, constant-time arithmetic): https://cryptography.akadian.ca/book/.
  The number theory itself: https://math.akadian.ca/books/.
