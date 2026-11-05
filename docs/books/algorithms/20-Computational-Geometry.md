# 20. Computational geometry

*A map program must decide which country a click falls in. A game must find which walls a bullet's path crosses. A
robot must know whether a straight drive from here to there clips a rock. Each of these questions is about points,
segments and polygons, and each has an obvious answer that a person sees at a glance, which a computer can get wrong in
three ways: by being slow, by mishandling special cases (three points on a line, a ray through a corner), and by
rounding. In this chapter you will build the one test that almost every geometric algorithm rests on, the orientation
test, see why it must be computed exactly, and then use it to decide whether segments cross, wrap a convex hull around a
cloud of points three different ways, sweep a line across the plane to find every crossing, measure polygons, and
finally divide the plane among sites (Voronoi diagrams and Delaunay triangulations) and search it for nearest
neighbours with k-d trees.*

!!! abstract "In this chapter"
    **You will learn:**

    - points as vectors, the cross product, and the orientation test, computed exactly with integers
    - a complete segment intersection test, including the collinear cases
    - three convex hull algorithms (gift wrapping, Graham scan, monotone chain) and why $\Omega(n \log n)$ is a lower bound
    - the sweep-line method: Shamos-Hoey, Bentley-Ottmann and the area of a union of rectangles
    - polygon area by the shoelace formula, Pick's theorem, and point in polygon by ray casting and winding numbers
    - Voronoi diagrams, Delaunay triangulations and the empty-circle property, and nearest-neighbour search in k-d trees

    **You need:** [Chapter 5](05-Sorting-by-Comparison.md) (sorting and the $\Omega(n \log n)$ lower bound),
    [Chapter 8](08-Trees-and-Balanced-Search-Trees.md) (balanced search trees) and
    [Chapter 9](09-Heaps-and-Priority-Queues.md) (priority queues). School geometry: coordinates, slopes, the area of a
    triangle. [Chapter 11](11-Divide-and-Conquer.md), 11.6, has the closest pair of points.

    **Levels:** 20.1 and 20.2 are beginner to intermediate; 20.3 to 20.5 are intermediate; 20.6 is advanced.

## 20.1 Points, vectors and the orientation test

**Points and vectors.** A point in the plane is a pair of numbers $p = (p_x, p_y)$. The difference of two points,
$b - a = (b_x - a_x, b_y - a_y)$, is a **vector**: an arrow saying how to get from $a$ to $b$. Vectors can be added and
scaled; points can only be subtracted (to give a vector) or moved by a vector. We will store everything as tuples of
integers, for a reason that comes at the end of this section.

**The question.** Walk from point $o$ to point $a$, then turn towards point $b$. Do you turn left, turn right, or go
straight on? Almost every algorithm in this chapter reduces to asking this question many times.

**The cross product.** For vectors $u = (u_x, u_y)$ and $v = (v_x, v_y)$ define

$$
u \times v = u_x v_y - u_y v_x .
$$

(In three dimensions the cross product is a vector; this number is its $z$-component when $u$ and $v$ lie in the
$xy$-plane.) Two facts make it useful.

**Lemma 20.1.** $u \times v = |u| \, |v| \sin\theta$, where $\theta$ is the angle turned counter-clockwise from the direction
of $u$ to the direction of $v$. So $u \times v > 0$ when $v$ points to the left of $u$, $u \times v < 0$ when it points to
the right, and $u \times v = 0$ when they are parallel. Moreover $|u \times v|$ is the area of the parallelogram spanned by
$u$ and $v$, twice the area of the triangle.

*Proof.* Write $u = |u|(\cos\alpha, \sin\alpha)$ and $v = |v|(\cos\beta, \sin\beta)$. Then $u_x v_y - u_y v_x =
|u||v|(\cos\alpha \sin\beta - \sin\alpha \cos\beta) = |u||v|\sin(\beta - \alpha)$, and $\beta - \alpha = \theta$. The area of a
parallelogram is base times height, $|u| \cdot |v| |\sin \theta|$. $\square$

**The orientation test.** For three points, set

$$
\operatorname{cross}(o, a, b) = (a - o) \times (b - o) = (a_x - o_x)(b_y - o_y) - (a_y - o_y)(b_x - o_x) .
$$

Its sign says which way the path $o \to a \to b$ turns: positive for a **left turn** (counter-clockwise), negative for
a **right turn** (clockwise), zero when the three points are **collinear**.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 220" role="img" aria-label="Three panels. Left: going from o to a then turning left to b, the cross product is positive. Middle: turning right, negative. Right: o, a, b on one line, zero.">
<line x1="40.0" y1="170.0" x2="157.2" y2="152.0" stroke="currentColor" stroke-width="1.6"/><polygon points="165.1,150.8 156.8,156.1 155.5,148.1" fill="currentColor"/>
<line x1="170.0" y1="150.0" x2="125.8" y2="61.6" stroke="#eea66f" stroke-width="1.6"/><polygon points="122.2,54.5 129.9,60.7 122.6,64.3" fill="#eea66f"/>
<circle cx="40.0" cy="170.0" r="4" fill="currentColor"/>
<circle cx="170.0" cy="150.0" r="4" fill="currentColor"/>
<circle cx="120.0" cy="50.0" r="4" fill="currentColor"/>
<text x="28.0" y="175.0" font-size="13" text-anchor="middle" fill="currentColor">o</text>
<text x="182.0" y="155.0" font-size="13" text-anchor="middle" fill="currentColor">a</text>
<text x="132.0" y="46.0" font-size="13" text-anchor="middle" fill="currentColor">b</text>
<text x="107.0" y="25.0" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">left turn</text>
<text x="107.0" y="212.0" font-size="13" text-anchor="middle" fill="currentColor">cross &gt; 0</text>
<line x1="253.0" y1="70.0" x2="370.2" y2="88.0" stroke="currentColor" stroke-width="1.6"/><polygon points="378.1,89.2 368.5,91.9 369.8,83.9" fill="currentColor"/>
<line x1="383.0" y1="90.0" x2="338.8" y2="178.4" stroke="#eea66f" stroke-width="1.6"/><polygon points="335.2,185.5 335.6,175.7 342.9,179.3" fill="#eea66f"/>
<circle cx="253.0" cy="70.0" r="4" fill="currentColor"/>
<circle cx="383.0" cy="90.0" r="4" fill="currentColor"/>
<circle cx="333.0" cy="190.0" r="4" fill="currentColor"/>
<text x="241.0" y="75.0" font-size="13" text-anchor="middle" fill="currentColor">o</text>
<text x="395.0" y="95.0" font-size="13" text-anchor="middle" fill="currentColor">a</text>
<text x="345.0" y="186.0" font-size="13" text-anchor="middle" fill="currentColor">b</text>
<text x="320.0" y="25.0" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">right turn</text>
<text x="320.0" y="212.0" font-size="13" text-anchor="middle" fill="currentColor">cross &lt; 0</text>
<line x1="456.0" y1="180.0" x2="525.6" y2="127.8" stroke="currentColor" stroke-width="1.6"/><polygon points="532.0,123.0 527.2,131.6 522.4,125.2" fill="currentColor"/>
<line x1="536.0" y1="120.0" x2="605.6" y2="67.8" stroke="#eea66f" stroke-width="1.6"/><polygon points="612.0,63.0 607.2,71.6 602.4,65.2" fill="#eea66f"/>
<circle cx="456.0" cy="180.0" r="4" fill="currentColor"/>
<circle cx="536.0" cy="120.0" r="4" fill="currentColor"/>
<circle cx="616.0" cy="60.0" r="4" fill="currentColor"/>
<text x="444.0" y="185.0" font-size="13" text-anchor="middle" fill="currentColor">o</text>
<text x="548.0" y="125.0" font-size="13" text-anchor="middle" fill="currentColor">a</text>
<text x="628.0" y="56.0" font-size="13" text-anchor="middle" fill="currentColor">b</text>
<text x="533.0" y="25.0" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">collinear</text>
<text x="533.0" y="212.0" font-size="13" text-anchor="middle" fill="currentColor">cross = 0</text>
</svg>
<figcaption>Figure 20.1. The orientation test. The sign of cross(o, a, b) tells whether the path from o through a turns left towards b, turns right, or goes straight on.</figcaption>
</figure>

For example $\operatorname{cross}((0,0), (4,0), (2,3)) = 4 \cdot 3 - 0 \cdot 2 = 12 > 0$: walking east and then looking at a point
above the line, you turn left. Changing $b$ to $(2, -3)$ gives $-12$, a right turn, and $(0,0), (2,2), (5,5)$ gives
$2 \cdot 5 - 2 \cdot 5 = 0$. The test uses two multiplications and five subtractions, no division, no square root, no angle.
That is the point: angles need trigonometry, which needs floating point.

**Why exact arithmetic.** If the coordinates are integers of absolute value at most $2^b$, every difference is at most
$2^{b+1}$, so each product is at most $2^{2b+2}$ and the cross product is at most $2^{2b+3}$ in absolute value. With
64-bit machine integers that is safe for $b \le 30$; Python's integers never overflow, so the test is always exact.

