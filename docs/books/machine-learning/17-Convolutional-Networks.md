# 17. Convolutional neural networks

*A photograph is a grid of numbers, and the network of [Chapter 15](15-Neural-Networks-and-Backpropagation.md)
can take any list of numbers as input. Yet a plain fully connected network is a poor way to see: it needs far too
many weights, and what it learns about a cat in the top-left corner teaches it nothing about a cat in the
bottom-right. This chapter builds the fix, the convolutional layer, from scratch: one small filter slid over the
whole image, the same weights at every position. You will compute convolutions by hand, prove that they commute with
shifts, derive their backward pass and check it numerically, train a tiny convolutional network that recognises bars
in places it has never seen them, then follow the architectures that took the idea from reading cheques to
segmenting medical images.*

!!! abstract "In this chapter"
    **You will learn:**

    - why fully connected layers fail on images, counted in weights and shown on data
    - what a convolution is, computed by hand: filters, edges, stride, padding, channels, and the output-size formula
    - pooling and receptive fields, with the recurrence that gives a unit's field of view, proved
    - translation equivariance, proved, and how pooling turns it into (partial) invariance
    - the backward pass through convolution and pooling, derived and checked against finite differences
    - the landmark architectures (LeNet, AlexNet, VGG, ResNet) and the idea each added
    - transfer learning, what filters learn, and how detection and segmentation (U-Net) reuse the same layers

    **You need:** [Chapter 15](15-Neural-Networks-and-Backpropagation.md) (layers, backpropagation, computational
    graphs) and [Chapter 16](16-Training-Deep-Networks.md) (initialisation, batch norm, residual connections).
    Matrix products and NumPy broadcasting from [Chapter 3](03-The-Math-Toolkit.md).

    **Levels:** 17.1 to 17.3 are beginner to intermediate; 17.4 to 17.6 are intermediate; 17.7 is advanced.

## 17.1 Images as arrays; why fully connected fails

A grey-scale image of height $H$ and width $W$ is an $H \times W$ array of numbers, one per **pixel** (picture
element), usually brightness from 0 (black) to 255 (white), rescaled to $[0, 1]$ before training. A colour image has
three such arrays, one each for red, green and blue, called **channels**, so it is an array of shape
$3 \times H \times W$. A batch of $N$ colour images is a four-dimensional array $N \times 3 \times H \times W$.
Deep-learning code calls such arrays **tensors**; here the word only means "array with several indices".

Nothing stops us from flattening an image into one long vector and feeding it to the multilayer perceptron of
[Chapter 15](15-Neural-Networks-and-Backpropagation.md). A $224 \times 224$ colour image (the size used in the
ImageNet competition) flattens to $224 \cdot 224 \cdot 3 = 150{,}528$ numbers. Three things then go wrong.

**Too many weights.** A first hidden layer of only 1000 units needs one weight per (input, unit) pair. The first part
of the chapter's first program counts them:

```python
--8<-- "books/machine-learning/ch17_convolution.py"
```

```
1. parameters of one layer on a 224 x 224 colour image
   fully connected to 1000 units: 150,529,000 weights
   64 filters of 3 x 3 x 3      : 1,792 weights

2. image (6 x 6)
      0    0    0    9    9    9
      0    0    0    9    9    9
      0    0    0    9    9    9
      0    0    0    9    9    9
      0    0    0    9    9    9
      0    0    0    9    9    9
   Sobel-x response (4 x 4)
      0   36   36    0
      0   36   36    0
      0   36   36    0
      0   36   36    0
   Sobel-y response (4 x 4)
      0    0    0    0
      0    0    0    0
      0    0    0    0
      0    0    0    0

3. output size floor((n + 2p - k) / s) + 1, checked
   n=  6 k=3 s=1 p=0: formula   4, code   4
   n=  6 k=3 s=1 p=1: formula   6, code   6
   n=  7 k=3 s=2 p=0: formula   3, code   3
   n=  7 k=3 s=2 p=1: formula   4, code   4
   n=224 k=7 s=2 p=3: formula 112, code 112

4. a 4 x 4 feature map
      1    3    2    0
      4    6    1    1
      0    2    5    7
      1    1    8    3
   2 x 2 max pooling
      6    2
      2    8
   2 x 2 average pooling
   3.50 1.00
   1.00 5.75

5. receptive field of one unit after a stack of layers (kernel k, stride s)
   after conv3: receptive field  3 x  3, jump 1
   after conv3: receptive field  5 x  5, jump 1
   after pool2: receptive field  6 x  6, jump 2
   after conv3: receptive field 10 x 10, jump 2
   after conv3: receptive field 14 x 14, jump 2
   after pool2: receptive field 16 x 16, jump 4
   after conv3: receptive field 24 x 24, jump 4
   brute force: one input pixel reaches 25 outputs after two 3x3 convs (a 5 x 5 block)

6. translation equivariance: conv(shift(x)) == shift(conv(x))? True
   shift 1: pooled max 1.508 -> 1.508; pooled map unchanged? False equals pooled map moved 0? False
   shift 2: pooled max 1.508 -> 1.508; pooled map unchanged? False equals pooled map moved 1? True
   shift 3: pooled max 1.508 -> 1.508; pooled map unchanged? False equals pooled map moved 1? False
```

A hundred and fifty million weights for one layer, more than there are pixels in a hundred thousand images of a
small dataset. A model with that many free numbers and not enough data overfits ([Chapter 8](08-Overfitting-and-Regularization.md)).
The convolutional layer in the second line, 64 filters of size $3 \times 3$ over 3 channels, has 1,792.

**No sense of nearness.** Flattening throws away the grid. The MLP's first layer would learn exactly as well if we
shuffled the pixels by a fixed random permutation before training, because the permutation just reorders its
weights. But in real images, nearby pixels belong together: an edge, a corner, a patch of fur are all *local*
patterns, a few pixels wide.

**No reuse across positions.** A vertical edge looks the same whether it is at the left of the picture or the
right. A fully connected unit that has learned to spot an edge at column 10 has weights for column 10 only; to spot
the same edge at column 200 it must learn it again from examples with edges there.

The second program shows the third problem on data. It makes $12 \times 12$ images of short bars, horizontal,
vertical or diagonal, plus noise, and trains on images where the bar always starts in the left half (columns 0 to 3).
Then it tests on new images with the bar in the left half, and on images with the bar in the *right* half (columns 4
to 7), where no training bar ever was. The fully connected net (MLP) gets 0.357 on the moved bars, about chance for
three classes; the convolutional net (CNN), with 44 times fewer weights, gets 0.997. The rest of this chapter
explains why. The full output of that program is in 17.4.

A **convolutional neural network** (CNN) builds the two missing assumptions into its layers. *Locality:* each unit
looks only at a small window of the layer below. *Weight sharing:* every window uses the same weights. Both are
assumptions about the world, an **inductive bias** (a preference built into a model before it sees data). They are
right for images, sound and many grids, and that is why CNNs need so much less data than MLPs there.

### Where the idea came from

In 1959 and 1962, the neurophysiologists David Hubel and Torsten Wiesel recorded single neurons in the visual cortex
of cats and found cells that responded to an edge at one orientation in one small region of the visual field
("simple cells"), and cells that responded to the same edge anywhere within a larger region ("complex cells").
Kunihiko Fukushima's **neocognitron** (1980) turned this into a layered model of alternating feature-detecting and
position-tolerant layers, with the same detector repeated over the image, though trained without backpropagation.
Yann LeCun and colleagues at Bell Labs trained such shared-weight networks with backpropagation to read handwritten
zip codes (LeCun et al., 1989), the line that led to LeNet in 17.5. The biology inspired the design; modern CNNs are
not models of the brain, and we will justify every piece by what it does, not by analogy.

## 17.2 Convolution from scratch: filters, edges, stride, padding

**The question:** how do we apply one small detector everywhere in an image?

Take a small array of weights $w$ of size $k \times k$, called a **filter** or **kernel** (typical $k$ is 3, 5 or
7). Lay it over a $k \times k$ patch of the image, multiply the overlapping numbers pairwise, and add the products.
That sum is one output number. Slide the filter one pixel to the right and repeat; at the end of a row, go down one
pixel. The output array is a **feature map**: how strongly the filter's pattern appears at each position.

In symbols, for an image $x$ and a filter $w$ indexed from 0,

$$
y[i, j] = \sum_{a=0}^{k-1} \sum_{b=0}^{k-1} w[a, b] \, x[i + a, \, j + b].
$$

Mathematicians call this **cross-correlation**. True **convolution** flips the filter first,
$y[i, j] = \sum_{a,b} w[a, b] \, x[i - a, j - b]$. Deep-learning libraries compute cross-correlation and call it
convolution. Since the filter is learned, the difference does not matter: the network simply learns the flipped
filter. We follow the libraries and say "convolution" for the formula above. (The flip will reappear honestly in
the backward pass, 17.4.)

### A filter that finds edges

