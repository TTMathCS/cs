# 18. Perception and robotics

*Every agent so far received its percepts as clean symbols: a board position, a word, a reward. A robot receives
millions of brightness values per second and acts by turning motors. This chapter answers the question: how does an
agent turn raw sensor data into a usable picture of the world, and turn decisions into physical motion? You will find
edges and corners in an image from scratch, recover depth from a stereo pair and prove how its error grows with
distance, compute the kinematics of an arm and a wheeled rover, estimate a robot's path and a map of landmarks at the
same time, plan collision-free motion with random trees and roadmaps, and close the loop with a PID controller. The
chapter ends with what real Mars vehicles do with these ideas, as NASA and JPL report it.*

!!! abstract "In this chapter"
    **You will learn:**

    - how an image becomes edges and corners (Sobel filters, the Harris structure tensor), and what convolutional
      networks changed
    - depth from two cameras: triangulation $Z = fB/d$, block matching, occlusions, and the proof that depth error grows
      as $Z^2$
    - sensors, actuators and kinematics: forward and inverse kinematics of a two-link arm, the Jacobian and its
      singularities, a differential-drive rover
    - the SLAM problem, and why with linear measurements it is a sparse least-squares problem; loop closure measured
    - configuration space, the probabilistic roadmap with a proof of probabilistic completeness, and the RRT from scratch
    - PID control: why proportional control leaves an error, why the integral removes it, stability by the
      characteristic polynomial, and integrator windup
    - how Mars rovers and the Ingenuity helicopter use stereo vision, visual odometry, autonomous navigation and
      target selection

    **You need:** [Chapter 2](02-Intelligent-Agents.md) (agents; the Mars autonomy section 2.6),
    [Chapter 4](04-Heuristic-Search.md) (A\* on a terrain grid) and [Chapter 13](13-Reasoning-over-Time.md) (Kalman and
    particle filters, robot localization). Convolution from
    [Machine learning, Chapter 17](../machine-learning/17-Convolutional-Networks.md) helps for 18.1. Vectors, matrices and
    least squares ([Machine learning, Chapter 4](../machine-learning/04-Linear-Regression.md)).

    **Levels:** 18.1 and 18.3 are beginner to intermediate; 18.2 and 18.6 are intermediate; 18.4 and 18.5 are
    advanced; 18.7 is for everyone.

## 18.1 Seeing: images, edges, features; what CNNs changed

**The question:** a camera hands the agent a grid of numbers. Where in those numbers are the objects?

### Images as arrays

A grey-scale **image** is a 2-D array $I(r, c)$ of brightness values, one per **pixel** (picture element), here
scaled to between 0 and 1; $r$ is the row and $c$ the column. A colour image has three such arrays (red, green,
blue). A single pixel value says almost nothing: it depends on the lighting, the surface and the camera. What carries
information is how values **change** from pixel to pixel. Where a bright rock meets dark soil the brightness jumps;
that jump is an **edge**, and edges outline objects.

### Gradients and the Sobel filter

The rate of change of brightness is the **gradient** $\nabla I = (I_x, I_y)$, the derivatives across columns and down
rows. On a grid we estimate a derivative by a difference. The **central difference**
$I_x(r, c) \approx \frac{1}{2}\big(I(r, c+1) - I(r, c-1)\big)$ is accurate to second order: by Taylor's theorem,
$I(c \pm 1) = I(c) \pm I'(c) + \tfrac{1}{2}I''(c) \pm \tfrac{1}{6}I'''(c) + \dots$, and subtracting cancels the even
terms, leaving $I'(c) + \tfrac{1}{6}I'''(c) + \dots$. Differences amplify noise, so we also average over the
neighbouring rows with weights $(1, 2, 1)/4$. The product of the two is the **Sobel filter** (Sobel and Feldman,
1968):

