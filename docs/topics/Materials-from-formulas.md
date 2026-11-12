# How 3D materials are made from formulas guide

*Stone, plaster, bronze, glass, leather and wool drawn by a computer from a few lines of math each, with no photographs: the algorithms, the formulas behind them, and small examples worked by hand. The real recipes are those of the Crown in the Arcadia Welcome Center on [akadian.ca](https://www.akadian.ca/palace/crown/). Four parts: stop at the one you need.*

[In one minute](#in-one-minute) · [Do it](#do-it) · [Expert](#expert) · [Now and next](#now-and-next)

!!! note "Where these recipes come from"
    Every number on this page is copied from real code. The six materials of the Crown (polished basalt, plaster, bronze, glass, leather and the wool rugs) were written as formulas for Blender, in the files `tools/render/lib.py`, `crown_rooms.py`, `seating.py` and `furn.py` of the Arcadia City art repository. Blender lit them once and saved the result as pictures, which is how today's Crown page works. The Crown has since been **rewritten to compute everything live in the browser** (the Arrival hall and the Door's room so far, at a test address that is not public yet, 12 November 2026). Its own shader code is described in [The new Crown page: what it actually computes](#the-new-crown-page-what-it-actually-computes), with every place where it differs from the textbook forms. The other sections explain the standard formulas, using the old recipes' numbers.

## In one minute

A material on a screen is two questions answered for every pixel, many times a second.

1. **What is the surface like at this exact point?** Its colour, how rough or polished it is, and whether it has tiny bumps. A photograph could answer, but it costs megabytes and repeats. A **formula** answers from the point's position alone: give it $x, y, z$ in metres and it returns a colour. The trick is a function that looks random but is not: **noise**. The same point always gives the same answer, so the stone does not flicker, and a whole floor fits in a few hundred bytes of code.
2. **How does this surface send light to the eye?** Light arriving from the sun leaves a matte wall in every direction, but leaves polished stone mostly in one direction, as a highlight. A metal colours its reflection; glass reflects only a few percent head-on and much more at a grazing angle. These rules are formulas too, from optics and probability: the surface is imagined as millions of tiny mirrors pointing in random directions, and roughness says how random.

The basalt floor of the Crown, for example, is: *fine grains about 4 mm across, from a cell pattern; slow darker clouds, from noise; slabs 1.2 m by 0.6 m with 3 mm joints, from a brick formula; and a polish that varies between "roughness" 0.13 and 0.27, from more noise.* That is the whole floor.

<figure class="play" data-play="noise"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> Five patterns, each computed pixel by pixel from x and y. Add octaves to fBm and watch finer detail appear; then see how the basalt recipe mixes two of them. Nothing here is a stored picture.</figcaption></figure>

<figure class="play" data-play="shade"><span class="ai-tag">AI-created</span><figcaption><b>Try it.</b> A ball lit by one sun, every pixel computed with the formulas on this page, using the numbers of the Crown's six materials. Move the roughness: the highlight spreads and fades. Right: the light that arrives at 45° and where it leaves. Simplified: one sun, a blurred sky, a simple tone curve, and glass seen straight through without bending.</figcaption></figure>

## Do it

**Make a piece of the basalt floor in Python** (needs only `numpy`). It writes `basalt.png`, 1.8 m by 1.2 m of floor at 2 mm a pixel, and prints the worked numbers used further down.

```python
--8<-- "guides/materials/materials.py"
```

Output (checked):

```text
fade(0.3) = 0.16308
value noise between 0.2 and 0.8 at t = 0.3: 0.29785
fBm of octaves 0.4, -0.2, 0.6 (roughness 0.5): 0.62857
slab joint at (2.0, 0.9): 0  at (2.0, 1.199): 1
gradient noise on a line: min -0.67, max 0.84, mean 0.07
roughness on this piece: 0.162 .. 0.239
wrote basalt.png
```

**The same pattern on the graphics card** (WebGL2, the browser's 3D). A *fragment shader* is a small program the card runs once for every pixel, on thousands of cores at once. This one gives the same slabs, grains and clouds as the Python; it was checked by drawing it in a browser and comparing.

```glsl
--8<-- "guides/materials/basalt.frag"
```

**With three.js** (the library the site's engine uses), the light response is ready-made: `MeshPhysicalMaterial` has the parameters below, and the formulas behind them are in [The light: how a surface answers](#the-light-how-a-surface-answers). This is a direct translation of the old Blender numbers. The new Crown page does **not** use it: it writes its own light formulas in one shader (see [below](#the-new-crown-page-what-it-actually-computes)).

```js
import * as THREE from "three";
const bronze  = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(0.40, 0.29, 0.19), metalness: 1, roughness: 0.35 });
const plaster = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(0.85, 0.80, 0.72), roughness: 0.9 });
const glass   = new THREE.MeshPhysicalMaterial({ color: 0xffffff, roughness: 0, transmission: 1, ior: 1.52, thickness: 0.01 });
const leather = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(0.30, 0.14, 0.06), roughness: 0.43, clearcoat: 0.25, clearcoatRoughness: 0.35 });
const rug     = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(0.24, 0.20, 0.17), roughness: 1, sheen: 1, sheenRoughness: 0.5, sheenColor: 0xffffff });
const basalt  = new THREE.MeshPhysicalMaterial({ color: new THREE.Color(0.04, 0.039, 0.038), roughness: 0.2, clearcoat: 0.4, clearcoatRoughness: 0.1 });
// new THREE.Color(r, g, b) takes linear numbers, as Blender's do; the pattern (grains, slabs) is added with a shader or a node graph
```

## Expert

### The map of the whole method

| Step | The question | The algorithm | Where it is below |
|---|---|---|---|
| 1 | a random-looking number for a point, the same every time | integer **hash** | [Hashing](#1-hashing-random-but-repeatable) |
| 2 | a smooth random field | **value** and **gradient (Perlin) noise** | [Noise](#2-noise-smooth-randomness) |
| 3 | detail at every size, like real stone | **fractal Brownian motion** (fBm, octaves) | [fBm](#3-fbm-detail-at-every-size) |
| 4 | grains, pebbles, pores, leather | **Voronoi / Worley cells** | [Cells](#4-cells-voronoi-and-worley-noise) |
| 5 | slabs, joints, a rug's border | **tilings** with floor and fract | [Tilings](#5-tilings-slabs-joints-and-borders) |
| 6 | bands and rings (marble, travertine, wood) | **sine waves with a noisy phase** | [Waves](#6-waves-bands-and-rings) |
| 7 | small bumps without extra geometry | **bump mapping** (a height's gradient tilts the normal) | [Bumps](#7-bumps-height-to-normal) |
| 8 | how much light leaves towards the eye | **BRDF**: Lambert diffuse, **GGX** microfacets, Smith shadowing, **Fresnel** | [Light](#the-light-how-a-surface-answers) |
| 9 | coats, cloth, glass | **layering**, **sheen**, **transmission** | [Layers](#11-layers-clear-coat-sheen-and-glass) |
| 10 | all the light in the room, not just the sun | the **rendering equation**, solved by **Monte Carlo** (Blender) or approximated live (browser) | [Whole room](#12-all-the-light-in-the-room) |
| 11 | what the new Crown page really does | value noise, ring coordinates, anti-aliasing by `fwidth`, GGX, shadow maps, light probes | [The new Crown page](#the-new-crown-page-what-it-actually-computes) |

Notation: vectors are bold or have arrows only when needed; $\mathbf n$ is the surface normal (unit length, pointing out), $\mathbf l$ the direction towards the light, $\mathbf v$ towards the eye, all unit vectors; $\mathbf a\cdot\mathbf b$ is the [dot product](https://math.akadian.ca/books/linear-algebra/01-Vectors.html), the cosine of the angle between two unit vectors. Colours are **linear** numbers from 0 to 1, proportional to light energy, not the sRGB numbers a screen uses (see [Common mistakes](#common-mistakes)).

### The pattern: what the surface is like at each point

#### 1. Hashing: random but repeatable

Every pattern below starts from the same need: give a whole-number point $(i, j)$ of a grid, get back a number that looks random, and always the same one for the same point. That is a **hash function**, the same idea as in a [hash table](../data-structures/hash-table.md), but chosen for good mixing rather than for spreading keys.

The one in this page's code multiplies by large odd numbers, mixes with XOR and shifts, and lets the arithmetic wrap at $2^{32}$:

$$h \leftarrow (73856093\,i) \oplus (19349663\,j) \oplus s,\qquad h \leftarrow h \oplus (h \gg 13),\quad h \leftarrow 1540483477\,h,\quad h \leftarrow h \oplus (h \gg 15)$$

(all mod $2^{32}$; $\oplus$ is XOR, $\gg$ a right shift; $s$ a seed). The first two primes are from Teschner and others (2003), the multiplier is MurmurHash2's. Dividing by $2^{32}$ turns $h$ into a number in $[0, 1)$. Blender has its own, for example the Brick Texture's

$$n \leftarrow (n + 1013) \wedge (2^{31}-1),\quad n \leftarrow (n \gg 13) \oplus n,\quad t = \tfrac12\,\frac{\big(n\,(60493\,n^2 + 19990303) + 1376312589\big) \wedge (2^{31}-1)}{2^{30}}$$

with $n = 65536\cdot\text{row} + \text{brick}$, which gives each slab its own small change of shade (row 1, brick 1 gives $t \approx 0.109$; brick 2 gives $t \approx 0.294$, computed with 32-bit arithmetic).

Why not `random()`? A random-number generator gives a *sequence*: to know the value at a point you would have to store it. A hash is a pure function of the point, so the graphics card can compute any pixel in any order, in parallel, and nothing is stored.

#### 2. Noise: smooth randomness

Hash values on a grid are like static on an old television: random, but jumping from point to point. Real stone changes **smoothly**. Noise fills the space between grid points.

**Value noise.** Put a random height at every whole number and blend between neighbours. A straight-line blend leaves kinks at the whole numbers, so the blend uses a curve that is flat at both ends. Ken Perlin's 2002 choice is

$$\operatorname{fade}(t) = 6t^5 - 15t^4 + 10t^3,$$

which has $\operatorname{fade}(0)=0$, $\operatorname{fade}(1)=1$, and its first *and second* derivatives zero at both ends ($\operatorname{fade}'(t) = 30t^2(1-t)^2$, $\operatorname{fade}''(t) = 60t(1-t)(1-2t)$), so neither slope nor curvature jumps at a grid line. The older curve $3t^2 - 2t^3$ has zero slope at the ends but a jump in curvature, which shows as faint creases under light.

*Worked example.* Heights 0.2 at $x=2$ and 0.8 at $x=3$; find the noise at $x = 2.3$. Here $t = 0.3$:

$$\operatorname{fade}(0.3) = 6(0.00243) - 15(0.0081) + 10(0.027) = 0.01458 - 0.1215 + 0.27 = 0.16308,$$

$$\text{noise} = 0.2 + (0.8 - 0.2)(0.16308) = 0.29785.$$

The fade curve has kept us close to the left value: at $t=0.3$ a straight line would give 0.38.

**Gradient (Perlin) noise.** Value noise shows its grid, because the extremes sit on the grid points. Perlin's 1985 idea: at each grid point store a random **slope** (a gradient vector $\mathbf g$), not a height, and let the height there be 0. Near a corner $\mathbf c$ the corner "predicts" the height $\mathbf g_{\mathbf c}\cdot(\mathbf p-\mathbf c)$, a tilted plane through 0; the noise blends the predictions of the $2^d$ corners around $\mathbf p$ (4 in 2D, 8 in 3D) with $\operatorname{fade}$ in each direction.

*Worked example in 1D.* Slopes $g_0 = +1$ at $x=2$ and $g_1 = -1$ at $x=3$; at $x = 2.3$: the left corner predicts $g_0 \cdot 0.3 = 0.3$, the right predicts $g_1\cdot(0.3 - 1) = 0.7$, and

$$\text{noise} = 0.3 + (0.7 - 0.3)\cdot 0.16308 = 0.36523.$$

Between two whole numbers the curve rises from 0, turns and comes back to 0: the bumps fall between grid points, and the grid is much harder to see. Each output needs $2^d$ hashes and dot products, so 3D noise costs 8 of each per call. In Blender this is the **Noise Texture** (3D Perlin noise, scaled by about 0.982 so its output stays roughly in $[-1, 1]$; the constant is in Cycles' `noise.h`, chosen by experiment by the OSL developers).

#### 3. fBm: detail at every size

One noise has one size of feature. A real wall has blotches a metre wide, patches a centimetre wide and grains a tenth of a millimetre wide. **Fractal Brownian motion** adds copies of noise, each finer and weaker:

$$\operatorname{fBm}(\mathbf p) = \sum_{i=0}^{D} r^i\,\operatorname{noise}(\lambda^i\,\mathbf p),$$

where $D$ is Blender's **Detail**, $r$ its **Roughness** (how strong each finer copy is, default 0.5) and $\lambda$ its **Lacunarity** (how much finer, default 2). Each copy is an **octave**, since $\lambda = 2$ doubles the frequency as an octave does in music. Blender's Cycles code (`fractal_noise.h`) runs $i = 0, 1, \dots, \lfloor D \rfloor$, so **Detail 8 means 9 octaves**; a fractional Detail blends in one more; and with "Normalize" on it squeezes the sum into $[0,1]$:

$$\text{Fac} = \tfrac12\,\frac{\sum_i r^i n_i}{\sum_i r^i} + \tfrac12.$$

*Worked example.* Three octaves gave $n_0 = 0.4$, $n_1 = -0.2$, $n_2 = 0.6$, with $r = 0.5$: the sum is $0.4 - 0.1 + 0.15 = 0.45$, the weights add to $1 + 0.5 + 0.25 = 1.75$, so $\text{Fac} = 0.5\cdot 0.45/1.75 + 0.5 = 0.62857$.

The name: Brownian motion, the path of a pollen grain knocked about by molecules, looks equally rough at every zoom; Mandelbrot and Van Ness (1968) generalized it to "fractional" Brownian motion, and with $r = 1/2$, $\lambda = 2$ this sum imitates it (its power falls off about as $1/f^2$, like Brownian motion's). See the [probability book's chapter on Brownian motion](https://math.akadian.ca/books/probability/16-Brownian-Motion.html).

*What the Crown's numbers mean.* Blender's **Scale** multiplies the position first, and the floor's coordinates are in metres, so octave $i$ has features about $1/(\text{Scale}\cdot 2^i)$ metres across:

| Material, use | Scale, Detail | Octaves | Biggest feature | Finest feature |
|---|---|---|---|---|
| Basalt, roughness clouds | 3, 8 | 9 | 33 cm | $\tfrac{1}{3\cdot 2^8}$ m $\approx$ 1.3 mm |
| Plaster, bumps | 40, 10 | 11 | 2.5 cm | $\tfrac{1}{40\cdot 2^{10}}$ m $\approx$ 0.024 mm |
| Plaster, colour blotches | 0.6, 4 | 5 | 1.7 m | 10 cm |
| Rug, colour | 2.5, 6 | 7 | 40 cm | 6 mm |

(The finest plaster octave is far smaller than a pixel. In an offline render that does no harm, since Blender averages many samples per pixel; in a live renderer it must be cut off, see [Common mistakes](#common-mistakes).)

#### 4. Cells: Voronoi and Worley noise

Stone grains, pebbles, pores and the pebbled grain of leather are **cells**, not clouds. Steven Worley (1996): scatter one random point in every unit square (or cube), using the hash for its position; at a point $\mathbf p$, measure the distance to the **nearest** one:

$$F_1(\mathbf p) = \min_k \lVert \mathbf p - \mathbf q_k \rVert.$$

$F_1$ is 0 at each point and largest on the borders between cells: the borders are the **Voronoi diagram** of the points (every place closer to one point than to any other forms that point's cell; see [computational geometry](../books/algorithms/20-Computational-Geometry.md)). Code looks only in the 3 × 3 squares around $\mathbf p$ (Blender's `voronoi.h`: 3 × 3 × 3 cubes in 3D), so each call does 9 (or 27) hashes and distances. (A check of 200 000 random points found no case where a wider 5 × 5 search gave a nearer point.)

*Worked example.* At $\mathbf p = (0.5, 0.5)$ with nearby points $(0.2, 0.9)$, $(0.7, 0.3)$ and $(1.4, 0.6)$:

$$\sqrt{0.3^2 + 0.4^2} = 0.5,\qquad \sqrt{0.2^2 + 0.2^2} \approx 0.283,\qquad \sqrt{0.9^2 + 0.1^2} \approx 0.906,$$

so $F_1 \approx 0.283$, from the second point.

In the Crown (Blender's **Voronoi Texture**, F1, Euclidean distance, Randomness 1):

- **Basalt grains**: Scale 260, so cells $1/260$ m $\approx$ 3.8 mm; the colour is $0.6\,F_1 + 0.5\,\text{fBm}$, so each grain is darker at its centre and lighter at its edge.
- **Leather grain**: Scale 520, cells $\approx$ 1.9 mm, used as a *height* (bump), so the surface rises towards the cell borders and dips at each point, like the small pits of real hide.
- Bouclé and wool upholstery use the same cells at Scale 340 and 700 (loops 2.9 mm and 1.4 mm), the bump inverted.

#### 5. Tilings: slabs, joints and borders

Man-made patterns are exact, and come from `floor` (which tile am I in?) and the remainder (where in the tile am I?).

**Slabs** (Blender's Brick Texture, the basalt floor): slabs $w = 1.2$ m long, rows $h = 0.6$ m deep, joints $m = 3$ mm, every other row shifted by half a slab (Offset 0.5, applied to rows where $\text{row} \bmod 2 = 0$):

$$\text{row} = \lfloor y/h \rfloor,\quad s = \begin{cases} 0.5\,w & \text{row even}\\ 0 & \text{row odd}\end{cases},\quad \text{brick} = \Big\lfloor \tfrac{x+s}{w} \Big\rfloor,$$

$$u = x + s - w\cdot\text{brick},\quad v = y - h\cdot \text{row},\qquad \text{joint if } \min(u,\ v,\ w-u,\ h-v) < m.$$

*Worked example.* At $(2.0, 0.9)$: row $=\lfloor 1.5\rfloor = 1$ (odd, no shift), brick $= \lfloor 2.0/1.2 \rfloor = 1$, $u = 0.8$, $v = 0.3$; the nearest edge is $\min(0.8, 0.3, 0.4, 0.3) = 0.3$ m away: inside a slab. At $(2.0, 1.199)$: $v = 0.599$, and $h - v = 0.001 < 0.003$: on a joint. (The Python above prints exactly these two answers.)

**A rug's border** (`rug_material` in `furn.py`) uses the rug's own coordinates $u, v \in [0, 1]$ across its width and length. The distance to the nearest edge is $\min(u, 1-u)$; the border band is where that lies between 0.035 and 0.047 (and, along the length, between 0.045 and 0.061). On the Arrival hall's 11 m rug that is a band 13 cm wide, 38.5 cm in from each side. At $u = 0.04,\ v = 0.5$: $\min(0.04, 0.96) = 0.04$, which is inside $(0.035, 0.047)$, while along the length $\min(0.5, 0.5) = 0.5$ is in the plain field: border colour.

These are comparisons, so their edges are perfectly sharp, one pixel jagged. A live renderer usually replaces each `<` by a `smoothstep` over the width of one pixel; the new Crown does this for its slab joints (see [below](#the-new-crown-page-what-it-actually-computes)).

#### 6. Waves: bands and rings

Marble, travertine and wood (other rooms of the Crown) use Blender's **Wave Texture**. From its source (`wave.h`): take a coordinate, for bands along $x$ the value $n = 20x$, for rings around $x$ the distance $n = 20\sqrt{y^2 + z^2}$; add noise to the *phase*, $n \mathrel{+}= \text{Distortion}\cdot(2\,\text{fBm} - 1)$; output $\tfrac12 + \tfrac12 \sin(n - \pi/2)$. Without distortion these are straight stripes or perfect rings; the noisy phase bends them into veins (marble, Distortion 14) or growth rings (wood, Distortion 9, stretched along the board by scaling the coordinates 0.12 : 2.2 : 2.2). This is Perlin's 1985 marble idea, $\sin(x + \text{turbulence})$.

#### 7. Bumps: height to normal

Light depends on which way the surface faces, its normal $\mathbf n$. Real plaster has tiny hills and dips; modelling them as geometry would take millions of triangles. **Bump mapping** (Blinn, 1978) keeps the flat triangle and only *tilts the normal* as if the surface had a height $h(x,y)$ added along $\mathbf n$. For a flat floor with normal $(0,0,1)$ and a small height field, the tilted normal is

$$\mathbf n' = \operatorname{normalize}\big(-k\,\partial_x h,\ -k\,\partial_y h,\ 1\big),$$

with $k$ a strength. The surface leans away from where the height increases: the [gradient](https://math.akadian.ca/books/calculus/15-Functions-of-Several-Variables.html) of $h$, nothing else. The derivatives come from **finite differences**: evaluate $h$ at the point and a tiny step $\delta$ away, $\partial_x h \approx (h(x+\delta, y) - h(x,y))/\delta$. Blender's Bump node does exactly this, with $\delta$ the size of one pixel's footprint on the surface (Cycles' `displace.h`: it takes the heights at the centre and at one step along each screen direction, builds the surface gradient, and blends the result with the old normal by **Strength**).

*Worked example.* A plaster hill rises 1 mm over 4 mm along $x$: $\partial_x h = 0.25$, $\partial_y h = 0$, $k = 1$. Then $\mathbf n' = (-0.25, 0, 1)/\sqrt{1.0625} = (-0.243, 0, 0.970)$, tilted $\arctan 0.25 \approx 14.0°$. A sun low in the $-x$ direction now sees this slope more face-on, so it is brighter; that is all a bump is.

Bumps used in the Crown: plaster (fBm, Strength 0.08 for the regolith plaster, Distance 2 mm), leather (cells, 0.18), rug pile (fBm at Scale 900, about 1 mm, Strength 0.6), linen (two crossed waves multiplied, a weave).

### The light: how a surface answers

#### 8. The BRDF, and one sun

For light arriving from direction $\mathbf l$ and leaving towards $\mathbf v$, a material is described by one function, its **BRDF** $f(\mathbf l, \mathbf v)$ (bidirectional reflectance distribution function, Nicodemus 1965). With one sun of brightness $E$ (its irradiance on a surface facing it), the light reaching the eye from a point is

$$L = f(\mathbf l,\mathbf v)\; E\; \max(0,\ \mathbf n\cdot\mathbf l).$$

The factor $\mathbf n\cdot\mathbf l$ is Lambert's cosine law (1760): a surface tilted away from the sun catches less of it, as a sheet of paper does when turned edgeways. Everything that makes basalt look different from plaster is inside $f$. Modern materials, both Blender's **Principled BSDF** and three.js's `MeshPhysicalMaterial`, split $f$ into a **diffuse** part (light that enters, scatters inside and comes out in any direction) and a **specular** part (light reflected at the surface):

$$f = f_\text{diffuse} + f_\text{specular}.$$

#### 9. Diffuse: Lambert

The simplest material sends light out equally in every direction:

$$f_\text{diffuse} = \frac{\rho}{\pi},$$

where $\rho$ is its colour (albedo, the fraction of light it sends back). The $\pi$ is not decoration: integrating $\cos\theta$ over the half-sphere of directions gives $\pi$, so $\rho/\pi$ sends back exactly $\rho$ of what arrives, never more. Plaster in the Crown has $\rho = (0.85, 0.80, 0.72)$: it returns 85% of red light, 72% of blue, which is a warm off-white. Both Blender 4 and three.js use this Lambert term (Blender's Principled BSDF changed to it from Disney's diffuse in version 4.0). Metals have **no** diffuse part: light that enters a metal is absorbed.

#### 10. Specular: microfacets, GGX, Smith and Fresnel

The **microfacet** model (Torrance and Sparrow 1967; Cook and Torrance 1982) imagines the surface as countless tiny flat mirrors. A mirror sends light from $\mathbf l$ to $\mathbf v$ only if it faces exactly halfway between them, along the **half vector**

$$\mathbf h = \operatorname{normalize}(\mathbf l + \mathbf v).$$

So the specular light is: *what fraction of the facets face along $\mathbf h$* ($D$), times *how much of that light is not blocked by neighbouring facets* ($G$), times *how much a mirror reflects at this angle* ($F$):

$$f_\text{specular} = \frac{D(\mathbf h)\;G(\mathbf l,\mathbf v)\;F(\mathbf v\cdot\mathbf h)}{4\,(\mathbf n\cdot\mathbf l)(\mathbf n\cdot\mathbf v)}.$$

(The 4 and the two cosines convert from "facets" to "light per direction"; a derivation is in Walter and others, 2007.)

**$D$: GGX.** The facet directions follow the GGX (Trowbridge–Reitz) distribution, Walter, Marschner, Li and Torrance (2007):

$$D(\mathbf h) = \frac{\alpha^2}{\pi\,\big((\mathbf n\cdot\mathbf h)^2(\alpha^2 - 1) + 1\big)^2},\qquad \alpha = \text{roughness}^2.$$

The square, $\alpha = \text{roughness}^2$, is Burley's 2012 suggestion (Disney), so that the roughness slider feels even to an artist; Blender (`closure.h`: `alpha = sqr(roughness)`) and three.js (`roughness.pow2()`) both do it. Facing straight along $\mathbf n$, $D = 1/(\pi\alpha^2)$. Worked numbers for the Crown:

| Material | roughness | $\alpha$ | peak $D = 1/(\pi\alpha^2)$ | facet angle where $D$ halves |
|---|---|---|---|---|
| Basalt (polished, lowest) | 0.13 | 0.0169 | 1114 | 0.6° |
| Basalt (typical) | 0.20 | 0.040 | 199 | 1.5° |
| Bronze | 0.35 | 0.1225 | 21.2 | 4.6° |
| Leather (cognac, middle) | 0.43 | 0.185 | 9.3 | 7.0° |
| Plaster | 0.90 | 0.81 | 0.49 | 63° |

(The half-angle solves $\big(c^2(\alpha^2-1)+1\big)^2 = 2\alpha^4$ for $c = \cos\theta_h$, giving $c^2 = (1 - \sqrt2\,\alpha^2)/(1-\alpha^2)$. A reflection turns through twice the facet's angle, so on the basalt floor a lamp's reflection is blurred over only about 3°: a sharp but soft reflection, which is why the code's comment says "a mirror finish read as a wet floor" and the roughness was raised to 0.13–0.27, varying across the floor so the reflection breaks up a little, as in honed stone.) The total over all facets always comes to the same (the distribution is normalized: $\int D(\mathbf h)(\mathbf n\cdot\mathbf h)\,d\omega_h = 1$), so a rough surface's highlight is **wider and dimmer**, never brighter: energy is conserved.

**$G$: Smith shadowing.** Some facets hide behind others, from the light (shadowing) or from the eye (masking), most at grazing angles. Smith's (1967) model, with Heitz's (2014) height-correlated form, is what three.js uses; it combines $G$ with the denominator into a "visibility" term

$$V = \frac{G}{4(\mathbf n\cdot\mathbf l)(\mathbf n\cdot\mathbf v)} = \frac{0.5}{(\mathbf n\cdot\mathbf l)\sqrt{(\mathbf n\cdot\mathbf v)^2(1-\alpha^2)+\alpha^2} \;+\; (\mathbf n\cdot\mathbf v)\sqrt{(\mathbf n\cdot\mathbf l)^2(1-\alpha^2)+\alpha^2}},$$

so $f_\text{specular} = D\,V\,F$ (three.js `V_GGX_SmithCorrelated`).

**$F$: Fresnel.** How much a smooth surface reflects depends on the angle; Fresnel's equations (1823) give it exactly. For an unpolarized ray hitting glass of refractive index $n$ at angle $\theta_i$, with $\theta_t$ from Snell's law $\sin\theta_i = n\sin\theta_t$ ([physics: refraction](https://physics.akadian.ca/topics/waves/level-7/01-refraction-and-snells-law.html)):

$$F = \frac12\left[\left(\frac{\cos\theta_i - n\cos\theta_t}{\cos\theta_i + n\cos\theta_t}\right)^2 + \left(\frac{n\cos\theta_i - \cos\theta_t}{n\cos\theta_i + \cos\theta_t}\right)^2\right].$$

Head-on ($\theta_i = 0$) this is $F_0 = \left(\frac{n-1}{n+1}\right)^2$. For the Crown's window glass, $n = 1.52$:

$$F_0 = \left(\frac{0.52}{2.52}\right)^2 = 0.2063^2 \approx 0.0426,$$

about 4%: you see through a window head-on, and almost all non-metals ($n \approx 1.5$) share this 4%. Schlick (1994) replaced the exact formula with

$$F \approx F_0 + (1 - F_0)(1 - \cos\theta)^5,$$

and three.js uses a faster variant from Karis (Epic Games, 2013), $F_0 + (1-F_0)\,2^{(-5.55473c - 6.98316)c}$ with $c = \mathbf v\cdot\mathbf h$. How close are they, for $n = 1.52$? (Computed.)

| Angle from head-on | 0° | 45° | 60° | 75° | 85° |
|---|---|---|---|---|---|
| Exact Fresnel | 0.0426 | 0.0530 | 0.0925 | 0.257 | 0.615 |
| Schlick | 0.0426 | 0.0446 | 0.0725 | 0.257 | 0.649 |
| Karis's variant (three.js) | 0.0427 | 0.0471 | 0.0751 | 0.254 | 0.652 |

At 60° Schlick reflects about 0.07 where the truth is 0.09: a rule of thumb, accurate head-on and at grazing angles, too low in between. Real-time renderers accept it because it costs one power instead of square roots and divisions, and the eye forgives it.

**Metals.** A metal reflects strongly and in colour, and transmits nothing into a diffuse layer. In both Blender and three.js a "metallic" material uses its **base colour as $F_0$**: Crown bronze reflects $(0.40, 0.29, 0.19)$ head-on, rising towards white at grazing angles. (Blender 4 gives metals a slightly richer Fresnel, the "F82-tint" model of Hoffman, 2019, which can dip at about 82°; three.js uses Schlick. Real polished copper has $F_0$ about $(0.95, 0.64, 0.54)$; the Crown's darker bronze is an artistic choice for aged metal, not a measured one.) The "metallic" slider between 0 and 1 is a blend of the two models, meant for edges and dust, not a physical in-between.

#### 11. Layers: clear coat, sheen and glass

**Clear coat.** Lacquered wood, sealed stone and finished leather have a thin transparent layer on top: a second, smoother specular lobe with $F_0 = 0.04$ (index 1.5), and what it reflects is taken away from the layer below:

$$f = w\,f_\text{coat} + (1 - w\,F_\text{coat})\,f_\text{base},$$

with $w$ the coat's weight (a common energy-preserving approximation; Blender's and three.js's exact layering differ in detail). The Crown's basalt has a coat of weight 0.4 and roughness 0.1 over its 0.13–0.27 stone: a sharp faint reflection over a softer one. The cognac leather has weight 0.25, roughness 0.35, over a base whose roughness wanders between 0.34 and 0.52 with noise ("worn paler at the edges", says the code).

**Sheen.** Cloth is a forest of fibres. At grazing angles you look along the fibres and see their sides lit, so velvet and wool glow at their edges where a hard surface would darken. three.js uses the "Charlie" sheen (Estevez and Kulla, Sony Pictures Imageworks, 2017), a distribution that, unlike GGX, is *largest* when $\mathbf h$ lies sideways:

$$D_\text{sheen}(\mathbf h) = \frac{(2 + 1/\alpha)\,\sin^{1/\alpha}\theta_h}{2\pi},\qquad \alpha = \text{sheen roughness}^2,$$

with Neubelt and Pettineo's (2013) visibility $V = 1/\big(4(\mathbf n\cdot\mathbf l + \mathbf n\cdot\mathbf v - (\mathbf n\cdot\mathbf l)(\mathbf n\cdot\mathbf v))\big)$. Blender 4 uses a different, newer sheen, the microfiber model of Zeltner, Burley and Chiang (2022), fitted to simulations of fibres with linearly transformed cosines. The Crown's wool rugs: roughness 1.0 (no shine at all), sheen weight 1.0, sheen roughness 0.5. The new Crown page uses neither: it brightens the rug by a simple rule at grazing angles (see [below](#the-new-crown-page-what-it-actually-computes)).

**Glass.** A ray reaching glass is split: $F$ reflected, $1 - F$ refracted into it (bent by Snell's law) and out the other side. The old Blender recipe (`lib.glass`) has a deliberate trick: **the camera and reflections see real glass, every other ray passes straight through as if the window were open**. Real glass bends and focuses sunlight into caustics, which a path tracer finds only with great noise; skipping that let sunlight and shadows come through the Crown's windows cleanly, at the cost of tiny physical errors in the light on the floor (4% too much, by the $F_0$ above). In a browser the usual tool is three.js's `transmission`, which blurs and bends what is behind the object using a picture of the scene drawn just before; the new Crown uses neither: its glass is a see-through layer whose opacity is its Fresnel reflection (see [below](#the-new-crown-page-what-it-actually-computes)).

#### 12. All the light in the room

One sun is not enough. A room is lit mostly by light that has already bounced: off the floor onto the ceiling, off the ceiling onto the sofa. The full statement is Kajiya's **rendering equation** (1986): the light leaving a point is what it emits plus, for every incoming direction $\omega_i$ over the half-sphere $\Omega$, the BRDF times the light arriving times the cosine,

$$L_o(\mathbf x, \omega_o) = L_e(\mathbf x, \omega_o) + \int_{\Omega} f(\omega_i, \omega_o)\, L_i(\mathbf x, \omega_i)\,(\mathbf n\cdot\omega_i)\, d\omega_i,$$

and $L_i$ is itself the $L_o$ of some other point, so the equation calls itself.

**How Blender solves it (today's page).** Cycles is a **path tracer**: it estimates the integral by **Monte Carlo**, following random paths of light, $N$ per pixel, and averaging. The average's error shrinks like $1/\sqrt N$ ([law of large numbers](https://math.akadian.ca/books/probability/07-Inequalities-and-the-Law-of-Large-Numbers.html), [central limit theorem](https://math.akadian.ca/books/probability/12-The-Central-Limit-Theorem.html)), so halving the grain costs four times the work. The Crown's renders used up to 192 paths a pixel, up to 4 diffuse and 4 glossy bounces, adaptive sampling (stop a pixel once its estimated noise is below 0.025) and Intel's Open Image Denoise to clean the rest (`lib.py`, `reset()` and `render()`). The sky is Nishita's physical sky model (1993: sunlight scattered by air, dust and ozone) and the sun a disc 0.53° wide, so shadows have soft edges. That costs minutes per picture on a CPU, which is why the result was **baked**: saved into pictures once. Walking the whole ring of today's page downloads 199 MB, mostly those saved pictures and the models that carry them (measured 12 November 2026).

**How a live page approximates it.** A browser has about 16 ms per frame, so it cannot trace hundreds of paths per pixel. Standard real-time tools, all available in three.js: the sun's direct light exactly as in section 8, with **shadow maps** (draw the scene from the sun, store depths, and compare); light from the sky and from bounces through **environment maps** prefiltered by roughness (the "split-sum" of Karis 2013) or **light probes** (a few numbers per point of a grid, often spherical harmonics); reflections in the floor by **screen-space reflections** or a mirrored camera; and a **tone map** at the end to squeeze bright light into what a screen shows (Blender used AgX, which three.js r186 also has). What the new Crown chose is in the next section.

### The new Crown page: what it actually computes

*Read from the code on 12 November 2026: Arcadia City repository, `palace/crown/formula/` (`shaders.js`, `mats.js`, `gi.js`, `light.js`), commit 4f07b86. The page is at a test address and not public yet, so this can still change.*

The rewrite does not use three.js's ready-made materials. Every surface is drawn by **one shader** with a switch on the material's kind, and the colours and roughness numbers come from the old Blender recipes (`mats.js`). The formulas are simpler and cheaper than Blender's, because they must run 60 times a second.

**The noise it uses.** Not Perlin's gradient noise but **value noise** (section 2), with a hash of Dave Hoskins's "hash without sine" kind (multiply by small constants, take fractions: `p = fract(p * 0.1031); p += dot(p, p.zyx + 31.32); h = fract((p.x + p.y) * p.z)`), and the older blend curve $3t^2 - 2t^3$ instead of Perlin's quintic. At $t = 0.3$ that gives $3(0.09) - 2(0.027) = 0.216$ where the quintic gave 0.163. Its fBm has **4 octaves**, each $\times 2.03$ finer (not exactly 2, and shifted by 7.1 each time, so the octaves' grids never line up) and half as strong, divided by $0.5 + 0.25 + 0.125 + 0.0625 = 0.9375$ to stay in $[0, 1]$. Cells (Voronoi $F_1$, 3 × 3 squares) are used only for the soil.

**Anti-aliasing, built in.** Every fine pattern is multiplied by

$$\operatorname{fade}(P, s) = \operatorname{clamp}\big(1 - 0.9\, s\, w,\ 0,\ 1\big),$$

where $s$ is the pattern's frequency per metre and $w$ = `fwidth(P)`, how far apart neighbouring pixels are on the surface (the graphics card gives it for free). This is the cure for the first [common mistake](#common-mistakes): the basalt's grain ($s = 260$) is at full strength up close, at $1 - 0.9 \cdot 260 \cdot 0.001 \approx 0.77$ when a pixel covers 1 mm, and gone (replaced by its average) once a pixel covers $1/(0.9\cdot 260)$ m $\approx 4.3$ mm.

| Material | What the new page computes |
|---|---|
| **Basalt floor** | Slabs in **ring coordinates**: $q = (125\,\beta/1.2,\ r/0.6)$, with $\beta$ the bearing in radians and $r$ the distance from the ring's centre, every other row shifted by half. So slabs are 1.2 m long at radius 125 m (longer outside, shorter inside, as stone laid round a ring would be) and 0.6 m deep. Each slab's tone is $0.9 + 0.1\cdot\text{hash}(\text{slab})$. Joints by a `smoothstep` widened by `fwidth`, fading out in the distance. Grain: value noise at 260 per metre, faded as above; clouds: fBm at 0.7 per metre; colour between the old ramp's two ends. Roughness $0.13 + 0.14\cdot$fBm(3 per metre), 0.5 on the joints. The "coat" 0.4 raises $F_0$ from 0.04 to $0.04 + 0.04\cdot 0.4 = 0.056$; there is no separate coat highlight. The floor **mirrors the room**: the room is drawn a second time from under the floor into a picture, and that picture is read back blurred by roughness (mip level $8\times$roughness, five samples). |
| **Plaster, ceiling** | colour $\times\big(1 + 0.06\,(\text{fBm}(1.3P) - 0.5)\big)$ (the ceiling 0.05 at 0.9 per metre); bump from fBm at 55 per metre, faded; roughness 0.9 and 0.92. |
| **Bronze** | a plain metal: $F_0$ = (0.40, 0.29, 0.19), roughness 0.35, colour wandering $\pm4\%$ with fBm at 2 per metre; no patina, no bump. |
| **Glass** | not refracted: a see-through layer whose opacity is $0.9F + 0.03$ with Schlick's $F = 0.04 + 0.96(1 - \mathbf n\cdot\mathbf v)^5$, showing the bounced light seen along the reflection plus a sharp sun glint ($(\mathbf r\cdot\mathbf l)^{3000}$). Head-on: 4% reflection, 6.6% opaque. A frosted variant glows with the light on both its sides. |
| **Cognac leather** | colour wandering $\pm16\%$ with value noise at 3.5 per metre, and roughness from 0.34 to 0.52 by the same noise (as in Blender); grain: a bump from value noise at 300 and 60 per metre (not Voronoi cells); coat 0.25, so $F_0 = 0.05$. |
| **Wool rug** | the same border band as Blender (0.035 to 0.047 across, 0.045 to 0.061 along); the field darkened up to 70% of the way towards 0.82 of itself by fBm at 2.5 per metre; pile bump from value noise at 240 per metre; roughness 0.95. **Sheen** is a rule of thumb, not a sheen BRDF: colour $\times\big(1 + 0.5(1 - \mathbf n\cdot\mathbf v)^3\big)$, so $\times 1.06$ seen at 60° from straight on and $\times 1.28$ at 80°. |
| Also | walnut and oak: rings $\operatorname{fract}(6(y+z) + 3\,\text{fBm})$ along the grain; travertine: beds and pits; bark: noise in the branch's own coordinates; leaves: a colour picked by each leaf's random number, light through the back; alabaster: $\tfrac12 + \tfrac12\sin(9y + 10\,\text{fBm})$ veins that glow. |

**The bump** is the same surface-gradient formula as Blender's (section 7), with the screen derivatives `dFdx`, `dFdy` of the position and of the height (Mikkelsen, 2010, "Bump Mapping Unparametrized Surfaces on the GPU").

**The light on a surface.**

- **Diffuse**: Lambert, colour $\times\ (\mathbf n\cdot\mathbf l)\times$ the light, metals none.
- **Specular**: GGX for $D$ and Schlick for $F$, as in section 10, with $\alpha = \text{roughness}^2$. The shadowing term is its own simplification built on the Schlick–GGX form $\frac{\mathbf n\cdot\mathbf l}{(\mathbf n\cdot\mathbf l)(1-k)+k}$ with Karis's $k = (\text{roughness}+1)^2/8$ (2013), combined with a denominator and a factor 0.75 that are not one of the published forms; why those constants were chosen is not written in the code.
- **Reflections of the room**: what a mirror would see, from the light probes below, weighted by Schlick's Fresnel whose grazing value is lowered for rough surfaces, $F_0 + (\max(1 - \text{roughness}, F_0) - F_0)(1 - \mathbf n\cdot\mathbf v)^5$ (a known shortcut, as in Lagarde's notes), so a matte wall does not turn into a mirror at a grazing angle.
- **The sun's shadow**: one **shadow map** drawn from the sun when it moves, read with **PCSS** (Fernando, NVIDIA, 2005): first search how far in front the blocker stands, then blur the shadow's edge by that, since the sun is a disc and not a point; 8 + 16 samples on a spiral turned by "interleaved gradient noise" per pixel (Jimenez, 2014), and a bias from the receiver plane's slope so a floor the sun grazes does not shadow itself.
- **Lamps**: points and spots with a smooth cut-off at a range, and "lines of light" round the ring for the coves and wall washers.
- **Bounced light**: about 2,000 **light probes** on a grid in ring coordinates (a layer every 1.6 m along the ring, closer on either side of a wall so light does not leak between rooms; 10 across; 8 up, closer near the floor). In a background worker, 192 rays leave each probe evenly over the sphere and are traced against a **bounding-volume hierarchy** (a tree of boxes over the triangles, split at the middle of the longest side, at most 4 triangles a leaf); each hit point is lit by the sun (with a shadow ray), the lamps and the previous round's bounced light; **three rounds** make three bounces. Each probe keeps 4 numbers per colour, the first two bands of **spherical harmonics** (the mean light and its lean, "L1"), and surfaces read them back between probes with a non-linear fit that never goes below zero (its author describes it as Geomerics' non-linear L1 fit). This is the live version of section 12's integral: few directions, few bounces, worked out once per time of day.
- **After the picture**: screen-space ambient occlusion (12 samples, blurred, the soft dark in corners), bloom (shrink, spread, add back), AgX tone mapping like Blender's, a slight vignette and a dither of $\pm\tfrac12$ of a step against banding. The sky is an analytic gradient from butterscotch to darker overhead with blue glow round the sun (exponential halos) and hashed stars, not Nishita's physical model.

What it does not have yet, from its own notes: the rest of the ring, and a speed check on a real graphics card.

### The old Blender recipes in one table

Exactly as in the old Blender code (linear colours; roughness 0 = mirror, 1 = matte).

| Material | Pattern | Light response |
|---|---|---|
| **Polished basalt** (`crown_rooms.py`, `basalt()`) | colour ramp from (0.018, 0.018, 0.019) to (0.06, 0.058, 0.056) driven by $0.6\,F_1$(cells, Scale 260) $+ 0.5\,$fBm(Scale 0.7, Detail 6); slabs 1.2 × 0.6 m, half offset, 3 mm joints at 0.4 brightness, each slab's brightness set between 1 and 0.92 by its hash | not metal; roughness $0.13 + 0.14\cdot$fBm(Scale 3, Detail 8), so 0.13 to 0.27; clear coat 0.4, roughness 0.1 |
| **Regolith plaster** (`lib.plaster`) | colour blends (0.85, 0.80, 0.72) towards a copy 7 to 9% darker by fBm(Scale 0.6, Detail 4); bump fBm(Scale 40, Detail 10, roughness 0.65), Strength 0.08 | Lambert-like: roughness 0.9 |
| **Bronze** | none: one colour | metal; $F_0$ = (0.40, 0.29, 0.19), roughness 0.35 (dark bronze (0.17, 0.13, 0.10), 0.4) |
| **Mars glass** (`lib.glass`) | none | index 1.52, roughness 0, tint (0.93, 0.95, 0.93); camera and reflection rays see glass, other rays pass straight through |
| **Cognac leather** (`seating.fabric`, "leather") | colour (0.30, 0.14, 0.06) varied ±16% by fBm(Scale 3.5, Detail 4); grain: cells at Scale 520 as bump, Strength 0.18 | not metal; roughness from the same fBm mapped to 0.34 to 0.52; clear coat 0.25, roughness 0.35 |
| **Wool rug, dark** (`furn.rug_material`) | field (0.24, 0.20, 0.17) blended up to 35% towards a copy about 20% darker by fBm(Scale 2.5, Detail 6); border band (0.50, 0.44, 0.36); pile bump fBm(Scale 900), Strength 0.6 | roughness 1.0; sheen 1.0, sheen roughness 0.5 |

The new Crown page starts from the same colours and roughness values (its `mats.js` copies them) but computes the patterns with simpler formulas of its own, as the previous section shows.

### What it costs

Per pixel, per frame: one 3D gradient noise is 8 hashes and dot products and 7 blends; an fBm of 9 octaves is 9 of those; a 3D Voronoi is 27 hashes and distances. The basalt then needs about 7 × 8 + 27 = 83 hashes for its colour (fBm of Detail 6, then 3D cells) and 9 × 8 = 72 for its roughness: about 155 per pixel. At 1920 × 1080 that is about 2 million pixels, so a few hundred million small operations per frame, 60 times a second: comfortable for a desktop graphics card, heavy for a phone (an estimate, not a measurement). The usual remedies: fewer octaves far away, **bake** the pattern once into a small texture in the browser at load time, or compute it only where it shows.

### Common mistakes

| Mistake | What happens |
|---|---|
| **Detail finer than a pixel** | An octave smaller than a pixel turns into shimmering, crawling dots when you walk (aliasing). By the [sampling theorem](https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem), a pixel covering $w$ metres can show frequencies up to $1/(2w)$. Plaster's octave $i$ has frequency $40\cdot2^i$ per metre; at $w = 2$ mm the limit is 250, so keep $40\cdot 2^i \le 250$, $i \le \log_2 6.25 \approx 2.6$: only octaves 0 to 2, and fade the next one out. Offline renderers hide this by averaging many samples per pixel; a live one must cut octaves by distance (Ebert and others, *Texturing and Modeling*, on antialiasing procedural textures). The Python and GLSL above do **not** do this: their grains, about 4 mm, are drawn with pixels of 2 to 4 mm, at or past the limit, so they would speckle and crawl in a moving view. |
| **Mixing up linear and sRGB numbers** | Formulas work in linear light; screens expect sRGB. Plaster's 0.85 linear is 237 out of 255 on screen, not 217; basalt's 0.018 is 36, not 5. Skipping the conversion makes everything too dark and too contrasty, and lighting looks wrong. |
| **Forgetting roughness²** | GGX takes $\alpha = \text{roughness}^2$. Feeding roughness in directly makes every material look much rougher than its number says. |
| **Too smooth** | A perfect mirror floor reads as wet, as the Crown's own code notes; real polished stone has roughness about 0.1 to 0.3 and varies. |
| **Breaking energy conservation** | Adding a coat or sheen on top without taking light away from the base makes surfaces glow brighter than the light that hits them. |
| **Visible repetition** | Hash with a weak function, or reuse one noise for colour and roughness, and grid lines or repeated shapes appear. Use different seeds or offsets per use (the try-it picture shifts each octave by a different offset). |
| **Far from the origin** | 32-bit floats keep about 7 digits. At 100 km from the origin a position is only good to about 1 cm, so 4 mm grains turn to blocks. Blender's noise wraps coordinates at 100 000 for this reason (`noise.h`); a ring 1 km across is safe, a planet is not. |
| **Bump scale in the wrong units** | Bump strength is relative to the step between samples; the same numbers look stronger on a small object than on a big one unless the distance is set in metres (Blender's Distance). |

### Best practices

- Keep the **pattern** (colour, roughness, height as functions of position) separate from the **light response** (the BRDF). Then one set of formulas can be lit by Blender, three.js or anything else.
- Work in metres, so every Scale reads as a size: Scale 260 = cells 3.8 mm.
- Use measured numbers where they exist ($F_0$ from the refractive index, metal colours from measured data) and say which numbers are artistic choices.
- Test a material on a sphere under one light first (as in the try-it above), then in the room.
- Check the result by eye at the distance people will see it, on a phone too: a detail nobody can see is cost without benefit.

### Learn it properly

- Math behind it: [vectors and the dot product](https://math.akadian.ca/books/linear-algebra/01-Vectors.html), [functions of several variables and gradients](https://math.akadian.ca/books/calculus/15-Functions-of-Several-Variables.html), [vector calculus](https://math.akadian.ca/books/calculus/17-Vector-Calculus.html), [Brownian motion](https://math.akadian.ca/books/probability/16-Brownian-Motion.html), [randomness in computing](https://math.akadian.ca/books/probability/19-Randomness-in-Computing.html).
- Algorithms: [hash tables](../data-structures/hash-table.md), [computational geometry and Voronoi diagrams](../books/algorithms/20-Computational-Geometry.md), [randomized algorithms](../books/algorithms/21-Randomized-and-Amortized-Analysis.md).
- Light: [refraction and Snell's law](https://physics.akadian.ca/topics/waves/level-7/01-refraction-and-snells-law.html).
- Books: Pharr, Jakob and Humphreys, *Physically Based Rendering*, 4th ed. (2023), free at [pbr-book.org](https://pbr-book.org/); Ebert, Musgrave, Peachey, Perlin and Worley, *Texturing and Modeling: A Procedural Approach*, 3rd ed. (2003); Akenine-Möller and others, *Real-Time Rendering*, 4th ed. (2018).
- Code: Blender's Cycles shaders ([`intern/cycles/kernel/svm`](https://github.com/blender/blender/tree/main/intern/cycles/kernel/svm): `noise.h`, `fractal_noise.h`, `voronoi.h`, `wave.h`, `brick.h`, `displace.h`); three.js's lighting functions (`D_GGX`, `V_GGX_SmithCorrelated`, `F_Schlick`, `D_Charlie` in [`src/nodes/functions`](https://github.com/mrdoob/three.js/tree/dev/src/nodes/functions)); Google's [Filament material guide](https://google.github.io/filament/Filament.md.html), a clear write-up of the real-time formulas.

### Check yourself

??? question "1. Blender's Noise Texture has Scale 3 and Detail 8. How many octaves is that, and what are the biggest and smallest features, if the coordinates are in metres?"

    Detail 8 runs octaves $i = 0$ to 8: **9 octaves**. Octave $i$ has features about $1/(3\cdot 2^i)$ m across: 33 cm for $i=0$ and $1/768$ m $\approx$ **1.3 mm** for $i = 8$.

??? question "2. Compute the 1D value noise at x = 5.5 between heights 0.1 (at 5) and 0.9 (at 6). Why is the answer exactly halfway?"

    $t = 0.5$: $\operatorname{fade}(0.5) = 6/32 - 15/16 + 10/8 = 0.1875 - 0.9375 + 1.25 = 0.5$. Noise $= 0.1 + 0.8 \cdot 0.5 = 0.5$. The curve $6t^5-15t^4+10t^3$ is symmetric about $t = \tfrac12$: $\operatorname{fade}(1-t) = 1 - \operatorname{fade}(t)$, so the middle is always halfway.

??? question "3. Why is gradient noise always 0 at whole numbers, and why does that help?"

    At a corner $\mathbf c$ itself, the offset $\mathbf p - \mathbf c$ is zero, so that corner's prediction $\mathbf g\cdot(\mathbf p-\mathbf c)$ is 0, and the fade weights there are 1 for that corner and 0 for the rest. So the noise is 0 on the grid and its hills and valleys fall *between* grid points, at varied places; the eye no longer finds a regular grid of highs and lows as it does in value noise.

??? question "4. Show that F0 for index 1.33 (water) is about 2%, and say what it means for a puddle seen head-on and at a grazing angle."

    $F_0 = (0.33/2.33)^2 = 0.1416^2 \approx 0.020$: 2% reflected looking straight down, so you see the ground through it. At a grazing angle $F$ rises towards 1 (Schlick: $F_0 + (1-F_0)(1-\cos\theta)^5$, and $\cos\theta \to 0$), so the far part of the puddle is a mirror of the sky.

??? question "5. Roughness goes from 0.2 to 0.4. By what factor does the peak of the GGX highlight change?"

    $\alpha$ goes from 0.04 to 0.16, four times. Peak $D = 1/(\pi\alpha^2)$ falls by $4^2 = 16$: from 199 to 12.4. The highlight is 16 times dimmer at its peak and correspondingly wider; the total reflected stays about the same.

??? question "6. A pixel covers 5 mm of plaster. Which octaves of fBm(Scale 40) should be kept?"

    The limit is $1/(2\cdot 0.005) = 100$ per metre. Octave $i$ has frequency $40\cdot 2^i$: 40, 80, 160... Keep $i = 0$ and $1$ (40 and 80), fade out $i = 2$ (160 is above 100), drop the rest.

??? question "7. Why does bronze have no diffuse colour, and where does its colour come from?"

    Light that refracts into a metal is absorbed within a fraction of a micrometre by its free electrons, so nothing scatters back out as diffuse light. All the light that leaves is reflected at the surface, and a metal's Fresnel reflectance depends on wavelength: copper alloys reflect red more than blue. So the material's colour is its $F_0$, used as the specular colour.

## Now and next

*Last checked: 12 November 2026.*

- **One material language for every program.** OpenPBR Surface (Academy Software Foundation, first released 2024, built on Autodesk Standard Surface and Adobe Standard Material) and MaterialX aim to make the same recipe look the same in Blender, film renderers and real-time engines. three.js already includes MaterialX's noise functions; Blender's Principled BSDF was redesigned along the same lines in version 4.0 (2023).
- **WebGPU.** The browser's newer graphics interface, now in Chrome, Edge, Safari 26 and Firefox (Windows first), lets pages run compute shaders: bake noise into textures, build light probes, even trace a few rays per pixel, on the visitor's own card. three.js's WebGPU renderer, which the site's engine uses, falls back to WebGL2 where it is missing.
- **Neural materials.** Instead of hand-written formulas, a small neural network per material is trained on a detailed layered material and evaluated in real time (for example Zeltner and others, NVIDIA, "Real-Time Neural Appearance Models", 2024). Very realistic, but a network, not a formula you can read.
- **Real-time path tracing with denoising.** Games now trace a few paths per pixel and clean them up with temporal and learned denoisers, and resampled importance sampling ("ReSTIR", Bitterli and others, 2020) picks which lights to sample. In browsers this is still experimental.
- **Open questions:** how to filter procedural detail perfectly at every distance (still done with rules of thumb), how to fit measured real materials with few parameters, and how much of the full rendering equation a phone can afford.

## Sources

- Perlin, K. "An Image Synthesizer." SIGGRAPH 1985; "Improving Noise." SIGGRAPH 2002 (the $6t^5 - 15t^4 + 10t^3$ curve).
- Worley, S. "A Cellular Texture Basis Function." SIGGRAPH 1996.
- Mandelbrot, B. and Van Ness, J. "Fractional Brownian Motions, Fractional Noises and Applications." *SIAM Review* 10 (1968).
- Teschner, M. and others. "Optimized Spatial Hashing for Collision Detection of Deformable Objects." VMV 2003 (the primes 73856093 and 19349663).
- Blinn, J. "Simulation of Wrinkled Surfaces." SIGGRAPH 1978.
- Nicodemus, F. "Directional Reflectance and Emissivity of an Opaque Surface." *Applied Optics* 4 (1965).
- Torrance, K. and Sparrow, E. "Theory for Off-Specular Reflection from Roughened Surfaces." *JOSA* 57 (1967); Cook, R. and Torrance, K. "A Reflectance Model for Computer Graphics." *ACM TOG* 1 (1982).
- Walter, B., Marschner, S., Li, H. and Torrance, K. "Microfacet Models for Refraction through Rough Surfaces." EGSR 2007 (GGX).
- Smith, B. "Geometrical Shadowing of a Random Rough Surface." *IEEE Trans. Antennas and Propagation* 15 (1967); Heitz, E. "Understanding the Masking-Shadowing Function in Microfacet-Based BRDFs." *JCGT* 3 (2014).
- Schlick, C. "An Inexpensive BRDF Model for Physically-based Rendering." *Computer Graphics Forum* 13 (1994).
- Burley, B. "Physically-Based Shading at Disney." SIGGRAPH 2012 course; Karis, B. "Real Shading in Unreal Engine 4." SIGGRAPH 2013 course.
- Estevez, A. and Kulla, C. "Production Friendly Microfacet Sheen BRDF." Sony Pictures Imageworks, 2017; Neubelt, D. and Pettineo, M. "Crafting a Next-Gen Material Pipeline for The Order: 1886." SIGGRAPH 2013 course; Zeltner, T., Burley, B. and Chiang, M. "Practical Multiple-Scattering Sheen Using Linearly Transformed Cosines." SIGGRAPH 2022 talk.
- Hoffman, N. "Generalization of Adobe's Fresnel Model." 2019 (the F82-tint metal Fresnel).
- Kajiya, J. "The Rendering Equation." SIGGRAPH 1986.
- Mikkelsen, M. "Bump Mapping Unparametrized Surfaces on the GPU." *Journal of Graphics, GPU, and Game Tools* 15 (2010).
- Fernando, R. "Percentage-Closer Soft Shadows." SIGGRAPH 2005 sketch; Jimenez, J. "Next Generation Post Processing in Call of Duty: Advanced Warfare." SIGGRAPH 2014 course (interleaved gradient noise).
- The new Crown page: Arcadia City repository, `palace/crown/formula/` (`shaders.js`, `mats.js`, `gi.js`, `light.js`), commit 4f07b86, read 12 November 2026.
- Nishita, T. and others. "Display of the Earth Taking into Account Atmospheric Scattering." SIGGRAPH 1993.
- Blender source, Cycles kernel (`noise.h`, `fractal_noise.h`, `voronoi.h`, `wave.h`, `brick.h`, `displace.h`, `closure.h`), and three.js r186 source (`D_GGX`, `V_GGX_SmithCorrelated`, `F_Schlick`, `D_Charlie`, `V_Neubelt`), read 12 November 2026.
- The Crown's recipes: Arcadia City art repository, `tools/render/lib.py`, `crown_rooms.py`, `seating.py`, `furn.py`, read 12 November 2026.