The image in Figure 17.1 is dark (0) on the left and bright (9) on the right. The filter is the **Sobel filter** for
the $x$ direction, an old tool of image processing (Irwin Sobel and Gary Feldman described it in a 1968 talk). Its
left column is negative and its right column positive, so it computes "brightness on the right minus brightness on
the left", with the middle row counted twice.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 265" role="img" aria-label="A 6 by 6 image, dark on the left and bright on the right, a 3 by 3 Sobel filter, and the 4 by 4 output. The highlighted 3 by 3 patch of the input, multiplied entry by entry with the filter and summed, gives the highlighted output value 36. The output is 36 in the two middle columns where the edge is, and 0 elsewhere.">
<text x="110" y="25" font-size="14" text-anchor="middle" fill="currentColor">input 6 x 6</text>
<rect x="20" y="40" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="35" y="60" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="50" y="40" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="65" y="60" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="80" y="40" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="95" y="60" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="110" y="40" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="125" y="60" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="140" y="40" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="155" y="60" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="170" y="40" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="185" y="60" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="20" y="70" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="35" y="90" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="50" y="70" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="65" y="90" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="80" y="70" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="95" y="90" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="110" y="70" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="125" y="90" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="140" y="70" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="155" y="90" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="170" y="70" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="185" y="90" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="20" y="100" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="35" y="120" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="50" y="100" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="65" y="120" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="80" y="100" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="95" y="120" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="110" y="100" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="125" y="120" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="140" y="100" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="155" y="120" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="170" y="100" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="185" y="120" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="20" y="130" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="35" y="150" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="50" y="130" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="65" y="150" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="80" y="130" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="95" y="150" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="110" y="130" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="125" y="150" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="140" y="130" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="155" y="150" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="170" y="130" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="185" y="150" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="20" y="160" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="35" y="180" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="50" y="160" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="65" y="180" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="80" y="160" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="95" y="180" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="110" y="160" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="125" y="180" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="140" y="160" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="155" y="180" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="170" y="160" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="185" y="180" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="20" y="190" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="35" y="210" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="50" y="190" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="65" y="210" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="80" y="190" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="95" y="210" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="110" y="190" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="125" y="210" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="140" y="190" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="155" y="210" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="170" y="190" width="30" height="30" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="185" y="210" font-size="13" text-anchor="middle" fill="currentColor">9</text>
<rect x="50" y="40" width="90" height="90" fill="none" stroke="currentColor" stroke-width="3"/>
<text x="307" y="70" font-size="14" text-anchor="middle" fill="currentColor">filter (Sobel-x)</text>
<rect x="262" y="85" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="277" y="105" font-size="13" text-anchor="middle" fill="currentColor">-1</text>
<rect x="292" y="85" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="307" y="105" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="322" y="85" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="337" y="105" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<rect x="262" y="115" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="277" y="135" font-size="13" text-anchor="middle" fill="currentColor">-2</text>
<rect x="292" y="115" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="307" y="135" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="322" y="115" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="337" y="135" font-size="13" text-anchor="middle" fill="currentColor">2</text>
<rect x="262" y="145" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="277" y="165" font-size="13" text-anchor="middle" fill="currentColor">-1</text>
<rect x="292" y="145" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="307" y="165" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="322" y="145" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="337" y="165" font-size="13" text-anchor="middle" fill="currentColor">1</text>
<text x="231" y="135" font-size="22" text-anchor="middle" fill="currentColor">&#8902;</text>
<text x="381" y="137" font-size="22" text-anchor="middle" fill="currentColor">=</text>
<text x="480" y="55" font-size="14" text-anchor="middle" fill="currentColor">output 4 x 4</text>
<rect x="420" y="70" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="435" y="90" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="450" y="70" width="30" height="30" fill="#eea66f" fill-opacity="0.85" stroke="currentColor" stroke-width="1"/>
<text x="465" y="90" font-size="13" text-anchor="middle" fill="currentColor">36</text>
<rect x="480" y="70" width="30" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1"/>
<text x="495" y="90" font-size="13" text-anchor="middle" fill="currentColor">36</text>
<rect x="510" y="70" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="525" y="90" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="420" y="100" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="435" y="120" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="450" y="100" width="30" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1"/>
<text x="465" y="120" font-size="13" text-anchor="middle" fill="currentColor">36</text>
<rect x="480" y="100" width="30" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1"/>
<text x="495" y="120" font-size="13" text-anchor="middle" fill="currentColor">36</text>
<rect x="510" y="100" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="525" y="120" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="420" y="130" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="435" y="150" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="450" y="130" width="30" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1"/>
<text x="465" y="150" font-size="13" text-anchor="middle" fill="currentColor">36</text>
<rect x="480" y="130" width="30" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1"/>
<text x="495" y="150" font-size="13" text-anchor="middle" fill="currentColor">36</text>
<rect x="510" y="130" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="525" y="150" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="420" y="160" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="435" y="180" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<rect x="450" y="160" width="30" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1"/>
<text x="465" y="180" font-size="13" text-anchor="middle" fill="currentColor">36</text>
<rect x="480" y="160" width="30" height="30" fill="#7ccf9a" fill-opacity="0.5" stroke="currentColor" stroke-width="1"/>
<text x="495" y="180" font-size="13" text-anchor="middle" fill="currentColor">36</text>
<rect x="510" y="160" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1"/>
<text x="525" y="180" font-size="13" text-anchor="middle" fill="currentColor">0</text>
<text x="300" y="250" font-size="13" text-anchor="middle" fill="currentColor">highlighted: 9&#183;1 + 9&#183;2 + 9&#183;1 = 36 (the six zero pixels add nothing)</text>
</svg>
<figcaption>Figure 17.1. One step of a convolution. The filter is laid over a 3 x 3 patch, the nine products are added, and the sum is one output pixel. Sliding the filter one pixel at a time fills the 4 x 4 output, which lights up exactly where the dark-to-bright edge is.</figcaption>
</figure>

Trace the first output row by hand. The patch for $y[0, 0]$ is columns 0 to 2 of rows 0 to 2, all zeros: the sum
is 0. For $y[0, 1]$ the patch is columns 1 to 3; only column 3 is bright, and it meets the filter's right column
$(1, 2, 1)$, so $y[0,1] = 9 + 18 + 9 = 36$. For $y[0, 2]$ the patch is columns 2 to 4: column 3 meets the middle
column of zeros and column 4 meets the right column, again 36. For $y[0, 3]$, columns 3 to 5 are all 9; the left
column gives $-9 - 18 - 9 = -36$ and the right column $+36$, total 0. Every row is the same:

| output column | patch columns | pixel values in patch columns | sum |
|---|---|---|---|
| 0 | 0, 1, 2 | 0, 0, 0 | 0 |
| 1 | 1, 2, 3 | 0, 0, 9 | 36 |
| 2 | 2, 3, 4 | 0, 9, 9 | 36 |
| 3 | 3, 4, 5 | 9, 9, 9 | 0 |

The response is large exactly where the edge is and zero on flat regions. The same filter turned on its side, the
Sobel filter for $y$, responds to horizontal edges and gives all zeros here, as part 2 of the program shows. A
filter is a **template**: the sum of products is the dot product of the filter with the patch, so by
[Chapter 3](03-The-Math-Toolkit.md) it is largest when the patch "points the same way" as the filter. A CNN does not
use hand-made filters: it learns them, and in 17.6 we will see that it learns edge detectors anyway.

### Size of the output: padding and stride

With an $n \times n$ image and a $k \times k$ filter, the filter fits in $n - k + 1$ positions along each axis, so the
output is $(n-k+1) \times (n-k+1)$: our $6 \times 6$ became $4 \times 4$. Two knobs change this.

**Padding** $p$ adds $p$ rows and columns of zeros around the image before sliding. With $p = (k-1)/2$ for odd $k$
the output has the same size as the input ("same" padding). Without padding, every layer shrinks the map and pixels
near the border take part in fewer outputs.

**Stride** $s$ moves the filter $s$ pixels at a time instead of 1. Stride 2 roughly halves each side of the output,
a cheap way to shrink the map.

**Claim.** With padding $p$ and stride $s$, the output side is

$$
n_{\text{out}} = \left\lfloor \frac{n + 2p - k}{s} \right\rfloor + 1 .
$$

*Proof.* The padded image has side $n + 2p$. The filter's first position starts at 0, the $t$-th (counting from 0)
at $ts$, and a position is valid when the filter fits, $ts + k \le n + 2p$, that is $t \le (n + 2p - k)/s$. The valid
$t$ are $0, 1, \dots, \lfloor (n+2p-k)/s \rfloor$, which is the claimed count. $\square$

Part 3 of the program checks the formula against the code for five cases, the last being the first layer of
ResNet: a $7 \times 7$ filter, stride 2, padding 3, turning 224 into 112.

### Channels and many filters

Real layers have many input channels and many filters. With $C$ input channels, a filter is a $C \times k \times k$
block, and the sum runs over all three indices:

$$
y[f, i, j] = b_f + \sum_{c=1}^{C} \sum_{a=0}^{k-1} \sum_{b=0}^{k-1} w[f, c, a, b] \, x[c, \, i + a, \, j + b].
$$

Here $f$ numbers the filters, $1 \le f \le F$, and $b_f$ is a bias per filter. Each filter produces one output
channel, so a layer maps $C$ channels to $F$ channels, with $F C k^2 + F$ weights, *whatever the image size*. For the
first line of the program's output, $F = 64$, $C = 3$, $k = 3$: $64 \cdot 27 + 64 = 1{,}792$. The cost in
multiplications is $F C k^2$ per output position, so $H_{\text{out}} W_{\text{out}} F C k^2$ for the layer: weights
are few, but arithmetic is not.