$$
S_x = \frac{1}{8}\begin{pmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{pmatrix} = \frac{1}{4}\begin{pmatrix} 1 \\ 2 \\ 1 \end{pmatrix}\cdot\frac{1}{2}\begin{pmatrix} -1 & 0 & 1 \end{pmatrix},
\qquad S_y = S_x^{\top}.
$$

Applying a filter means sliding it over the image and, at each position, taking the sum of the products of the
filter's entries with the pixels under it. This is **correlation**; flipping the filter first gives **convolution**,
and for learning the difference does not matter (it is explained in full, with stride and padding, in
[Machine learning, Section 17.2](../machine-learning/17-Convolutional-Networks.md#172-convolution-from-scratch-filters-edges-stride-padding)).
Because $S_x$ is an outer product, one 3×3 pass equals a vertical 3-tap pass followed by a horizontal one, which
matters for speed on large images.

**Worked example.** At a vertical edge where the three columns under the filter have brightness 0.2, 0.2, 0.9 in
every row, $S_x$ gives $\frac{1}{8}(-1 - 2 - 1)(0.2) + \frac{1}{8}(1 + 2 + 1)(0.9) = \frac{4}{8}(0.9 - 0.2) = 0.35$:
half the step, because the difference spans two pixels. $S_y$ gives 0, since every row is the same. On flat ground
both are near 0. The gradient **magnitude** $\sqrt{I_x^2 + I_y^2}$ is large on edges whatever their direction, and the
direction $\operatorname{atan2}(I_y, I_x)$ points across the edge.

The **Canny edge detector** (Canny, 1986), still the standard, adds three steps: smooth with a Gaussian first; keep a
pixel only if its magnitude is a maximum along the gradient direction (**non-maximum suppression**, which thins the
two-pixel-wide edges our simple threshold gives); and use two thresholds, keeping weak edge pixels only when they
connect to strong ones (**hysteresis**).

### Corners: the structure tensor

Edges are good outlines but poor landmarks: slide a small window along an edge and the image under it does not
change, so a point on an edge cannot be located along it. A **corner** changes in every direction. Measure the change
when a window $W$ is shifted by $(u, v)$:

$$
E(u, v) = \sum_{(r, c) \in W}\big(I(r + v, c + u) - I(r, c)\big)^2 \approx \sum_{W}(I_x u + I_y v)^2 = \begin{pmatrix} u & v \end{pmatrix} M \begin{pmatrix} u \\ v \end{pmatrix},
\qquad M = \sum_{W}\begin{pmatrix} I_x^2 & I_x I_y \\ I_x I_y & I_y^2 \end{pmatrix},
$$

using the first-order Taylor expansion $I(r + v, c + u) \approx I(r, c) + I_x u + I_y v$. The 2×2 symmetric matrix $M$
is the **structure tensor**. Its eigenvalues $\lambda_1 \ge \lambda_2 \ge 0$ are the largest and smallest values of
$E$ over unit shifts (a standard fact about quadratic forms). So:

- both small: flat region, no shift changes anything;
- $\lambda_1$ large, $\lambda_2$ small: an edge, which changes only across it;
- both large: a corner.

Harris and Stephens (1988) avoided computing eigenvalues by scoring $R = \det M - k(\operatorname{tr} M)^2$ with
$k \approx 0.05$, since $\det M = \lambda_1\lambda_2$ and $\operatorname{tr} M = \lambda_1 + \lambda_2$: $R$ is large
only when both eigenvalues are.

The program draws a 24×24 image of a bright rectangular "rock" on darker ground with a little noise, computes Sobel
gradients, thresholds the magnitude, and finds Harris corners as local maxima of $R$.

```python
--8<-- "books/ai/ch18_edges.py"
```

```
1. Sobel gradient at a few pixels (row, col in the original image)
   (12, 6): gx +0.359  gy -0.027  magnitude 0.360
   (12,17): gx -0.355  gy +0.001  magnitude 0.355
   ( 7,12): gx -0.005  gy +0.361  magnitude 0.361
   (12,12): gx -0.006  gy +0.010  magnitude 0.012
   ( 3, 3): gx -0.013  gy -0.006  magnitude 0.014

2. edge map, threshold half the largest magnitude (0.197); # = edge
   ......................
   ......................
   ......................
   .....############.....
   ....##############....
   ....##..........##....
   ....##..........##....
   ....##..........##....
   ....##..........##....
   ....##..........##....
   ....##..........##....
   ....##..........##....
   ....##..........##....
   ....##############....
   .....############.....
   ......................
   84 edge pixels

3. Harris corners (local maxima of R above 10% of the largest)
   corner at row  7, col  6   R = 0.12642
   corner at row 16, col  6   R = 0.12082
   corner at row  7, col 17   R = 0.11315
   corner at row 16, col 17   R = 0.10737

4. eigenvalues of the structure tensor: what kind of place is it?
   flat background      lambda1 0.0027  lambda2 0.0005
   middle of left edge  lambda1 0.7794  lambda2 0.0014
   top-left corner      lambda1 0.5044  lambda2 0.3176
```

Part 1 confirms the worked example: 0.359 and −0.355 across the left and right sides (the sign says which way
brightness increases), 0.361 down the top, and about 0.01 inside the rock and on the ground. Part 2's edge map shows
image rows 3 to 18: the outline is two pixels thick for the reason computed above. Part 3 finds exactly the four
corners. Part 4 is the eigenvalue test made visible: on flat ground both eigenvalues are about 0.003 or less; on the
middle of an edge one is 0.78 and the other 0.001; at a corner both are large (0.50 and 0.32). Figure 18.1 shows the
image, the edges and the corners.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 290" role="img" aria-label="Two 24 by 24 pixel grids. Left: the image, a bright rectangle on a dark background. Right: the Sobel edge pixels form a two-pixel-wide rectangular outline, with the four Harris corners circled at its corners.">
<rect x="30" y="20" width="240" height="240" fill="none" stroke="currentColor" stroke-width="1"/>
<rect x="90" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="100" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="110" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="120" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="130" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.84"/>
<rect x="140" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="150" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="160" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="170" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="180" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="190" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="200" y="90" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="90" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="100" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="110" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="120" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="130" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="140" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="150" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="160" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="170" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="180" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="190" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="200" y="100" width="10" height="10" fill="#eea66f" fill-opacity="0.91"/>
<rect x="90" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="100" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="110" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="120" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.91"/>
<rect x="130" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="140" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="150" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="160" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="170" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="180" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="190" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.91"/>
<rect x="200" y="110" width="10" height="10" fill="#eea66f" fill-opacity="0.91"/>
<rect x="90" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="100" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.93"/>
<rect x="110" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="120" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="130" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="140" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="150" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="160" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="170" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="180" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="190" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="200" y="120" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="90" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.94"/>
<rect x="100" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="110" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="120" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="130" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="140" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="150" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="160" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="170" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="180" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.91"/>
<rect x="190" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="200" y="130" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="90" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="100" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="110" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="120" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="130" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="140" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="150" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.91"/>
<rect x="160" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="170" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="180" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.80"/>
<rect x="190" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="200" y="140" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="90" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="100" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="110" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="120" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="130" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="140" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="150" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="160" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="170" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="180" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="190" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="200" y="150" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="90" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.91"/>
<rect x="100" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="110" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="120" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="130" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="140" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="150" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.92"/>
<rect x="160" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="170" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.85"/>
<rect x="180" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.92"/>
<rect x="190" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="200" y="160" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="90" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="100" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="110" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="120" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="130" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="140" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="150" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="160" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.91"/>
<rect x="170" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="180" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="190" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="200" y="170" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="90" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.90"/>
<rect x="100" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="110" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="120" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="130" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="140" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.88"/>
<rect x="150" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.91"/>
<rect x="160" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.86"/>
<rect x="170" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="180" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<rect x="190" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.87"/>
<rect x="200" y="180" width="10" height="10" fill="#eea66f" fill-opacity="0.89"/>
<text x="150.0" y="282.0" font-size="12" text-anchor="middle" fill="currentColor">the image (24 x 24 pixels)</text>
<rect x="330" y="20" width="240" height="240" fill="none" stroke="currentColor" stroke-width="1"/>
<rect x="390" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="400" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="410" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="420" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="430" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="440" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="450" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="460" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="470" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="480" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="490" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="80" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="400" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="410" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="420" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="430" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="440" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="450" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="460" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="470" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="480" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="490" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="90" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="100" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="100" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="100" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="100" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="110" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="110" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="110" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="110" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="120" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="120" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="120" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="120" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="130" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="130" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="130" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="130" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="140" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="140" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="140" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="140" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="150" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="150" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="150" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="150" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="160" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="160" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="160" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="160" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="170" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="170" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="170" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="170" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="380" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="400" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="410" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="420" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="430" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="440" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="450" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="460" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="470" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="480" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="490" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="510" y="180" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="390" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="400" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="410" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="420" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="430" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="440" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="450" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="460" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="470" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="480" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="490" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<rect x="500" y="190" width="10" height="10" fill="#9cc9ea" fill-opacity="0.9" stroke="currentColor" stroke-width="0.3"/>
<text x="450.0" y="282.0" font-size="12" text-anchor="middle" fill="currentColor">Sobel edges (magnitude above half the maximum)</text>
<circle cx="395.0" cy="95.0" r="6" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
<circle cx="395.0" cy="185.0" r="6" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
<circle cx="505.0" cy="95.0" r="6" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
<circle cx="505.0" cy="185.0" r="6" fill="none" stroke="#7ccf9a" stroke-width="2.5"/>
</svg>
<figcaption>Figure 18.1. The program's image (left) and its edge map (right): pixels whose Sobel gradient magnitude exceeds half the maximum. Circles mark the four Harris corners found in part 3, at rows 7 and 16, columns 6 and 17.</figcaption>
</figure>

### Features and matching

To recognise the same point in two images (for stereo, for tracking, for building maps), a corner is not enough; we
need a **descriptor**, a vector summarising the patch around it that stays similar when the view changes. Lowe's
SIFT (2004) finds points at a characteristic scale, assigns each a dominant gradient orientation, and describes it by
histograms of gradient directions in a grid around it, which makes the descriptor largely unchanged by rotation,
scale and moderate changes of viewpoint and lighting. Matching two images is then nearest-neighbour search among
descriptors.

### What CNNs changed

Every filter above was designed by a person. A **convolutional neural network** (CNN) stacks many layers of filters
and learns all of them from labelled examples by gradient descent; the first layers of trained networks learn filters
much like Sobel's and like oriented edge detectors, and deeper layers combine them into parts and objects. The
turning point was AlexNet (Krizhevsky, Sutskever and Hinton, 2012), which won the ImageNet classification challenge of
2012 with a top-5 error of 15.3 percent against 26.2 percent for the second-best entry, as their paper reports. Since
then learned features have replaced hand-designed ones for recognition, detection and segmentation. The
[Machine learning book's Chapter 17](../machine-learning/17-Convolutional-Networks.md) builds convolution,
backpropagation through it, the classic architectures and detection from scratch; we do not repeat it. Hand-designed
geometry has not disappeared: stereo, visual odometry and map building still rest on the projective geometry of the
next sections, often with learned features plugged into it, and flight systems with small computers and strict
verification rules use the classical methods.

## 18.2 3-D from images: stereo, depth

**The question:** a single image loses the third dimension. How can a robot tell how far away a rock is?

### The pinhole camera

In the **pinhole model**, a point at position $(X, Y, Z)$ in the camera's frame ($Z$ along the viewing direction)
projects to the image point

$$
x = f\,\frac{X}{Z}, \qquad y = f\,\frac{Y}{Z},
$$

where $f$ is the **focal length** measured in pixels and $(x, y)$ is measured from the image centre. Dividing by $Z$
is what makes far things small, and it is also what loses depth: every point on the ray through the pinhole and
$(x, y)$ lands on the same pixel. One image cannot say where on the ray the point is.

### Two cameras: triangulation

Place a second camera a distance $B$ (the **baseline**) to the right of the first, pointing the same way. The same
point is at $X$ for the left camera and $X - B$ for the right one, with the same $Z$. So

$$
x_L = f\,\frac{X}{Z}, \qquad x_R = f\,\frac{X - B}{Z}, \qquad d = x_L - x_R = \frac{fB}{Z},
$$

and therefore

$$
Z = \frac{fB}{d}.
$$

The difference $d$ is the **disparity**: how far the point shifts between the two images (Figure 18.2). Near points
shift a lot, far points little, points at infinity not at all. This is the **similar triangles** argument: the
triangle formed by the point and the two camera centres (base $B$, height $Z$) is similar to the one formed by the
point's two images and the camera centres (base $d$, height $f$).

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 620 300" role="img" aria-label="Two camera centres a baseline B apart, each with an image plane at distance f in front. Dashed rays from a point P at depth Z pass through the image planes at different horizontal positions; the difference is the disparity d.">
<defs><marker id="arr182" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>
<circle cx="300" cy="40" r="6" fill="#eea66f" stroke="currentColor"/>
<text x="312.0" y="44.0" font-size="13" text-anchor="start" fill="currentColor">point P at depth Z</text>
<circle cx="210" cy="250" r="5" fill="#9cc9ea" stroke="currentColor"/>
<line x1="155.0" y1="190.0" x2="265.0" y2="190.0" stroke="currentColor" stroke-width="1.8"/>
<line x1="300.0" y1="40.0" x2="210.0" y2="250.0" stroke="currentColor" stroke-width="1.2" stroke-dasharray="5 4"/>
<text x="210.0" y="272.0" font-size="12" text-anchor="middle" fill="currentColor">left camera centre</text>
<circle cx="235.7" cy="190" r="4" fill="#7ccf9a" stroke="currentColor"/>
<line x1="210.0" y1="250.0" x2="210.0" y2="182.0" stroke="currentColor" stroke-width="1.2" stroke-dasharray="2 3"/>
<circle cx="370" cy="250" r="5" fill="#9cc9ea" stroke="currentColor"/>
<line x1="315.0" y1="190.0" x2="425.0" y2="190.0" stroke="currentColor" stroke-width="1.8"/>
<line x1="300.0" y1="40.0" x2="370.0" y2="250.0" stroke="currentColor" stroke-width="1.2" stroke-dasharray="5 4"/>
<text x="370.0" y="272.0" font-size="12" text-anchor="middle" fill="currentColor">right camera centre</text>
<circle cx="350.0" cy="190" r="4" fill="#7ccf9a" stroke="currentColor"/>
<line x1="370.0" y1="250.0" x2="370.0" y2="182.0" stroke="currentColor" stroke-width="1.2" stroke-dasharray="2 3"/>
<text x="150.0" y="182.0" font-size="11" text-anchor="end" fill="currentColor">image plane</text>
<line x1="210.0" y1="288.0" x2="370.0" y2="288.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr182)" marker-start="url(#arr182)"/>
<text x="290.0" y="283.0" font-size="12" text-anchor="middle" fill="currentColor">baseline B</text>
<line x1="560.0" y1="40.0" x2="560.0" y2="250.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr182)" marker-start="url(#arr182)"/>
<text x="566.0" y="145.0" font-size="13" text-anchor="start" fill="currentColor">Z</text>
<line x1="470.0" y1="190.0" x2="470.0" y2="250.0" stroke="currentColor" stroke-width="1.2" marker-end="url(#arr182)" marker-start="url(#arr182)"/>
<text x="476.0" y="224.0" font-size="13" text-anchor="start" fill="currentColor">f</text>
<text x="120.0" y="70.0" font-size="12" text-anchor="middle" fill="currentColor">disparity d = x_L - x_R</text>
<text x="120.0" y="90.0" font-size="12" text-anchor="middle" fill="currentColor">similar triangles:</text>
<text x="120.0" y="110.0" font-size="13" text-anchor="middle" fill="currentColor" font-weight="bold">Z = f B / d</text>
</svg>
<figcaption>Figure 18.2. Stereo triangulation with two parallel cameras. The point P projects to x_L in the left image and x_R in the right; the disparity d = x_L - x_R satisfies d / f = B / Z by similar triangles, so Z = f B / d.</figcaption>
</figure>

**Rectification and the epipolar constraint.** With the two cameras parallel and side by side, a point's two images
lie on the same row: $y_L = y_R = fY/Z$. In general, the possible matches for a pixel in one image lie on a line in
the other (the **epipolar line**), a consequence of the geometry of two views (Hartley and Zisserman's book proves it).
Real stereo rigs are calibrated and their images **rectified** (resampled) so that epipolar lines become rows. Then
the search for a match is one-dimensional: along the same row.

### Matching by blocks

To find the disparity of a pixel, compare a small window around it in the left image with windows at shifts
$d = 0, 1, \dots, d_{\max}$ along the same row in the right image, and keep the shift with the smallest cost. A simple
cost is the **sum of absolute differences** (SAD) of the pixel values. Scharstein and Szeliski (2002) surveyed and
benchmarked the many refinements (other costs, smoothness between neighbouring pixels, sub-pixel estimates).

Block matching fails in known places:

- **texture-less surfaces** (smooth sand, a clear sky): every shift looks the same;
- **repetitive texture**: several shifts look equally good;
- **occlusions**: near a near object's side, some background visible to one camera is hidden from the other, so the
  pixel has no true match at all;
- **depth discontinuities**: a window straddling a near and a far surface has no single disparity.

The program builds a synthetic rectified pair: a random-dot textured terrain 8 m away and a rock 2 m away, with
$f = 200$ pixels and $B = 0.2$ m (illustrative numbers, not those of any flight camera). The true disparities are
$200 \times 0.2/8 = 5$ and $200 \times 0.2/2 = 20$ pixels. It then runs SAD block matching with 7×7 windows, using
2-D cumulative sums so that each window sum costs four additions.

```python
--8<-- "books/ai/ch18_stereo.py"
```

```
1. scene: far terrain at 8.0 m (disparity 5 px), rock at 2.0 m (disparity 20 px)
   f = 200 px, baseline B = 0.2 m, images 60 x 100, windows 7 x 7

2. block matching on 3456 interior pixels
   within 1 px of the true disparity: 0.940
   median disparity on the rock 20, on the terrain 5
   wrong pixels: 206, of which 206 lie near the rock's left or right side

3. row 30 of the disparity map (the rock covers columns 50..69; terrain at 35..49 is hidden from the right camera)
   column    33  36  39  42  45  48  51  54  57  60  63  66  69  72  75
   found      5   5  13  11  24  20  20  20  20  20  20  20  20   5   5
   true       5   5   5   5   5   5  20  20  20  20  20  20  20   5   5

4. depth on the rock: median 2.00 m; on the terrain: median 8.00 m

5. depth error for a 1-pixel disparity error, dZ = Z^2 / (f B)
    Z (m)  d (px)  dZ (m)
        1    40.0   0.025
        2    20.0   0.100
        4    10.0   0.400
        8     5.0   1.600
       16     2.5   6.400
```

94 percent of the interior pixels get the right disparity to within one pixel, and the medians give the right depths
(2.00 m and 8.00 m). All 206 wrong pixels lie near the rock's sides, and part 3 shows why: the terrain at columns 35
to 49 is hidden from the right camera by the rock, so its windows have no true match, and the matcher returns
nonsense (13, 11, 24) there. Real systems detect such pixels with a **left-right consistency check** (match right to
left as well and discard pixels where the two disagree) and mark them as unknown rather than guessing.

### How depth error grows with distance

**Theorem.** If the disparity is measured with an error $\delta d$, the depth error is approximately

$$
\delta Z \approx \frac{Z^2}{fB}\,\delta d.
$$

**Proof.** $Z = fB/d$, so $\frac{dZ}{dd} = -\frac{fB}{d^2} = -\frac{fB}{(fB/Z)^2} = -\frac{Z^2}{fB}$, and to first
order $|\delta Z| = |dZ/dd|\,\delta d$. $\square$

The error grows with the **square** of the distance (part 5: 2.5 cm at 1 m, 1.6 m at 8 m, 6.4 m at 16 m for a
1-pixel error with these numbers), and shrinks in proportion to the baseline and the focal length. This is why a
rover's stereo cameras give good 3-D maps of the next few metres and coarse ones far away, and why the hazard-avoidance
decisions of 18.7 are made on the near field. Sub-pixel matching (fitting a parabola to the costs around the best
shift) reduces $\delta d$ to a fraction of a pixel.

**Other ways to get depth.** One moving camera gives a baseline over time (**structure from motion**), at the price of
also estimating the motion, which leads to 18.4. Active sensors (laser scanners, called lidar, and structured light)
measure range directly. Networks trained on images with known depth can estimate depth from one image, from learned
cues such as size and texture gradients, but without the geometric guarantee of triangulation.

**On real rovers.** Curiosity and Perseverance carry pairs of navigation cameras (Navcams) on the mast and pairs of
hazard-avoidance cameras (Hazcams) on the body, all mounted as stereo pairs (Maki and colleagues describe them in
their 2012 and 2020 papers). Rover software computes 3-D range maps from these pairs and uses them to judge terrain
before and during drives, a line of work that goes back to JPL's stereo research for planetary rovers (Matthies,
1992; Goldberg, Maimone and Matthies, 2002).

## 18.3 Robots: sensors, actuators, kinematics

**The question:** what is a robot made of, and how do joint angles and wheel speeds become positions?

### Sensors and actuators

A **robot** is an agent with a physical body. Its **sensors** split into two kinds:

- **proprioceptive** sensors measure the robot itself: wheel and joint **encoders** (count rotations), an
  **inertial measurement unit** (IMU: accelerometers and gyroscopes, measuring acceleration and rotation rate),
  motor currents;
- **exteroceptive** sensors measure the world: cameras, lidar, sonar, contact and force sensors, GPS on Earth.

Its **actuators** produce motion: electric motors turning wheels or joints through gears, sometimes hydraulic or
pneumatic drives. The robot's **degrees of freedom** (DOF) are the number of independent numbers that fix its
configuration: a planar arm with two rotating joints has 2, a car on a plane has 3 (position $x, y$ and heading
$\theta$), a rigid body in space has 6. Mars rovers since Sojourner have used six wheels on a **rocker-bogie**
suspension that lets the wheels follow uneven ground and keep the body steady.

**Kinematics** relates the robot's internal variables (joint angles, wheel rotations) to positions in space, without
asking which forces cause the motion (that is **dynamics**).

### A two-link arm

Take an arm in a plane with a fixed base, a first link of length $L_1$ at angle $\theta_1$ from the horizontal, and a
second link of length $L_2$ at angle $\theta_2$ relative to the first (Figure 18.3). Adding the two link vectors gives
the **forward kinematics**, the position of the hand:

$$
x = L_1\cos\theta_1 + L_2\cos(\theta_1 + \theta_2), \qquad y = L_1\sin\theta_1 + L_2\sin(\theta_1 + \theta_2).
$$

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 520 300" role="img" aria-label="A two-link arm: from the base, link L1 at angle theta1 above the horizontal, then link L2 at angle theta2 relative to the direction of the first link, ending at the hand (x, y). The forward kinematics formulas are written beside it.">
<line x1="50.0" y1="250.0" x2="470.0" y2="250.0" stroke="currentColor" stroke-width="1.2" stroke-opacity="0.5"/>
<line x1="90" y1="250" x2="219.9" y2="175.0" stroke="#9cc9ea" stroke-width="10" stroke-linecap="round"/>
<line x1="219.9" y1="175.0" x2="219.9" y2="70.0" stroke="#eea66f" stroke-width="10" stroke-linecap="round"/>
<circle cx="90.0" cy="250.0" r="7" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="219.9" cy="175.0" r="7" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="219.9" cy="70.0" r="5" fill="currentColor"/>
<path d="M130,250 A40,40 0 0 0 124.6,230.0" fill="none" stroke="currentColor"/>
<text x="142.0" y="240.0" font-size="13" text-anchor="start" fill="currentColor">θ1</text>
<line x1="219.9" y1="175.0" x2="271.9" y2="145.0" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 4"/>
<path d="M249.3,158.0 A34,34 0 0 0 219.9,141.0" fill="none" stroke="currentColor"/>
<text x="255.9" y="145.0" font-size="13" text-anchor="start" fill="currentColor">θ2</text>
<text x="165.0" y="234.5" font-size="13" text-anchor="start" fill="currentColor">L1</text>
<text x="231.9" y="126.5" font-size="13" text-anchor="start" fill="currentColor">L2</text>
<text x="229.9" y="64.0" font-size="13" text-anchor="start" fill="currentColor">hand (x, y)</text>
<text x="90.0" y="272.0" font-size="12" text-anchor="middle" fill="currentColor">base</text>
<text x="300.0" y="60.0" font-size="12" text-anchor="start" fill="currentColor">x = L1 cos θ1 + L2 cos(θ1 + θ2)</text>
<text x="300.0" y="80.0" font-size="12" text-anchor="start" fill="currentColor">y = L1 sin θ1 + L2 sin(θ1 + θ2)</text>
</svg>
<figcaption>Figure 18.3. A planar two-link arm. The first angle is measured from the horizontal, the second from the direction of the first link (dashed). Adding the two link vectors gives the hand position.</figcaption>
</figure>

**Inverse kinematics** goes backwards: which angles put the hand at a target $(x, y)$? Here it has a closed form. The
base, the elbow and the hand form a triangle with sides $L_1$, $L_2$ and $\rho = \sqrt{x^2 + y^2}$, so by the law of
cosines

$$
\cos\theta_2 = \frac{x^2 + y^2 - L_1^2 - L_2^2}{2L_1L_2}.
$$

If the right side is outside $[-1, 1]$ the target is out of reach ($\rho > L_1 + L_2$ or $\rho < |L_1 - L_2|$).
Otherwise there are two solutions, $\theta_2 = \pm\arccos(\cdot)$, the elbow bent one way or the other, and then
$\theta_1 = \operatorname{atan2}(y, x) - \operatorname{atan2}(L_2\sin\theta_2,\, L_1 + L_2\cos\theta_2)$, the direction
to the target minus the angle the second link adds. Arms with more joints rarely have a closed form, and redundant
arms (more joints than needed) have infinitely many solutions.

### The Jacobian and singularities

The **Jacobian** $J$ is the matrix of partial derivatives of the hand position with respect to the joint angles. It
maps joint velocities to hand velocity, $\dot{p} = J\dot\theta$:

$$
J = \begin{pmatrix} -L_1\sin\theta_1 - L_2\sin(\theta_1 + \theta_2) & -L_2\sin(\theta_1 + \theta_2) \\ L_1\cos\theta_1 + L_2\cos(\theta_1 + \theta_2) & L_2\cos(\theta_1 + \theta_2) \end{pmatrix}.
$$

**Claim.** $\det J = L_1L_2\sin\theta_2$. **Proof.** Write $s_1 = \sin\theta_1$, $s_{12} = \sin(\theta_1 + \theta_2)$
and so on. Then $\det J = (-L_1s_1 - L_2s_{12})L_2c_{12} + L_2s_{12}(L_1c_1 + L_2c_{12})$. The $L_2^2$ terms cancel,
leaving $L_1L_2(s_{12}c_1 - s_1c_{12}) = L_1L_2\sin(\theta_1 + \theta_2 - \theta_1) = L_1L_2\sin\theta_2$. $\square$

So $J$ is singular exactly when $\theta_2 = 0$ or $\pi$: the arm is fully stretched or folded back. At a
**singularity** the hand cannot move in some direction however fast the joints turn (stretched out, it cannot move
outward), and near one, small hand motions need very large joint speeds. The Jacobian also gives a general iterative
inverse-kinematics method: repeat $\theta \leftarrow \theta + J^{\top}(JJ^{\top} + \lambda^2 I)^{-1}(p_{\text{target}} - p(\theta))$.
This is **damped least squares** (the Levenberg-Marquardt idea): Newton's method on the position error, with a small
$\lambda$ that keeps the step bounded near singularities.

### A wheeled rover

A **differential-drive** robot has two driven wheels a distance $b$ apart (plus passive wheels). If the left and right
wheels move at speeds $v_L$ and $v_R$, the robot's forward speed and turning rate are

$$
v = \frac{v_R + v_L}{2}, \qquad \omega = \frac{v_R - v_L}{b},
$$

because the centre moves at the average speed, and the difference of the wheel speeds, spread over the distance $b$
between them, is a rotation. The pose evolves by $\dot x = v\cos\theta$, $\dot y = v\sin\theta$, $\dot\theta = \omega$.
With constant wheel speeds the robot drives a circle of radius $v/\omega$. Equal speeds drive straight; opposite
speeds turn in place. Adding up these motions from encoder readings is **odometry** (or dead reckoning); wheel slip
makes its error grow without bound, which is why rovers check it with vision (18.7).

```python
--8<-- "books/ai/ch18_kinematics.py"
```

```
1. forward kinematics
   theta = (  0.0,    0.0) deg -> hand (+1.7000, +0.0000)
   theta = ( 90.0,    0.0) deg -> hand (+0.0000, +1.7000)
   theta = (  0.0,   90.0) deg -> hand (+1.0000, +0.7000)
   theta = ( 45.0,  -90.0) deg -> hand (+1.2021, +0.2121)

2. inverse kinematics for the target (1.2, 0.5)
   theta = (  -9.58,   81.79) deg -> check (1.2000, 0.5000)
   theta = (  54.82,  -81.79) deg -> check (1.2000, 0.5000)
   target (2.0, 0.0) is beyond L1 + L2 = 1.7: []

3. the Jacobian: det J = L1 L2 sin(theta2)
   theta2 =  90.0 deg: det J = +0.7000  (L1 L2 sin theta2 = +0.7000)
   theta2 =  30.0 deg: det J = +0.3500  (L1 L2 sin theta2 = +0.3500)
   theta2 =   0.0 deg: det J = +0.0000  (L1 L2 sin theta2 = +0.0000)

4. iterative IK, damped least squares: dtheta = J^T (J J^T + lambda^2 I)^-1 (target - fk)
   iteration 1: error 1.25e-01
   iteration 2: error 8.46e-03
   iteration 3: error 3.24e-04
   iteration 4: error 1.26e-05
   iteration 5: error 4.86e-07
   iteration 6: error 1.88e-08
   iteration 7: error 7.27e-10
   iteration 8: error 2.81e-11
   converged to (-9.58, 81.79) deg

5. differential drive: wheels 0.5 m apart; left 0.20 m/s, right 0.30 m/s for 10 s
   v = 0.250 m/s, omega = 0.200 rad/s, turning radius v/omega = 1.250 m
   integrated pose (1.1384, 1.7690, 114.59 deg)
   exact arc       (1.1366, 1.7702, 114.59 deg)
```

Part 1 checks the formulas at easy angles (stretched along $x$: $(1.7, 0)$; elbow at 90 degrees: $(1, 0.7)$). Part 2
gives both inverse solutions for $(1.2, 0.5)$, $\theta_2 = \pm 81.79$ degrees, and both reproduce the target exactly.
Part 3 confirms $\det J = L_1L_2\sin\theta_2$, zero at the stretched configuration. Part 4 converges to the first
solution in 8 steps; the error falls by a roughly constant factor per step rather than squaring, because the damping
term makes each step slightly shorter than Newton's. Part 5 integrates a gentle left turn for 10 s with 1000 small
steps and lands about 2 mm from the exact arc of radius 1.25 m.

## 18.4 Localization and mapping: the SLAM idea

*Level: advanced.*

**The question:** to know where it is, a robot needs a map; to build a map, it needs to know where it was each time it
looked. How can it do both at once?

[Chapter 13](13-Reasoning-over-Time.md) solved half of this. With a known map, a Kalman or particle filter tracks the
robot's pose from motion and sensor readings (**localization**; Monte Carlo localization is in
[Section 13.5](13-Reasoning-over-Time.md#135-particle-filters-and-robot-localization)). With known poses, building a
map is just recording what was seen where (**mapping**). **Simultaneous localization and mapping (SLAM)** estimates
both: the robot's path $x_{0:t}$ and the map $m$, from controls or odometry $u_{1:t}$ and observations $z_{1:t}$:

$$
P(x_{0:t}, m \mid z_{1:t}, u_{1:t}).
$$

The essential fact, made precise by Smith, Self and Cheeseman (1990), is that the errors in the robot's pose and in
the landmark positions are **correlated**: if the robot believes it is 1 m further east than it is, every landmark it
maps afterwards is also placed 1 m too far east. Treating them separately throws that information away. Keeping the
joint distribution means that when the robot recognises an old landmark and finds it "moved", it can correct the
whole path and all the landmarks seen since, at once. That event is a **loop closure**.

### The linear case is least squares

Assume the robot's heading is known, so that positions add linearly, and that all noise is Gaussian. Each odometry
reading says $x_{t+1} - x_t = u_t + \text{noise}$ with standard deviation $\sigma_u$; each landmark sighting says
$m_j - x_t = z + \text{noise}$ with $\sigma_z$; and we fix $x_0 = 0$ to remove the freedom of shifting everything (the
measurements are all relative). The likelihood of all the data is a product of Gaussians, so its logarithm is, up to
constants,

$$
-\frac{1}{2}\sum_t \frac{\lVert x_{t+1} - x_t - u_t\rVert^2}{\sigma_u^2} - \frac{1}{2}\sum_{(t, j)} \frac{\lVert m_j - x_t - z_{tj}\rVert^2}{\sigma_z^2}.
$$

Maximising it (with a flat prior this is also the most probable estimate, the MAP) is a **weighted least-squares**
problem: stack every measurement as a row of a matrix $A$ (a $+1$ and a $-1$ in the columns of the two unknowns
involved, divided by that measurement's $\sigma$), and solve $\min_\theta \lVert A\theta - b\rVert^2$ for the vector
$\theta$ of all poses and landmarks. The normal equations $A^{\top}A\,\theta = A^{\top}b$ have the **information
matrix** $A^{\top}A$, which is **sparse**: a pose is linked only to the poses just before and after it and to the
landmarks it saw. That sparsity is what makes large SLAM problems solvable; modern solvers factor the sparse matrix
instead of inverting a dense covariance.

With real robots the measurements are nonlinear (range and bearing, unknown heading), and the solution is found by
Gauss-Newton iterations, each one a linear problem of exactly this sparse form. This view of SLAM as a graph of poses
and constraints solved by optimisation began with Lu and Milios (1997) and is called **graph SLAM**. The earlier
**EKF-SLAM** keeps a Kalman filter over the pose and all landmarks, a dense covariance costing $O(n^2)$ per update for
$n$ landmarks; **FastSLAM** (Montemerlo and colleagues, 2002) uses particles for the path and small Kalman filters per
landmark.

The program drives a robot around a 10 m square, 1 m per step, with noisy odometry (0.15 m per step and axis) and a
sensor that measures the relative position of landmarks within 4.5 m (noise 0.05 m).

```python
--8<-- "books/ai/ch18_slam.py"
```

```
1. 41 poses, 8 landmarks, 40 odometry steps, 74 landmark sightings
   odometry noise 0.15 m per step and axis, landmark noise 0.05 m, sensor range 4.5 m

2. error of the estimated path (RMS over all poses) and of the final pose
   dead reckoning : path 0.426 m, final pose 0.859 m
   SLAM (all data): path 0.094 m, final pose 0.072 m, map 0.091 m
   SLAM without loop closure (no re-sighting of landmarks 0 and 7 after step 30):
                    path 0.191 m, final pose 0.713 m, map 0.099 m

3. the information matrix A^T A is 49 x 49 with 277 non-zero entries of 2401
   (each pose is linked only to its neighbours in time and to the landmarks it saw)

4. which landmarks each pose saw, every 5 steps
   pose  0 at (   0,   0): landmarks [0, 7]
   pose  5 at (   5,   0): landmarks [0, 1]
   pose 10 at (  10,   0): landmarks [1, 2]
   pose 15 at (  10,   5): landmarks [2, 3]
   pose 20 at (  10,  10): landmarks [3, 4]
   pose 25 at (   5,  10): landmarks [4, 5]
   pose 30 at (   0,  10): landmarks [5, 6]
   pose 35 at (   0,   5): landmarks [6, 7]
   pose 40 at (   0,   0): landmarks [0, 7]
```

Dead reckoning ends 0.86 m from where the robot really is (its starting point). The SLAM estimate of the whole path
has an RMS error 4.5 times smaller (0.094 m against 0.426 m), and its final pose is within 7 cm. Part 2's last line isolates the loop closure: remove the
sightings of the first two landmarks after step 30 (the robot coming home) and the final pose error goes back to
0.71 m, because nothing ties the end of the loop to its beginning. The map is good either way (each landmark was seen
from nearby poses), but the path is not. Part 3 shows the sparsity: 277 non-zero entries out of 2401. Figure 18.4
draws the three paths.

<figure class="mars-fig" markdown="0">
<svg viewBox="60 45 380 370" role="img" aria-label="A square loop with eight landmarks around it. The dotted true path is a 10 m square. The orange dead-reckoning path wanders and ends about 0.9 m from the start. The blue SLAM estimate lies almost on top of the true path, and the estimated landmarks sit inside the true landmark squares.">
<polyline points="140.0,330.0 162.0,330.0 184.0,330.0 206.0,330.0 228.0,330.0 250.0,330.0 272.0,330.0 294.0,330.0 316.0,330.0 338.0,330.0 360.0,330.0 360.0,308.0 360.0,286.0 360.0,264.0 360.0,242.0 360.0,220.0 360.0,198.0 360.0,176.0 360.0,154.0 360.0,132.0 360.0,110.0 338.0,110.0 316.0,110.0 294.0,110.0 272.0,110.0 250.0,110.0 228.0,110.0 206.0,110.0 184.0,110.0 162.0,110.0 140.0,110.0 140.0,132.0 140.0,154.0 140.0,176.0 140.0,198.0 140.0,220.0 140.0,242.0 140.0,264.0 140.0,286.0 140.0,308.0 140.0,330.0" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="2 3" stroke-opacity="0.7"/>
<polyline points="140.0,330.0 168.7,338.4 192.1,340.3 212.6,341.0 228.0,341.8 247.1,330.8 269.8,332.0 290.9,334.2 309.4,335.5 333.0,336.3 358.2,336.9 358.3,309.8 360.1,289.5 359.5,265.7 365.8,244.6 365.0,219.3 362.1,198.2 365.0,174.3 365.3,150.1 356.0,124.8 352.8,108.3 331.7,105.9 308.3,109.5 286.4,109.7 269.0,107.2 247.6,103.5 225.0,106.6 204.9,104.7 182.2,107.3 160.9,115.5 141.2,113.9 135.8,135.7 132.6,155.2 125.9,180.2 128.3,198.4 121.1,222.0 122.2,246.0 127.5,271.9 128.6,297.4 133.3,319.5 132.0,347.2" fill="none" stroke="#eea66f" stroke-width="2"/>
<polyline points="140.0,330.0 164.0,329.1 185.4,328.7 208.3,330.3 230.3,330.0 251.6,329.3 274.5,330.0 296.1,330.1 317.3,331.4 341.6,329.6 363.2,329.6 362.7,307.0 361.0,285.5 360.5,263.8 362.1,240.7 361.9,219.3 362.2,197.5 359.9,175.2 362.7,152.6 360.6,130.5 361.4,108.5 340.3,108.2 317.0,109.3 294.3,110.3 274.6,109.1 250.4,108.8 228.4,109.0 207.9,110.2 184.6,109.8 163.2,110.2 141.8,110.3 141.7,130.2 141.0,153.6 138.6,176.4 142.0,197.4 141.5,220.1 140.7,240.6 141.7,263.1 142.0,285.5 143.5,307.6 140.9,328.7" fill="none" stroke="#9cc9ea" stroke-width="2"/>
<rect x="179.0" y="369.0" width="10" height="10" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="186.1" cy="373.9" r="3" fill="currentColor"/>
<rect x="311.0" y="369.0" width="10" height="10" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="317.8" cy="373.3" r="3" fill="currentColor"/>
<rect x="399.0" y="281.0" width="10" height="10" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="407.0" cy="285.5" r="3" fill="currentColor"/>
<rect x="399.0" y="149.0" width="10" height="10" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="405.8" cy="153.4" r="3" fill="currentColor"/>
<rect x="311.0" y="61.0" width="10" height="10" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="317.1" cy="64.4" r="3" fill="currentColor"/>
<rect x="179.0" y="61.0" width="10" height="10" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="185.4" cy="64.5" r="3" fill="currentColor"/>
<rect x="91.0" y="149.0" width="10" height="10" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="96.8" cy="153.6" r="3" fill="currentColor"/>
<rect x="91.0" y="281.0" width="10" height="10" fill="#7ccf9a" stroke="currentColor"/>
<circle cx="97.1" cy="285.0" r="3" fill="currentColor"/>
<line x1="188.4" y1="162.8" x2="212.4" y2="162.8" stroke="currentColor" stroke-width="2" stroke-dasharray="2 3"/>
<text x="218.4" y="166.8" font-size="12" text-anchor="start" fill="currentColor">true path</text>
<line x1="188.4" y1="182.8" x2="212.4" y2="182.8" stroke="#eea66f" stroke-width="2"/>
<text x="218.4" y="186.8" font-size="12" text-anchor="start" fill="currentColor">dead reckoning</text>
<line x1="188.4" y1="202.8" x2="212.4" y2="202.8" stroke="#9cc9ea" stroke-width="2"/>
<text x="218.4" y="206.8" font-size="12" text-anchor="start" fill="currentColor">SLAM estimate</text>
<rect x="195.4" y="217.8" width="10" height="10" fill="#7ccf9a" stroke="currentColor"/>
<text x="218.4" y="226.8" font-size="12" text-anchor="start" fill="currentColor">landmark</text>
<circle cx="200.4" cy="242.8" r="3" fill="currentColor"/>
<text x="218.4" y="246.8" font-size="12" text-anchor="start" fill="currentColor">estimated landmark</text>
<text x="148.0" y="322.0" font-size="11" text-anchor="start" fill="currentColor">start and end</text>
<text x="124.0" y="365.2" font-size="11" text-anchor="start" fill="currentColor">dead reckoning ends here</text>
<circle cx="132.0" cy="347.2" r="4" fill="#eea66f" stroke="currentColor"/>
<text x="250.0" y="405.0" font-size="12" text-anchor="middle" fill="currentColor">a 10 m square, 1 m per step; grid units in metres</text>
</svg>
<figcaption>Figure 18.4. SLAM on the program's loop. Dead reckoning (orange) accumulates error and ends 0.86 m from home; the joint least-squares estimate (blue) of the path and the landmarks, using the loop closure at the end, stays within about 0.1 m of the truth.</figcaption>
</figure>

**What the toy leaves out.** The program knows which landmark each sighting belongs to. Real robots must decide
that (**data association**), and a wrong match, such as two similar rocks taken for the same one, can distort the
whole map; robust SLAM systems check loop closures before accepting them. Heading is uncertain and makes the problem
nonlinear. And the map may be dense (every surface point from stereo or lidar), not a few landmarks.
**Visual odometry**, estimating motion between consecutive camera frames by tracking features (18.1) and
triangulating them (18.2), is the short-range building block: it corrects wheel slip without building a lasting map.

## 18.5 Motion planning: configuration space, RRT (LaValle 1998), PRM

*Level: advanced.*

**The question:** a robot must get from here to there without hitting anything. How do we search for a path through
a continuous space, possibly with many dimensions?

### Configuration space

A **configuration** is a complete specification of the robot's position: for the two-link arm $(\theta_1, \theta_2)$,
for a car $(x, y, \theta)$, for a 7-joint arm seven angles. The set of all configurations is the **configuration
space** $\mathcal{C}$ (Lozano-Pérez, 1983), with one dimension per degree of freedom. The configurations where the
robot touches an obstacle form $\mathcal{C}_{\text{obs}}$; the rest is $\mathcal{C}_{\text{free}}$. Motion planning
becomes: find a continuous path in $\mathcal{C}_{\text{free}}$ from the start configuration to the goal. The robot,
however complicated its shape, is a **point** in $\mathcal{C}$.

**Example: a disc robot.** A round robot of radius $\rho$ that only translates has configuration $(x, y)$, its centre.
It touches an obstacle exactly when its centre is within distance $\rho$ of the obstacle. So
$\mathcal{C}_{\text{obs}}$ is the obstacle **grown** by $\rho$ in every direction (the Minkowski sum of the obstacle and
a disc of radius $\rho$); a circular rock of radius $r$ becomes a circle of radius $r + \rho$. For a robot that also
rotates, the growth depends on the angle and $\mathcal{C}_{\text{obs}}$ is a complicated 3-D shape, which is why one
usually does not compute it explicitly: one only asks "is this configuration free?" (a **collision check**) and "is
this straight segment free?".

**Why not a grid?** Chapter 4 planned rover paths with A\* on a grid, and for 2 or 3 dimensions that is excellent. But a
grid with $k$ cells per dimension has $k^D$ cells; for a 7-joint arm with 100 values per joint that is $10^{14}$. Exact
planning is hard in general: Reif (1979) proved that planning for a robot made of many independently moving parts
(the generalised "mover's problem") is PSPACE-hard. Practical planners for high dimensions give up completeness for
**sampling**.

### Probabilistic roadmaps

A **probabilistic roadmap (PRM)** (Kavraki, Švestka, Latombe and Overmars, 1996) works in two phases:

1. **Learn:** sample $n$ random free configurations; connect each to its $k$ nearest neighbours when the straight
   segment between them is free. This graph is the **roadmap**.
2. **Query:** add the start and goal, connect them in the same way, and run a shortest-path search on the graph
   ([Dijkstra's algorithm](../../graphs/dijkstra.md), or A\*).

The roadmap can answer many queries in the same environment, which suits a robot arm working in a fixed cell.

**Theorem (probabilistic completeness of PRM).** Suppose a path from start to goal exists with **clearance**
$\delta > 0$: every point of the path is at distance at least $\delta$ from $\mathcal{C}_{\text{obs}}$. Suppose the
roadmap joins every pair of samples (and the start and goal) that are at most $1.5\,\delta$ apart and whose
connecting segment is free. Then the probability that the roadmap contains no path from start to goal decreases
exponentially in the number of samples $n$.

**Proof.** Choose points $p_1 = \text{start}, p_2, \dots, p_m = \text{goal}$ along the path, consecutive ones at
most $\delta/2$ apart; for a path of length $\ell$ about $m \approx 2\ell/\delta$ suffice. Let $B_i$ be the ball
of radius $\delta/2$ around $p_i$. Suppose every $B_i$ contains a sample $q_i$ (take $q_1$ = start, $q_m$ = goal).

*The samples are close:* $\lVert q_i - q_{i+1}\rVert \le \delta/2 + \delta/2 + \delta/2 = 1.5\,\delta$.

*Their segment is free:* every point of the segment $p_ip_{i+1}$ (length at most $\delta/2$) is within $\delta/4$
of $p_i$ or $p_{i+1}$, so its clearance is at least $\delta - \delta/4 = 3\delta/4$. The distance to a convex set
(here the segment $p_ip_{i+1}$) is a convex function, so along the segment $q_iq_{i+1}$ it is at most its value at the
ends, which is at most $\delta/2$. So every point of $q_iq_{i+1}$ has clearance at least $3\delta/4 - \delta/2 > 0$.

Hence the roadmap contains the path $q_1, q_2, \dots, q_m$. It can fail only if some ball is empty. Let $\mu > 0$ be
the fraction of $\mathcal{C}$'s volume that one ball occupies. A uniform sample misses a given ball with probability
$1 - \mu$, all $n$ samples miss it with probability $(1 - \mu)^n$, and by the union bound over the $m$ balls

$$
P(\text{failure}) \le m(1 - \mu)^n \le m\,e^{-\mu n}. \qquad\square
$$

This is the argument of Kavraki, Kolountzakis and Latombe (1998). It also shows the weakness: $\mu$ is tiny for **narrow
passages** (small $\delta$, and the volume of a ball shrinks like $\delta^D$ in $D$ dimensions), so many samples are
needed exactly where the problem is hard. Sampling strategies that place more samples near obstacles address this.

### Rapidly-exploring random trees

An **RRT** (LaValle, 1998) grows a single tree from the start, suited to one-off queries and to robots whose motion is
constrained (a car cannot move sideways). Each iteration:

1. pick a random configuration $q_{\text{rand}}$ (with a small probability, the goal itself: **goal bias**);
2. find the tree node $q_{\text{near}}$ nearest to it;
3. **steer**: move from $q_{\text{near}}$ a fixed step toward $q_{\text{rand}}$, giving $q_{\text{new}}$;
4. if the segment from $q_{\text{near}}$ to $q_{\text{new}}$ is free, add $q_{\text{new}}$ to the tree with parent
   $q_{\text{near}}$;
5. stop when a new node can be joined to the goal.

Why does this explore rapidly? A node is selected for extension with probability equal to the volume of its
**Voronoi cell**, the region of space closer to it than to any other node. Nodes on the frontier of the tree, next to
large unexplored regions, have the largest cells, so the tree is pulled outward into empty space, the **Voronoi
bias**. RRTs are probabilistically complete (the probability of finding an existing path tends to 1 as the number of
iterations grows), but they are **not optimal**: the path is jagged and its length does not converge to the shortest.
Karaman and Frazzoli (2011) proved this and introduced RRT\*, which rewires the tree as it grows and is asymptotically
optimal. In practice, a cheap fix is **shortcutting**: repeatedly replace a stretch of the path by a straight segment
when that segment is free.

The program plans for a disc robot of radius 0.3 m among five circular rocks in a 10 m square, from $(1, 1)$ to
$(9, 9)$: the C-space obstacles are the rocks grown by 0.3 m, and collision checks are exact (the closest point of a
segment to a circle's centre).

```python
--8<-- "books/ai/ch18_motion.py"
```

```
straight-line distance start -> goal: 11.314 (blocked: True)

1. one RRT run (seed 1): 267 iterations, 119 tree nodes, path of 38 points
   path length 17.556; after shortcutting 14.562

2. RRT over 20 seeds
   solved 20 of 20; tree size mean 156; path length mean 17.64, min 16.18, max 19.35

3. PRM: 300 free samples, each tried against its 10 nearest neighbours
   seed 200: 1794 free edges, shortest roadmap path 14.801 with 19 points
   seed 201: 1788 free edges, shortest roadmap path 14.839 with 21 points
   seed 202: 1778 free edges, shortest roadmap path 14.847 with 19 points
```

The RRT found a path after 267 iterations with 119 nodes (many samples are rejected because the step lands in an
obstacle). Its path is 17.56 m, much longer than needed; shortcutting brings it to 14.56 m (Figure 18.5). Over 20
seeds the RRT always succeeds, with path lengths from 16.2 to 19.4 m: random and suboptimal, as the theory says. The
PRM, which keeps 300 samples and up to 10 connections each, finds paths of 14.80 to 14.85 m through its denser graph,
close to the shortcut RRT path, at the cost of about 1800 collision-checked edges.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 420 420" role="img" aria-label="A 10 m square with five circular rocks, each surrounded by a dashed circle 0.3 m larger. A light blue tree of short branches grows from the start at the lower left; a black jagged path through it reaches the goal at the upper right, and a green dashed shortcut path of three straight segments follows it more directly.">
<rect x="10" y="10" width="400" height="400" fill="none" stroke="currentColor"/>
<circle cx="210.0" cy="210.0" r="72.0" fill="none" stroke="currentColor" stroke-dasharray="3 3"/>
<circle cx="210.0" cy="210.0" r="60.0" fill="#eea66f" fill-opacity="0.55" stroke="currentColor"/>
<circle cx="130.0" cy="130.0" r="52.0" fill="none" stroke="currentColor" stroke-dasharray="3 3"/>
<circle cx="130.0" cy="130.0" r="40.0" fill="#eea66f" fill-opacity="0.55" stroke="currentColor"/>
<circle cx="290.0" cy="290.0" r="52.0" fill="none" stroke="currentColor" stroke-dasharray="3 3"/>
<circle cx="290.0" cy="290.0" r="40.0" fill="#eea66f" fill-opacity="0.55" stroke="currentColor"/>
<circle cx="310.0" cy="110.0" r="44.0" fill="none" stroke="currentColor" stroke-dasharray="3 3"/>
<circle cx="310.0" cy="110.0" r="32.0" fill="#eea66f" fill-opacity="0.55" stroke="currentColor"/>
<circle cx="110.0" cy="270.0" r="44.0" fill="none" stroke="currentColor" stroke-dasharray="3 3"/>
<circle cx="110.0" cy="270.0" r="32.0" fill="#eea66f" fill-opacity="0.55" stroke="currentColor"/>
<line x1="50.0" y1="370.0" x2="70.0" y2="369.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="70.0" y1="369.0" x2="79.0" y2="351.1" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="79.0" y1="351.1" x2="89.1" y2="333.9" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="89.1" y1="333.9" x2="103.2" y2="319.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="103.2" y1="319.7" x2="122.1" y2="313.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="122.1" y1="313.2" x2="141.2" y2="319.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="141.2" y1="319.2" x2="161.1" y2="316.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="161.1" y1="316.7" x2="173.8" y2="301.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="173.8" y1="301.3" x2="193.8" y2="300.5" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="193.8" y1="300.5" x2="211.9" y2="291.9" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="211.9" y1="291.9" x2="228.9" y2="302.5" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="161.1" y1="316.7" x2="169.7" y2="334.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="193.8" y1="300.5" x2="198.8" y2="300.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="173.8" y1="301.3" x2="167.5" y2="282.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="50.0" y1="370.0" x2="40.0" y2="352.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="167.5" y1="282.3" x2="154.0" y2="267.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="40.0" y1="352.7" x2="39.7" y2="332.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="228.9" y1="302.5" x2="243.5" y2="316.1" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="39.7" y1="332.7" x2="53.9" y2="328.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="198.8" y1="300.4" x2="204.0" y2="319.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="204.0" y1="319.7" x2="187.1" y2="326.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="39.7" y1="332.7" x2="30.4" y2="315.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="243.5" y1="316.1" x2="256.5" y2="331.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="70.0" y1="369.0" x2="64.6" y2="388.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="40.0" y1="352.7" x2="21.9" y2="361.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="30.4" y1="315.0" x2="28.7" y2="295.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="28.7" y1="295.0" x2="43.6" y2="281.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="50.0" y1="370.0" x2="34.7" y2="372.8" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="167.5" y1="282.3" x2="164.7" y2="274.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="169.7" y1="334.7" x2="173.3" y2="354.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="256.5" y1="331.3" x2="258.0" y2="351.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="173.3" y1="354.4" x2="188.8" y2="367.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="258.0" y1="351.3" x2="257.4" y2="371.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="258.0" y1="351.3" x2="277.5" y2="346.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="277.5" y1="346.7" x2="294.6" y2="357.1" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="257.4" y1="371.3" x2="244.0" y2="383.9" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="79.0" y1="351.1" x2="94.6" y2="354.9" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="28.7" y1="295.0" x2="18.9" y2="277.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="257.4" y1="371.3" x2="265.3" y2="389.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="28.7" y1="295.0" x2="42.0" y2="301.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="294.6" y1="357.1" x2="306.0" y2="340.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="243.5" y1="316.1" x2="226.5" y2="324.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="141.2" y1="319.2" x2="132.8" y2="337.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="18.9" y1="277.6" x2="19.5" y2="257.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="277.5" y1="346.7" x2="275.8" y2="345.8" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="306.0" y1="340.7" x2="325.9" y2="338.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="19.5" y1="257.6" x2="32.0" y2="242.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="325.9" y1="338.7" x2="332.8" y2="319.9" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="332.8" y1="319.9" x2="351.8" y2="326.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="34.7" y1="372.8" x2="25.4" y2="373.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="32.0" y1="242.0" x2="31.6" y2="222.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="228.9" y1="302.5" x2="215.4" y2="305.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="226.5" y1="324.7" x2="223.7" y2="344.5" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="94.6" y1="354.9" x2="88.9" y2="368.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="31.6" y1="222.0" x2="45.5" y2="207.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="45.5" y1="207.6" x2="49.5" y2="188.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="49.5" y1="188.0" x2="62.8" y2="173.1" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="94.6" y1="354.9" x2="98.4" y2="343.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="62.8" y1="173.1" x2="65.8" y2="153.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="21.9" y1="361.4" x2="10.8" y2="345.1" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="173.8" y1="301.3" x2="167.8" y2="294.9" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="351.8" y1="326.2" x2="359.9" y2="344.5" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="88.9" y1="368.4" x2="101.5" y2="384.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="294.6" y1="357.1" x2="305.1" y2="374.1" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="351.8" y1="326.2" x2="363.1" y2="327.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="65.8" y1="153.4" x2="65.3" y2="133.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="188.8" y1="367.0" x2="182.9" y2="386.1" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="305.1" y1="374.1" x2="309.8" y2="376.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="43.6" y1="281.7" x2="44.9" y2="261.8" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="359.9" y1="344.5" x2="358.7" y2="354.8" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="65.8" y1="153.4" x2="85.5" y2="157.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="43.6" y1="281.7" x2="62.3" y2="279.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="65.3" y1="133.4" x2="61.3" y2="113.8" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="61.3" y1="113.8" x2="71.6" y2="96.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="88.9" y1="368.4" x2="80.2" y2="381.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="34.7" y1="372.8" x2="37.6" y2="374.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="223.7" y1="344.5" x2="217.1" y2="358.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="71.6" y1="96.6" x2="90.7" y2="90.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="363.1" y1="327.0" x2="366.7" y2="307.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="366.7" y1="307.4" x2="367.9" y2="301.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="367.9" y1="301.2" x2="352.9" y2="288.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="101.5" y1="384.0" x2="104.6" y2="396.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="366.7" y1="307.4" x2="384.5" y2="316.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="173.3" y1="354.4" x2="158.6" y2="368.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="352.9" y1="288.0" x2="353.1" y2="268.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="353.1" y1="268.0" x2="354.6" y2="248.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="10.8" y1="345.1" x2="11.5" y2="325.1" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="89.1" y1="333.9" x2="73.4" y2="330.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="217.1" y1="358.6" x2="208.9" y2="370.8" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="354.6" y1="248.0" x2="352.3" y2="228.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="45.5" y1="207.6" x2="56.8" y2="200.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="352.3" y1="228.2" x2="353.6" y2="208.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="94.6" y1="354.9" x2="110.7" y2="365.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="353.6" y1="208.2" x2="351.8" y2="188.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="351.8" y1="188.3" x2="348.9" y2="168.5" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="90.7" y1="90.7" x2="100.8" y2="73.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="348.9" y1="168.5" x2="329.1" y2="165.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="348.9" y1="168.5" x2="352.3" y2="148.8" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="71.6" y1="96.6" x2="69.7" y2="76.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="358.7" y1="354.8" x2="375.5" y2="365.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="309.8" y1="376.4" x2="299.3" y2="393.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="352.3" y1="148.8" x2="355.8" y2="129.1" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="355.8" y1="129.1" x2="359.3" y2="109.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="69.7" y1="76.7" x2="51.8" y2="67.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="40.0" y1="352.7" x2="41.2" y2="354.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="32.0" y1="242.0" x2="50.2" y2="233.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="329.1" y1="165.6" x2="309.1" y2="164.5" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="62.8" y1="173.1" x2="44.9" y2="164.4" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="62.8" y1="173.1" x2="66.7" y2="172.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="100.8" y1="73.4" x2="92.4" y2="55.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="359.3" y1="109.4" x2="362.9" y2="89.7" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="354.6" y1="248.0" x2="334.7" y2="249.3" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="375.5" y1="365.6" x2="379.7" y2="381.5" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="362.9" y1="89.7" x2="375.4" y2="74.2" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="384.5" y1="316.6" x2="399.4" y2="303.8" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="379.7" y1="381.5" x2="372.1" y2="400.0" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="375.4" y1="74.2" x2="371.0" y2="54.6" stroke="#9cc9ea" stroke-width="1.2"/>
<line x1="371.0" y1="54.6" x2="370.0" y2="50.0" stroke="#9cc9ea" stroke-width="1.2"/>
<polyline points="50.0,370.0 70.0,369.0 79.0,351.1 89.1,333.9 103.2,319.7 122.1,313.2 141.2,319.2 161.1,316.7 173.8,301.3 193.8,300.5 211.9,291.9 228.9,302.5 243.5,316.1 256.5,331.3 258.0,351.3 277.5,346.7 294.6,357.1 306.0,340.7 325.9,338.7 332.8,319.9 351.8,326.2 363.1,327.0 366.7,307.4 367.9,301.2 352.9,288.0 353.1,268.0 354.6,248.0 352.3,228.2 353.6,208.2 351.8,188.3 348.9,168.5 352.3,148.8 355.8,129.1 359.3,109.4 362.9,89.7 375.4,74.2 371.0,54.6 370.0,50.0" fill="none" stroke="currentColor" stroke-width="2.2"/>
<polyline points="50.0,370.0 306.0,340.7 351.8,326.2 370.0,50.0" fill="none" stroke="#7ccf9a" stroke-width="3" stroke-dasharray="7 4"/>
<circle cx="50" cy="370" r="6" fill="#7ccf9a" stroke="currentColor"/>
<text x="60.0" y="386.0" font-size="12" text-anchor="start" fill="currentColor">start</text>
<circle cx="370" cy="50" r="6" fill="#7ccf9a" stroke="currentColor"/>
<text x="366.0" y="38.0" font-size="12" text-anchor="end" fill="currentColor">goal</text>
</svg>
<figcaption>Figure 18.5. The RRT of part 1 (seed 1): 119 tree nodes (blue), the found path of 17.56 m (black) and the shortcut path of 14.56 m (green, dashed). Dashed circles are the C-space obstacles, the rocks grown by the robot's radius.</figcaption>
</figure>

## 18.6 Control: PID from scratch

**The question:** the planner says "be at this point". The motors take force commands, and the world pushes back
(friction, slopes, loads). How do we compute the command that gets us there and keeps us there?

### Open loop and closed loop

**Open-loop** control computes the commands in advance ("full power for 2 s") and hopes. Any error in the model, such
as an unexpected slope, goes uncorrected. **Closed-loop** or **feedback** control measures the result and corrects it
continuously: the command is a function of the **error** $e(t) = x_{\text{target}} - x(t)$. This is the reflex agent of
Chapter 2, running fast.

The **PID controller** combines three terms:

$$
u(t) = K_p\,e(t) + K_i\int_0^t e(s)\,ds + K_d\,\frac{de}{dt}.
$$

- **Proportional:** push in proportion to how far off we are.
- **Integral:** push in proportion to the accumulated past error, so a small error that persists keeps growing the
  command.
- **Derivative:** push against the rate of change, damping the motion before it overshoots. (With a fixed target,
  $de/dt = -\dot x$; using $-K_d\dot x$ avoids a huge "kick" at the moment the target jumps.)

The idea is old: Minorsky analysed three-term control for automatic ship steering in 1922, and Ziegler and Nichols
(1942) gave tuning rules still taught today.

### The plant and three facts

Our "plant" (the system being controlled) is a cart of mass 1 with friction $c$, on a slope that pulls it back with a
constant force $g$:

$$
\ddot x = u - c\,\dot x - g.
$$

**Fact 1: proportional control alone stops short.** With $u = K_p e$, at rest ($\dot x = \ddot x = 0$) we need
$0 = K_p(x_{\text{target}} - x) - g$, so the cart settles at error $e_\infty = g/K_p$. A stronger gain shrinks the error
but never removes it, and (Fact 3) makes oscillation worse.

**Fact 2: the integral term removes constant errors.** If the closed loop with integral action settles to rest at all,
then the integral's rate of change, which is $e$ itself, must be zero there; otherwise the integral, and with it the
command, would keep growing, and the system would not be at rest. So any steady state has $e = 0$, whatever the
constant disturbance. The integral automatically finds the force $g$ needed to hold the cart on the slope.

**Fact 3: stability is decided by a polynomial.** Write $z = \int e$; around the target, with $\dot e = -\dot x$, the
closed loop with PID (derivative on the measurement) satisfies
$\dddot{z} + (c + K_d)\ddot z + K_p\dot z + K_i z = \text{constant}$, a linear differential equation whose solutions
are sums of $e^{st}$ with $s$ the roots of the **characteristic polynomial**

$$
s^3 + (c + K_d)\,s^2 + K_p\,s + K_i.
$$

The error dies out exactly when every root has negative real part. For a cubic $s^3 + a_2 s^2 + a_1 s + a_0$ the
**Routh-Hurwitz criterion** says this holds if and only if all $a_i > 0$ and $a_2 a_1 > a_0$ (a standard result; see
Åström and Murray). Here: $(c + K_d)K_p > K_i$. Too much integral gain makes the loop unstable. With $K_i = 0$
(PD) the polynomial is $s^2 + (c + K_d)s + K_p$, stable whenever both coefficients are positive, with damping ratio
$\zeta = (c + K_d)/(2\sqrt{K_p})$: below 1 it oscillates, at or above 1 it does not. With P alone, $c = 0.5$ and
$K_p = 4$, $\zeta = 0.5/4 = 0.125$: strong oscillation.

```python
--8<-- "books/ai/ch18_pid.py"
```

```
1. step from x = 0 to x = 1 m against the slope (2% settling band)
   controller                 overshoot  settles at  final error
   P   (kp 4)                     46.4%       never       0.1209
   PD  (kp 4, kd 3)                0.0%       never       0.1250
   PID (kp 4, ki 2, kd 3)         22.7%      5.57 s      -0.0000
   PID (kp 4, ki 20, kd 3)       950.6%       never      -9.5058
   P alone stops short by g / kp = 0.1250 m

2. Routh-Hurwitz test for s^3 + (c + kd) s^2 + kp s + ki: stable iff (c + kd) kp > ki
   ki =  2: (c + kd) kp = 14.0 > 2  -> stable; largest real part of the roots -0.750
   ki = 20: (c + kd) kp = 14.0 < 20  -> unstable; largest real part of the roots +0.161

3. position at selected times
   t (s)         P      PD     PID
     0.5     0.372   0.246   0.272
     1.0     1.071   0.563   0.687
     2.0     1.283   0.840   1.165
     3.0     0.501   0.877   1.217
     5.0     1.110   0.875   1.048
     8.0     0.994   0.875   0.994
    15.0     0.879   0.875   1.000

4. the motor saturates at |u| <= 1.5: integrator windup
   PID, plain integrator: overshoot  33.8%, settles at 6.04 s, final error -0.0000
   PID, with clamping   : overshoot  12.2%, settles at 5.83 s, final error -0.0000
```

Each fact appears in the output (Figure 18.6):

- **P** oscillates (46 percent overshoot, $\zeta = 0.125$) and settles 0.125 m short, exactly $g/K_p$; it never
  enters the 2 percent band around the target.
- **PD** has no overshoot ($\zeta = 3.5/4 = 0.875$) but stops at the same 0.125 m short: damping does not remove the
  steady error.
- **PID** with $K_i = 2$ reaches the target exactly (the final error prints as −0.0000, a residue below 0.00005)
  and settles in 5.6 s; the integral costs some overshoot (22.7 percent).
- **PID** with $K_i = 20$ violates $(c + K_d)K_p = 14 > K_i$ and the oscillation grows; numpy's root finder confirms a
  root with real part +0.161.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 300" role="img" aria-label="Position against time for 15 seconds. The P controller rises to 1.46, swings down to about 0.5, and oscillates with decreasing amplitude around 0.875. The PD controller rises smoothly to 0.875 and stays there. The PID controller overshoots to about 1.23 and settles at the target 1.">
<line x1="60.0" y1="250.0" x2="560.0" y2="250.0" stroke="currentColor" stroke-width="1.2"/>
<line x1="60.0" y1="250.0" x2="60.0" y2="40.0" stroke="currentColor" stroke-width="1.2"/>
<line x1="56.0" y1="250.0" x2="60.0" y2="250.0" stroke="currentColor" stroke-width="1.2"/>
<text x="52.0" y="254.0" font-size="11" text-anchor="end" fill="currentColor">0</text>
<line x1="56.0" y1="180.0" x2="60.0" y2="180.0" stroke="currentColor" stroke-width="1.2"/>
<text x="52.0" y="184.0" font-size="11" text-anchor="end" fill="currentColor">0.5</text>
<line x1="56.0" y1="110.0" x2="60.0" y2="110.0" stroke="currentColor" stroke-width="1.2"/>
<text x="52.0" y="114.0" font-size="11" text-anchor="end" fill="currentColor">1</text>
<line x1="56.0" y1="40.0" x2="60.0" y2="40.0" stroke="currentColor" stroke-width="1.2"/>
<text x="52.0" y="44.0" font-size="11" text-anchor="end" fill="currentColor">1.5</text>
<line x1="60.0" y1="250.0" x2="60.0" y2="254.0" stroke="currentColor" stroke-width="1.2"/>
<text x="60.0" y="268.0" font-size="11" text-anchor="middle" fill="currentColor">0</text>
<line x1="160.0" y1="250.0" x2="160.0" y2="254.0" stroke="currentColor" stroke-width="1.2"/>
<text x="160.0" y="268.0" font-size="11" text-anchor="middle" fill="currentColor">3</text>
<line x1="260.0" y1="250.0" x2="260.0" y2="254.0" stroke="currentColor" stroke-width="1.2"/>
<text x="260.0" y="268.0" font-size="11" text-anchor="middle" fill="currentColor">6</text>
<line x1="360.0" y1="250.0" x2="360.0" y2="254.0" stroke="currentColor" stroke-width="1.2"/>
<text x="360.0" y="268.0" font-size="11" text-anchor="middle" fill="currentColor">9</text>
<line x1="460.0" y1="250.0" x2="460.0" y2="254.0" stroke="currentColor" stroke-width="1.2"/>
<text x="460.0" y="268.0" font-size="11" text-anchor="middle" fill="currentColor">12</text>
<line x1="560.0" y1="250.0" x2="560.0" y2="254.0" stroke="currentColor" stroke-width="1.2"/>
<text x="560.0" y="268.0" font-size="11" text-anchor="middle" fill="currentColor">15</text>
<line x1="60.0" y1="110.0" x2="560.0" y2="110.0" stroke="currentColor" stroke-width="1.2" stroke-dasharray="4 4" stroke-opacity="0.6"/>
<text x="560.0" y="104.0" font-size="11" text-anchor="end" fill="currentColor">target 1 m</text>
<polyline points="60.0,250.0 63.4,247.5 66.7,240.5 70.0,229.4 73.4,214.9 76.7,197.7 80.0,178.7 83.4,158.5 86.7,138.1 90.0,118.4 93.4,99.9 96.7,83.4 100.0,69.4 103.4,58.4 106.7,50.6 110.0,46.2 113.4,45.1 116.7,47.3 120.0,52.5 123.4,60.4 126.7,70.5 130.0,82.3 133.4,95.3 136.7,109.0 140.0,122.6 143.4,135.8 146.7,148.1 150.0,158.9 153.4,168.0 156.7,175.1 160.0,179.9 163.4,182.5 166.7,182.9 170.0,181.0 173.4,177.2 176.7,171.6 180.0,164.6 183.4,156.5 186.7,147.6 190.0,138.4 193.4,129.2 196.7,120.4 200.0,112.3 203.4,105.2 206.7,99.3 210.0,94.8 213.4,91.8 216.7,90.3 220.0,90.3 223.4,91.8 226.7,94.6 230.0,98.6 233.4,103.4 236.7,109.0 240.0,115.0 243.4,121.2 246.7,127.4 250.0,133.2 253.4,138.6 256.7,143.2 260.0,147.0 263.4,149.9 266.7,151.8 270.0,152.6 273.4,152.4 276.7,151.3 280.0,149.2 283.4,146.5 286.7,143.1 290.0,139.3 293.4,135.2 296.7,131.0 300.0,126.9 303.4,123.0 306.7,119.5 310.0,116.4 313.4,114.0 316.7,112.2 320.0,111.0 323.4,110.6 326.7,110.8 330.0,111.7 333.4,113.2 336.7,115.1 340.0,117.4 343.4,120.0 346.7,122.8 350.0,125.6 353.4,128.4 356.7,130.9 360.0,133.3 363.4,135.3 366.7,136.8 370.0,138.0 373.4,138.7 376.7,138.9 380.0,138.7 383.4,138.0 386.7,137.0 390.0,135.6 393.4,134.0 396.7,132.2 400.0,130.3 403.4,128.5 406.7,126.6 410.0,124.9 413.4,123.4 416.7,122.1 420.0,121.1 423.4,120.3 426.7,119.9 430.0,119.8 433.4,120.0 436.7,120.5 440.0,121.3 443.4,122.2 446.7,123.3 450.0,124.5 453.4,125.8 456.7,127.1 460.0,128.3 463.4,129.4 466.7,130.4 470.0,131.3 473.4,131.9 476.7,132.4 480.0,132.6 483.4,132.6 486.7,132.5 490.0,132.1 493.4,131.6 496.7,130.9 500.0,130.2 503.4,129.4 506.7,128.5 510.0,127.6 513.4,126.8 516.7,126.1 520.0,125.4 523.4,124.9 526.7,124.5 530.0,124.2 533.4,124.0 536.7,124.0 540.0,124.2 543.4,124.4 546.7,124.8 550.0,125.3 553.4,125.8 556.7,126.3" fill="none" stroke="#eea66f" stroke-width="2.4"/>
<polyline points="60.0,250.0 63.4,247.8 66.7,242.1 70.0,234.3 73.4,225.2 76.7,215.5 80.0,205.7 83.4,196.1 86.7,187.1 90.0,178.7 93.4,171.1 96.7,164.3 100.0,158.2 103.4,152.9 106.7,148.4 110.0,144.4 113.4,141.1 116.7,138.3 120.0,135.9 123.4,134.0 126.7,132.4 130.0,131.1 133.4,130.1 136.7,129.3 140.0,128.7 143.4,128.2 146.7,127.8 150.0,127.6 153.4,127.4 156.7,127.2 160.0,127.2 163.4,127.1 166.7,127.1 170.0,127.1 173.4,127.1 176.7,127.1 180.0,127.2 183.4,127.2 186.7,127.2 190.0,127.3 193.4,127.3 196.7,127.3 200.0,127.3 203.4,127.4 206.7,127.4 210.0,127.4 213.4,127.4 216.7,127.4 220.0,127.4 223.4,127.5 226.7,127.5 230.0,127.5 233.4,127.5 236.7,127.5 240.0,127.5 243.4,127.5 246.7,127.5 250.0,127.5 253.4,127.5 256.7,127.5 260.0,127.5 263.4,127.5 266.7,127.5 270.0,127.5 273.4,127.5 276.7,127.5 280.0,127.5 283.4,127.5 286.7,127.5 290.0,127.5 293.4,127.5 296.7,127.5 300.0,127.5 303.4,127.5 306.7,127.5 310.0,127.5 313.4,127.5 316.7,127.5 320.0,127.5 323.4,127.5 326.7,127.5 330.0,127.5 333.4,127.5 336.7,127.5 340.0,127.5 343.4,127.5 346.7,127.5 350.0,127.5 353.4,127.5 356.7,127.5 360.0,127.5 363.4,127.5 366.7,127.5 370.0,127.5 373.4,127.5 376.7,127.5 380.0,127.5 383.4,127.5 386.7,127.5 390.0,127.5 393.4,127.5 396.7,127.5 400.0,127.5 403.4,127.5 406.7,127.5 410.0,127.5 413.4,127.5 416.7,127.5 420.0,127.5 423.4,127.5 426.7,127.5 430.0,127.5 433.4,127.5 436.7,127.5 440.0,127.5 443.4,127.5 446.7,127.5 450.0,127.5 453.4,127.5 456.7,127.5 460.0,127.5 463.4,127.5 466.7,127.5 470.0,127.5 473.4,127.5 476.7,127.5 480.0,127.5 483.4,127.5 486.7,127.5 490.0,127.5 493.4,127.5 496.7,127.5 500.0,127.5 503.4,127.5 506.7,127.5 510.0,127.5 513.4,127.5 516.7,127.5 520.0,127.5 523.4,127.5 526.7,127.5 530.0,127.5 533.4,127.5 536.7,127.5 540.0,127.5 543.4,127.5 546.7,127.5 550.0,127.5 553.4,127.5 556.7,127.5" fill="none" stroke="#9cc9ea" stroke-width="2.4"/>
<polyline points="60.0,250.0 63.4,247.7 66.7,241.8 70.0,233.3 73.4,223.1 76.7,211.8 80.0,199.9 83.4,187.9 86.7,176.1 90.0,164.6 93.4,153.7 96.7,143.4 100.0,133.9 103.4,125.3 106.7,117.4 110.0,110.4 113.4,104.2 116.7,98.8 120.0,94.1 123.4,90.1 126.7,86.8 130.0,84.1 133.4,82.0 136.7,80.4 140.0,79.3 143.4,78.6 146.7,78.2 150.0,78.2 153.4,78.4 156.7,78.9 160.0,79.7 163.4,80.5 166.7,81.6 170.0,82.7 173.4,83.9 176.7,85.2 180.0,86.6 183.4,88.0 186.7,89.3 190.0,90.7 193.4,92.1 196.7,93.4 200.0,94.7 203.4,96.0 206.7,97.2 210.0,98.4 213.4,99.5 216.7,100.5 220.0,101.5 223.4,102.5 226.7,103.3 230.0,104.2 233.4,104.9 236.7,105.6 240.0,106.3 243.4,106.8 246.7,107.4 250.0,107.9 253.4,108.3 256.7,108.7 260.0,109.0 263.4,109.3 266.7,109.6 270.0,109.9 273.4,110.1 276.7,110.2 280.0,110.4 283.4,110.5 286.7,110.6 290.0,110.7 293.4,110.8 296.7,110.8 300.0,110.8 303.4,110.9 306.7,110.9 310.0,110.9 313.4,110.9 316.7,110.9 320.0,110.8 323.4,110.8 326.7,110.8 330.0,110.8 333.4,110.7 336.7,110.7 340.0,110.6 343.4,110.6 346.7,110.6 350.0,110.5 353.4,110.5 356.7,110.5 360.0,110.4 363.4,110.4 366.7,110.3 370.0,110.3 373.4,110.3 376.7,110.3 380.0,110.2 383.4,110.2 386.7,110.2 390.0,110.2 393.4,110.1 396.7,110.1 400.0,110.1 403.4,110.1 406.7,110.1 410.0,110.1 413.4,110.0 416.7,110.0 420.0,110.0 423.4,110.0 426.7,110.0 430.0,110.0 433.4,110.0 436.7,110.0 440.0,110.0 443.4,110.0 446.7,110.0 450.0,110.0 453.4,110.0 456.7,110.0 460.0,110.0 463.4,110.0 466.7,110.0 470.0,110.0 473.4,110.0 476.7,110.0 480.0,110.0 483.4,110.0 486.7,110.0 490.0,110.0 493.4,110.0 496.7,110.0 500.0,110.0 503.4,110.0 506.7,110.0 510.0,110.0 513.4,110.0 516.7,110.0 520.0,110.0 523.4,110.0 526.7,110.0 530.0,110.0 533.4,110.0 536.7,110.0 540.0,110.0 543.4,110.0 546.7,110.0 550.0,110.0 553.4,110.0 556.7,110.0" fill="none" stroke="#7ccf9a" stroke-width="2.4"/>
<line x1="400" y1="173.0" x2="422" y2="173.0" stroke="#eea66f" stroke-width="2.4"/>
<text x="428.0" y="177.0" font-size="11" text-anchor="start" fill="currentColor">P: oscillates, stops short</text>
<line x1="400" y1="191.0" x2="422" y2="191.0" stroke="#9cc9ea" stroke-width="2.4"/>
<text x="428.0" y="195.0" font-size="11" text-anchor="start" fill="currentColor">PD: no overshoot, stops short</text>
<line x1="400" y1="209.0" x2="422" y2="209.0" stroke="#7ccf9a" stroke-width="2.4"/>
<text x="428.0" y="213.0" font-size="11" text-anchor="start" fill="currentColor">PID: reaches the target</text>
<text x="310.0" y="288.0" font-size="12" text-anchor="middle" fill="currentColor">time (s)</text>
<text x="18.0" y="140.0" font-size="12" text-anchor="middle" fill="currentColor" transform="rotate(-90 18 140)">position (m)</text>
</svg>
<figcaption>Figure 18.6. Step responses from the program (every 0.1 s). P oscillates and settles 0.125 m short; PD is well damped but stops at the same place; PID reaches the target, paying for it with some overshoot.</figcaption>
</figure>

**Windup.** Real motors have a maximum force. While the command is saturated, the error stays large and the integral
keeps growing; when the cart finally arrives, the oversized integral pushes it far past the target. Part 4 limits the
force to 1.5: the plain integrator overshoots 33.8 percent, while **clamping** (not integrating while saturated) cuts
the overshoot to 12.2 percent. Every practical PID implementation has some such anti-windup rule.

PID is a reflex. It has no model of the future and cannot plan; it is good at holding a set-point against unknown
steady disturbances, which is why it is everywhere, from motor drivers to thermostats. Controllers that do use a
model, such as **model predictive control** (solve a short planning problem at every step, apply the first command,
repeat), connect control to the planning chapters of this book.

<figure class="play" data-play="pid"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> A PID controller driving a rover 10 m up a slope (a made-up model). With P alone it stops short; add I to close the gap, D to calm the overshoot.</figcaption></figure>

## 18.7 Autonomy on Mars

**The question:** what does all this look like on a real robot that no one can steer in real time?

As [Section 2.6](02-Intelligent-Agents.md#26-autonomy-with-long-delays-why-a-mars-rover-must-decide-for-itself)
explained, radio signals take about 3 to 22 minutes one way between Earth and Mars, depending on where the two
planets are in their orbits, and commands are usually sent once per Martian day. A rover cannot be driven with a
joystick; it must close its own perception-action loops. The facts below come from NASA and JPL publications listed at
the end; where a figure is not given there, we leave it out.

**Seeing and judging the ground (18.1, 18.2).** Curiosity and Perseverance carry stereo Navcams and Hazcams (Maki
and colleagues, 2012 and 2020). In autonomous navigation the rover takes stereo images, computes a 3-D map of the
terrain ahead, rates patches of ground by slope, step height and roughness, and evaluates candidate paths toward a
goal that the team on Earth has chosen. This lineage goes back to JPL's stereo navigation software on the Mars
Exploration Rovers Spirit and Opportunity (Goldberg, Maimone and Matthies, 2002). Perseverance's enhanced AutoNav,
with dedicated hardware for image processing, plans while driving rather than stopping to think between short
segments, which Verma and colleagues (2023) describe as substantially increasing how far it can travel in a sol.
Planning over the rated terrain is the cost-based search of [Chapter 4](04-Heuristic-Search.md#46-path-planning-on-a-mars-like-terrain-grid).

**Knowing where it is (18.3, 18.4).** Wheel odometry on loose sand and slopes slips. On Spirit and Opportunity,
**visual odometry** tracked features between stereo image pairs taken before and after short moves to measure the
rover's true motion and correct the wheel estimate; Maimone, Cheng and Matthies (2007) report on its first two years
of use, including on slopes where slip was severe. This is the local, short-range part of the SLAM problem of 18.4.

**Choosing what to look at (18.1).** AEGIS (Autonomous Exploration for Gathering Increased Science) finds rocks in
the rover's own images after a drive, ranks them by criteria the scientists set (such as size and brightness), and
points an instrument at the best target without waiting for Earth. It was first used on Opportunity in 2010 (Estlin
and colleagues, 2012), deployed on Curiosity in 2016 to choose targets for the ChemCam laser spectrometer (Francis and
colleagues, 2017), and is used on Perseverance with SuperCam. In this chapter's terms it is edge and region detection
followed by a scoring rule.

**Landing by vision.** During its descent in February 2021, Perseverance used **terrain-relative navigation**: it took
images of the ground, matched features in them against a map made beforehand from orbital images, and used the
resulting position to choose a safe touchdown spot within its reach. It is feature matching (18.1) used for
localization (18.4).

**Flying by vision.** The Ingenuity helicopter, carried by Perseverance, made the first powered, controlled flight on
another planet on 19 April 2021 and flew 72 times before damage to its rotor blades ended its mission in January 2024.
Its navigation combined an IMU, a laser rangefinder for height and a downward-looking camera whose images it tracked
for features to estimate its motion, under the simplifying assumption that the ground is roughly flat (Bayard and
colleagues, 2019, describe the design). The vision system mattered in both of its best-known incidents. On its sixth
flight, JPL reported that one navigation image was lost, after which images were matched with the wrong times, and
the helicopter swayed in flight before landing safely. After the final flight, NASA's investigation concluded that the
most likely cause was that the navigation system could not track enough surface features over smooth, featureless
sand ripples, the failure case of 18.1 (no texture, no corners) appearing in flight.

**What is not autonomous.** The scientists choose the destinations and what counts as interesting; engineers plan
much of each day's activity on Earth and check it in simulation. Onboard autonomy fills in what cannot wait for the
next communication window: where exactly to put the wheels, how far the rover really moved, which rock to zap now.
Every piece is a technique from this chapter, made robust enough to run where no one can fix it.

## In practice

OpenCV provides Sobel and Canny filters, Harris corners, SIFT and stereo block matching; the Open Motion Planning
Library (OMPL) provides PRM, RRT, RRT\* and many variants; ROS connects sensors, estimators and controllers on real
robots; graph-SLAM back ends such as g2o and GTSAM solve the sparse least-squares problems of 18.4 at scale.

## Check yourself

??? question "1. Apply the Sobel filters S_x and S_y (with the factor 1/8) to the 3x3 patch whose rows are (0.2, 0.2, 0.9), (0.2, 0.2, 0.9), (0.2, 0.2, 0.9). What are the gradient magnitude and direction?"

    $S_x$: the left column (weights −1, −2, −1) sums to $-4 \times 0.2 = -0.8$, the right column (1, 2, 1) to
    $4 \times 0.9 = 3.6$; total $2.8/8 = 0.35$. $S_y$: each row has the same values, so the top row (weights −1, −2,
    −1 on 0.2, 0.2, 0.9) and the bottom row (1, 2, 1 on the same values) cancel: 0. Magnitude 0.35, direction
    $\operatorname{atan2}(0, 0.35) = 0$: pointing to the right, across a vertical edge, toward the brighter side.

??? question "2. For a window on a perfectly straight vertical edge, I_y = 0 everywhere and I_x is non-zero. What are the structure tensor's eigenvalues, and what are det M, trace M and the Harris score R?"

    $M = \begin{pmatrix} \sum I_x^2 & 0 \\ 0 & 0 \end{pmatrix}$, so $\lambda_1 = \sum I_x^2 > 0$ and $\lambda_2 = 0$.
    $\det M = 0$, $\operatorname{tr} M = \lambda_1$, and $R = 0 - k\lambda_1^2 < 0$. Harris scores are negative on
    edges, near zero on flat regions and positive on corners, which is why thresholding $R > 0$ (or at a positive
    fraction of its maximum, as in the program) keeps only corners.

??? question "3. A stereo camera has f = 1000 pixels and B = 0.4 m. A rock shows a disparity of 25 pixels. How far is it, and what is the depth error for a matching error of 0.25 pixels?"

    $Z = fB/d = 1000 \times 0.4/25 = 16$ m. $\delta Z \approx Z^2\delta d/(fB) = 256 \times 0.25/400 = 0.16$ m. At 4 m
    the same matching error would give $16 \times 0.25/400 = 0.01$ m: sixteen times smaller, because the error grows
    as $Z^2$.

??? question "4. With f = 1000 pixels and a matching error of 0.25 pixels, what baseline is needed for a depth error of 5 cm at 10 m?"

    From $\delta Z = Z^2\delta d/(fB)$, $B = Z^2\delta d/(f\,\delta Z) = 100 \times 0.25/(1000 \times 0.05) = 0.5$ m.
    Halving the required error at the same distance doubles the baseline; doubling the distance quadruples it.

??? question "5. For a two-link arm with L1 = L2 = 1, find both inverse kinematics solutions for the target (1, 1) and check one with the forward kinematics."

    $\cos\theta_2 = (1 + 1 - 1 - 1)/2 = 0$, so $\theta_2 = \pm 90°$. For $\theta_2 = +90°$:
    $\theta_1 = \operatorname{atan2}(1, 1) - \operatorname{atan2}(1, 1 + 0) = 45° - 45° = 0°$. For $\theta_2 = -90°$:
    $\theta_1 = 45° - \operatorname{atan2}(-1, 1) = 45° + 45° = 90°$. Check $(0°, 90°)$:
    $x = \cos 0 + \cos 90° = 1$, $y = \sin 0 + \sin 90° = 1$. Check $(90°, -90°)$: $x = 0 + \cos 0 = 1$,
    $y = 1 + \sin 0 = 1$. Both reach $(1, 1)$.

??? question "6. A differential-drive rover has wheels 0.5 m apart. Which wheel speeds make it drive a circle of radius 2 m to the left at 0.2 m/s? Which make it turn on the spot?"

    We need $v = 0.2$ and $\omega = v/R = 0.1$ rad/s. Then $v_R + v_L = 0.4$ and $v_R - v_L = \omega b = 0.05$, so
    $v_R = 0.225$ m/s and $v_L = 0.175$ m/s. Turning on the spot needs $v = 0$: $v_R = -v_L$, with
    $\omega = 2v_R/b$.

??? question "7. One-dimensional SLAM by hand: x_0 = 0 is fixed. Odometry says x_1 - x_0 = 1.0. From x_0 the robot measures a landmark at m - x_0 = 2.0, and from x_1 at m - x_1 = 0.9. All three measurements have the same standard deviation. Find the least-squares estimates of x_1 and m."

    Minimise $(x_1 - 1)^2 + (m - 2)^2 + (m - x_1 - 0.9)^2$. Setting the derivatives to zero:
    $2x_1 - m = 0.1$ and $2m - x_1 = 2.9$. Then $m = 2x_1 - 0.1$, so $4x_1 - 0.2 - x_1 = 2.9$, $x_1 = 1.0333$ and
    $m = 1.9667$. The measurements disagree by 0.1 (going via $x_1$ gives $1.0 + 0.9 = 1.9$, directly 2.0), and least
    squares spreads the disagreement equally over the three measurements: each residual is $0.1/3$.

??? question "8. Prove that for a disc robot of radius rho that only translates, the C-space obstacle of a convex obstacle O is the set of points within distance rho of O. Is it convex?"

    The robot at centre $p$ occupies the closed disc $D(p, \rho)$. It intersects $O$ if and only if some point $o \in O$
    has $\lVert o - p\rVert \le \rho$, that is, if and only if the distance from $p$ to $O$ is at most $\rho$. So
    $\mathcal{C}_{\text{obs}} = \{p : \operatorname{dist}(p, O) \le \rho\} = O \oplus D(0, \rho)$, the Minkowski sum.
    It is convex: if $p = o + a$ and $q = o' + a'$ with $o, o' \in O$ and $\lVert a\rVert, \lVert a'\rVert \le \rho$,
    then $tp + (1-t)q = (to + (1-t)o') + (ta + (1-t)a')$, a point of $O$ (convex) plus a vector of length at most
    $\rho$ (the disc is convex).

??? question "9. In the PRM completeness bound, a path is covered by m = 20 balls, each occupying a fraction mu = 0.01 of the space. How many samples make the failure bound at most 0.001?"

    We need $20(0.99)^n \le 0.001$, so $n \ge \ln(0.001/20)/\ln 0.99 = (-9.903)/(-0.01005) = 985.4$: $n = 986$
    samples. With the looser bound $20e^{-0.01n} \le 0.001$, $n \ge 991$. If the passage were half as wide in 3
    dimensions, $\mu$ would shrink by a factor of 8 and about 8 times as many samples would be needed.

??? question "10. For the cart on the slope (g = 0.5) with P control, what gain gives a steady error of 1 cm? With c = 0.5, what is the damping ratio then, and why is PID the better answer?"

    $e_\infty = g/K_p = 0.01$ needs $K_p = 50$. The damping ratio is $\zeta = c/(2\sqrt{K_p}) = 0.5/(2 \times 7.07) = 0.035$:
    almost undamped, a long-ringing oscillation. Increasing the gain trades steady error for oscillation. PID removes
    the steady error with a moderate $K_p$ (Fact 2), and $K_d$ provides the damping.

??? question "11. Write code: check the Routh-Hurwitz condition (c + kd) kp > ki against numpy's polynomial roots for 1000 random gains in [0, 10] with c = 0.5."

    ```python
    import numpy as np

    rng = np.random.default_rng(0)
    agree = 0
    for _ in range(1000):
        kp, ki, kd = rng.uniform(0, 10, 3)
        routh = (0.5 + kd) * kp > ki
        roots = max(np.roots([1, 0.5 + kd, kp, ki]).real) < 0
        agree += routh == roots
    print(agree, "of 1000 agree")   # 1000 of 1000 agree
    ```

    All 1000 agree. (The test needs all coefficients positive as well, which holds here since the gains are drawn
    from positive values.)

??? question "12. Write code: inverse kinematics for a three-link planar arm with links 1, 0.8 and 0.5 by damped least squares, reaching (1.5, 0.8). Why is there no unique answer?"

    ```python
    import numpy as np

    Ls = np.array([1.0, 0.8, 0.5])

    def fk(t):
        a = np.cumsum(t)                      # absolute angle of each link
        return np.array([np.sum(Ls * np.cos(a)), np.sum(Ls * np.sin(a))])

    def jac(t):
        a = np.cumsum(t)
        J = np.zeros((2, 3))
        for i in range(3):                    # joint i moves links i, i+1, ...
            J[0, i] = -np.sum(Ls[i:] * np.sin(a[i:]))
            J[1, i] = np.sum(Ls[i:] * np.cos(a[i:]))
        return J

    t, target = np.array([0.3, 0.3, 0.3]), np.array([1.5, 0.8])
    for _ in range(20):
        J = jac(t)
        t = t + J.T @ np.linalg.solve(J @ J.T + 0.01 * np.eye(2), target - fk(t))
    print(np.degrees(t), np.linalg.norm(target - fk(t)))
    # [-13.48858942  55.69948755  55.25382227] 0.0
    ```

    Three joint angles must satisfy two equations, so the solutions form a one-dimensional family (the arm is
    **redundant**); the iteration returns the one nearest its starting guess, in the sense of the least-squares
    steps. The extra freedom can be used for a secondary goal, such as staying away from joint limits.

## What you learned

- Edges are places of large image gradient (Sobel: a smoothed central difference); corners are where the structure
  tensor has two large eigenvalues (Harris). CNNs learn such filters, and much more, from data.
- Two calibrated, rectified cameras give depth by triangulation, $Z = fB/d$; block matching finds $d$ except at
  occlusions and on texture-less ground, and depth error grows as $Z^2/(fB)$.
- Forward kinematics adds link vectors; inverse kinematics has a closed form for two links and is solved by damped
  least squares in general; the Jacobian is singular when $\sin\theta_2 = 0$. A differential drive turns with
  $\omega = (v_R - v_L)/b$, and odometry drifts.
- SLAM estimates the path and the map together because their errors are correlated; with linear Gaussian
  measurements it is sparse weighted least squares, and loop closures correct the accumulated drift.
- Motion planning works in configuration space; PRMs are probabilistically complete with failure probability falling
  exponentially in the number of samples; RRTs explore by Voronoi bias but are not optimal.
- PID control: P leaves a steady error $g/K_p$, the integral removes it, the characteristic polynomial decides
  stability, and saturation needs anti-windup.
- Mars rovers and Ingenuity use these ideas, stereo hazard maps, visual odometry, AEGIS target selection and
  vision-based landing and flight, because the 3 to 22 minute signal delay leaves them no choice.

**Next:** [Chapter 19](19-Multi-Agent-Systems.md), where the agent is no longer alone: other agents with their own goals
share the world, and game theory takes over.

## Further reading

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020: chapter 25 (computer vision)
  and chapter 26 (robotics).
- R. Szeliski, *Computer Vision: Algorithms and Applications*, 2nd ed., 2022; R. Hartley and A. Zisserman, *Multiple
  View Geometry in Computer Vision*, 2nd ed., 2004.
- J. Canny, "A computational approach to edge detection", *IEEE Transactions on Pattern Analysis and Machine
  Intelligence* 8, 1986; C. Harris and M. Stephens, "A combined corner and edge detector", Alvey Vision Conference,
  1988; D. G. Lowe, "Distinctive image features from scale-invariant keypoints", *International Journal of Computer
  Vision* 60, 2004.
- A. Krizhevsky, I. Sutskever and G. E. Hinton, "ImageNet classification with deep convolutional neural networks",
  NeurIPS 2012.
- D. Scharstein and R. Szeliski, "A taxonomy and evaluation of dense two-frame stereo correspondence algorithms",
  *International Journal of Computer Vision* 47, 2002; L. Matthies, "Stereo vision for planetary rovers: stochastic
  modeling to near real-time implementation", *International Journal of Computer Vision* 8, 1992.
- S. Thrun, W. Burgard and D. Fox, *Probabilistic Robotics*, MIT Press, 2005 (localization, SLAM); K. M. Lynch and
  F. C. Park, *Modern Robotics: Mechanics, Planning, and Control*, 2017 (kinematics); S. M. LaValle, *Planning
  Algorithms*, 2006.
- R. Smith, M. Self and P. Cheeseman, "Estimating uncertain spatial relationships in robotics", in *Autonomous Robot
  Vehicles*, 1990; F. Lu and E. Milios, "Globally consistent range scan alignment for environment mapping",
  *Autonomous Robots* 4, 1997; M. Montemerlo, S. Thrun, D. Koller and B. Wegbreit, "FastSLAM: a factored solution to
  the simultaneous localization and mapping problem", AAAI 2002; H. Durrant-Whyte and T. Bailey, "Simultaneous
  localization and mapping: part I", *IEEE Robotics and Automation Magazine* 13, 2006.
- T. Lozano-Pérez, "Spatial planning: a configuration space approach", *IEEE Transactions on Computers* 32, 1983;
  J. H. Reif, "Complexity of the mover's problem and generalizations", FOCS 1979.
- L. E. Kavraki, P. Švestka, J.-C. Latombe and M. H. Overmars, "Probabilistic roadmaps for path planning in
  high-dimensional configuration spaces", *IEEE Transactions on Robotics and Automation* 12, 1996; L. E. Kavraki,
  M. N. Kolountzakis and J.-C. Latombe, "Analysis of probabilistic roadmaps for path planning", *IEEE Transactions on
  Robotics and Automation* 14, 1998.
- S. M. LaValle, "Rapidly-exploring random trees: a new tool for path planning", Technical Report 98-11, Iowa State
  University, 1998; S. Karaman and E. Frazzoli, "Sampling-based algorithms for optimal motion planning",
  *International Journal of Robotics Research* 30, 2011.
- N. Minorsky, "Directional stability of automatically steered bodies", *Journal of the American Society of Naval
  Engineers* 34, 1922; J. G. Ziegler and N. B. Nichols, "Optimum settings for automatic controllers", *Transactions
  of the ASME* 64, 1942; K. J. Åström and R. M. Murray, *Feedback Systems*, Princeton University Press, 2008.
- J. N. Maki and colleagues, "The Mars Science Laboratory engineering cameras", *Space Science Reviews* 170, 2012;
  J. N. Maki and colleagues, "The Mars 2020 engineering cameras and microphone on the Perseverance rover",
  *Space Science Reviews* 216, 2020.
- S. B. Goldberg, M. W. Maimone and L. Matthies, "Stereo vision and rover navigation software for planetary
  exploration", IEEE Aerospace Conference, 2002; M. Maimone, Y. Cheng and L. Matthies, "Two years of visual odometry
  on the Mars Exploration Rovers", *Journal of Field Robotics* 24(3), 2007; V. Verma and colleagues, "Autonomous
  robotics is driving Perseverance rover's progress on Mars", *Science Robotics* 8(80), 2023.
- T. A. Estlin and colleagues, "AEGIS automated science targeting for the MER Opportunity rover", *ACM Transactions on
  Intelligent Systems and Technology* 3(3), 2012; R. Francis and colleagues, "AEGIS autonomous targeting for ChemCam
  on Mars Science Laboratory: deployment and results of initial science team use", *Science Robotics* 2(7), 2017.
- D. S. Bayard and colleagues, "Vision-based navigation for the NASA Mars Helicopter", AIAA SciTech Forum, 2019; NASA
  and JPL mission pages and news releases on Ingenuity and on Perseverance's landing.
- On this site: [Machine learning, Chapter 17](../machine-learning/17-Convolutional-Networks.md) (CNNs, detection,
  segmentation); this book's [Chapter 4](04-Heuristic-Search.md) (A\* on terrain), [Chapter 13](13-Reasoning-over-Time.md)
  (Kalman and particle filters) and [Chapter 2](02-Intelligent-Agents.md) (agents and Mars autonomy);
  [Dijkstra's algorithm](../../graphs/dijkstra.md); the Algorithms book's
  [Chapter 20](../algorithms/20-Computational-Geometry.md) (geometric primitives such as segment tests) and
  [Chapter 16](../algorithms/16-Shortest-Paths.md) (shortest paths on the roadmap).