With floating-point coordinates, the products are rounded, and when the three points are nearly collinear the rounding
error can be larger than the true value: the computed sign is then garbage. The program at the end of 20.2 repeats the
classic experiment of Kettner, Mehlhorn, Pion, Schirra and Yap ("Classroom Examples of Robustness Problems in Geometric
Computations", 2008): take $q = (12, 12)$, $r = (24, 24)$, and a $64 \times 64$ grid of points $p$ within 63 units in
the last place of $(0.5, 0.5)$, and compare the floating-point sign with the exact sign of the same numbers (computed with
Python's `Fraction`). **2164 of the 4096 points get the wrong sign,** 2052 of them wrongly reported as exactly collinear.
An algorithm that asks "is $p$ left of $qr$?" twice in different forms can then receive contradictory answers and loop
forever or crash.

The remedies, in order of preference: use integer (or rational) coordinates and exact arithmetic, as this chapter does;
or use **robust adaptive predicates** (Jonathan Shewchuk, 1997), which compute in floating point and fall back to exact
arithmetic only when the result is too close to zero to trust; or snap the input to a grid. Adding an "epsilon"
tolerance, the usual first idea, does not fix the problem: it replaces wrong answers by inconsistent ones.

## 20.2 Segment intersection

**The question.** Do the segments $p_1 p_2$ and $p_3 p_4$ share a point? A rover's path planner asks exactly this when it
checks whether a straight drive between two waypoints would cross the outline of a hazard, and a drawing program asks it
for every pair of lines it must render.

The idea: the segments cross properly if each one **straddles** the other's line, that is, $p_3$ and $p_4$ are on
opposite sides of the line through $p_1 p_2$, *and* $p_1$ and $p_2$ are on opposite sides of the line through $p_3 p_4$.
One straddle is not enough, as the right half of Figure 20.2 shows.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 620 250" role="img" aria-label="Two panels. Left: segments p1p2 and p3p4 cross; p3 and p4 lie on opposite sides of p1p2 and p1 and p2 on opposite sides of p3p4. Right: p3 and p4 are on opposite sides of the line through p1p2, but p1 and p2 are on the same side of p3p4, so the segments do not meet.">
<line x1="40" y1="160" x2="260" y2="60" stroke="#9cc9ea" stroke-width="3"/>
<line x1="70" y1="60" x2="230" y2="170" stroke="#eea66f" stroke-width="3"/>
<circle cx="40.0" cy="160.0" r="4" fill="currentColor"/>
<text x="26.0" y="164.0" font-size="13" text-anchor="middle" fill="currentColor">p1</text>
<circle cx="260.0" cy="60.0" r="4" fill="currentColor"/>
<text x="274.0" y="64.0" font-size="13" text-anchor="middle" fill="currentColor">p2</text>
<circle cx="70.0" cy="60.0" r="4" fill="currentColor"/>
<text x="56.0" y="64.0" font-size="13" text-anchor="middle" fill="currentColor">p3</text>
<circle cx="230.0" cy="170.0" r="4" fill="currentColor"/>
<text x="244.0" y="174.0" font-size="13" text-anchor="middle" fill="currentColor">p4</text>
<text x="150.0" y="22.0" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">they cross</text>
<text x="150.0" y="205.0" font-size="12" text-anchor="middle" fill="currentColor">p3, p4 on opposite sides of p1p2</text>
<text x="150.0" y="223.0" font-size="12" text-anchor="middle" fill="currentColor">p1, p2 on opposite sides of p3p4</text>
<line x1="350" y1="160" x2="570" y2="60" stroke="#9cc9ea" stroke-width="3"/>
<line x1="470" y1="40" x2="590" y2="150" stroke="#eea66f" stroke-width="3"/>
<circle cx="350.0" cy="160.0" r="4" fill="currentColor"/>
<text x="336.0" y="164.0" font-size="13" text-anchor="middle" fill="currentColor">p1</text>
<circle cx="570.0" cy="60.0" r="4" fill="currentColor"/>
<text x="584.0" y="64.0" font-size="13" text-anchor="middle" fill="currentColor">p2</text>
<circle cx="470.0" cy="40.0" r="4" fill="currentColor"/>
<text x="456.0" y="44.0" font-size="13" text-anchor="middle" fill="currentColor">p3</text>
<circle cx="590.0" cy="150.0" r="4" fill="currentColor"/>
<text x="604.0" y="154.0" font-size="13" text-anchor="middle" fill="currentColor">p4</text>
<text x="460.0" y="22.0" font-size="14" text-anchor="middle" fill="currentColor" font-weight="bold">they do not meet</text>
<text x="460.0" y="205.0" font-size="12" text-anchor="middle" fill="currentColor">p3, p4 on opposite sides of p1p2</text>
<text x="460.0" y="223.0" font-size="12" text-anchor="middle" fill="currentColor">p1, p2 on the same side of p3p4</text>
</svg>
<figcaption>Figure 20.2. Two straddle tests. On the left each segment's endpoints lie on opposite sides of the other's line, so they cross. On the right only one straddle holds: the orange segment's line cuts the blue segment, but the orange segment itself stops short.</figcaption>
</figure>

Write $d_1 = \operatorname{orient}(p_3, p_4, p_1)$, $d_2 = \operatorname{orient}(p_3, p_4, p_2)$, $d_3 = \operatorname{orient}(p_1, p_2, p_3)$ and
$d_4 = \operatorname{orient}(p_1, p_2, p_4)$, each $+1$, $-1$ or $0$.

**Theorem 20.2.** The closed segments $p_1 p_2$ and $p_3 p_4$ intersect if and only if either
(a) $d_1 d_2 < 0$ and $d_3 d_4 < 0$, or
(b) some $d_i = 0$ and the corresponding point lies on the other segment (for example $d_1 = 0$ and $p_1$ lies between
$p_3$ and $p_4$).

*Proof.* If (a) holds, $p_1$ and $p_2$ are strictly on opposite sides of the line $L$ through $p_3 p_4$. A segment that
starts on one side of a line and ends on the other crosses it (the signed distance to $L$ changes sign continuously along
the segment, so it is zero somewhere), so $p_1 p_2$ meets $L$ at exactly one point $x$, and $x$ is not $p_1$ or $p_2$. In the
same way $p_3 p_4$ meets the line through $p_1 p_2$ at exactly one point. The two lines are not parallel (otherwise $p_1$
and $p_2$ would be on the same side), so they meet in exactly one point, which must be both of these: it lies on both
segments. If (b) holds, the named endpoint is a common point.

Conversely, suppose the segments share a point $x$. If no $d_i$ is 0, no endpoint is on the other segment's line. Then $x$
is on the line $L$ through $p_3 p_4$ and strictly between $p_1$ and $p_2$, and $p_1$ and $p_2$ are not on $L$, so they must be
on opposite sides of it: $d_1 d_2 < 0$. Symmetrically $d_3 d_4 < 0$. That is (a). If some $d_i = 0$ but the segments are
not collinear, the endpoint on the other line must be the common point $x$ (two non-parallel lines meet once), so (b)
holds. If all four are 0 the segments lie on one line and they overlap only if an endpoint of one lies on the other,
which is (b) again. $\square$

```python
def segments_intersect(p1, p2, p3, p4):
    d1, d2 = orient(p3, p4, p1), orient(p3, p4, p2)
    d3, d4 = orient(p1, p2, p3), orient(p1, p2, p4)
    if d1 * d2 < 0 and d3 * d4 < 0:
        return True
    return (d1 == 0 and on_segment(p3, p4, p1)) or (d2 == 0 and on_segment(p3, p4, p2)) or \
           (d3 == 0 and on_segment(p1, p2, p3)) or (d4 == 0 and on_segment(p1, p2, p4))
```

Here `on_segment(p, q, r)`, for a point $r$ already known to be collinear with $p$ and $q$, checks that $r$ is inside the
bounding box of $p$ and $q$. The test answers yes or no with four orientation tests and no division.

**Worked examples** (all checked by the program):

| segments | $d_1, d_2, d_3, d_4$ | result |
|---|---|---|
| $(0,0)$–$(4,4)$ and $(0,4)$–$(4,0)$ | $-1, +1, +1, -1$ | cross, case (a) |
| $(0,0)$–$(2,2)$ and $(3,3)$–$(5,5)$ | $0, 0, 0, 0$ | collinear, disjoint: no |
| $(0,0)$–$(3,3)$ and $(3,3)$–$(5,0)$ | $-1, 0, 0, -1$ | touch at $(3,3)$, case (b) |
| $(0,0)$–$(4,0)$ and $(2,0)$–$(6,0)$ | $0, 0, 0, 0$ | collinear overlap, case (b) |
| $(0,0)$–$(4,0)$ and $(1,1)$–$(3,2)$ | $-1, -1, +1, +1$ | no |

**Where they cross.** When the answer is yes and the segments are not parallel, the crossing point is $p_1 + t(p_2 - p_1)$
with

$$
t = \frac{(p_3 - p_1) \times (p_4 - p_3)}{(p_2 - p_1) \times (p_4 - p_3)} .
$$

(Derivation: the point $p_1 + t(p_2 - p_1)$ lies on the line through $p_3$ and $p_4$ exactly when its vector from $p_3$ is
parallel to $p_4 - p_3$, that is, $(p_1 + t(p_2 - p_1) - p_3) \times (p_4 - p_3) = 0$; this is linear in $t$.) Here a division
is unavoidable, so the program returns the coordinates as exact fractions: $(0,0)$–$(4,4)$ and $(0,4)$–$(5,0)$ cross at
$(20/9, 20/9)$. Note that deciding *whether* segments cross needs only the signs, which is why algorithms are designed
to ask yes-or-no questions (**predicates**) wherever possible and to construct new points rarely.

The program for 20.1, 20.2 and 20.5:

```python
--8<-- "books/algorithms/ch20_basics.py"
```

```
1. Orientation
   (0,0),(4,0),(2,3): 1  (0,0),(4,0),(2,-3): -1  (0,0),(2,2),(5,5): 0
2. Floating point gets orientation wrong near a line
   2164 of 4096 nearby points get the wrong sign with floats (2052 of them 'collinear' by mistake)
3. Segment intersection
   ((0, 0), (4, 4), (0, 4), (4, 0)) -> True
   ((0, 0), (2, 2), (3, 3), (5, 5)) -> False
   ((0, 0), (3, 3), (3, 3), (5, 0)) -> True
   ((0, 0), (4, 0), (2, 0), (6, 0)) -> True
   ((0, 0), (4, 0), (1, 1), (3, 2)) -> False
   crossing point of (0,0)-(4,4) and (0,4)-(5,0): (Fraction(20, 9), Fraction(20, 9))
4. Shoelace area and point in polygon
   twice the signed area: 36  area: 18.0
   Pick: interior 11, boundary 16, I + B/2 - 1 = 18.0
   (3, 1): inside, winding 1
   (3, 3): outside, winding 0
   (1, 3): inside, winding 1
   (6, 2): boundary
   (3, 2): boundary
   pentagram centre: ray casting outside | winding number 2
```

## 20.3 Convex hulls

**The problem.** Hammer nails into a board at the given points and stretch a rubber band around all of them. When you let
go, the band snaps to the **convex hull**: the smallest convex polygon containing every point. (A set is **convex** if the
segment between any two of its points stays inside it.) The hull is the first thing to compute about a cloud of points:
its corners are the "extreme" points, its diameter is the farthest pair, and many other algorithms start from it.

We describe the hull by listing its **vertices** (the nails the band touches at a corner) in counter-clockwise order.
Points that lie on a hull edge without being a corner are left out.

**A characterization we will use.** For a convex polygon listed counter-clockwise, every turn $v_{i-1} \to v_i \to v_{i+1}$
is a strict left turn, and every input point lies on or to the left of every directed edge $v_i \to v_{i+1}$. Conversely,
a directed segment $p \to q$ between two input points is a hull edge (in counter-clockwise order) exactly when no input
point is strictly to its right, and no point beyond $q$ is collinear with it.

### Gift wrapping (Jarvis march)

Start at a point certainly on the hull, the lowest one (leftmost among the lowest). From the current hull vertex $p$,
the next vertex is the point $q$ such that every other point is to the left of $p \to q$: find it by scanning all points
and keeping the "most clockwise" candidate, replacing the candidate $q$ by $r$ whenever $r$ is to the right of $p \to q$
(or collinear and farther). Repeat until you return to the start. This is how you would wrap a present: always turn as
little as possible.

**Theorem 20.3 (Jarvis 1973).** Gift wrapping finds the hull in $O(nh)$ time, where $h$ is the number of hull vertices.

*Proof.* Correctness: by the characterization, the point chosen from $p$ has no point to its right, so $p \to q$ is a hull
edge, and the walk visits hull vertices in counter-clockwise order until it closes. Time: each of the $h$ steps scans all
$n$ points with one orientation test each. $\square$

$O(nh)$ is **output-sensitive**: excellent when the hull is small, as for random points in a disc (the expected hull size
grows only like $n^{1/3}$, a result going back to Rényi and Sulanke in the 1960s), terrible when all points are on the hull, where it
becomes $O(n^2)$. The program shows both: for 2000 random points in a disc the hull has 43 vertices and gift wrapping
makes $86\,000$ orientation tests, but for 2000 points on a circle it makes $4\,000\,000$.

### Graham scan

**The idea** (Ronald Graham, 1972). Sort the
points by angle around the lowest point $p_0$. Then walk through them in that order, keeping a stack of the hull so far.
Each new point is added on top; before that, while the top two stack points and the new point make a right turn (or go
straight), the top point cannot be on the hull, so pop it.

```python
stack = [p0]
for p in points_sorted_by_angle:
    while len(stack) >= 2 and cross(stack[-2], stack[-1], p) <= 0:
        stack.pop()
    stack.append(p)
```

The angular sort uses the orientation test as its comparison ($a$ comes before $b$ if $b$ is to the left of $p_0 \to a$),
so it needs no angles and no division. Ties (points collinear with $p_0$) go nearest first.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 420 340" role="img" aria-label="Nine points and their convex hull with vertices (0,0), (4,0), (5,3), (3,5), (0,4). Dashed rays from the lowest point (0,0) show the angular order used by Graham scan, numbered 1 to 8.">
<polygon points="60,290 260,290 310,140 210,40 60,90" fill="#7ccf9a" fill-opacity="0.25" stroke="currentColor" stroke-width="2"/>
<line x1="60" y1="290" x2="260" y2="290" stroke="#eea66f" stroke-width="1" stroke-dasharray="4 4"/>
<line x1="60" y1="290" x2="160" y2="240" stroke="#eea66f" stroke-width="1" stroke-dasharray="4 4"/>
<line x1="60" y1="290" x2="260" y2="190" stroke="#eea66f" stroke-width="1" stroke-dasharray="4 4"/>
<line x1="60" y1="290" x2="310" y2="140" stroke="#eea66f" stroke-width="1" stroke-dasharray="4 4"/>
<line x1="60" y1="290" x2="160" y2="140" stroke="#eea66f" stroke-width="1" stroke-dasharray="4 4"/>
<line x1="60" y1="290" x2="210" y2="40" stroke="#eea66f" stroke-width="1" stroke-dasharray="4 4"/>
<line x1="60" y1="290" x2="110" y2="140" stroke="#eea66f" stroke-width="1" stroke-dasharray="4 4"/>
<line x1="60" y1="290" x2="60" y2="90" stroke="#eea66f" stroke-width="1" stroke-dasharray="4 4"/>
<circle cx="260.0" cy="290.0" r="5" fill="currentColor"/>
<text x="271.0" y="282.0" font-size="12" text-anchor="middle" fill="currentColor">1</text>
<circle cx="160.0" cy="240.0" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="171.0" y="232.0" font-size="12" text-anchor="middle" fill="currentColor">2</text>
<circle cx="260.0" cy="190.0" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="271.0" y="182.0" font-size="12" text-anchor="middle" fill="currentColor">3</text>
<circle cx="310.0" cy="140.0" r="5" fill="currentColor"/>
<text x="321.0" y="132.0" font-size="12" text-anchor="middle" fill="currentColor">4</text>
<circle cx="160.0" cy="140.0" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="171.0" y="132.0" font-size="12" text-anchor="middle" fill="currentColor">5</text>
<circle cx="210.0" cy="40.0" r="5" fill="currentColor"/>
<text x="221.0" y="32.0" font-size="12" text-anchor="middle" fill="currentColor">6</text>
<circle cx="110.0" cy="140.0" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="121.0" y="132.0" font-size="12" text-anchor="middle" fill="currentColor">7</text>
<circle cx="60.0" cy="90.0" r="5" fill="currentColor"/>
<text x="71.0" y="82.0" font-size="12" text-anchor="middle" fill="currentColor">8</text>
<circle cx="60.0" cy="290.0" r="5" fill="currentColor"/>
<text x="40.0" y="294.0" font-size="12" text-anchor="middle" fill="currentColor">p0</text>
<text x="210.0" y="330.0" font-size="12" text-anchor="middle" fill="currentColor">hull: (0,0) (4,0) (5,3) (3,5) (0,4); orange points are inside</text>
</svg>
<figcaption>Figure 20.3. Graham scan on nine points. Dashed rays from the lowest point p0 show the angular order 1 to 8. The scan keeps a stack; points 2, 3, 5 and 7 are pushed and later popped when a right turn reveals that they lie inside.</figcaption>
</figure>

**Trace** on the nine points of Figure 20.3, $p_0 = (0,0)$:

| step | point | popped | stack after |
|---|---|---|---|
| 1 | $(4,0)$ | | $(0,0)\,(4,0)$ |
| 2 | $(2,1)$ | | $(0,0)\,(4,0)\,(2,1)$ |
| 3 | $(4,2)$ | $(2,1)$ | $(0,0)\,(4,0)\,(4,2)$ |
| 4 | $(5,3)$ | $(4,2)$ | $(0,0)\,(4,0)\,(5,3)$ |
| 5 | $(2,3)$ | | $(0,0)\,(4,0)\,(5,3)\,(2,3)$ |
| 6 | $(3,5)$ | $(2,3)$ | $(0,0)\,(4,0)\,(5,3)\,(3,5)$ |
| 7 | $(1,3)$ | | $(0,0)\,(4,0)\,(5,3)\,(3,5)\,(1,3)$ |
| 8 | $(0,4)$ | $(1,3)$ | $(0,0)\,(4,0)\,(5,3)\,(3,5)\,(0,4)$ |

At step 3, $(4,0) \to (2,1) \to (4,2)$ is a right turn, so $(2,1)$ is popped; $(0,0) \to (4,0) \to (4,2)$ is a left turn, so the
popping stops. The final stack is the hull.

**Theorem 20.4 (Graham 1972).** Graham scan computes the convex hull in $O(n \log n)$ time.

*Proof.* Correctness. Let $q_1, \ldots, q_{n-1}$ be the sorted points. **Invariant:** after processing $q_k$, the stack
holds, from bottom to top, the vertices of the convex hull of $\{p_0, q_1, \ldots, q_k\}$ in counter-clockwise order, ending
with $q_k$. It holds after $q_1$ (two points). Suppose it holds after $q_{k-1}$. The new point $q_k$ is a hull vertex of the
larger set: it is the most counter-clockwise point seen from $p_0$ (farthest among ties), so nothing lies beyond it. A
stack vertex $s$ with neighbour $t$ below it is still a hull vertex after adding $q_k$ exactly when $t \to s \to q_k$ is a
left turn; if it is not, $s$ lies inside the triangle $p_0, t, q_k$ (or on its edge) and is not a corner of the new hull.
And once a left turn is found, all vertices further down remain, because the old hull was convex and $q_k$ is beyond all
of them in angle. So popping until a left turn and then pushing $q_k$ gives exactly the new hull.

Time. Sorting takes $O(n \log n)$ comparisons. In the scan each point is pushed once and popped at most once, so the
total number of pops over the whole loop is at most $n$, and the loop does $O(n)$ work in all (the same amortized
argument as for KMP in [Chapter 18](18-String-Algorithms.md)). $\square$

### Andrew's monotone chain

A. M. Andrew (1979) noticed that sorting by angle is unnecessary. Sort the points by $x$ (then $y$). The **lower hull**,
from the leftmost to the rightmost point, is found by the same stack scan over the points from left to right; the **upper
hull** by the same scan from right to left. Glue them together. Sorting by coordinates is simpler and more robust than
sorting by angle, and it handles collinear points with no special rule, which makes this the version most people write.

```python
def monotone_chain(points):
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]
```

Its correctness proof is the Graham invariant with "angle from $p_0$" replaced by "$x$-coordinate", applied to each
half. After the sort, each point is pushed twice (once per half) and popped at most twice, so the scans make fewer than
$4n$ orientation tests: the program counts $5994$ for 2000 points on a circle, against four million for gift wrapping.

### The lower bound

**Theorem 20.5.** Any algorithm that outputs the hull vertices in order, and uses only comparisons and arithmetic
(the algebraic decision tree model), needs $\Omega(n \log n)$ time in the worst case.

*Proof by reduction from sorting.* Given numbers $x_1, \ldots, x_n$ to sort, make the points $(x_i, x_i^2)$. They lie on the
parabola $y = x^2$, which is convex, so every point is a hull vertex, and the counter-clockwise order of the hull, starting
from the leftmost point, is the order of increasing $x$. So a hull algorithm followed by $O(n)$ extra work sorts. Sorting
needs $\Omega(n \log n)$ in this model (Ben-Or 1983 extended the decision-tree bound of [Chapter 5](05-Sorting-by-Comparison.md)
to algebraic decision trees), so the hull does too. $\square$

The program does this reduction: the hull of $(x, x^2)$ for twelve random integers lists them in sorted order. Andrew
Yao (1981) showed that the bound holds even for algorithms that only have to *identify* which points are hull vertices,
without ordering them. Output-sensitive algorithms beat $n \log n$ when $h$ is small: Kirkpatrick and Seidel (1986) gave
$O(n \log h)$, and Timothy Chan (1996) a much simpler $O(n \log h)$ method that runs gift wrapping on hulls of small groups.
In three dimensions the hull can still be found in $O(n \log n)$ (Preparata and Hong 1977); the Quickhull program, Qhull,
is the standard implementation in any dimension.

```python
--8<-- "books/algorithms/ch20_hull.py"
```

```
1. A small example
   gift_wrapping   [(0, 0), (4, 0), (5, 3), (3, 5), (0, 4)]
   graham_scan     [(0, 0), (4, 0), (5, 3), (3, 5), (0, 4)]
   monotone_chain  [(0, 0), (4, 0), (5, 3), (3, 5), (0, 4)]
2. Random tests, with collinear and duplicate points
   all three hulls agree: True
3. Orientation tests: points in a disc (small hull) and on a circle (all on hull)
   n=  500 disc   hull size    23: gift wrapping     11500 tests, monotone chain   1969
   n=  500 circle hull size   500: gift wrapping    250000 tests, monotone chain   1494
   n= 2000 disc   hull size    43: gift wrapping     86000 tests, monotone chain   7950
   n= 2000 circle hull size  2000: gift wrapping   4000000 tests, monotone chain   5994
4. Sorting by convex hull: the hull of (x, x^2) lists the x in order
   input: [0, 31, 43, 15, -41, 17, -29, 7, -48, 49, -45, 2]
   hull order: [-48, -45, -41, -29, 0, 2, 7, 15, 17, 31, 43, 49]
```

(The monotone chain counts exclude the comparisons of the initial sort, which are not orientation tests.)

<figure class="play" data-play="hull"><span class="ai-tag">AI-created</span><figcaption><b>Watch it.</b> Gift wrapping on made-up points: from the leftmost point, keep turning to the point with every other point on one side. Tap to add points.</figcaption></figure>

## 20.4 Sweep-line algorithms

**The problem.** Given $n$ segments, report every pair that crosses. Checking all pairs with Theorem 20.2 costs
$\binom{n}{2} = O(n^2)$ tests. If there are many crossings, nothing can be faster, since we must print them all; but often
there are few (the streets of a city map cross mostly at corners). Can we pay only for the crossings that exist?

**The sweep-line idea.** Imagine a vertical line moving from left to right across the plane. At any moment it cuts some
of the segments, and those segments are **ordered** from bottom to top along it. Two segments can only cross if they are
**neighbours** in this order just before they cross. So instead of comparing all pairs, keep the current order (the
**status**) in a balanced search tree ([Chapter 8](08-Trees-and-Balanced-Search-Trees.md)), and compare only segments that
become neighbours. The order changes only at **events**: when the line reaches a left endpoint (insert a segment), a right
endpoint (delete one), or a crossing (two neighbours swap). Events are kept in a priority queue
([Chapter 9](09-Heaps-and-Priority-Queues.md)) ordered by $x$.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 520 260" role="img" aria-label="A vertical sweep line crosses four segments. The status lists them from bottom to top as d, c, b, a. Segments b and c are neighbours and cross to the right of the line, so that crossing is already in the event queue.">
<line x1="40" y1="40" x2="470" y2="90" stroke="currentColor" stroke-width="2.5"/>
<circle cx="40.0" cy="40.0" r="3" fill="currentColor"/>
<circle cx="470.0" cy="90.0" r="3" fill="currentColor"/>
<text x="482.0" y="95.0" font-size="14" text-anchor="middle" fill="currentColor">a</text>
<line x1="60" y1="120" x2="440" y2="200" stroke="#9cc9ea" stroke-width="2.5"/>
<circle cx="60.0" cy="120.0" r="3" fill="currentColor"/>
<circle cx="440.0" cy="200.0" r="3" fill="currentColor"/>
<text x="452.0" y="205.0" font-size="14" text-anchor="middle" fill="currentColor">b</text>
<line x1="90" y1="220" x2="460" y2="110" stroke="#eea66f" stroke-width="2.5"/>
<circle cx="90.0" cy="220.0" r="3" fill="currentColor"/>
<circle cx="460.0" cy="110.0" r="3" fill="currentColor"/>
<text x="472.0" y="115.0" font-size="14" text-anchor="middle" fill="currentColor">c</text>
<line x1="30" y1="235" x2="400" y2="240" stroke="currentColor" stroke-width="2.5"/>
<circle cx="30.0" cy="235.0" r="3" fill="currentColor"/>
<circle cx="400.0" cy="240.0" r="3" fill="currentColor"/>
<text x="412.0" y="245.0" font-size="14" text-anchor="middle" fill="currentColor">d</text>
<line x1="220" y1="15" x2="220" y2="250" stroke="currentColor" stroke-width="1.3" stroke-dasharray="6 4"/>
<text x="220.0" y="12.0" font-size="12" text-anchor="middle" fill="currentColor">sweep line</text>
<circle cx="274.5" cy="165.2" r="7" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
<text x="274.5" y="151.2" font-size="12" text-anchor="middle" fill="currentColor">next event</text>
<text x="380.0" y="30.0" font-size="12" text-anchor="middle" fill="currentColor">status, bottom to top: d, c, b, a</text>
</svg>
<figcaption>Figure 20.4. A sweep line crossing four segments. The status lists them in order along the line. Segments b and c are neighbours there and cross to the right, so their crossing is already waiting in the event queue; segments a and d are not neighbours of each other and are never compared.</figcaption>
</figure>

**Shamos and Hoey (1976): is there any crossing?** Process the $2n$ endpoints from left to right. At a left endpoint,
insert the segment into the status and test it against its new neighbours above and below. At a right endpoint, delete the
segment and test its former neighbours, which have just become adjacent, against each other. Stop at the first crossing
found. Each event costs $O(\log n)$ with a balanced tree, so the whole is $O(n \log n)$.

**Lemma 20.6.** If some pair of segments crosses, let $x^*$ be the leftmost crossing point and $s, t$ two segments crossing
there. Then just before $x^*$ (and after every event to the left of it), $s$ and $t$ are adjacent in the status, and they
became adjacent at some event at or before the last event to the left of $x^*$.

*Proof sketch* (assuming general position: no three segments through one point, no vertical segments). Take a vertical
line slightly to the left of $x^*$, after the last event before $x^*$. If some segment $u$ lay between $s$ and $t$ on this
line, then $u$ would have to end, or cross $s$ or $t$, before reaching $x^*$, since $s$ and $t$ meet at $x^*$ and squeeze
everything between them. An endpoint there would be an event after the line, contradicting the choice of line; a
crossing would be a crossing to the left of $x^*$, contradicting minimality. So $s$ and $t$ are adjacent there; the event
that made them adjacent was an insertion or deletion before $x^*$, at which the algorithm tested them. $\square$

**Bentley and Ottmann (1979): report every crossing.** Do the same, but do not stop: whenever two segments become adjacent
and cross to the right of the current line, put their crossing point into the event queue. At a crossing event, report
it, swap the two segments in the status, and test each of them against its new outer neighbour. By the lemma applied
again after each processed crossing, every crossing becomes an event before the sweep reaches it.

**Theorem 20.7.** Bentley-Ottmann reports all $k$ crossings of $n$ segments in $O((n + k) \log n)$ time and $O(n + k)$ space
(in general position).

*Proof sketch.* There are $2n + k$ events. Each event does $O(1)$ status-tree operations, $O(1)$ crossing tests and
$O(1)$ queue operations, each $O(\log n)$ (the queue holds $O(n + k)$ items and $\log(n + k) = O(\log n)$ because
$k \le n^2$). $\square$

The general-position assumptions hide real work: vertical segments, segments that share endpoints, three segments through
one point and overlapping collinear segments all need extra rules, which is why robust implementations (for example in
the CGAL library) are long. When $k$ is close to $n^2$, the brute force $O(n^2)$ is better than $O(n^2 \log n)$. Chazelle and
Edelsbrunner (1992) reached the optimal $O(n \log n + k)$, and Balaban (1995) did so with linear space.

**The same idea elsewhere.** A sweep line turns a two-dimensional problem into a sequence of one-dimensional updates.
The program's second sweep computes the **area of a union of axis-parallel rectangles**: between two consecutive $x$-events
the covered length along the line is constant, so the area is the sum of (covered length) × (strip width). With a segment
tree ([Chapter 10](10-Union-Find-and-Range-Queries.md)) over the $y$-coordinates, keeping cover counts, each event costs
$O(\log n)$ and the whole is $O(n \log n)$ (Bentley 1977); the program uses a plain array, $O(n)$ per event, which is enough
to check the answer against counting unit squares. The closest pair of points
([Chapter 11](11-Divide-and-Conquer.md)) also has a sweep-line solution, and Fortune's algorithm for Voronoi diagrams
(20.6) is a sweep.

```python
--8<-- "books/algorithms/ch20_sweep.py"
```

```
1. Bentley-Ottmann against brute force
   n= 10:   10 crossings by brute force, sweep finds   10, same: True, events 30
   n= 40:  129 crossings by brute force, sweep finds  129, same: True, events 209
   n= 80:  656 crossings by brute force, sweep finds  656, same: True, events 816
2. Union of rectangles
   sweep: 27  unit squares counted: 27
   40 random rectangles: sweep 4785  grid count 4785
```

The event counts are exactly $2n + k$: for $n = 80$, $160 + 656 = 816$. The program keeps the status in a Python list
with linear-time insertion, which is simpler than a balanced tree and fine at this size; the event logic is the real
algorithm.

## 20.5 Polygon area and point in polygon

A **polygon** is given by its vertices $v_0, v_1, \ldots, v_{n-1}$ in order around the boundary; the edges are $v_i v_{i+1}$,
with $v_n = v_0$. It is **simple** if the edges meet only at shared endpoints of consecutive edges.

### The shoelace formula

**The question.** What is the area of a polygon given by its corners?

**Theorem 20.8 (shoelace formula).** For a simple polygon with vertices listed counter-clockwise,

$$
\text{area} = \frac{1}{2} \sum_{i=0}^{n-1} \left( x_i y_{i+1} - x_{i+1} y_i \right) = \frac{1}{2} \sum_{i=0}^{n-1} v_i \times v_{i+1} .
$$

Listed clockwise, the sum is the negative of the area. (The name comes from the criss-cross pattern of the products when
the coordinates are written in two columns.)

*Proof idea.* $\frac{1}{2} v_i \times v_{i+1}$ is the **signed** area of the triangle with corners at the origin, $v_i$ and
$v_{i+1}$: positive if the origin sees the edge go counter-clockwise, negative otherwise (Lemma 20.1). For a convex polygon
with the origin inside, all terms are positive and the triangles exactly tile the polygon. In general, the triangles for
edges on the "far side" of the polygon, seen from the origin, add area that the "near side" triangles subtract again, so
each point of the plane is counted (number of times the boundary winds around it) times, which is 1 inside a simple
counter-clockwise polygon and 0 outside. A full proof is a discrete form of Green's theorem, or induction by cutting off
one triangle at a time (every simple polygon with more than three vertices has a diagonal, a classical lemma). $\square$

For the house-shaped polygon $(0,0), (6,0), (6,4), (3,2), (0,4)$ (a rectangle with a V cut out of its top), the sum is
$0 + 24 + (12 - 12) + (12 - 0) + 0 = 36$, so the area is 18: the rectangle's 24 minus the notch's 6. The cost is $O(n)$,
with integers only (twice the area is always an integer for integer vertices).

**Pick's theorem** (Georg Pick, 1899). For a simple polygon whose vertices have integer coordinates, with $I$ lattice points
strictly inside and $B$ on the boundary, the area is $I + B/2 - 1$. The number of lattice points on an edge from $(x_1, y_1)$
to $(x_2, y_2)$, counting one endpoint, is $\gcd(|x_2 - x_1|, |y_2 - y_1|)$ ([Chapter 19](19-Number-Theoretic-Algorithms.md)).
For the house, $B = 6 + 4 + 1 + 1 + 4 = 16$ and the program counts $I = 11$: $11 + 8 - 1 = 18$. Turned around, Pick gives
the number of interior lattice points from the area, without counting them.

### Point in polygon

**The question.** Is point $q$ inside the polygon? For a convex polygon it is easy: $q$ is inside exactly when it is to the
left of every edge, an $O(n)$ test, or $O(\log n)$ with binary search (exercise 6). For a general polygon the edges point
every which way.

**Ray casting.** Shoot a ray from $q$ to the right and count how many edges it crosses. By the **Jordan curve theorem** (a
simple closed curve splits the plane into an inside and an outside, and you cross the curve each time you go from one to
the other), $q$ is inside exactly when the count is **odd**: a ray that starts inside must leave, and each further crossing
switches sides again, and far to the right it is outside.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 560 280" role="img" aria-label="A five-sided polygon shaped like a house with a V-shaped notch in its top. Rays to the right from three points: from (3,1) one crossing, inside; from (3,3) two crossings, outside; from (0.5,3.5) three crossings, inside.">
<polygon points="40,250 370,250 370,30 205,140 40,30" fill="#9cc9ea" fill-opacity="0.3" stroke="currentColor" stroke-width="2"/>
<line x1="205.0" y1="195.0" x2="411.5" y2="195.0" stroke="#7ccf9a" stroke-width="1.6"/><polygon points="419.5,195.0 410.5,199.1 410.5,190.9" fill="#7ccf9a"/>
<circle cx="205.0" cy="195.0" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="1"/>
<text x="425.0" y="199.0" font-size="12" text-anchor="start" fill="currentColor">1 crossing: inside</text>
<circle cx="370.0" cy="195.0" r="3.5" fill="currentColor"/>
<line x1="205.0" y1="85.0" x2="411.5" y2="85.0" stroke="#eea66f" stroke-width="1.6"/><polygon points="419.5,85.0 410.5,89.0 410.5,81.0" fill="#eea66f"/>
<circle cx="205.0" cy="85.0" r="5" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<text x="425.0" y="89.0" font-size="12" text-anchor="start" fill="currentColor">2 crossings: outside</text>
<circle cx="287.5" cy="85.0" r="3.5" fill="currentColor"/>
<circle cx="370.0" cy="85.0" r="3.5" fill="currentColor"/>
<line x1="67.5" y1="57.5" x2="411.5" y2="57.5" stroke="#7ccf9a" stroke-width="1.6"/><polygon points="419.5,57.5 410.5,61.5 410.5,53.5" fill="#7ccf9a"/>
<circle cx="67.5" cy="57.5" r="5" fill="#7ccf9a" stroke="currentColor" stroke-width="1"/>
<text x="425.0" y="61.5" font-size="12" text-anchor="start" fill="currentColor">3 crossings: inside</text>
<circle cx="81.2" cy="57.5" r="3.5" fill="currentColor"/>
<circle cx="328.8" cy="57.5" r="3.5" fill="currentColor"/>
<circle cx="370.0" cy="57.5" r="3.5" fill="currentColor"/>
<text x="40.0" y="266.0" font-size="11" text-anchor="middle" fill="currentColor">(0,0)</text>
<text x="370.0" y="266.0" font-size="11" text-anchor="middle" fill="currentColor">(6,0)</text>
<text x="370.0" y="22.0" font-size="11" text-anchor="middle" fill="currentColor">(6,4)</text>
<text x="205.0" y="156.0" font-size="11" text-anchor="middle" fill="currentColor">(3,2)</text>
<text x="40.0" y="22.0" font-size="11" text-anchor="middle" fill="currentColor">(0,4)</text>
</svg>
<figcaption>Figure 20.5. Ray casting in the house polygon. A ray to the right from an inside point crosses the boundary an odd number of times (1 or 3), from an outside point an even number (2).</figcaption>
</figure>

**The special cases.** A ray can pass exactly through a vertex, or run along a horizontal edge. The clean fix is the
**half-open rule**: an edge counts as crossed if one endpoint is strictly above the ray's line and the other is on or
below it. A vertex touching the ray from above and below is then counted once (correctly, the ray passes from one side to
the other); a vertex where both edges are on the same side is counted zero or two times (correctly, the ray only grazes
the polygon); and horizontal edges are never counted. Points exactly on the boundary are detected first with the
orientation test. The code compares the crossing's $x$-coordinate with $q_x$ exactly, as a fraction:

```python
if (a[1] > y) != (b[1] > y):          # the edge straddles the line of the ray
    x_cross = a[0] + Fraction((y - a[1]) * (b[0] - a[0]), b[1] - a[1])
    if x < x_cross:
        inside = not inside
```

(Multiplying out the fraction gives an integer-only version, with the inequality flipped when $b_y < a_y$.)

**Winding numbers.** For polygons that cross themselves, "inside" is ambiguous. The **winding number** of the boundary
around $q$ counts how many times the boundary goes counter-clockwise around $q$: add 1 for each upward edge that passes to
the right of $q$ (with $q$ on its left), subtract 1 for each downward edge that passes to the right of $q$ (with $q$ on
its right). For a simple counter-clockwise polygon it is 1 inside and 0 outside. For a five-pointed star drawn in one
stroke, the centre has winding number 2 but an even crossing count, so the **even-odd rule** says "outside" and the
**nonzero rule** says "inside"; the program shows both. Graphics formats such as SVG and PDF let the author choose the
fill rule for exactly this reason.

## 20.6 Voronoi diagrams, Delaunay triangulations and k-d trees

*Level: advanced.*

### Voronoi diagrams

**The problem.** Given $n$ **sites** (say, the fire stations of a city, or landing sites on a map), divide the plane into
regions by which site is nearest. The region of site $p$, its **Voronoi cell**, is

$$
V(p) = \{ x : |x - p| \le |x - q| \text{ for every other site } q \} .
$$

The boundary between two sites' halves of the plane is the **perpendicular bisector** of the segment between them, so
$V(p)$ is the intersection of $n - 1$ half-planes: a convex polygon, possibly unbounded. The cells, with their edges and
vertices, form the **Voronoi diagram**. A Voronoi **vertex** is a point equidistant from three (or more) sites and closer
to them than to any other: the centre of a circle through three sites with no site inside.

**Its size is linear.** The diagram is a planar graph (add one vertex "at infinity" to end the unbounded edges). Euler's
formula for connected planar graphs, $V - E + F = 2$, with $F = n$ cells and every vertex of degree at least 3, so
$2E \ge 3V$, gives at most $2n - 5$ vertices and $3n - 6$ edges for $n \ge 3$. So a diagram of a million sites has at most
three million edges, not $n^2$.

**Building it.** Steven Fortune's **sweep-line algorithm** (1987) builds the diagram in $O(n \log n)$ time. Its sweep is
subtle: the part of the diagram already fixed lies behind a "beach line" of parabolic arcs, and events are sites and
circle tops. Because the diagram can be used to sort (sites on a line have cells in sorted order), $O(n \log n)$ is
optimal. In practice one often builds its dual instead.

### Delaunay triangulations

**Definition.** Connect two sites by an edge whenever their Voronoi cells share an edge. The result, for points in
**general position** (no four on a circle), is a triangulation of the convex hull of the sites: the **Delaunay
triangulation** (Boris Delaunay, 1934). Each Voronoi vertex corresponds to a Delaunay triangle, namely the three sites
equidistant from it, and the vertex is that triangle's **circumcentre**.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 520 370" role="img" aria-label="Five points with their Delaunay triangulation drawn solid and their Voronoi diagram drawn dashed. Each Voronoi vertex is the centre of the circle through the three corners of one triangle, and each Voronoi edge crosses one Delaunay edge at right angles.">
<defs><clipPath id="vor20clip"><rect x="0" y="0" width="520" height="370"/></clipPath></defs>
<polygon points="120.0,300.0 288.0,300.0 204.0,174.0" fill="#9cc9ea" fill-opacity="0.25" stroke="currentColor" stroke-width="1.8"/>
<polygon points="120.0,300.0 204.0,174.0 120.0,90.0" fill="#9cc9ea" fill-opacity="0.25" stroke="currentColor" stroke-width="1.8"/>
<polygon points="288.0,300.0 204.0,174.0 330.0,132.0" fill="#9cc9ea" fill-opacity="0.25" stroke="currentColor" stroke-width="1.8"/>
<polygon points="204.0,174.0 330.0,132.0 120.0,90.0" fill="#9cc9ea" fill-opacity="0.25" stroke="currentColor" stroke-width="1.8"/>
<circle cx="204.0" cy="265.0" r="91.0" fill="none" stroke="#7ccf9a" stroke-width="1.5"/>
<line x1="204.0" y1="265.0" x2="99.0" y2="195.0" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4"/>
<line x1="204.0" y1="265.0" x2="286.1" y2="210.3" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4"/>
<line x1="286.1" y1="210.3" x2="235.5" y2="58.5" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4"/>
<line x1="99.0" y1="195.0" x2="235.5" y2="58.5" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4"/>
<line x1="204.0" y1="265.0" x2="204.0" y2="601.0" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4" clip-path="url(#vor20clip)"/>
<line x1="286.1" y1="210.3" x2="612.1" y2="291.8" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4" clip-path="url(#vor20clip)"/>
<line x1="235.5" y1="58.5" x2="301.4" y2="-271.0" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4" clip-path="url(#vor20clip)"/>
<line x1="99.0" y1="195.0" x2="-237.0" y2="195.0" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4" clip-path="url(#vor20clip)"/>
<rect x="200.0" y="261.0" width="8" height="8" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<rect x="95.0" y="191.0" width="8" height="8" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<rect x="282.1" y="206.3" width="8" height="8" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<rect x="231.5" y="54.5" width="8" height="8" fill="#eea66f" stroke="currentColor" stroke-width="1"/>
<circle cx="120.0" cy="300.0" r="5" fill="currentColor"/>
<text x="108.0" y="316.0" font-size="11" text-anchor="middle" fill="currentColor">(0,0)</text>
<circle cx="288.0" cy="300.0" r="5" fill="currentColor"/>
<text x="302.0" y="316.0" font-size="11" text-anchor="middle" fill="currentColor">(4,0)</text>
<circle cx="204.0" cy="174.0" r="5" fill="currentColor"/>
<text x="218.0" y="166.0" font-size="11" text-anchor="middle" fill="currentColor">(2,3)</text>
<circle cx="330.0" cy="132.0" r="5" fill="currentColor"/>
<text x="344.0" y="124.0" font-size="11" text-anchor="middle" fill="currentColor">(5,4)</text>
<circle cx="120.0" cy="90.0" r="5" fill="currentColor"/>
<text x="108.0" y="82.0" font-size="11" text-anchor="middle" fill="currentColor">(0,5)</text>
</svg>
<figcaption>Figure 20.6. Five sites with their Delaunay triangulation (solid, shaded) and Voronoi diagram (dashed, with square vertices). Each Voronoi vertex is the circumcentre of one triangle; the green circle through (0,0), (4,0) and (2,3) contains no other site. Voronoi edges cross Delaunay edges at right angles; edges with one end at infinity leave the picture.</figcaption>
</figure>

**Theorem 20.9 (empty-circle property).** A triangle on three sites is a Delaunay triangle if and only if its circumcircle
has no site strictly inside.

*Proof.* The centre $c$ of the circle through $a$, $b$, $d$ is equidistant from them, at distance $r$. It is a Voronoi vertex
of exactly these sites when no other site is closer to $c$ than $r$, that is, when no site is inside the circle. $\square$

**The in-circle test.** As orientation is the predicate for hulls, the predicate for Delaunay is: given $a, b, c$ in
counter-clockwise order, is $d$ strictly inside their circumcircle? It is the sign of a $3 \times 3$ determinant:

$$
\operatorname{incircle}(a, b, c, d) = \det \begin{pmatrix} a_x - d_x & a_y - d_y & (a_x - d_x)^2 + (a_y - d_y)^2 \\ b_x - d_x & b_y - d_y & (b_x - d_x)^2 + (b_y - d_y)^2 \\ c_x - d_x & c_y - d_y & (c_x - d_x)^2 + (c_y - d_y)^2 \end{pmatrix} ,
$$

positive exactly when $d$ is inside. *Why:* lift each point $(x, y)$ to the paraboloid $z = x^2 + y^2$. A circle in the plane
lifts to the intersection of the paraboloid with a plane, and points inside the circle lift to points below that plane.
The determinant is (up to sign) the orientation test in three dimensions: which side of the plane through the lifted $a$,
$b$, $c$ the lifted $d$ is on. This lifting also shows that the Delaunay triangulation is the projection of the lower convex
hull of the lifted points, so a 3D hull algorithm computes it.

**Why Delaunay triangulations are the good ones.** Among all triangulations of a point set, the Delaunay triangulation
maximizes the smallest angle (Sibson 1978): it avoids long thin triangles, which is why it is the standard mesh for
interpolating terrain heights and for finite-element simulations. It also contains, as subgraphs, the nearest-neighbour
graph and the Euclidean minimum spanning tree ([Chapter 17](17-Spanning-Trees-Flows-and-Matching.md)), so those can be
found in $O(n \log n)$ by running Kruskal's algorithm on its $O(n)$ edges instead of all $n^2$ pairs.

**Counting triangles.** If $h$ sites are on the hull and the rest inside (general position), every Delaunay triangulation,
like every triangulation of the points, has exactly $2n - 2 - h$ triangles. Euler's formula gives this: with $T$ triangles
plus the outer face, $F = T + 1$; each triangle has 3 edge sides and the outer face has $h$, and each edge has two sides, so
$2E = 3T + h$; then $n - E + F = 2$ solves to $T = 2n - 2 - h$. The program checks it for 10, 60 and 200 random points.

**Building it: Bowyer-Watson.** Add the points one at a time (Adrian Bowyer and David Watson, independently, 1981). Start
with one huge triangle containing everything. To add a point $p$, find all triangles whose circumcircle contains $p$
(they form a connected, star-shaped hole around $p$), delete them, and connect $p$ to every edge of the hole's boundary.
The new triangles satisfy the empty-circle property, by an argument about which circles can contain which points. As
written in the program (scanning all triangles for each point) this is $O(n^2)$. With the points inserted in **random
order** and a structure that locates the triangle containing $p$, the expected time is $O(n \log n)$ (Guibas, Knuth and
Sharir 1992), the method used in practice. The program checks every triangle's circumcircle against every point with the
exact integer in-circle test, and prints the four Voronoi vertices of Figure 20.6 as circumcentres.

### k-d trees for nearest neighbours

**The problem.** Given $n$ points, answer many queries "which point is closest to $q$?". With the Voronoi diagram this is
point location: find the cell containing $q$, $O(\log n)$ per query after $O(n \log n)$ preprocessing, using a planar
point-location structure. That is optimal but complicated, and in three or more dimensions Voronoi diagrams get huge. The
practical structure, in any dimension, is the **k-d tree** (Jon Bentley, 1975; "k-d" means $k$-dimensional).

**Building.** Split the points at the median $x$-coordinate: the median point is the root, the left half and the right half
become subtrees. In each subtree split at the median $y$, then $x$ again, alternating. The tree has height $\lceil \log_2 (n+1)
\rceil$, and with a linear-time median ([Chapter 6](06-Sorting-in-Linear-Time-and-Selection.md)) building takes
$O(n \log n)$. Each node corresponds to a rectangle of the plane, split in two by its point.

**Searching.** Descend towards $q$ as in a binary search tree, then on the way back up, keep the best distance $\delta$ found
so far. At a node splitting on coordinate $j$ at value $s$, the far subtree can only hold a closer point if the ball of
radius $\delta$ around $q$ reaches across the splitting line, that is, if $|q_j - s| < \delta$. Otherwise skip the whole
subtree.

**Correctness.** Every point in the skipped subtree lies on the far side of the line, so its distance to $q$ is at least the
distance from $q$ to the line, $|q_j - s| \ge \delta$: it cannot beat the best. Nothing that could win is skipped. (The code
compares squared distances, to stay in exact arithmetic for integer inputs.)

**Cost.** In the worst case a query can visit many nodes, $O(n)$ for adversarial inputs and $O(\sqrt n)$ in the worst case
for a range query in two dimensions (Lee and Wong 1977). For points spread fairly evenly, Friedman, Bentley and Finkel
(1977) showed that the expected cost is $O(\log n)$ in fixed dimension. The program agrees: for 20 000 random points, 200
random queries visited on average 20.7 nodes, against 20 000 distance computations for brute force, and every answer
matched brute force. In high dimensions (dozens of coordinates, as for image or text embeddings) the pruning test almost
never succeeds and k-d trees degrade to brute force, the **curse of dimensionality**; there, approximate methods such as
locality-sensitive hashing and graph-based indexes take over (see the [Machine learning book](../machine-learning/index.md)).

```python
--8<-- "books/algorithms/ch20_proximity.py"
```

```
1. Delaunay triangulation of random points
   n= 10:  12 triangles (2n - 2 - h = 12), every circumcircle empty: True
   n= 60: 109 triangles (2n - 2 - h = 109), every circumcircle empty: True
   n=200: 383 triangles (2n - 2 - h = 383), every circumcircle empty: True
   five points [(0, 0), (4, 0), (2, 3), (5, 4), (0, 5)]
     triangle (0, 1, 2): Voronoi vertex (2.000, 0.833)
     triangle (0, 2, 4): Voronoi vertex (-0.500, 2.500)
     triangle (1, 2, 3): Voronoi vertex (3.955, 2.136)
     triangle (2, 3, 4): Voronoi vertex (2.750, 5.750)
2. k-d tree nearest neighbour
   20000 points, 200 queries: all equal to brute force: True, average nodes visited 20.7
```

### Geometry and motion

Robots use these structures directly. A path that follows the edges of the Voronoi diagram of the obstacles stays as far
as possible from all of them, a classical way to plan safe routes; visibility graphs (connect every pair of obstacle
corners that can see each other, then run a shortest-path search from [Chapter 16](16-Shortest-Paths.md)) give the
shortest routes that just graze the corners. On Mars, where commands take between about 3 and 22 minutes to arrive, a
rover cannot wait for a human to approve every metre: Perseverance's AutoNav system builds a map of the terrain ahead and
plans its own drive around hazards, which needs exactly this kind of fast, robust geometry.

### In practice

CGAL (the Computational Geometry Algorithms Library, in C++) implements nearly everything in this chapter with exact
predicates. In Python, `scipy.spatial` wraps Qhull for convex hulls, Delaunay triangulations and Voronoi diagrams and has a
fast k-d tree (`KDTree`); Shapely (on the GEOS library) handles polygons, intersections and point-in-polygon tests for maps.
Shewchuk's Triangle program is a standard for quality Delaunay meshes, and his robust predicates are used widely.

## Check yourself

??? question "1. Is the path $(1,1) \to (4,2) \to (2,5)$ a left turn, a right turn or straight?"

    $\operatorname{cross} = (4 - 1)(5 - 1) - (2 - 1)(2 - 1) = 12 - 1 = 11 > 0$: a left turn. The triangle on these three points has area
    $11/2$.

??? question "2. Do the segments $(1,3)$–$(4,0)$ and $(0,0)$–$(2,2)$ intersect? If so, where?"

    $d_1 = \operatorname{orient}((0,0),(2,2),(1,3)) = 2 \cdot 3 - 2 \cdot 1 = 4 > 0$; $d_2 = \operatorname{orient}((0,0),(2,2),(4,0)) = 0 - 8 < 0$. So
    $(1,3)$ and $(4,0)$ are on opposite sides of the second segment's line. $d_3 = \operatorname{orient}((1,3),(4,0),(0,0)) = 3 \cdot (-3) -
    (-3)(-1) = -12 < 0$, $d_4 = \operatorname{orient}((1,3),(4,0),(2,2)) = 3 \cdot (-1) - (-3)(1) = 0$. So case (a) fails but $d_4 = 0$ and
    $(2,2)$ lies on the segment from $(1,3)$ to $(4,0)$ (its $x$ is between 1 and 4, its $y$ between 0 and 3): case (b). They
    touch at $(2,2)$, the endpoint of the second segment.

??? question "3. Find the area of the quadrilateral $(1,1), (5,1), (4,4), (2,3)$ with the shoelace formula."

    Terms $x_i y_{i+1} - x_{i+1} y_i$: $1 \cdot 1 - 5 \cdot 1 = -4$; $5 \cdot 4 - 4 \cdot 1 = 16$; $4 \cdot 3 - 2 \cdot 4 = 4$; $2 \cdot 1 - 1 \cdot 3 = -1$.
    Sum $15$, so the area is $7.5$ (positive: the order is counter-clockwise).

??? question "4. Run Graham scan by hand on $(2,0), (0,1), (3,2), (1,2), (2,4), (4,1)$."

    $p_0 = (2,0)$. Angular order: $(4,1), (3,2), (2,4), (1,2), (0,1)$. Stack: push $(4,1)$; push $(3,2)$ (left turn
    $(2,0) \to (4,1) \to (3,2)$); at $(2,4)$, $(4,1) \to (3,2) \to (2,4)$ is a right turn, pop $(3,2)$, then push $(2,4)$; push $(1,2)$;
    at $(0,1)$, $(2,4) \to (1,2) \to (0,1)$ is a right turn ($\operatorname{cross} = (-1)(-3) - (-2)(-2) = -1$), pop $(1,2)$, push $(0,1)$. Hull:
    $(2,0), (4,1), (2,4), (0,1)$.

??? question "5. Graham scan pops when the turn is $\le 0$, not $< 0$. What goes wrong with $< 0$?"

    With $< 0$, collinear points are kept on the stack. Then points lying in the middle of a hull edge are reported as
    hull vertices, which violates the convention (and, worse, with several collinear points at the end of the angular
    order the output can double back along the last edge). Using $\le 0$ removes them. If you *want* the collinear boundary
    points, you must also sort the last ray's collinear points farthest first.

??? question "6. Write code that tests whether a point is inside a convex polygon (counter-clockwise, no collinear vertices) in $O(\log n)$ time."

    Binary search for the wedge from $v_0$ that contains $q$, then test one edge:

    ```python
    def in_convex(q, P):
        n = len(P)
        if cross(P[0], P[1], q) < 0 or cross(P[0], P[n - 1], q) > 0:
            return False                      # outside the angle at P[0]
        lo, hi = 1, n - 1
        while hi - lo > 1:                    # invariant: q is in the wedge P[0], P[lo], P[hi]
            mid = (lo + hi) // 2
            if cross(P[0], P[mid], q) >= 0:
                lo = mid
            else:
                hi = mid
        return cross(P[lo], P[lo + 1], q) >= 0
    ```

    The rays from $v_0$ to the other vertices are sorted by angle, so the wedge can be found by binary search, and then
    $q$ is inside exactly when it is left of (or on) the one edge $v_{lo} v_{lo+1}$ that closes the wedge. Checked against ray
    casting on 3000 random points around a 10-vertex hull. Points on the boundary count as inside.

??? question "7. In the lower-bound reduction, why does the hull of the points $(x_i, x_i^2)$ contain every point, and how is the sorted order read off?"

    The parabola $y = x^2$ is strictly convex: for $a < b < c$, the point $(b, b^2)$ lies strictly below the chord from
    $(a, a^2)$ to $(c, c^2)$ (because $\operatorname{cross} = (b - a)(c - a)(c - b) > 0$ for the three points in order). So no point is inside
    the hull or on an edge, and every point is a vertex. Going counter-clockwise from the leftmost point, the lower hull
    runs left to right through all the points (there is no upper hull besides the closing edge), so reading the $x$
    values from the leftmost vertex gives them sorted. Finding the leftmost vertex costs $O(n)$.

??? question "8. Use Pick's theorem to count the lattice points strictly inside the triangle $(0,0), (5,0), (0,3)$."

    Area $= 7.5$. Boundary points: $\gcd(5,0) + \gcd(5,3) + \gcd(0,3) = 5 + 1 + 3 = 9$. So $I = A - B/2 + 1 = 7.5 - 4.5 + 1 = 4$. They are
    $(1,1), (2,1), (3,1), (1,2)$.

??? question "9. Four points at the corners of a square are not in general position for Delaunay. Why, and what happens?"

    All four lie on one circle, the square's circumcircle. Both diagonals give triangulations in which no point is
    *strictly* inside any circumcircle, so both are Delaunay: the Delaunay triangulation is not unique. The Voronoi diagram
    is unique, but it has a vertex of degree 4 at the centre of the square. The in-circle test returns exactly 0 there,
    which is why it must be computed exactly: with rounding the two choices could be mixed inconsistently.

??? question "10. Write code that checks whether a polygon (vertices in order) is convex."

    It is convex (allowing collinear vertices) when all nonzero turns have the same sign:

    ```python
    def is_convex(poly):
        signs = set()
        n = len(poly)
        for i in range(n):
            c = cross(poly[i], poly[(i + 1) % n], poly[(i + 2) % n])
            if c:
                signs.add(c > 0)
        return len(signs) <= 1

    print(is_convex([(0, 0), (4, 0), (4, 3), (0, 3)]))           # True
    print(is_convex([(0, 0), (6, 0), (6, 4), (3, 2), (0, 4)]))   # False: the house has a notch
    ```

    This assumes the polygon is simple. A self-intersecting polygon such as a star drawn in one stroke has all turns of
    the same sign but is not convex; checking that the total turning is one full turn (or that the edges' directions
    increase monotonically through one revolution) catches it.

??? question "11. In the k-d tree search, why is it safe to skip the far subtree when $(q_j - s)^2 \ge \delta^2$, and why must the near subtree be searched first?"

    Every point in the far subtree has coordinate $j$ on the other side of $s$, so its distance to $q$ is at least
    $|q_j - s| \ge \delta$, never better than the best so far. Searching the near side first matters for speed, not
    correctness: it usually finds a close point quickly, making $\delta$ small, so that the far subtrees can be skipped.
    Searching the far side first would still give the right answer but visit many more nodes.

??? question "12. A Delaunay triangulation of 200 points has 383 triangles. How many points are on the hull, and how many edges does it have?"

    $T = 2n - 2 - h$ gives $383 = 398 - h$, so $h = 15$. Edges: $2E = 3T + h = 1149 + 15 = 1164$, so $E = 582$. Check with Euler:
    $n - E + F = 200 - 582 + 384 = 2$. (The Voronoi diagram then has 383 vertices, one per triangle, and 582 edges, one per
    Delaunay edge.)

## What you learned

- The cross product gives the orientation test, the sign of a small integer expression; computed exactly it is reliable,
  while floating point gets near-collinear cases wrong about half the time.
- Two segments meet exactly when each straddles the other's line, or an endpoint lies on the other segment; four
  orientation tests decide it.
- Convex hulls: gift wrapping in $O(nh)$, Graham scan and Andrew's monotone chain in $O(n \log n)$ with a stack that pops
  every right turn; $\Omega(n \log n)$ is a lower bound because hulls can sort.
- A sweep line keeps the objects cut by a moving line in order and only compares neighbours: Bentley-Ottmann reports $k$
  crossings in $O((n + k) \log n)$.
- The shoelace formula gives polygon area in $O(n)$; Pick's theorem links area and lattice points; ray casting with a
  half-open rule and winding numbers decide point in polygon.
- Voronoi diagrams and Delaunay triangulations are dual, have linear size, and are characterized by empty circles; the
  in-circle test is orientation one dimension up.
- k-d trees answer nearest-neighbour queries by pruning subtrees the search ball cannot reach, fast in low dimensions.

**Next:** [Chapter 21](21-Randomized-and-Amortized-Analysis.md), the tools for analysing algorithms that use randomness
or pay for expensive steps with cheap ones.

## Further reading

- M. de Berg, O. Cheong, M. van Kreveld and M. Overmars, *Computational Geometry: Algorithms and Applications*, 3rd ed. 2008: the standard textbook, with Fortune's sweep, point location and randomized Delaunay construction.
- F. P. Preparata and M. I. Shamos, *Computational Geometry: An Introduction*, 1985.
- J. O'Rourke, *Computational Geometry in C*, 2nd ed. 1998, with careful code for all the basic predicates.
- CLRS (Cormen, Leiserson, Rivest, Stein, *Introduction to Algorithms*, 4th ed. 2022), chapter 33; Sedgewick and Wayne (*Algorithms*, 4th ed. 2011) for geometric applications of search trees.
- R. L. Graham, "An Efficient Algorithm for Determining the Convex Hull of a Finite Planar Set", *Information Processing Letters* 1, 1972.
- R. A. Jarvis, "On the Identification of the Convex Hull of a Finite Set of Points in the Plane", *Information Processing Letters* 2, 1973.
- A. M. Andrew, "Another Efficient Algorithm for Convex Hulls in Two Dimensions", *Information Processing Letters* 9, 1979.
- T. M. Chan, "Optimal Output-Sensitive Convex Hull Algorithms in Two and Three Dimensions", *Discrete & Computational Geometry* 16, 1996.
- M. I. Shamos and D. Hoey, "Geometric Intersection Problems", FOCS 1976.
- J. L. Bentley and T. A. Ottmann, "Algorithms for Reporting and Counting Geometric Intersections", *IEEE Transactions on Computers* C-28, 1979.
- S. Fortune, "A Sweepline Algorithm for Voronoi Diagrams", *Algorithmica* 2, 1987.
- L. J. Guibas, D. E. Knuth and M. Sharir, "Randomized Incremental Construction of Delaunay and Voronoi Diagrams", *Algorithmica* 7, 1992.
- J. L. Bentley, "Multidimensional Binary Search Trees Used for Associative Searching", *Communications of the ACM* 18(9), 1975.
- J. H. Friedman, J. L. Bentley and R. A. Finkel, "An Algorithm for Finding Best Matches in Logarithmic Expected Time", *ACM Transactions on Mathematical Software* 3(3), 1977.
- J. R. Shewchuk, "Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates", *Discrete & Computational Geometry* 18, 1997.
- L. Kettner, K. Mehlhorn, S. Pion, S. Schirra and C. Yap, "Classroom Examples of Robustness Problems in Geometric Computations", *Computational Geometry* 40, 2008.
- On this site: [Chapter 11](11-Divide-and-Conquer.md) (closest pair), [Chapter 16](16-Shortest-Paths.md) (searching the graphs that geometry builds), [Chapter 17](17-Spanning-Trees-Flows-and-Matching.md) (minimum spanning trees), [Chapter 19](19-Number-Theoretic-Algorithms.md) (gcds for lattice points), and the [Machine learning book](../machine-learning/index.md) for nearest neighbours in high dimensions. Coordinates, vectors and determinants: https://math.akadian.ca/books/.