A $1 \times 1$ convolution ($k = 1$) is worth a moment. It looks at one pixel only, so it does not mix positions; it
mixes channels, applying the same $F \times C$ matrix at every pixel. It is a fully connected layer applied
pixel by pixel, used to change the number of channels cheaply (17.5).

### Convolution is a linear map with a special matrix

Fix the filter. Every output is a weighted sum of inputs, so $y = Ax$ for some matrix $A$ if we flatten $x$ and $y$.
Row $(i,j)$ of $A$ holds the filter's $k^2$ weights in the columns of the patch's pixels and zeros elsewhere. So $A$
is **sparse** (each row has only $k^2$ nonzeros out of $n^2$) and its rows are shifted copies of each other (the
same $k^2$ numbers). A fully connected layer is a dense matrix with every entry free; a convolution is the same kind
of map with almost all entries forced to zero and the rest forced to be equal. Seen this way, a CNN is an MLP with a
very strong, very well-chosen constraint, which is why everything from [Chapter 15](15-Neural-Networks-and-Backpropagation.md)
still applies.

## 17.3 Pooling; receptive fields; translation equivariance

**The question:** a filter sees a $3 \times 3$ window. How does the network come to recognise a whole face, which
spans a hundred pixels? And why does a shifted cat still look like a cat to it?

### Pooling

A **pooling** layer shrinks a feature map by summarising small blocks. **Max pooling** with a $2 \times 2$ window
and stride 2 replaces each non-overlapping $2 \times 2$ block by its largest value; **average pooling** by its mean.
Part 4 of the program works one example: the top-left block of

$$
\begin{bmatrix} 1 & 3 & 2 & 0 \\ 4 & 6 & 1 & 1 \\ 0 & 2 & 5 & 7 \\ 1 & 1 & 8 & 3 \end{bmatrix}
$$

is $\{1, 3, 4, 6\}$, with maximum 6 and mean 3.5; the four blocks give the max-pooled map
$\begin{bmatrix} 6 & 2 \\ 2 & 8 \end{bmatrix}$ and the average-pooled map
$\begin{bmatrix} 3.5 & 1 \\ 1 & 5.75 \end{bmatrix}$. Pooling has no weights. It does three things: it cuts the size
(and so the cost of later layers) by four; it makes later filters see a wider area; and it makes the output less
sensitive to exactly where in the block a feature was. Max pooling asks "did this feature appear anywhere in this
block?", a natural question for a detector. Many modern networks use stride-2 convolutions instead of pooling, which
does the shrinking with learned weights.

**Global pooling** takes the maximum or mean over the *whole* map, leaving one number per channel. Our tiny CNN in
17.4 ends with global max pooling: "how strongly did each detector fire anywhere?"

### Receptive fields

The **receptive field** of a unit is the set of input pixels that can affect it. A unit after one $3 \times 3$
convolution sees a $3 \times 3$ window. A unit after two sees a $5 \times 5$ window: it sees a $3 \times 3$ block of
first-layer units, and their windows, each shifted by one pixel, together cover $5 \times 5$. Figure 17.2 draws this
in one dimension.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 250" role="img" aria-label="Three rows of nine units: input, layer 1, layer 2. One unit in layer 2 is connected to three units in layer 1, which together are connected to five input units, all highlighted.">
<line x1="322" y1="62" x2="264" y2="113" stroke="#eea66f" stroke-width="2.2"/>
<line x1="322" y1="62" x2="322" y2="113" stroke="#eea66f" stroke-width="2.2"/>
<line x1="322" y1="62" x2="380" y2="113" stroke="#eea66f" stroke-width="2.2"/>
<line x1="264" y1="137" x2="206" y2="188" stroke="#eea66f" stroke-width="2.2"/>
<line x1="264" y1="137" x2="264" y2="188" stroke="#eea66f" stroke-width="2.2"/>
<line x1="264" y1="137" x2="322" y2="188" stroke="#eea66f" stroke-width="2.2"/>
<line x1="322" y1="137" x2="264" y2="188" stroke="#eea66f" stroke-width="2.2"/>
<line x1="322" y1="137" x2="322" y2="188" stroke="#eea66f" stroke-width="2.2"/>
<line x1="322" y1="137" x2="380" y2="188" stroke="#eea66f" stroke-width="2.2"/>
<line x1="380" y1="137" x2="322" y2="188" stroke="#eea66f" stroke-width="2.2"/>
<line x1="380" y1="137" x2="380" y2="188" stroke="#eea66f" stroke-width="2.2"/>
<line x1="380" y1="137" x2="438" y2="188" stroke="#eea66f" stroke-width="2.2"/>
<text x="4" y="205" font-size="13" fill="currentColor">input</text>
<circle cx="90" cy="200" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="148" cy="200" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="206" cy="200" r="12" fill="#eea66f" fill-opacity="1" stroke="currentColor" stroke-width="1"/>
<circle cx="264" cy="200" r="12" fill="#eea66f" fill-opacity="1" stroke="currentColor" stroke-width="1"/>
<circle cx="322" cy="200" r="12" fill="#eea66f" fill-opacity="1" stroke="currentColor" stroke-width="1"/>
<circle cx="380" cy="200" r="12" fill="#eea66f" fill-opacity="1" stroke="currentColor" stroke-width="1"/>
<circle cx="438" cy="200" r="12" fill="#eea66f" fill-opacity="1" stroke="currentColor" stroke-width="1"/>
<circle cx="496" cy="200" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="554" cy="200" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="4" y="130" font-size="13" fill="currentColor">layer 1</text>
<circle cx="90" cy="125" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="148" cy="125" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="206" cy="125" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="264" cy="125" r="12" fill="#eea66f" fill-opacity="1" stroke="currentColor" stroke-width="1"/>
<circle cx="322" cy="125" r="12" fill="#eea66f" fill-opacity="1" stroke="currentColor" stroke-width="1"/>
<circle cx="380" cy="125" r="12" fill="#eea66f" fill-opacity="1" stroke="currentColor" stroke-width="1"/>
<circle cx="438" cy="125" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="496" cy="125" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="554" cy="125" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="4" y="55" font-size="13" fill="currentColor">layer 2</text>
<circle cx="90" cy="50" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="148" cy="50" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="206" cy="50" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="264" cy="50" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="322" cy="50" r="12" fill="#eea66f" fill-opacity="1" stroke="currentColor" stroke-width="1"/>
<circle cx="380" cy="50" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="438" cy="50" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="496" cy="50" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<circle cx="554" cy="50" r="12" fill="#9cc9ea" fill-opacity="0.45" stroke="currentColor" stroke-width="1"/>
<text x="322" y="235" font-size="13" text-anchor="middle" fill="currentColor">receptive field: 5 input positions</text>
</svg>
<figcaption>Figure 17.2. Receptive fields grow with depth. Each unit of a 3-wide convolution sees 3 units below it; one unit two layers up sees 5 input positions. With stride or pooling in between, the field grows faster.</figcaption>
</figure>

To count in general, let $r_\ell$ be the receptive field side after layer $\ell$ and $j_\ell$ the **jump**: how many
input pixels apart two neighbouring units of layer $\ell$ are. The input has $r_0 = 1$, $j_0 = 1$.

**Claim.** A layer with kernel $k_\ell$ and stride $s_\ell$ (convolution or pooling) gives

$$
r_\ell = r_{\ell-1} + (k_\ell - 1)\, j_{\ell-1}, \qquad j_\ell = j_{\ell-1}\, s_\ell .
$$

*Proof.* A unit of layer $\ell$ reads $k_\ell$ consecutive units of layer $\ell - 1$ along each axis. Consecutive
units there have receptive fields of side $r_{\ell-1}$, each starting $j_{\ell-1}$ input pixels after the previous one.
The first of the $k_\ell$ starts at some position $q$ and the last at $q + (k_\ell - 1) j_{\ell-1}$, and it ends
$r_{\ell-1}$ pixels later, so together they cover $(k_\ell - 1) j_{\ell-1} + r_{\ell-1}$ pixels with no gaps (gaps
would need $j_{\ell-1} > r_{\ell-1}$, which the recurrence never produces when every $k_\ell \ge s_\ell$, as in every
standard network). Neighbouring units of layer $\ell$ are $s_\ell$ units of layer $\ell-1$ apart, which is
$s_\ell j_{\ell-1}$ input pixels. $\square$

Part 5 of the program runs the recurrence for a small VGG-like stack, conv, conv, pool, conv, conv, pool, conv:
the field grows $3, 5, 6, 10, 14, 16, 24$. Notice that after each pooling, every later $3 \times 3$ conv adds 4 or
8 pixels instead of 2: shrinking the map makes each later filter cover more of the image. The program also checks
the first two steps by brute force: a single bright input pixel, pushed through two $3 \times 3$ convolutions of
ones, changes exactly 25 outputs, a $5 \times 5$ block. Deep networks reach receptive fields of hundreds of pixels this
way, enough to see whole objects, while every single filter stays small.

### Translation equivariance

Write $T_d$ for the operation "shift the image $d$ pixels to the right": $(T_d x)[i, j] = x[i, j - d]$. A map $F$ is
**equivariant** to shifts if shifting the input shifts the output by the same amount, $F(T_d x) = T_d F(x)$, and
**invariant** if shifting the input does not change the output at all, $F(T_d x) = F(x)$. For recognising *what*
is in a picture we want invariance; for finding *where* it is (17.7) we want equivariance.

**Theorem.** Convolution with any filter $w$ (stride 1) is equivariant to shifts, on an infinite grid or a grid that
wraps around at the edges.

*Proof.* Let $y = w \star x$ be the convolution. Then

$$
\begin{aligned}
(w \star T_d x)[i, j] &= \sum_{a,b} w[a, b] \, (T_d x)[i + a, \, j + b]
= \sum_{a,b} w[a, b] \, x[i + a, \, j + b - d] \\
&= y[i, \, j - d] = (T_d \, y)[i, j]. \qquad \square
\end{aligned}
$$

The proof uses only that the same weights $w[a,b]$ are applied at every position: weight sharing *is*
equivariance. Applying an elementwise function such as ReLU keeps equivariance (shifting then squashing each number
is the same as squashing then shifting), so a stack of stride-1 convolutions and activations is equivariant too.
On a finite image the border spoils this a little, because a shifted image has new pixels at one edge, so the
equality holds for every output whose window stays inside the image. Part 6 of the program checks it on a blob
placed away from the edges.

**Pooling and invariance.** Stride breaks exact equivariance. A $2 \times 2$ pool with stride 2 commutes with shifts by
2 pixels (the blocks move by one), but a shift by 1 pixel moves features across block boundaries and changes the
pooled map in a way that is not a shift. The program shows exactly this: shifting the input by 2 moves the pooled
map by 1 block, while shifts of 1 or 3 give pooled maps that are neither unchanged nor shifted. **Global** pooling,
on the other hand, is invariant: if $h$ is an equivariant feature map then
$\max_{i,j} (T_d h)[i,j] = \max_{i,j} h[i,j]$, since shifting only relabels the positions over which the maximum is
taken. The program's global maximum is 1.508 at every shift. That is how our tiny CNN recognises bars in the right
half after training only on the left: equivariant detectors, then global max pooling.

A widely read caution: in large real networks, small shifts can still change predictions noticeably, because strides
and pooling break equivariance in the way just shown (Azulay and Weiss, 2019; Zhang, 2019). "CNNs are shift
invariant" is true of the ideal, not exactly of every trained model.

## 17.4 Backprop through convolution

**The question:** to train filters with gradient descent we need $\partial L / \partial w$ and, to pass the error to
earlier layers, $\partial L / \partial x$. What are they?

Let $y = w \star x$ (one channel, stride 1, no padding), and suppose backpropagation has already given us
$\delta[i, j] = \partial L / \partial y[i, j]$ for every output. The chain rule from
[Chapter 15](15-Neural-Networks-and-Backpropagation.md) says: to get the derivative with respect to any variable, add,
over every output it affects, (derivative of $L$ with respect to that output) times (derivative of that output with
respect to the variable).

**Gradient for the filter.** The weight $w[a,b]$ appears in every output $y[i,j]$, multiplied by $x[i+a, j+b]$, so

$$
\frac{\partial L}{\partial w[a, b]} = \sum_{i, j} \delta[i, j] \, x[i + a, \, j + b].
$$

That is itself a cross-correlation: of the input $x$ with the error map $\delta$ used as the filter. Because the
weights are shared, their gradient is a *sum* over all positions, each position contributing what it would contribute
if it had its own copy of the weights.

**Gradient for the input.** The pixel $x[p, q]$ appears in output $y[i,j]$ when $p = i + a$ and $q = j + b$ for some
valid $a, b$, with coefficient $w[p - i, q - j]$. So

$$
\frac{\partial L}{\partial x[p, q]} = \sum_{i, j} \delta[i, j] \, w[p - i, \, q - j],
$$

summed over the $(i,j)$ for which $w[p-i, q-j]$ exists. Look at the indices: $p - i$, a minus sign. This is a true
convolution (with the flip) of $\delta$ with $w$, taken over every overlap, a "full" convolution, which is the same as
padding $\delta$ with $k-1$ zeros and cross-correlating with the filter rotated by 180 degrees. Another way to say
it: each $\delta[i,j]$ "stamps" a copy of $w$, scaled by $\delta[i,j]$, onto the input-gradient at the place where its
patch was. In matrix language, the forward pass is $y = Ax$ and the backward pass is $\partial L/\partial x = A^\top
\delta$: the backward pass is the **transpose** of the forward one, and the transpose of a convolution is a
convolution with the flipped filter.

### A hand-worked example

Take a $3 \times 3$ input, a $2 \times 2$ filter, and an error map that is 1 on the diagonal:

$$
x = \begin{bmatrix} 1 & 2 & 0 \\ 0 & 1 & 3 \\ 2 & 1 & 1 \end{bmatrix}, \qquad
w = \begin{bmatrix} 1 & 0 \\ -1 & 2 \end{bmatrix}, \qquad
\delta = \begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}.
$$

Forward: $y[0,0] = 1 \cdot 1 + 2 \cdot 0 + 0 \cdot (-1) + 1 \cdot 2 = 3$, and likewise $y[0,1] = 7$, $y[1,0] = 0$,
$y[1,1] = 2$. Filter gradient: since $\delta$ is 1 only at $(0,0)$ and $(1,1)$,
$\partial L/\partial w[a,b] = x[a, b] + x[1+a, 1+b]$, which gives

$$
\frac{\partial L}{\partial w} = \begin{bmatrix} 1+1 & 2+3 \\ 0+1 & 1+1 \end{bmatrix}
= \begin{bmatrix} 2 & 5 \\ 1 & 2 \end{bmatrix}.
$$

Input gradient: $\delta[0,0] = 1$ stamps $w$ at the top-left, $\delta[1,1] = 1$ stamps $w$ one step down and right,
and where they overlap (the centre pixel) the entries add, $2 + 1 = 3$:

$$
\frac{\partial L}{\partial x} = \begin{bmatrix} 1 & 0 & 0 \\ -1 & 2 + 1 & 0 \\ 0 & -1 & 2 \end{bmatrix}
= \begin{bmatrix} 1 & 0 & 0 \\ -1 & 3 & 0 \\ 0 & -1 & 2 \end{bmatrix}.
$$

All three results were checked with the chapter's `conv2d`, and the input gradient equals the padded convolution of
$\delta$ with $w$ rotated by 180 degrees, as the formula said.

### Backward through pooling and ReLU

Max pooling passes each block's maximum forward, so the output depends on that one input only (with slope 1), and on
the other three not at all (slope 0, as long as there are no ties). Backward, each output's gradient is **routed** to
the position that held the maximum, and the other positions get 0. The forward pass must remember where the maxima
were. Average pooling sends $1/4$ of each gradient to each of the four inputs. ReLU multiplies the gradient by 1
where its input was positive and by 0 elsewhere, as in [Chapter 15](15-Neural-Networks-and-Backpropagation.md).

### Making it fast: im2col

The double loop over positions in `conv2d` is slow in Python. The standard trick, **im2col** ("image to columns"),
copies every $C \times k \times k$ patch into one column of a big matrix $X_{\text{col}}$ of shape
$Ck^2 \times H_{\text{out}} W_{\text{out}}$. Then the whole layer is a single matrix product,
$Y = W_{\text{mat}} X_{\text{col}}$, where $W_{\text{mat}}$ is $F \times Ck^2$, one flattened filter per row. The
backward pass is two more products: $\partial L / \partial W_{\text{mat}} = \Delta X_{\text{col}}^\top$ and
$\partial L / \partial X_{\text{col}} = W_{\text{mat}}^\top \Delta$, followed by **col2im**, which adds each column
entry back to the pixel it was copied from (a pixel lies in up to $k^2$ patches, so its gradient is a sum). col2im is
the transpose of im2col, so the whole backward pass is again "the transpose of the forward pass". Libraries use
this, or the fast Fourier transform for large filters, or the Winograd minimal-filtering method for small ones; all
compute the same numbers.

The second program implements the layer this way, for batches and many channels, and checks all three gradients
against centred finite differences ([Chapter 3](03-The-Math-Toolkit.md)). Then it trains the tiny CNN of 17.1,
conv ($8$ filters, $3 \times 3$, same padding) $\to$ ReLU $\to$ global max pool $\to$ linear $\to$ softmax, with plain
mini-batch gradient descent, next to an MLP with 32 hidden units:

```python
--8<-- "books/machine-learning/ch17_cnn.py"
```

```
1. gradient check of the conv layer (loss = sum(out * R) for a fixed random R)
   dx: max relative error 9.9e-11
   dw: max relative error 9.5e-11
   db: max relative error 6.5e-11

2. horizontal / vertical / diagonal bars, trained with bars in the LEFT half only
   after 10 epochs: loss CNN 0.017  MLP 0.692
   after 20 epochs: loss CNN 0.008  MLP 0.326
   after 30 epochs: loss CNN 0.005  MLP 0.150
                              CNN     MLP
   parameters                 107    4739
   train                    1.000   0.988
   test, left half          1.000   0.757
   test, RIGHT half         0.997   0.357

3. the learned 3 x 3 filters (rounded), and which class each one votes for
   filter 0: [  1.6  -0.3  -0.1 |   1.4  -0.2  -0.2 |   1.5  -0.1  -0.3]  -> vert
   filter 1: [ -0.6  -0.0   0.3 |  -0.4   1.2   0.6 |  -0.4   0.9  -0.3]  -> vert
   filter 2: [  0.2   0.2  -0.7 |  -0.1  -1.0  -1.0 |   0.1  -0.7  -0.4]  -> diag
   filter 3: [  1.7   1.6   1.7 |  -0.5  -0.3  -0.3 |   0.2  -0.2  -0.4]  -> horiz
   filter 4: [  0.1  -0.3  -0.0 |  -0.0  -0.0  -0.1 |  -0.2  -0.5  -0.7]  -> vert
   filter 5: [  0.0   1.2  -0.3 |  -0.7  -0.0   1.6 |  -0.2  -0.5  -0.6]  -> diag
   filter 6: [ -0.3  -0.2   0.0 |   1.4  -0.5  -0.1 |  -0.5   1.5  -0.2]  -> diag
   filter 7: [ -0.3  -0.1  -0.3 |   0.2  -0.5   0.6 |  -0.1  -0.6   1.1]  -> vert

4. transfer: a NEW task (anti-diagonal vs diagonal vs horizontal, bars anywhere,
   noisier), few labelled examples; mean test accuracy over 4 runs
     examples   frozen + new head   fine-tuned   from scratch
            6               0.398        0.482          0.474
           15               0.589        0.649          0.590
           60               0.583        0.763          0.746
```

The gradient check agrees to about $10^{-10}$, which is what centred differences with step $10^{-5}$ allow. The CNN,
with 107 weights, reaches loss 0.017 after 10 epochs, while the MLP with 4,739 weights is still at 0.692; both fit
the training set, but only the CNN keeps its accuracy on new left-half images (1.000 against 0.757) and on moved
bars (0.997 against 0.357). The MLP's failure on the right half is not a lack of training: it has weights for
right-half pixels that no training example ever pushed in a useful direction. Parts 3 and 4 of the output are
discussed in 17.6.

## 17.5 Architectures: LeNet, AlexNet, VGG, ResNet

**The question:** how do we stack these layers? The history of CNNs is mostly a history of answers, each one a
paper whose idea is now standard. Figure 17.3 shows how depth grew.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 600 275" role="img" aria-label="Bar chart on a log scale of the number of layers with weights: LeNet-5 7, AlexNet 8, VGG-19 19, GoogLeNet 22, ResNet-152 152.">
<text x="160" y="38" font-size="13" text-anchor="end" fill="currentColor">LeNet-5 (1998)</text>
<rect x="170" y="23" width="139.6" height="22" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
<text x="317.6" y="38" font-size="13" fill="currentColor">7</text>
<text x="160" y="78" font-size="13" text-anchor="end" fill="currentColor">AlexNet (2012)</text>
<rect x="170" y="63" width="149.1" height="22" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
<text x="327.1" y="78" font-size="13" fill="currentColor">8</text>
<text x="160" y="118" font-size="13" text-anchor="end" fill="currentColor">VGG-19 (2014)</text>
<rect x="170" y="103" width="211.2" height="22" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
<text x="389.2" y="118" font-size="13" fill="currentColor">19</text>
<text x="160" y="158" font-size="13" text-anchor="end" fill="currentColor">GoogLeNet (2014)</text>
<rect x="170" y="143" width="221.7" height="22" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
<text x="399.7" y="158" font-size="13" fill="currentColor">22</text>
<text x="160" y="198" font-size="13" text-anchor="end" fill="currentColor">ResNet-152 (2015)</text>
<rect x="170" y="183" width="360.3" height="22" fill="#7ccf9a" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
<text x="538.3" y="198" font-size="13" fill="currentColor">152</text>
<line x1="170" y1="225" x2="550" y2="225" stroke="currentColor" stroke-width="1"/>
<line x1="170.0" y1="221" x2="170.0" y2="229" stroke="currentColor" stroke-width="1"/>
<text x="170.0" y="244" font-size="12" text-anchor="middle" fill="currentColor">1</text>
<line x1="335.1" y1="221" x2="335.1" y2="229" stroke="currentColor" stroke-width="1"/>
<text x="335.1" y="244" font-size="12" text-anchor="middle" fill="currentColor">10</text>
<line x1="500.3" y1="221" x2="500.3" y2="229" stroke="currentColor" stroke-width="1"/>
<text x="500.3" y="244" font-size="12" text-anchor="middle" fill="currentColor">100</text>
<text x="360.0" y="263" font-size="12" text-anchor="middle" fill="currentColor">layers with weights (log scale)</text>
</svg>
<figcaption>Figure 17.3. Depth of the landmark networks, as counted in their papers. Residual connections made the jump from about twenty layers to more than a hundred possible.</figcaption>
</figure>

### LeNet-5 (1998)

LeCun, Bottou, Bengio and Haffner's "Gradient-based learning applied to document recognition" (1998) describes
**LeNet-5**, a network for $32 \times 32$ images of handwritten digits. Its pattern is the one every CNN since has
followed: convolution, subsampling, convolution, subsampling, then fully connected layers.

| layer | operation | output |
|---|---|---|
| input | grey digit | $1 \times 32 \times 32$ |
| C1 | 6 filters $5 \times 5$ | $6 \times 28 \times 28$ |
| S2 | $2 \times 2$ subsampling | $6 \times 14 \times 14$ |
| C3 | 16 filters $5 \times 5$ | $16 \times 10 \times 10$ |
| S4 | $2 \times 2$ subsampling | $16 \times 5 \times 5$ |
| C5 | 120 filters $5 \times 5$ | $120 \times 1 \times 1$ |
| F6 | fully connected | 84 |
| output | one unit per digit | 10 |

Each size follows from the output-size formula: $32 - 5 + 1 = 28$, halved to 14, $14 - 5 + 1 = 10$, halved to 5,
$5 - 5 + 1 = 1$. The paper reports about 60,000 trainable parameters. Its subsampling layers averaged each block and
then multiplied by a trainable coefficient, and its activations were scaled tanh functions. LeNet-style networks
were deployed to read cheques, and the paper also describes the MNIST database of handwritten digits, still a standard first test.

### AlexNet (2012)

For years after, CNNs stayed a niche: other methods, such as SVMs on hand-designed features ([Chapter 10](10-Support-Vector-Machines.md)),
did as well on the small datasets of the time, and large CNNs were too slow to train. Two things changed: the
**ImageNet** dataset (Deng et al., 2009), with over a million labelled photographs in 1000 classes for its annual
challenge, and graphics processors (GPUs) programmable for general arithmetic.

Krizhevsky, Sutskever and Hinton's "ImageNet classification with deep convolutional neural networks" (2012),
known as **AlexNet**, has five convolutional and three fully connected layers, 60 million parameters and 650,000
neurons, as the paper states. It was trained on two GPUs. The paper reports a top-5 test error of 15.3% in the
ILSVRC-2012 competition, against 26.2% for the second-best entry ("top-5 error" means the true class was not among
the model's five highest-scoring guesses). Its ingredients were mostly known individually; the paper showed what
they did together at scale:

- **ReLU** activations instead of tanh, which the paper reports trained several times faster ([Chapter 16](16-Training-Deep-Networks.md)).
- **Dropout** in the fully connected layers (Srivastava et al., 2014, in its journal form) against overfitting.
- **Data augmentation**: random crops and horizontal flips of the training images, and colour changes.
- An efficient GPU implementation of convolution.

This result is widely taken as the start of the deep-learning era in computer vision ([Chapter 1](01-What-Is-Machine-Learning.md)).

### VGG (2014): small filters, deep stacks

Simonyan and Zisserman's "Very deep convolutional networks for large-scale image recognition" (2014) asked a
simple question: what if every convolution is $3 \times 3$, and we just stack more of them? Their networks of 16 and
19 weight layers (VGG-16, VGG-19) use only $3 \times 3$ convolutions with stride 1 and $2 \times 2$ max pooling,
doubling the channels (64, 128, 256, 512) after each pooling.

Their argument for small filters is the receptive-field recurrence of 17.3. Two stacked $3 \times 3$ convolutions see
a $5 \times 5$ window, and three see $7 \times 7$. With $C$ channels in and out, two $3 \times 3$ layers have
$2 \cdot 9 C^2 = 18 C^2$ weights against $25 C^2$ for one $5 \times 5$; three $3 \times 3$ layers have $27 C^2$
against $49 C^2$ for one $7 \times 7$, 45% fewer. The stack also puts a non-linearity between the layers, so it can
represent more functions. VGG-16 has about 138 million parameters (the paper's table), most of them in the fully
connected layers at the end.

### ResNet (2015): depth that trains

Stacking more layers should never hurt in principle: a deeper network could copy a shallower one and make its extra
layers compute the identity. In practice, He, Zhang, Ren and Sun found that on the CIFAR-10 image dataset, plain networks of 56
layers had *higher training error* than networks of 20 layers, which is not overfitting but an optimisation failure.
Their paper "Deep residual learning for image recognition" (2016; posted 2015) fixed it with the **residual block**
of [Chapter 16](16-Training-Deep-Networks.md): the block computes $x + F(x)$, where $F$ is two or three convolutions
with batch normalisation. If the best thing a block can do is nothing, it only has to learn $F = 0$, which is easy,
and the gradient flows back through the "$+ x$" path unchanged.

Deep ResNets use a **bottleneck** block: a $1 \times 1$ convolution cuts 256 channels to 64, a $3 \times 3$ works on
the 64, and another $1 \times 1$ brings them back to 256. That costs $256 \cdot 64 + 9 \cdot 64 \cdot 64 + 64 \cdot 256
= 69{,}632$ weights, against $9 \cdot 256 \cdot 256 = 589{,}824$ for a single $3 \times 3$ convolution at 256
channels, about 8.5 times fewer. ResNets end with global average pooling and one fully connected layer instead of
VGG's large dense layers. The paper reports networks up to 152 layers on ImageNet, and that an ensemble of them
reached 3.57% top-5 error on the ImageNet test set, winning ILSVRC 2015. Residual connections are now everywhere,
including inside every transformer ([Chapter 19](19-Transformers.md)).

Other landmarks are worth one line each: GoogLeNet (Szegedy et al., 2015) with parallel "inception" branches of
different filter sizes; batch normalisation (Ioffe and Szegedy, 2015); MobileNets (Howard et al., 2017) with
depthwise-separable convolutions for phones; EfficientNet (Tan and Le, 2019), which scales depth, width and image
size together. Vision transformers ([Chapter 19](19-Transformers.md)) now compete with CNNs on large datasets, and
CNNs remain strong and cheap on smaller ones.

## 17.6 Transfer learning; what filters learn

**The question:** training AlexNet took a million labelled images. You have three hundred photographs of your own.
Can you still use a CNN?

### What filters learn

Part 3 of the program prints the eight $3 \times 3$ filters our tiny CNN learned, and the class each one votes for
most strongly in the final layer. Nobody told it what to look for, yet several are recognisable. Filter 3 has a row of
large positive weights $(1.7, 1.6, 1.7)$ on top and small negatives below: a horizontal-line detector, and it votes
"horizontal". Filter 0 has a column $(1.6, 1.4, 1.5)$ on the left: a vertical-line detector, voting "vertical".
Filter 6 has its large weights at positions $(1,0)$ and $(2,1)$, a short diagonal, voting "diagonal". Others are less
clean, as learned filters usually are, and some are nearly unused.

The same happens at scale. Krizhevsky et al. (2012) show the 96 first-layer filters of AlexNet (their Figure 3):
oriented edges at many angles, and colour blobs. Zeiler and Fergus (2014) projected the activations of deeper layers
back to pixel space and found textures and parts in middle layers and object-like patterns deeper. Yosinski, Clune,
Bengio and Lipson (2014) measured "how transferable" each layer is and found that early layers are general (they
help on other tasks almost unchanged) and the last layers specific to the training task.

Three ways to look inside a trained CNN, all using only the tools of this chapter:

- **Show the filters.** Only meaningful for the first layer, whose filters live in pixel space.
- **Activation maximisation.** Start from a random image and run gradient *ascent* on the pixels to make one unit
  fire as strongly as possible; the backward pass of 17.4 gives $\partial(\text{unit})/\partial x$. Without a
  penalty for noise the result is usually unreadable static, a reminder that a unit's "preferred image" is not
  obviously what it detects.
- **Saliency maps.** For one image, show $|\partial (\text{class score}) / \partial x|$ per pixel (Simonyan et al.,
  2013): which pixels would change the score most. [Chapter 22](22-Machine-Learning-in-Practice.md) discusses why
  such maps can mislead.

### Transfer learning

**Transfer learning** reuses a network trained on one task (the **source**, usually ImageNet) for another (the
**target**). Two common recipes:

1. **Feature extraction.** Keep every convolutional layer frozen (no updates), remove the last layer, and train a new
   last layer on the target data. Only a few thousand weights are learned, so a few hundred examples can be enough.
2. **Fine-tuning.** Start from the pretrained weights, replace the last layer, and train everything on the target
   data, usually with a small learning rate so the useful features are adjusted rather than destroyed.

Part 4 of the program tries both on a new task: tell anti-diagonal, diagonal and horizontal bars apart, now anywhere
in the image and with twice the noise, from only 6, 15 or 60 labelled examples. "From scratch" trains a fresh CNN
on the same examples. Read the table honestly. With 6 examples nothing works well (the numbers are near chance, 0.33,
to about 0.48, and vary a lot between runs). With 15, starting from the learned filters helps: fine-tuning reaches
0.649 against 0.590 from scratch. With 60, fine-tuning and training from scratch are about equal, while frozen
features stall at 0.583. Why do frozen features stall? The source task never contained anti-diagonal bars, so no
frozen filter detects them; the new head can only combine the detectors it was given. That is the general lesson in
miniature: transfer helps most when data is scarce and the source task needed features the target also needs, and
freezing is limited by what the source taught. Real ImageNet features are general enough that feature extraction
works surprisingly often, which is why it is the first thing practitioners try.

## 17.7 Beyond classification: detection, segmentation (U-Net 2015)

*Level: advanced.*

**The question:** classification answers "what is in this image?". A rover, a car or a radiologist needs "where is
each thing?" (detection) or "which pixels are which?" (segmentation).

### Object detection

A **detector** outputs a list of boxes, each with a class and a confidence score. A box is usually given by its
corners $(x_1, y_1, x_2, y_2)$. Two pieces of bookkeeping are needed by every detector, and the third program builds
both.

**Intersection over union.** To say whether a predicted box matches a true one, compute

$$
\operatorname{IoU}(A, B) = \frac{\text{area}(A \cap B)}{\text{area}(A \cup B)} ,
$$

which is 1 for identical boxes and 0 for disjoint ones. For $A = (0,0,4,4)$ and $B = (2,2,6,6)$, the overlap is the
$2 \times 2$ square $(2,2,4,4)$, area 4, and the union is $16 + 16 - 4 = 28$, so IoU $= 1/7 \approx 0.143$. A
prediction usually counts as correct when IoU $\ge 0.5$ with a true box of the same class; the standard summary
score, **mean average precision** (mAP), averages the area under the precision-recall curve
([Chapter 7](07-Evaluating-Models.md)) over classes, and in some benchmarks over several IoU thresholds.

**Non-maximum suppression.** A detector usually fires several overlapping boxes on one object. Greedy NMS keeps the
highest-scoring box, deletes every remaining box whose IoU with it exceeds a threshold, and repeats. In the program's
example, box 0 (score 0.90) overlaps boxes 1 and 2 with IoU 0.82 and 0.86, so both are deleted; box 4 (0.85)
overlaps box 3 with IoU 0.79, so box 3 is deleted; boxes 0 and 4 remain, one per object.

```python
--8<-- "books/machine-learning/ch17_detection.py"
```

```
1. intersection over union
   A=(0, 0, 4, 4) B=(2, 2, 6, 6): overlap 4, union 28, IoU = 0.1429
   A with itself: 1.0; A with (5, 5, 7, 7): 0.0

2. non-maximum suppression (threshold 0.5)
   box 0: (10, 10, 50, 50) score 0.90
   box 1: (12, 12, 52, 52) score 0.75
   box 2: (8, 11, 48, 49) score 0.80
   box 3: (60, 60, 90, 95) score 0.70
   box 4: (62, 58, 92, 93) score 0.85
   kept: [0, 4]   (one box per object)

3. a strided convolution shrinks; its transpose grows
   1-D conv, kernel [1. 2. 1.], stride 2: maps length 8 -> 3; matrix C is (3, 8)
   C =
       1  2  1  0  0  0  0  0
       0  0  1  2  1  0  0  0
       0  0  0  0  1  2  1  0
   transposed conv of [1, 0, 0] = [1. 2. 1. 0. 0. 0. 0. 0.]
   equals C^T y for random y? True
   <Cx, y> = -1.680905,  <x, C^T y> = -1.680905

4. segmentation scores on a 6 x 6 mask
   true pixels 12, predicted 12, both 9
   pixel IoU = 0.600, Dice = 0.750
```

How the boxes are proposed is where detectors differ. The oldest idea is a **sliding window**: run a classifier on
every window at several sizes. A CNN does this almost for free: by equivariance, a network made only of convolutions
and pooling, run on a larger image, outputs a *map* of class scores, one per window position, sharing all the
computation between overlapping windows. **R-CNN** (Girshick et al., 2014) classified about two thousand proposed
regions per image with a CNN; **Fast R-CNN** (Girshick, 2015) shared the convolutional features between regions;
**Faster R-CNN** (Ren et al., 2015) let the network propose the regions itself. **YOLO** (Redmon et al., 2016) and
**SSD** (Liu et al., 2016) skip proposals and predict boxes and classes for every cell of a coarse grid in one pass,
trading some accuracy for speed. Many later detectors are refinements of these two families.

### Semantic segmentation and U-Net

**Semantic segmentation** labels every pixel with a class: road, rock, sky. The output must have the size of the
input, but a classification CNN shrinks the image by pooling. The **fully convolutional network** of Long,
Shelhamer and Darrell (2015) replaced the dense layers with convolutions and **upsampled** the coarse score map back
to full size.

Upsampling with learned weights uses the **transposed convolution**. Take a stride-$s$ convolution as a matrix $C$,
which maps a long vector to a short one. Its transpose $C^\top$ maps short to long. Part 3 of the program writes the
$3 \times 8$ matrix of a 1-D convolution with kernel $(1, 2, 1)$ and stride 2, implements the transposed convolution
directly (each input value stamps a scaled copy of the kernel into the output, $s$ steps apart), and checks that it
equals $C^\top y$ and satisfies $\langle Cx, y\rangle = \langle x, C^\top y\rangle$. This is the same operation as
the input-gradient of 17.4: the backward pass of a strided convolution is a transposed convolution, so libraries get
the layer for free. (The older name "deconvolution" is misleading: it does not invert the convolution.)

Ronneberger, Fischer and Brox's **U-Net** (2015), designed for biomedical images with few training examples, has the
shape in Figure 17.4: an **encoder** that halves the size and doubles the channels four times, a **decoder** that
upsamples with "up-convolutions" and halves the channels, and **skip connections** that copy each encoder stage's
feature map across and join it (by concatenating channels) to the decoder stage of the same size.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 580 265" role="img" aria-label="The U shape of U-Net: three encoder stages going down with 64, 128 and 256 channels, a 512-channel bottom, three decoder stages going up with 256, 128 and 64 channels, and dashed skip connections joining each encoder stage to the decoder stage at the same size.">
<rect x="40" y="40" width="40" height="70" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="60" y="126" font-size="12" text-anchor="middle" fill="currentColor">64</text>
<rect x="110" y="90" width="40" height="55" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="130" y="161" font-size="12" text-anchor="middle" fill="currentColor">128</text>
<rect x="180" y="140" width="40" height="40" fill="#9cc9ea" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="200" y="196" font-size="12" text-anchor="middle" fill="currentColor">256</text>
<rect x="250" y="185" width="40" height="28" fill="#eea66f" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="270" y="229" font-size="12" text-anchor="middle" fill="currentColor">512</text>
<rect x="320" y="140" width="40" height="40" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="340" y="196" font-size="12" text-anchor="middle" fill="currentColor">256</text>
<rect x="390" y="90" width="40" height="55" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="410" y="161" font-size="12" text-anchor="middle" fill="currentColor">128</text>
<rect x="460" y="40" width="40" height="70" fill="#7ccf9a" fill-opacity="0.7" stroke="currentColor" stroke-width="1"/>
<text x="480" y="126" font-size="12" text-anchor="middle" fill="currentColor">64</text>
<line x1="80" y1="75.0" x2="106" y2="117.5" stroke="currentColor" stroke-width="1.3"/>
<circle cx="106" cy="117.5" r="2.5" fill="currentColor"/>
<line x1="150" y1="117.5" x2="176" y2="160.0" stroke="currentColor" stroke-width="1.3"/>
<circle cx="176" cy="160.0" r="2.5" fill="currentColor"/>
<line x1="220" y1="160.0" x2="246" y2="199.0" stroke="currentColor" stroke-width="1.3"/>
<circle cx="246" cy="199.0" r="2.5" fill="currentColor"/>
<line x1="290" y1="199.0" x2="316" y2="160.0" stroke="currentColor" stroke-width="1.3"/>
<circle cx="316" cy="160.0" r="2.5" fill="currentColor"/>
<line x1="360" y1="160.0" x2="386" y2="117.5" stroke="currentColor" stroke-width="1.3"/>
<circle cx="386" cy="117.5" r="2.5" fill="currentColor"/>
<line x1="430" y1="117.5" x2="456" y2="75.0" stroke="currentColor" stroke-width="1.3"/>
<circle cx="456" cy="75.0" r="2.5" fill="currentColor"/>
<line x1="80" y1="52" x2="460" y2="52" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4"/>
<line x1="150" y1="102" x2="390" y2="102" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4"/>
<line x1="220" y1="152" x2="320" y2="152" stroke="#eea66f" stroke-width="2" stroke-dasharray="6 4"/>
<text x="12" y="30" font-size="13" fill="currentColor">image</text>
<text x="560" y="30" font-size="13" text-anchor="end" fill="currentColor">mask</text>
<text x="120" y="250" font-size="13" text-anchor="middle" fill="currentColor">encoder: conv and pool</text>
<text x="430" y="250" font-size="13" text-anchor="middle" fill="currentColor">decoder: up-convolution</text>
<text x="270" y="35" font-size="13" text-anchor="middle" fill="currentColor">skip connections (copy and join)</text>
</svg>
<figcaption>Figure 17.4. The U-Net idea. The encoder shrinks the image and grows the channels, so units see context; the decoder grows it back to full size. Skip connections hand the fine detail from each encoder level straight across to the decoder level of the same size. (Channel numbers as in the original paper; it has four levels, three are drawn.)</figcaption>
</figure>

Why the skips? The deep, small maps know *what* is in a region (their receptive fields are large), but pooling has
thrown away *where* exactly the boundaries are. The early, large maps still have the fine detail. Joining them lets
each decoder stage combine context with precise position. The paper also relied heavily on data augmentation
(elastic deformations) to train from a few dozen annotated images. U-Net-shaped networks remain standard in medical
imaging, and the same shape is the denoising network inside many diffusion models ([Chapter 20](20-Generative-Models.md)).

Segmentation is scored per pixel. With $T$ the set of true pixels of a class and $P$ the predicted ones, the pixel
IoU is $|T \cap P| / |T \cup P|$ and the **Dice coefficient** is $2|T \cap P| / (|T| + |P|)$. The program's masks
have 12 pixels each and share 9, so IoU $= 9/15 = 0.6$ and Dice $= 18/24 = 0.75$. Dice is never smaller than IoU,
since $D = 2J/(1+J)$ for $J$ the IoU.

### A real example: terrain on Mars

Rovers on Mars are driven with commands sent hours ahead, since a signal takes between about 3 and 22 minutes each
way, and they must judge terrain for themselves between commands. Rothrock and colleagues at NASA's Jet Propulsion
Laboratory described **SPOC** (Soil Property and Object Classification, 2016), a fully convolutional network that
labels each pixel of rover and orbital images with a terrain class such as sand, bedrock or rock, to support route
planning and assess where wheels might slip. It is segmentation exactly as in this section, applied where nobody can
look at the picture in time.

## Check yourself

??? question "1. LeNet's input is 32 x 32. Follow it through a 5 x 5 conv (no padding), 2 x 2 pooling, a 5 x 5 conv and 2 x 2 pooling. What are the sizes?"

    By $n_{\text{out}} = \lfloor (n + 2p - k)/s \rfloor + 1$: $32 - 5 + 1 = 28$; pooling with $k = s = 2$ gives
    $\lfloor 26/2 \rfloor + 1 = 14$; $14 - 5 + 1 = 10$; pooling gives 5. These are the C1, S2, C3, S4 sizes of the
    table in 17.5.

??? question "2. How many weights (with biases) has a 3 x 3 convolution from 64 to 128 channels? Does it depend on the image size?"

    $F C k^2 + F = 128 \cdot 64 \cdot 9 + 128 = 73{,}856$. It does not depend on the image size: the same filters are
    used at every position. The *cost* in multiplications does: it is $H_{\text{out}} W_{\text{out}} \cdot 73{,}728$.

??? question "3. A layer has a 56 x 56 output, 64 input and 64 output channels and 3 x 3 filters. How many multiplications does one forward pass take?"

    $56 \cdot 56 \cdot 9 \cdot 64 \cdot 64 = 115{,}605{,}504$, about $1.2 \times 10^8$, for a layer with only
    $36{,}864$ weights. CNNs are cheap in memory for weights and expensive in arithmetic.

??? question "4. Compute the receptive field of three stacked 3 x 3 convolutions with stride 1. Then of a 'dilated' stack with dilations 1, 2, 4."

    With $j = 1$ throughout, $r = 1 + 2 + 2 + 2 = 7$. A dilated (or "atrous") convolution with dilation $d$ spaces
    its 3 taps $d$ pixels apart, so it acts like a kernel of side $2d + 1$ with holes: it adds $(k-1)d = 2d$ to the
    field. Dilations 1, 2, 4 give $r = 1 + 2 + 4 + 8 = 15$ with the same 27 weights per channel pair, without any
    pooling, which is why dilated convolutions are used when the output must stay full size.

??? question "5. Show that two stacked 3 x 3 convolutions without an activation between them are equivalent to a single 5 x 5 convolution. Why do real networks still stack them?"

    Each is linear and equivariant, so the composition is too; writing it out,
    $(v \star (w \star x))[i,j] = \sum_{a,b} v[a,b] \sum_{c,d} w[c,d]\, x[i+a+c, j+b+d]$, and grouping by
    $u = a + c$, $t = b + d$ (each from 0 to 4) gives one $5 \times 5$ filter $q[u,t] = \sum v[a,b] w[u-a, t-b]$.
    So without a non-linearity nothing is gained except fewer parameters ($18 C^2$ against $25 C^2$, and the
    product filters are a restricted family). With a ReLU in between, the stack computes non-linear functions a
    single linear filter cannot, which is the real reason.

??? question "6. Prove that a convolution with stride 2 is equivariant to shifts by 2 pixels but not, in general, to shifts by 1."

    With stride 2, $y[i] = \sum_a w[a] x[2i + a]$. Shift by 2: $\sum_a w[a] x[2i + a - 2] = \sum_a w[a] x[2(i-1)+a] =
    y[i-1]$, the output shifted by 1. Shift by 1: $\sum_a w[a] x[2i + a - 1]$ samples the odd positions that $y$
    never used, so in general it is not any shift of $y$. Example: $w = (1)$ (a $1 \times 1$ filter), $x = (1, 0, 0, 0)$:
    $y = (1, 0)$; shifting $x$ by 1 gives $(0, 1, 0, 0)$ and output $(0, 0)$, which is not a shift of $(1, 0)$.

??? question "7. Write the code: the backward pass of 2 x 2 max pooling with stride 2, for one 2-D map, and check it numerically."

    ```python
    import numpy as np

    def maxpool_forward(x):
        H, W = x.shape[0] // 2, x.shape[1] // 2
        blocks = x[:2*H, :2*W].reshape(H, 2, W, 2).transpose(0, 2, 1, 3).reshape(H, W, 4)
        arg = blocks.argmax(axis=2)                 # remember where each max was
        return blocks.max(axis=2), arg

    def maxpool_backward(dout, arg, shape):
        dx = np.zeros(shape)
        H, W = dout.shape
        for i in range(H):
            for j in range(W):
                a, b = divmod(arg[i, j], 2)          # position inside the 2x2 block
                dx[2*i + a, 2*j + b] = dout[i, j]   # route the gradient there
        return dx

    rng = np.random.default_rng(1)
    x = rng.normal(size=(4, 6)); R = rng.normal(size=(2, 3))
    y, arg = maxpool_forward(x)
    g = maxpool_backward(R, arg, x.shape)
    num = np.zeros_like(x); h = 1e-6
    for idx in np.ndindex(x.shape):
        xp = x.copy(); xp[idx] += h; xm = x.copy(); xm[idx] -= h
        num[idx] = (np.sum(maxpool_forward(xp)[0] * R) - np.sum(maxpool_forward(xm)[0] * R)) / (2 * h)
    print(np.abs(num - g).max())                    # about 1e-10
    ```

    Random inputs have no ties, so the numerical and analytic gradients agree; at a tie the maximum is not
    differentiable and libraries pick one position.

??? question "8. Compute the IoU of boxes (0, 0, 2, 2) and (1, 0, 3, 2). With NMS threshold 0.5, would the lower-scoring one survive?"

    Overlap: $x$ from 1 to 2, $y$ from 0 to 2, area 2. Union: $4 + 4 - 2 = 6$. IoU $= 1/3$. Since $1/3 \le 0.5$,
    NMS keeps both: they are treated as different objects. Whether that is right depends on the data, which is why the
    threshold is tuned.

??? question "9. A ResNet bottleneck maps 256 channels to 64 with a 1 x 1 conv. How many weights is that, and what does a 1 x 1 conv compute?"

    $256 \cdot 64 + 64 = 16{,}448$ with biases. At each pixel it multiplies the 256-vector of channel values by the
    same $64 \times 256$ matrix: a fully connected layer over channels, applied independently at every position. It
    mixes channels and never mixes positions.

??? question "10. Our tiny CNN ends with global max pooling. If we replaced it with flattening plus a fully connected layer, what would happen on the moved bars, and why?"

    The flattened map keeps position: the head would have separate weights for features at each position, and the
    weights for right-half positions would only have been trained on noise. The network would lose its invariance and
    behave much more like the MLP on moved bars. Equivariant features alone are not enough; the final step must
    throw position away (global pooling) for the classifier to be invariant.

??? question "11. Derive the input-gradient formula of 17.4 for stride 1 and show it is a cross-correlation of the zero-padded error map with the filter rotated by 180 degrees."

    From $y[i,j] = \sum_{a,b} w[a,b] x[i+a, j+b]$, $\partial y[i,j]/\partial x[p,q] = w[p-i, q-j]$ when
    $0 \le p - i, q - j \le k - 1$. So $\partial L/\partial x[p,q] = \sum_{i,j} \delta[i,j] w[p-i, q-j]$. Pad $\delta$
    with $k - 1$ zeros on every side, call it $\tilde\delta$ with $\tilde\delta[u,v] = \delta[u - k + 1, v - k + 1]$,
    and let $\tilde w[a,b] = w[k-1-a, k-1-b]$. Then
    $\sum_{a,b} \tilde w[a,b]\, \tilde\delta[p + a, q + b] = \sum_{a,b} w[k-1-a, k-1-b]\, \delta[p+a-k+1, q+b-k+1]$;
    put $i = p + a - k + 1$, so $k - 1 - a = p - i$, and similarly for $j$: this is $\sum_{i,j} w[p-i, q-j]\,\delta[i,j]$,
    the same sum. The hand example in 17.4 checks it numerically.

??? question "12. Why does the transposed convolution of a stride-2 convolution produce a 'checkerboard' pattern when its kernel has length 3?"

    Each input stamps the kernel $(1, 2, 1)$ at positions $2i, 2i+1, 2i+2$. Odd output positions receive one stamp
    (the middle weight 2), even interior positions receive two stamps (the end weights 1 and 1, from neighbouring
    inputs). With a constant input of 1 the output is $1, 2, 2, 2, 2, 2, 1, 0$: here the sums happen to match, but for a
    general kernel $(a, b, c)$ odd positions get $b$ and even ones $a + c$, which differ, giving a stripe that
    alternates every pixel. In 2-D this is the checkerboard artefact; Odena, Dumoulin and Olah (2016) analysed it and
    suggested resizing followed by an ordinary convolution instead.

## What you learned

- Fully connected layers on images need huge numbers of weights and learn nothing that carries over between
  positions; convolution builds in locality and weight sharing, with $FCk^2 + F$ weights per layer at any image size.
- A convolution slides a small filter and takes dot products; its output side is $\lfloor (n + 2p - k)/s \rfloor + 1$,
  and it is a sparse, shared-weight linear map.
- Receptive fields grow by $(k-1) \times$ jump per layer, and pooling or stride multiplies the jump; this is how small
  filters come to see whole objects.
- Weight sharing is translation equivariance, proved; global pooling turns it into invariance, while strides keep it
  only for shifts by multiples of the stride.
- The backward pass of a convolution is two more convolutions: input-with-error for the filter, and the transposed
  (flipped) convolution for the input; im2col makes all three matrix products.
- LeNet set the pattern, AlexNet showed it at scale on GPUs, VGG showed that deep stacks of $3 \times 3$ filters work,
  and ResNet's residual blocks made 100+ layers trainable.
- Pretrained features transfer to new tasks with little data; detection adds IoU and non-maximum suppression, and
  segmentation (U-Net) adds an upsampling decoder with skip connections.

**Next:** [Chapter 18](18-Sequence-Models.md), sequence models, which do for time what convolution did for space:
the same weights at every step, now with a memory.

## Further reading

- I. Goodfellow, Y. Bengio and A. Courville, *Deep Learning*, 2016: chapter 9 (convolutional networks).
- Y. LeCun, L. Bottou, Y. Bengio and P. Haffner, "Gradient-based learning applied to document recognition",
  *Proceedings of the IEEE* 86(11), 1998.
- Y. LeCun et al., "Backpropagation applied to handwritten zip code recognition", *Neural Computation* 1(4), 1989.
- K. Fukushima, "Neocognitron: a self-organizing neural network model for a mechanism of pattern recognition
  unaffected by shift in position", *Biological Cybernetics* 36, 1980.
- D. H. Hubel and T. N. Wiesel, "Receptive fields, binocular interaction and functional architecture in the cat's
  visual cortex", *Journal of Physiology* 160, 1962.
- A. Krizhevsky, I. Sutskever and G. E. Hinton, "ImageNet classification with deep convolutional neural networks",
  NeurIPS 2012.
- K. Simonyan and A. Zisserman, "Very deep convolutional networks for large-scale image recognition", 2014 (ICLR 2015).
- K. He, X. Zhang, S. Ren and J. Sun, "Deep residual learning for image recognition", CVPR 2016.
- M. D. Zeiler and R. Fergus, "Visualizing and understanding convolutional networks", ECCV 2014; J. Yosinski,
  J. Clune, Y. Bengio and H. Lipson, "How transferable are features in deep neural networks?", NeurIPS 2014.
- R. Girshick, J. Donahue, T. Darrell and J. Malik, "Rich feature hierarchies for accurate object detection and
  semantic segmentation", CVPR 2014; S. Ren, K. He, R. Girshick and J. Sun, "Faster R-CNN", NeurIPS 2015;
  J. Redmon, S. Divvala, R. Girshick and A. Farhadi, "You only look once", CVPR 2016.
- J. Long, E. Shelhamer and T. Darrell, "Fully convolutional networks for semantic segmentation", CVPR 2015;
  O. Ronneberger, P. Fischer and T. Brox, "U-Net: convolutional networks for biomedical image segmentation",
  MICCAI 2015.
- V. Dumoulin and F. Visin, "A guide to convolution arithmetic for deep learning", 2016 (sizes, strides, padding and
  transposed convolutions, with pictures).
- A. Azulay and Y. Weiss, "Why do deep convolutional networks generalize so poorly to small image
  transformations?", *Journal of Machine Learning Research* 20, 2019; R. Zhang, "Making convolutional networks
  shift-invariant again", ICML 2019.
- B. Rothrock, R. Kennedy, C. Cunningham, J. Papon, M. Heverly and M. Ono, "SPOC: deep learning-based terrain
  classification for Mars rover missions", AIAA SPACE 2016.
- On this site: [Chapter 15](15-Neural-Networks-and-Backpropagation.md), [Chapter 16](16-Training-Deep-Networks.md),
  [Chapter 19](19-Transformers.md) (vision transformers), and the FFT, which computes large convolutions fast, in
  the Algorithms book's [Chapter 11](../algorithms/11-Divide-and-Conquer.md).
