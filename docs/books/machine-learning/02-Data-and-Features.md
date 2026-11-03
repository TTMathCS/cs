# 2. Data and features

*A learner sees the world only through the numbers we give it. If a column is wrong, missing or measured in a silly
unit, the cleverest algorithm learns the wrong thing; if the split between training and test data lets answers leak
through, the scores we report are fiction. This chapter is about the raw material. You will learn what kinds of
features there are, how to clean a messy table, how to turn categories and words into numbers, why scaling matters
(and prove it for gradient descent), how to build new features from old ones, how to split data so that test scores
mean something, and how to look at data before modelling it.*

!!! abstract "In this chapter"
    **You will learn:**

    - the anatomy of a dataset: rows, columns, labels, and the kinds of features (numeric, categorical, ordinal, text,
      images)
    - how to handle missing values, outliers and duplicates, and why the median is more robust than the mean
    - one-hot, ordinal and hashed encodings, with the collision count of the hashing trick worked out
    - standardisation and min-max scaling, and a proof that badly scaled features slow gradient descent
    - feature engineering: logs, ratios, interactions and cyclic features
    - random, stratified, time-based and group-based splits, and how data leakage produces scores that are too good
      to be true
    - summary statistics, histograms and correlation, and why you must also plot (Anscombe's quartet)

    **You need:** [Chapter 1](01-What-Is-Machine-Learning.md) (training, validation and test sets; nearest
    neighbours). Means and medians from school. Some statistics helps; see
    [math.akadian.ca/books/statistics](https://math.akadian.ca/books/statistics/).

    **Levels:** 2.1 to 2.3 are beginner; 2.4 is beginner with an intermediate proof; 2.5 to 2.7 are beginner to
    intermediate.

## 2.1 Rows, columns, labels

What does a dataset look like to a learner? Almost always, like a table. Each **row** is one example: one flat for
sale, one patient, one image, one email. Each **column** is one thing measured about every example. One column, or
sometimes several, is the thing we want to predict, the **label** or **target**; the rest are the **features**.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 250" role="img" aria-label="A table with six columns: id, area, rooms, district, condition and price. The first five data columns are shaded as features and labelled X; the price column is shaded as the label y. One row is highlighted and labelled one example, x sub i and y sub i. Above the feature columns their kinds are written: numeric, numeric count, categorical, ordinal.">
  <text x="270" y="22" font-size="13" text-anchor="middle" fill="currentColor">features: the matrix X (n rows, m columns)</text>
  <text x="560" y="22" font-size="13" text-anchor="middle" fill="currentColor">label y</text>
  <rect x="120" y="32" width="380" height="186" fill="#9cc9ea" fill-opacity="0.2" stroke="none"/>
  <rect x="500" y="32" width="120" height="186" fill="#7ccf9a" fill-opacity="0.25" stroke="none"/>
  <text x="165" y="50" font-size="11" text-anchor="middle" fill="currentColor">numeric</text>
  <text x="260" y="50" font-size="11" text-anchor="middle" fill="currentColor">count</text>
  <text x="355" y="50" font-size="11" text-anchor="middle" fill="currentColor">categorical</text>
  <text x="450" y="50" font-size="11" text-anchor="middle" fill="currentColor">ordinal</text>
  <text x="560" y="50" font-size="11" text-anchor="middle" fill="currentColor">numeric</text>
  <text x="70" y="78" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">id</text>
  <text x="165" y="78" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">area (m²)</text>
  <text x="260" y="78" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">rooms</text>
  <text x="355" y="78" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">district</text>
  <text x="450" y="78" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">condition</text>
  <text x="560" y="78" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">price (k)</text>
  <line x1="20" y1="88" x2="620" y2="88" stroke="currentColor"/>
  <text x="70" y="110" font-size="13" text-anchor="middle" fill="currentColor">1</text>
  <text x="165" y="110" font-size="13" text-anchor="middle" fill="currentColor">52</text>
  <text x="260" y="110" font-size="13" text-anchor="middle" fill="currentColor">2</text>
  <text x="355" y="110" font-size="13" text-anchor="middle" fill="currentColor">north</text>
  <text x="450" y="110" font-size="13" text-anchor="middle" fill="currentColor">good</text>
  <text x="560" y="110" font-size="13" text-anchor="middle" fill="currentColor">210</text>
  <rect x="22" y="120" width="596" height="28" fill="#eea66f" fill-opacity="0.35" stroke="currentColor"/>
  <text x="70" y="139" font-size="13" text-anchor="middle" fill="currentColor">2</text>
  <text x="165" y="139" font-size="13" text-anchor="middle" fill="currentColor">75</text>
  <text x="260" y="139" font-size="13" text-anchor="middle" fill="currentColor">3</text>
  <text x="355" y="139" font-size="13" text-anchor="middle" fill="currentColor">south</text>
  <text x="450" y="139" font-size="13" text-anchor="middle" fill="currentColor">fair</text>
  <text x="560" y="139" font-size="13" text-anchor="middle" fill="currentColor">255</text>
  <text x="70" y="170" font-size="13" text-anchor="middle" fill="currentColor">3</text>
  <text x="165" y="170" font-size="13" text-anchor="middle" fill="currentColor">40</text>
  <text x="260" y="170" font-size="13" text-anchor="middle" fill="currentColor">1</text>
  <text x="355" y="170" font-size="13" text-anchor="middle" fill="currentColor">north</text>
  <text x="450" y="170" font-size="13" text-anchor="middle" fill="currentColor">poor</text>
  <text x="560" y="170" font-size="13" text-anchor="middle" fill="currentColor">140</text>
  <text x="320" y="200" font-size="13" text-anchor="middle" fill="currentColor">...</text>
  <text x="320" y="240" font-size="12" text-anchor="middle" fill="currentColor">highlighted row: one example, its features x_i and its label y_i (here i = 2)</text>
</svg>
<figcaption>A dataset as a table. Rows are examples; the feature columns form the matrix X and the label column is
the vector y. The id column is neither: it names the row and must not be used as a feature.</figcaption>
</figure>

In symbols, with $n$ examples and $m$ features, example $i$ has a feature vector $x_i=(x_{i1},\dots,x_{im})$ and a
label $y_i$. Stacking the feature vectors as rows gives an $n\times m$ table of numbers, the **feature matrix** $X$;
the labels form a list $y$ of length $n$. Chapter 3 calls $X$ a matrix and $y$ a vector and gives them their algebra.
For now the picture is enough: one row per example, one column per feature.

Notice the column `id`. It identifies the row but says nothing about the flat. A learner given `id` as a feature
might find a pattern in it by accident (for instance, if newer listings got higher ids and prices rose over time),
and that pattern would not carry over to new flats. Columns that are bookkeeping, not measurement, stay out of $X$.

### Kinds of features

Features come in a few kinds, and the kind decides how we may turn them into numbers. The psychologist S. S. Stevens
gave the classic classification of measurement scales in 1946; machine learning uses a simplified version.

- **Numeric** (or quantitative) features are numbers for which differences mean something: area in square metres,
  temperature, price. Some are **continuous** (any value in a range); some are **counts** (whole numbers, such as
  rooms). Arithmetic on them makes sense: a flat of 80 m² is 20 m² larger than one of 60 m².
- **Categorical** (or nominal) features take one of a set of values with no order: district, colour, country. "North"
  is not bigger than "south". The only meaningful question is "same or different".
- **Ordinal** features have an order but no meaningful distance: condition "poor < fair < good", school grades,
  survey answers from "strongly disagree" to "strongly agree". We know good is better than fair, but not whether the
  step from poor to fair equals the step from fair to good.
- **Text** is a sequence of words or characters of any length: a product review, an email.
- **Images** are grids of pixels, each pixel one number (grey level) or three (red, green, blue). A 28 by 28 grey image
  is 784 numbers; a colour photo of 1000 by 1000 pixels is three million.
- **Dates and times** look numeric but hide structure: day of week, month and hour repeat in cycles, and a date often
  matters through what happened before it.

Text and images do not fit in a fixed number of columns by themselves. Classic machine learning turns them into
fixed-length feature vectors by hand (word counts, edge detectors); deep learning (Part IV) learns that conversion as
part of the model. Either way, the learner finally sees a table of numbers.

### Where data comes from

Every dataset was collected by someone, for some purpose, in some way, and that history is part of the data. A table
of flats from one estate agent's website covers the flats that agent sells. Patients' records from one hospital
cover the patients who came to that hospital. Labels were written by people who could be tired, rushed or
inconsistent. Before modelling, it pays to ask: who collected this, how, and which examples are missing? The
answers decide what the model can be trusted on. Chapter 22 returns to this under the name "distribution shift".

## 2.2 Cleaning: missing values, outliers, duplicates

What do real tables look like before anyone tidies them? Here is a small made-up table of twelve flats, typed in the
way real data often is: with gaps, a repeated row and a typing error.

| id | area (m²) | rooms | district | condition | price (thousands) |
|---|---|---|---|---|---|
| 1 | 52 | 2 | north | good | 210 |
| 2 | 75 | 3 | south | fair | 255 |
| 3 | 40 | 1 | north | poor | 140 |
| 4 | 98 | 4 | east | good | 390 |
| 5 | (missing) | 2 | south | good | 205 |
| 6 | 63 | 3 | east | (missing) | 240 |
| 7 | 7500 | 3 | north | fair | 260 |
| 8 | 45 | 2 | south | fair | 170 |
| 9 | 88 | (missing) | east | good | 335 |
| 10 | 58 | 2 | north | good | 230 |
| 8 | 45 | 2 | south | fair | 170 |
| 11 | 70 | 3 | south | poor | 215 |

```python
--8<-- "books/machine-learning/ch02_cleaning.py"
```

Output:

```
12 rows
after dropping exact duplicates: 11 rows
  missing in area_m2  : 1
  missing in rooms    : 1
  missing in district : 0
  missing in condition: 1
  missing in price_k  : 0
area values: [40, 45, 52, 58, 63, 70, 75, 88, 98, 7500]
area mean = 808.9, median = 66.5
quartiles 53.5, 66.5, 84.75; Tukey fences [6.625, 131.625]
outside the fences: [7500]
z-scores: [-0.34, -0.33, -0.34, -0.32, -0.33, 3.0, -0.34, -0.32, -0.34, -0.33]
after the fix: mean = 66.4, median = 66.5
fill values: area 66.5, rooms 2.5, condition 'good'
id area rooms district condition price | missing flags
 1    52    2  north   good     210 | 0 0 0
 2    75    3  south   fair     255 | 0 0 0
 3    40    1  north   poor     140 | 0 0 0
 4    98    4  east    good     390 | 0 0 0
 5  66.5    2  south   good     205 | 1 0 0
 6    63    3  east    good     240 | 0 0 1
 7    75    3  north   fair     260 | 0 0 0
 8    45    2  south   fair     170 | 0 0 0
 9    88  2.5  east    good     335 | 0 1 0
10    58    2  north   good     230 | 0 0 0
11    70    3  south   poor     215 | 0 0 0
```

We go through the three problems in the order the program handles them.

### Duplicates

Row 8 appears twice. **Exact duplicates** are easy to find: compare whole rows, as `drop_duplicates` does with a set
of tuples (a [hash table](../../data-structures/hash-table.md), so it takes time proportional to the number of rows;
[Chapter 7 of the Algorithms book](../algorithms/07-Searching-and-Hashing.md) explains why). Why do duplicates
matter? Within the training set, a duplicated row simply counts twice, which slightly distorts the fit. The serious
damage happens when one copy lands in the training set and the other in the test set: then the test set contains an
example the model has already seen, and the test score is too good. With real data, duplicates are often not exact:
the same flat listed twice with slightly different text, the same photo resized. Finding **near-duplicates** is
harder and needs a similarity measure; Chapter 9 discusses fast neighbour search, which is the tool for it.

Not every repeat is a mistake. Two different flats may honestly have the same area, rooms, district, condition and
price. Here the `id` column tells us that row 8 really is one flat entered twice. Without such a key, deciding is a
judgement call, and you should write down what you decided.

### Missing values

Three cells are empty. What should we do? First, ask *why* a value is missing, because it changes what is safe. The
statistician Donald Rubin (1976) named three cases.

- **Missing completely at random**: the gap has nothing to do with any value, for example a page lost at random.
  Dropping such rows loses data but does not bias what remains.
- **Missing at random**: the chance of a gap depends on other *recorded* columns, for example older listings in one
  district never recorded the area. Then the other columns help to fill the gap sensibly.
- **Missing not at random**: the chance of a gap depends on the missing value itself, for example sellers of very
  small flats leave the area blank. Then the very fact that the value is missing carries information, and filling in
  an average hides it.

The usual tools, from crude to careful:

1. **Drop rows** with any missing value. Simple, and fine if few rows are affected and the gaps are random. With many
   columns, almost every row may have some gap, and you lose most of the data.
2. **Drop a column** that is mostly empty.
3. **Impute**: fill each gap with a typical value from the column, the **mean** or **median** for numbers, the
   **mode** (most common value) for categories. The program fills area with the median 66.5, rooms with the median
   2.5, and condition with the mode "good".
4. **Add a missing-value indicator**: a new 0/1 column saying "this value was filled in". The model can then learn
   whether being missing matters, which handles the not-at-random case. The program adds three such flags.
5. **Model-based imputation**: predict the missing value from the other columns with a small model (even
   nearest neighbours). Better, more work, and it must be fitted on training data only.

The last point applies to all of them: **compute imputation values from the training set only**, and reuse those
same values on validation, test and future data. If you compute the median from all the data, information from the
test set has flowed into the training process, a small case of the leakage studied in 2.6.

Look again at the filled-in rooms value, 2.5. A flat cannot have two and a half rooms. For a numeric model this is
harmless, it is a reasonable "middle" guess; but it is a reminder that imputed values are guesses, not data.

### Outliers

The area of flat 7 is 7500 m². A seven-thousand-square-metre flat with three rooms for 260 thousand is not plausible;
the price and rooms say it is about 75 m², and somebody left out the decimal point. An **outlier** is a value far from
the others. Some outliers are errors like this one; others are real and important (the one patient with an extreme
reaction, the one fraud). The rule is: **find them automatically, decide about them with knowledge**. Never delete
extreme values just because they are extreme.

Finding them needs a sense of "far". Look at what the single bad value does to the mean: with it, the mean area is
808.9 m², larger than every honest flat. The median, the middle value, is 66.5 with or without it. The median is
**robust**: to move it arbitrarily far you must corrupt half the data. The mean is not: one bad value can move it
anywhere. Statisticians say the mean has **breakdown point** 0 and the median has breakdown point $1/2$.

**The z-score rule and its blind spot.** A common rule flags a value as an outlier if it is more than 3 standard
deviations from the mean. The **standard deviation** $\sigma$ measures spread: the square root of the average squared
distance from the mean, $\sigma=\sqrt{\tfrac1n\sum_i(x_i-\bar x)^2}$, where $\bar x$ is the mean. The **z-score** of a
value is $z=(x-\bar x)/\sigma$, the number of standard deviations it lies from the mean. The program prints the
z-scores, and the obvious error, 7500, has $z$ just below 3.0 (it is 2.9999). The rule fails to flag it. That is no
accident.

**Claim.** In any list of $n$ numbers, no z-score is larger in size than $\sqrt{n-1}$.

**Proof.** Write $d_i=x_i-\bar x$ for the deviations. They add up to zero, so $d_1=-(d_2+\dots+d_n)$. By the
Cauchy-Schwarz inequality (the square of a sum of $n-1$ numbers is at most $n-1$ times the sum of their squares;
Chapter 3 proves it),

$$
d_1^2=(d_2+\dots+d_n)^2\le(n-1)(d_2^2+\dots+d_n^2)=(n-1)(n\sigma^2-d_1^2).
$$

Moving $d_1^2$ to the left gives $n\,d_1^2\le(n-1)\,n\sigma^2$, so $|d_1|/\sigma\le\sqrt{n-1}$. The same holds for
every $i$. $\square$

With $n=10$ areas, no z-score can exceed $\sqrt9=3$, however wrong a value is. The outlier inflates the standard
deviation by so much that it hides itself. This is called **masking**. The fix is to measure spread robustly.

**Tukey's fences.** The **quartiles** $Q_1$, $Q_2$, $Q_3$ split the sorted data into four equal parts ($Q_2$ is the
median). The **interquartile range** is $\mathrm{IQR}=Q_3-Q_1$, the width of the middle half of the data. John Tukey's
rule, from his book *Exploratory Data Analysis* (1977), flags anything outside

$$
\bigl[\,Q_1-1.5\,\mathrm{IQR},\;Q_3+1.5\,\mathrm{IQR}\,\bigr].
$$

For the areas, $Q_1=53.5$ and $Q_3=84.75$ (quartiles can be computed in a few slightly different ways; the program
uses one standard method), so $\mathrm{IQR}=31.25$ and the fences are $[6.625,\,131.625]$. Only 7500 is outside. Like
the median, the quartiles hardly move when one value goes wild, so the bad value cannot hide itself.

Once flagged, an outlier gets a decision: correct it (we checked: 75 m²), remove the row, cap the value at the fence
(called **winsorising**), or keep it and use a method that is not thrown by it (Chapter 4 shows how squared error
lets one point drag a fitted line). After the correction, the mean (66.4) and median (66.5) agree again.

## 2.3 Encoding: one-hot, ordinal, hashing

How do we feed "north", "south" and "east" to a learner that only does arithmetic? The tempting answer is to number
them: east = 0, north = 1, south = 2. That is usually a mistake. Numbers have order and distance, so this encoding
tells the model that north lies between east and south, and that south is twice as far from east as north is. For
nearest neighbours it makes south-to-east distances bigger than north-to-east ones; for a linear model it forces the
effect of district to grow in equal steps from east to north to south. None of that is true. The numbering made up
facts.

### One-hot encoding

**One-hot encoding** gives each category its own column, which is 1 if the example has that category and 0
otherwise. With three districts we get three columns.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 210" role="img" aria-label="On the left, a column of districts: north, south, north, east. An arrow leads to three columns headed east, north, south. Each row has a single 1, in the column of its district, and zeros elsewhere: north is 0 1 0, south is 0 0 1, east is 1 0 0. On the right, the ordinal condition column poor, fair, good maps to 0, 1, 2.">
  <text x="70" y="30" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">district</text>
  <text x="70" y="62" font-size="13" text-anchor="middle" fill="currentColor">north</text>
  <text x="70" y="92" font-size="13" text-anchor="middle" fill="currentColor">south</text>
  <text x="70" y="122" font-size="13" text-anchor="middle" fill="currentColor">north</text>
  <text x="70" y="152" font-size="13" text-anchor="middle" fill="currentColor">east</text>
  <line x1="115" y1="100" x2="160" y2="100" stroke="currentColor" stroke-width="1.5"/>
  <polygon points="168,100 158,95 158,105" fill="currentColor"/>
  <text x="140" y="90" font-size="11" text-anchor="middle" fill="currentColor">one-hot</text>
  <text x="210" y="30" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">east</text>
  <text x="270" y="30" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">north</text>
  <text x="330" y="30" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">south</text>
  <rect x="245" y="45" width="50" height="26" fill="#eea66f" fill-opacity="0.55" stroke="currentColor"/>
  <rect x="305" y="75" width="50" height="26" fill="#eea66f" fill-opacity="0.55" stroke="currentColor"/>
  <rect x="245" y="105" width="50" height="26" fill="#eea66f" fill-opacity="0.55" stroke="currentColor"/>
  <rect x="185" y="135" width="50" height="26" fill="#eea66f" fill-opacity="0.55" stroke="currentColor"/>
  <text x="210" y="62" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="270" y="62" font-size="13" text-anchor="middle" fill="currentColor">1</text>
  <text x="330" y="62" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="210" y="92" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="270" y="92" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="330" y="92" font-size="13" text-anchor="middle" fill="currentColor">1</text>
  <text x="210" y="122" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="270" y="122" font-size="13" text-anchor="middle" fill="currentColor">1</text>
  <text x="330" y="122" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="210" y="152" font-size="13" text-anchor="middle" fill="currentColor">1</text>
  <text x="270" y="152" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="330" y="152" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="270" y="190" font-size="12" text-anchor="middle" fill="currentColor">exactly one 1 per row; every pair of districts is at the same distance</text>
  <line x1="410" y1="20" x2="410" y2="170" stroke="currentColor" stroke-opacity="0.3"/>
  <text x="480" y="30" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">condition</text>
  <text x="590" y="30" font-size="13" text-anchor="middle" font-weight="bold" fill="currentColor">ordinal</text>
  <text x="480" y="62" font-size="13" text-anchor="middle" fill="currentColor">poor</text>
  <text x="480" y="92" font-size="13" text-anchor="middle" fill="currentColor">fair</text>
  <text x="480" y="122" font-size="13" text-anchor="middle" fill="currentColor">good</text>
  <line x1="515" y1="58" x2="560" y2="58" stroke="currentColor"/>
  <polygon points="566,58 558,54 558,62" fill="currentColor"/>
  <line x1="515" y1="88" x2="560" y2="88" stroke="currentColor"/>
  <polygon points="566,88 558,84 558,92" fill="currentColor"/>
  <line x1="515" y1="118" x2="560" y2="118" stroke="currentColor"/>
  <polygon points="566,118 558,114 558,122" fill="currentColor"/>
  <text x="590" y="62" font-size="13" text-anchor="middle" fill="currentColor">0</text>
  <text x="590" y="92" font-size="13" text-anchor="middle" fill="currentColor">1</text>
  <text x="590" y="122" font-size="13" text-anchor="middle" fill="currentColor">2</text>
  <text x="535" y="150" font-size="12" text-anchor="middle" fill="currentColor">order is real, so keep it</text>
</svg>
<figcaption>One-hot encoding for a category without order (left), and an ordinal code for a category with a real
order (right).</figcaption>
</figure>

Now every pair of different districts differs in exactly two columns, so they are all at the same distance
$\sqrt2$, and a linear model gets one separate number (one weight) per district, free to take any value. That is
exactly the information a category carries: same or different.

```python
--8<-- "books/machine-learning/ch02_encoding.py"
```

Output:

```
one-hot columns: ['east', 'north', 'south']
  north  -> [0 1 0]
  south  -> [0 0 1]
  north  -> [0 1 0]
  east   -> [1 0 0]
  south  -> [0 0 1]
  east   -> [1 0 0]
unseen district 'west' -> [0 0 0]
ordinal condition: [2, 1, 0, 2, 2, 1]

hashing trick, 8 buckets
  dust    hash = 2408302639  bucket 7  sign -
  storm   hash = 1297260451  bucket 3  sign +
  near    hash = 3472553267  bucket 3  sign -
  the     hash = 1916724902  bucket 6  sign +
  crater  hash = 2015642778  bucket 2  sign +
  rover   hash = 2029142491  bucket 3  sign +
  panel   hash =  956067131  bucket 3  sign +
  covered hash =  612096219  bucket 3  sign +
  in      hash = 1823041677  bucket 5  sign +
  'dust storm near the crater'    -> [ 0  0  1  0  0  0  1 -1]
  'rover panel covered in dust'   -> [ 0  0  0  3  0  1  0 -1]
1000 words into  1024 buckets: 484 colliding pairs (expected 487.8)
1000 words into 65536 buckets: 9 colliding pairs (expected 7.6)
```

Three practical points.

**The list of categories comes from the training set.** A new flat in a district never seen in training, "west",
gets all zeros: the model has nothing to say about it specifically, which is honest. Real systems sometimes add an
explicit "other" column for rare and unseen categories.

**The dummy-variable trap.** The three one-hot columns always add up to 1 in every row. If the model also has a
constant column of 1s (the intercept of a linear model, Chapter 4), then one column is the constant minus the other
two, and the columns are not independent. A linear model then has infinitely many equally good solutions (Chapter 4
explains why that breaks the exact solution). The usual fix is to drop one category, which becomes the **reference
category**: with east dropped, the north and south weights measure the difference from east. Methods with a penalty
on the weights (Chapter 8) cope with the full set.

**Width.** One-hot makes one column per category. For district that is three. For "postcode" it could be tens of
thousands, most of them seen only a few times. That is where the next two ideas come in.

### Ordinal encoding

Condition has a real order, poor < fair < good, and throwing it away wastes information. **Ordinal encoding** maps
the categories to 0, 1, 2 in order. It assumes the steps are equal, which may not be true, but it is often a good
compromise; if you doubt it, you can use one-hot and let the model learn each level separately. Use ordinal codes only
for categories whose order you know from the meaning, never the alphabetical order of their names.

### The hashing trick

Some features have a huge or open-ended set of values: words in emails, product codes, user names. One-hot needs a
**vocabulary**, a table from each value to its column, which can be enormous and which must be updated every time a
new word appears. The **hashing trick**, popularised for machine learning by Weinberger and colleagues (2009), skips
the vocabulary. Pick a number of **buckets** $b$. Send each value to column $h(\text{value}) \bmod b$, where $h$ is a
**hash function**: a fixed function that turns any string into a large, random-looking whole number. (Python's
built-in `hash` changes from run to run for strings, so the program uses a fixed hash from the standard library's
`hashlib`.) A text becomes a vector of $b$ counts, one per bucket, whatever words it contains.

The price is **collisions**: different words can land in the same bucket, and the model cannot tell them apart. In
the output, "storm", "near", "rover", "panel" and "covered" all land in bucket 3 of 8. How bad is this? With $b$
buckets and $m$ distinct words, and a hash that behaves like a random choice of bucket:

**Claim.** The expected number of pairs of distinct words that share a bucket is $\binom m2/b=m(m-1)/(2b)$.

**Proof.** For each of the $\binom m2$ pairs of words, define an indicator that is 1 if the two share a bucket. The
second word lands in the first one's bucket with probability $1/b$, so each indicator has expected value $1/b$. The
number of colliding pairs is the sum of the indicators, and the expected value of a sum is the sum of the expected
values (this is **linearity of expectation**, which holds even though the indicators are not independent; Chapter 3
explains expectation). So the expectation is $\binom m2\cdot\frac1b$. $\square$

For 1000 words in 1024 buckets that is $499500/1024\approx487.8$ pairs, and the program counts 484; in $2^{16}=65536$
buckets it is about 7.6, and the program counts 9. So collisions are frequent when $b$ is close to $m$ and rare when
$b$ is much larger. This is the birthday problem from probability: collisions start when $b$ is about $m^2$, not $m$.
In practice $b$ is set to something like $2^{18}$ or $2^{20}$, and the model is sparse enough that the few
collisions cost little accuracy.

**Signed hashing.** Look at the first text, "dust storm near the crater". "Storm" adds $+1$ to bucket 3 and "near" adds
$-1$, so bucket 3 ends at 0. The program uses a second hash bit to choose a sign $s(\text{word})=\pm1$ for each word.
This looks like it makes things worse, but it fixes a bias. When we compare two texts by multiplying their vectors
entry by entry and adding up (the dot product of Chapter 3, the basic measure of similarity), collisions without
signs always *add* spurious similarity. With random signs, a collision between two different words adds $+1$ or $-1$
with equal probability, so on average it adds nothing: the expected dot product of the hashed vectors equals the
dot product of the original word-count vectors (Weinberger et al. 2009 prove this and bound the variance). The
errors remain, but they cancel on average instead of piling up.

### Text and images, briefly

The vector of word counts used above, ignoring word order, is called a **bag of words**. It is crude, "dog bites man"
and "man bites dog" get the same vector, but it was the standard representation for text classification for decades,
and Chapter 12 builds a spam filter on it. Images are already numbers: a grey image of $h\times w$ pixels can be
flattened row by row into a vector of $hw$ numbers. Flattening throws away which pixels are neighbours, which is why
Chapter 17's convolutional networks, which keep the grid, do so much better on images.

## 2.4 Scaling: standardisation and min-max

Does it matter whether area is measured in square metres or square centimetres? For some learners not at all; for
others it changes everything. Nearest neighbours is in the second group. Distance adds squared differences across
features, so a feature with large numbers dominates. If area is in square centimetres (so 75 m² is 750 000) and rooms
are counted in ones, a difference of one room is invisible next to a difference of 1 cm² of floor. The neighbours are
then found by area alone, purely because of the unit we happened to pick.

**Scaling** puts all features on a comparable footing. Two methods cover most uses.

- **Standardisation**: subtract the mean and divide by the standard deviation, $z=(x-\mu)/\sigma$. Afterwards every
  feature has mean 0 and standard deviation 1, and a value of $z=2$ means "two standard deviations above average",
  whatever the original unit.
- **Min-max scaling**: map the smallest value to 0 and the largest to 1, $x'=(x-\min)/(\max-\min)$. Every feature then
  lies in $[0,1]$. It is simple, but a single outlier squeezes all other values into a small part of the range.

As with imputation, **the mean, standard deviation, minimum and maximum are computed on the training set** and reused
unchanged for every later example. The last line of the program's output standardises a new flat with the training
values; computing a new mean from the test set would make the same flat get different numbers depending on what else
was in its batch.

```python
--8<-- "books/machine-learning/ch02_scaling.py"
```

Output:

```
raw feature means [69.88  2.8 ] sds [19.16  1.04]
standardised means [0. 0.] sds [1. 1.]
min-max ranges [0. 0.] [1. 1.]
raw           condition number      75269.5   steps to converge: None
min-max       condition number        127.8   steps to converge: 880
standardised  condition number          6.8   steps to converge: 44
new flat standardised with the training mean and sd: [[0.789 0.197]]
```

The program fits the same model three times, a straight-line formula $\text{price}\approx w_0+w_1\cdot
\text{area}+w_2\cdot\text{rooms}$, by **gradient descent**: start with all weights zero, and repeatedly move them a
small step in the direction that reduces the average squared error fastest. (Chapter 4 derives the formula for the
step; Chapter 5 studies the method in depth.) It counts the steps until the error is within a millionth of the best
possible. With raw features it has not converged after 200 000 steps. With min-max scaling it takes 880; with
standardisation, 44. The model is the same and the best possible fit is the same; only the units changed.

### Why gradient descent needs scaling

*Level: intermediate.*

Why should units matter to an algorithm that only walks downhill? Because it uses **one step size for every
direction**. Picture the average squared error as a landscape over the weights, a valley whose lowest point is the
best fit. If one weight multiplies a feature with large numbers, a tiny change of that weight changes the predictions a
lot, so the valley is steep in that direction. A weight on a feature with small numbers sits in a shallow direction.
The valley is a long narrow trough.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 240" role="img" aria-label="Two contour plots of a loss. Left, badly scaled features: the contours are long thin ellipses, and the gradient-descent path zigzags across the narrow direction while creeping slowly along the long one; after twelve steps it is still far from the minimum. Right, standardised features: the contours are circles and the path goes straight to the minimum in a few steps.">
  <ellipse cx="165" cy="110" rx="30.0" ry="8.7" fill="none" stroke="currentColor" stroke-opacity="0.45"/>
  <ellipse cx="165" cy="110" rx="60.0" ry="17.3" fill="none" stroke="currentColor" stroke-opacity="0.45"/>
  <ellipse cx="165" cy="110" rx="90.0" ry="26.0" fill="none" stroke="currentColor" stroke-opacity="0.45"/>
  <ellipse cx="165" cy="110" rx="132.0" ry="38.1" fill="none" stroke="currentColor" stroke-opacity="0.45"/>
  <path d="M 39.0 74.0 L 57.9 138.8 L 74.0 87.0 L 87.6 128.4 L 99.2 95.3 L 109.1 121.8 L 117.5 100.6 L 124.6 117.5 L 130.7 104.0 L 135.8 114.8 L 140.2 106.1 L 143.9 113.1 L 147.1 107.5" fill="none" stroke="#eea66f" stroke-width="2"/>
  <circle cx="39.0" cy="74.0" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="57.9" cy="138.8" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="74.0" cy="87.0" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="87.6" cy="128.4" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="99.2" cy="95.3" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="109.1" cy="121.8" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="117.5" cy="100.6" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="124.6" cy="117.5" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="130.7" cy="104.0" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="135.8" cy="114.8" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="140.2" cy="106.1" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="143.9" cy="113.1" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="147.1" cy="107.5" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="165" cy="110" r="4" fill="#7ccf9a" stroke="currentColor"/>
  <ellipse cx="475" cy="110" rx="30.0" ry="30.0" fill="none" stroke="currentColor" stroke-opacity="0.45"/>
  <ellipse cx="475" cy="110" rx="60.0" ry="60.0" fill="none" stroke="currentColor" stroke-opacity="0.45"/>
  <ellipse cx="475" cy="110" rx="84.0" ry="84.0" fill="none" stroke="currentColor" stroke-opacity="0.45"/>
  <path d="M 400.0 83.0 L 437.5 96.5 L 456.2 103.2 L 465.6 106.6 L 470.3 108.3 L 472.7 109.2 L 473.8 109.6" fill="none" stroke="#eea66f" stroke-width="2"/>
  <circle cx="400.0" cy="83.0" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="437.5" cy="96.5" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="456.2" cy="103.2" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="465.6" cy="106.6" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="470.3" cy="108.3" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="472.7" cy="109.2" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="473.8" cy="109.6" r="3" fill="#eea66f" stroke="currentColor" stroke-width="0.8"/>
  <circle cx="475" cy="110" r="4" fill="#7ccf9a" stroke="currentColor"/>
  <text x="165" y="20" font-size="13" text-anchor="middle" fill="currentColor">badly scaled: a narrow valley</text>
  <text x="475" y="20" font-size="13" text-anchor="middle" fill="currentColor">standardised: a round bowl</text>
  <text x="165" y="226" font-size="12" text-anchor="middle" fill="currentColor">12 steps, still far from the minimum</text>
  <text x="475" y="226" font-size="12" text-anchor="middle" fill="currentColor">6 steps, essentially there</text>
</svg>
<figcaption>Gradient descent on a narrow valley (left) and a round bowl (right). Orange dots are the iterates and the
green dot is the minimum. A step large enough to make progress along the valley would overshoot across it, so the
method must take small steps and zigzag.</figcaption>
</figure>

We can make this exact for the simplest landscape, a quadratic bowl whose axes line up with the weights:

$$
f(w_1,w_2)=\tfrac12\left(\lambda_1w_1^2+\lambda_2w_2^2\right),\qquad 0<\lambda_1\le\lambda_2 .
$$

The minimum is at $(0,0)$. The numbers $\lambda_1,\lambda_2$ say how steeply the bowl curves in each direction; for a
squared-error loss they come from the sizes of the features (a feature with values ten times bigger gives a $\lambda$
a hundred times bigger). The slope (the partial derivative, Chapter 3) in direction 1 is $\lambda_1w_1$, and in
direction 2 it is $\lambda_2w_2$. A gradient-descent step with step size $\eta$ is

$$
w_1\leftarrow w_1-\eta\lambda_1w_1=(1-\eta\lambda_1)\,w_1,\qquad
w_2\leftarrow w_2-\eta\lambda_2w_2=(1-\eta\lambda_2)\,w_2 .
$$

So after $t$ steps, $w_1=(1-\eta\lambda_1)^t\,w_1^{(0)}$ and $w_2=(1-\eta\lambda_2)^t\,w_2^{(0)}$. Two facts follow.

1. **The step must be small for the steep direction.** If $\eta\lambda_2>2$, then $|1-\eta\lambda_2|>1$ and $w_2$
   grows in size at every step: the method blows up. So we need $\eta<2/\lambda_2$. (Between $1/\lambda_2$ and
   $2/\lambda_2$ the factor is negative, and $w_2$ flips sign each step: the zigzag in the picture.)
2. **Then the shallow direction is slow.** With $\eta$ at most about $1/\lambda_2$, the factor in direction 1 is at
   least $1-\lambda_1/\lambda_2$. Write $\kappa=\lambda_2/\lambda_1$, the **condition number**. The error in direction
   1 shrinks by a factor of only $1-1/\kappa$ per step. Since $(1-1/\kappa)^\kappa\approx e^{-1}$, it takes about
   $\kappa$ steps to shrink that error by a factor $e\approx2.7$, and about $\kappa\ln(1/\varepsilon)$ steps to shrink
   it by a factor $\varepsilon$.

So the number of steps grows in proportion to the condition number. For the raw flats $\kappa\approx75\,000$, so
reaching a relative accuracy of $10^{-6}$ would need on the order of $75\,000\times\ln(10^6)\approx10^6$ steps; the
program gave up at 200 000. Standardising brought $\kappa$ down to 6.8 and the step count to 44. A general bowl is
tilted, not lined up with the axes, but Chapter 3 shows that a rotation lines it up (the eigenvectors of section
3.6), and the same argument then applies in the rotated coordinates; Chapter 5 proves the general convergence rate.

Why is $\kappa$ still 6.8 and not 1 after standardisation? Because area and rooms are strongly correlated (bigger
flats have more rooms), which tilts and stretches the bowl in a way that per-feature scaling cannot remove. Removing
it needs a rotation as well, the whitening idea behind PCA in Chapter 14.

Why is the raw condition number so huge? Mostly because of the intercept. The constant column of 1s and the area
column (values near 70) point in almost the same direction, so changing the intercept by $c$ and the area weight by
$-c/70$ barely changes the predictions: the valley is very long in that combined direction. Centring the features
(subtracting the mean, the first half of standardisation) removes exactly that near-duplication.

**Which learners care?** Anything based on distances (nearest neighbours, $k$-means, kernel methods, support vector
machines) and anything trained by gradient descent (linear and logistic regression trained iteratively, neural
networks) is affected by scaling. Penalised models (Chapter 8) are too, because the penalty treats all weights alike.
Decision trees and their ensembles (Chapter 11) are not: a tree asks questions like "is area above 70?", and the same
question can be asked in any unit. The exact least-squares solution of Chapter 4 is also unaffected in its
predictions, though not in its numerical accuracy (section 4.7).

## 2.5 Feature engineering and interactions

Can we help a learner by giving it better columns? Often a lot. **Feature engineering** means building new features
from the raw ones, using what we know about the problem. Before deep learning it was where much of the skill in
applied machine learning lay, and for tables of data it still is. A few patterns cover much of it.

**Logs for skewed quantities.** Many quantities, such as incomes, prices, populations and waiting times, are
**skewed**: most values are modest and a few are very large. The output of `ch02_explore.py` (section 2.7) shows a
skewed set of commute times: mean 24.6 minutes, median 20.0, and a long right tail. Taking the logarithm turns
multiplicative differences into additive ones (a flat twice as expensive is always $\ln 2$ more, whether it costs 100
or 1000) and makes the histogram nearly symmetric. Many models fit such data far better on the log scale.

**Ratios and differences.** Price per square metre, debt divided by income, speed as distance over time: a ratio
often captures what matters better than either part. A linear model cannot form a ratio by itself, because it only
adds weighted features.

**Interactions.** An **interaction** feature is a product of two features, $x_1x_2$. It lets the effect of one depend
on the other. Here is the cleanest example, the XOR pattern from Chapter 1's history:

| $x_1$ | $x_2$ | label | $x_1x_2$ with $x_i\in\{-1,+1\}$ |
|---|---|---|---|
| $-1$ | $-1$ | 0 | $+1$ |
| $-1$ | $+1$ | 1 | $-1$ |
| $+1$ | $-1$ | 1 | $-1$ |
| $+1$ | $+1$ | 0 | $+1$ |

No straight line in the $(x_1,x_2)$ plane separates the two labels: the 0s are on one diagonal and the 1s on the
other. (Proof: a line separating them is a rule "label 1 if $w_1x_1+w_2x_2+b>0$". The two 1-points need
$-w_1+w_2+b>0$ and $w_1-w_2+b>0$; adding gives $b>0$. The two 0-points need $-w_1-w_2+b\le0$ and $w_1+w_2+b\le0$; adding
gives $b\le0$. Contradiction.) But with the product as a feature, the rule "label 1 if $x_1x_2<0$" is perfect. One
new column turned an impossible problem into a trivial one. Chapter 4 uses the same idea to fit curves with linear
regression (**polynomial features** $x$, $x^2$, $x^3$), and Chapter 9's kernel trick does it implicitly for very many
products at once.

**Cyclic features.** Hours of the day run 0 to 23 and then wrap round. Encoded as a plain number, 23:00 and 00:00 are
23 apart, though they are an hour apart in time. The fix is to place the hour on a circle: use two features,
$\sin(2\pi h/24)$ and $\cos(2\pi h/24)$. Then neighbouring hours are always at the same distance,
$2\sin(\pi/24)\approx0.261$, whether they are 6 and 7 or 23 and 0, and opposite hours (0 and 12) are at distance 2,
the diameter. The same trick works for day of the week, month and compass direction.

**Binning.** Turning a number into categories (age 0 to 17, 18 to 64, 65 and over) loses information but can capture a
non-linear effect for a linear model, and makes a feature robust to outliers.

**Aggregates.** For data with structure, summaries are often the best features: a customer's number of purchases in
the last 30 days, a sensor's average reading over the last hour. These must be computed using only information
available *at the time of the prediction*, which brings us to leakage.

How do we know an engineered feature helps? We try it and measure on the validation set, as in Chapter 1. Each
attempt is a choice, and every choice spends some of the validation set's honesty, so keep a record and keep the test
set untouched.

## 2.6 Splitting well

Chapter 1 split data at random into training, validation and test sets. Is random always right? No. The guiding
principle is: **the test set must relate to the training set in the same way that future data will relate to all the
data you have now.** Random splitting matches that only when the future looks like a random draw from the past.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 260" role="img" aria-label="Four ways to split, each a row of twenty small squares coloured training (blue) or test (orange). Random: test squares scattered. Stratified: rows coloured by class; the test takes the same share of each class. By time: squares ordered by date; the last ones are test. By group: squares grouped in boxes of four, one per patient; whole boxes are test.">
  <text x="20" y="36" font-size="13" font-weight="bold" fill="currentColor">random</text>
  <text x="20" y="96" font-size="13" font-weight="bold" fill="currentColor">stratified</text>
  <text x="20" y="156" font-size="13" font-weight="bold" fill="currentColor">by time</text>
  <text x="20" y="216" font-size="13" font-weight="bold" fill="currentColor">by group</text>
  <rect x="110" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="132" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="154" y="22" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="176" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="198" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="220" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="242" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="264" y="22" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="286" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="308" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="330" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="352" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="374" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="396" y="22" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="418" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="440" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="462" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="484" y="22" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="506" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="528" y="22" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="110" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="132" y="82" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="154" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="176" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="3"/>
  <rect x="198" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="220" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="242" y="82" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="264" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="286" y="82" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="3"/>
  <rect x="308" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="330" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="352" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="3"/>
  <rect x="374" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="396" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="418" y="82" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="440" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="462" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="3"/>
  <rect x="484" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="506" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="528" y="82" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="3"/>
  <rect x="110" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="132" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="154" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="176" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="198" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="220" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="242" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="264" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="286" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="308" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="330" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="352" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="374" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="396" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="418" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="440" y="142" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="462" y="142" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="484" y="142" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="506" y="142" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="528" y="142" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <line x1="110" y1="174" x2="540" y2="174" stroke="currentColor"/>
  <polygon points="548,174 538,169 538,179" fill="currentColor"/>
  <text x="560" y="178" font-size="12" fill="currentColor">time</text>
  <rect x="110" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="132" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="154" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="176" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="198" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="220" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="242" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="264" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="286" y="202" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="308" y="202" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="330" y="202" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="352" y="202" width="18" height="18" fill="#eea66f" fill-opacity="0.9" stroke="currentColor" stroke-width="1"/>
  <rect x="374" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="396" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="418" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="440" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="462" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="484" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="506" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="528" y="202" width="18" height="18" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor" stroke-width="1"/>
  <rect x="107" y="198" width="86" height="26" rx="4" fill="none" stroke="currentColor" stroke-dasharray="3 2"/>
  <rect x="195" y="198" width="86" height="26" rx="4" fill="none" stroke="currentColor" stroke-dasharray="3 2"/>
  <rect x="283" y="198" width="86" height="26" rx="4" fill="none" stroke="currentColor" stroke-dasharray="3 2"/>
  <rect x="371" y="198" width="86" height="26" rx="4" fill="none" stroke="currentColor" stroke-dasharray="3 2"/>
  <rect x="459" y="198" width="86" height="26" rx="4" fill="none" stroke="currentColor" stroke-dasharray="3 2"/>
  <rect x="440" y="240" width="14" height="14" fill="#9cc9ea" fill-opacity="0.8" stroke="currentColor"/>
  <text x="460" y="252" font-size="12" fill="currentColor">train</text>
  <rect x="510" y="240" width="14" height="14" fill="#eea66f" fill-opacity="0.9" stroke="currentColor"/>
  <text x="530" y="252" font-size="12" fill="currentColor">test</text>
  <text x="110" y="252" font-size="12" fill="currentColor">dark outline = the rare class (stratified row)</text>
</svg>
<figcaption>Four ways to choose a test set. Stratified keeps the class shares; by time keeps the future in the
future; by group keeps all records of one patient (or user, or rover traverse) on the same side.</figcaption>
</figure>

```python
--8<-- "books/machine-learning/ch02_splitting.py"
```

Output:

```
positives in a 40-example test set (should be 4):
  random:     min 0, max 10, fraction of splits with exactly 4: 0.22
  stratified: min 4, max 4

random walk, mean absolute error: random split 0.73, split by time 7.91
patients, 1-NN accuracy: random rows 1.00, whole patients held out 0.62
noise features, 5-fold CV accuracy: select on all data 0.92, select inside each fold 0.46
```

### Stratified splits

Suppose 10% of 200 examples are positive (say, faulty parts) and we take a test set of 40. On average it holds 4
positives. But over 1000 random splits the program saw anywhere from 0 to 10, and exactly 4 only 22% of the time. A
test set with 0 positives cannot measure how well we find faults at all. A **stratified** split samples each class
separately, taking 20% of the positives and 20% of the negatives, so the test set holds exactly 4 positives and 36
negatives every time. With rare classes, always stratify; the same applies to the folds of cross-validation (Chapter
7).

### Splitting by time

When the model will be used to predict the future, the test set must lie in the future of the training set. The
program's example is a **random walk**: each day's value is the previous day's plus a random step. We predict each
day's value from the nearest day we have (1-NN on the date). With a random split, almost every test day has training
days on both sides, so the prediction is an interpolation between yesterday and tomorrow, and the mean error is 0.73.
With a split by time (train on the first 400 days, test on the last 100), the model must forecast, and the mean error
is 7.91, more than ten times larger. The random split did not measure forecasting at all; it measured filling in gaps.
For anything with time in it (prices, sensor data, user behaviour), train on the past, validate on a later period, and
test on a still later one.

### Splitting by group

Often several rows belong to one larger unit: several scans of one patient, several photos of one rover traverse,
several sentences from one document, several purchases by one customer. Rows from one unit are more alike than rows
from different units. If the model will be used on *new* units (new patients), the test set must hold whole units the
model has never seen.

The program simulates 60 patients with 5 scans each. Each patient has a personal "signature" in the scans, and the
label (disease or not) is only weakly related to the features. With a random split of rows, every test scan has four
siblings in the training set, almost identical, and 1-NN copies their label: accuracy 1.00. Holding out whole
patients, the accuracy drops to 0.62, near the weak real signal. The first number measures "recognise a patient seen
before", which is useless for diagnosing a new one.

### Data leakage

**Data leakage** means that information which will not be available when the model is used has found its way into
training or evaluation. It is the most common reason for a model that scores brilliantly in development and fails in
use. Kaufman, Rosset, Perlich and Stitelman (2012) give a careful treatment; here are the main forms, each with an
example of the kind that happens in practice.

**Target leakage: a feature that is a consequence of the label.** A model to predict whether a hospital patient has a
certain infection is given, among many columns, "was this antibiotic prescribed". The antibiotic is prescribed
*because* doctors diagnosed the infection, so the column is nearly the label itself, and the model leans on it. At
the moment the model is supposed to help, before diagnosis, the column is not yet filled in. Similarly, a model to
predict which customers will cancel a subscription is given "number of support calls in the account's last month";
if the table was built after the fact, the cancellation call itself is counted. The test: for every feature, ask
**"would I know this value at the moment I make the prediction?"**

**Preprocessing on all the data.** Computing the scaling mean, the imputation median, or the vocabulary of words on
the whole dataset before splitting lets the test set influence training. For a mean, the effect is usually small. For
choosing features, it can be enormous, as the last line of the output shows. The program makes 50 examples with 5000
features of pure noise and labels from coin flips; there is nothing to learn, so honest accuracy is about 50%. It then
picks the 20 features most correlated with the label and runs 5-fold cross-validation (Chapter 7: split into 5 parts,
train on 4, test on the fifth, rotate). If the 20 features are chosen once, using all 50 labels, the cross-validated
accuracy is 0.92, a confident-looking result on pure noise. With 5000 noise features, some are correlated with the
labels by chance, *including the labels of the examples later used for testing*. If the features are chosen again
inside each fold, from the training part only, the accuracy is 0.46, about chance, which is the truth. Hastie,
Tibshirani and Friedman (2009, section 7.10.2) call this "the wrong and the right way to do cross-validation". The
rule is: **every step that learns anything from data, including cleaning, scaling, encoding and feature selection,
belongs inside the training side of the split.**

**Duplicates and near-duplicates across the split,** as in 2.2, and **group leakage**, as in the patient example.

**Temporal leakage**: features computed with future information, such as "average price over the month" used to
predict a price in the middle of that month, or a random split of time-ordered data.

A good habit when a result looks too good: find the single most important feature and ask how it could be known at
prediction time. Surprisingly often, it cannot.

## 2.7 Looking before modelling

What should you do with a new dataset before fitting anything? Look at it. Numbers first, then pictures, and the
pictures are not optional.

```python
--8<-- "books/machine-learning/ch02_explore.py"
```

Output:

```
       count   mean     sd    min     q1  median     q3    max
area      11   66.4   17.5   40.0   55.0    66.5   75.0   98.0
rooms     11    2.5    0.8    1.0    2.0     2.5    3.0    4.0
price     11  240.9   70.6  140.0  207.5   230.0  257.5  390.0
correlation matrix (area, rooms, price):
[[1.    0.834 0.942]
 [0.834 1.    0.795]
 [0.942 0.795 1.   ]]

commute times: mean 24.6, median 20.0
      3.4 to    13.7 | ############ 50
     13.7 to    24.1 | ################### 75
     24.1 to    34.4 | ######## 34
     34.4 to    44.7 | ##### 21
     44.7 to    55.1 | ### 11
     55.1 to    65.4 | # 3
     65.4 to    75.8 | # 3
     75.8 to    86.1 | # 3
after taking logs: mean 3.03, median 3.00
      1.2 to     1.6 | # 3
      1.6 to     2.0 | ## 7
      2.0 to     2.4 | ##### 19
      2.4 to     2.8 | ########## 39
      2.8 to     3.2 | ################ 63
      3.2 to     3.6 | ########## 38
      3.6 to     4.1 | ###### 23
      4.1 to     4.5 | ## 8

Anscombe's quartet
set   mean x  var x  mean y  var y   corr   fitted line
I       9.00  11.00    7.50   4.13  0.816   y = 3.00 + 0.500 x
II      9.00  11.00    7.50   4.13  0.816   y = 3.00 + 0.500 x
III     9.00  11.00    7.50   4.12  0.816   y = 3.00 + 0.500 x
IV      9.00  11.00    7.50   4.12  0.817   y = 3.00 + 0.500 x
```

### Summary statistics

For each numeric column: how many values, the mean and the median (a big gap between them signals skew or outliers),
the spread (standard deviation, and the quartiles), and the minimum and maximum (impossible values such as negative
ages or 7500 m² flats show up here first). For each categorical column: the number of distinct values and how often
each occurs (a category with three examples will be hard to learn). For the label: its distribution, which tells you
the baseline of Chapter 1. (The table uses the **sample** standard deviation, dividing by $n-1$ instead of $n$; Chapter
3 explains why that is the usual choice for estimating spread from a sample.)

### Histograms

A **histogram** cuts the range of a column into equal bins and counts the values in each. It shows the shape of a
distribution at a glance: one peak or two, symmetric or skewed, gaps, suspicious spikes (a spike at exactly 0 or 999
often means "missing" written as a number). The program's text histogram of 200 commute times has a long right tail:
mean 24.6 above median 20.0. After taking logs, the histogram is nearly symmetric, with mean and median almost equal.
The commute times were drawn from a **log-normal** distribution, whose log is normal by construction, so this is the
expected result; with real skewed data it is often roughly true.

### Correlation

The **correlation coefficient** of two columns (Pearson's $r$) measures how close they are to lying on a straight
line. For columns $x$ and $y$ with means $\bar x,\bar y$,

$$
r=\frac{\sum_i(x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum_i(x_i-\bar x)^2}\,\sqrt{\sum_i(y_i-\bar y)^2}} .
$$

The top line is large and positive when $x$ and $y$ are above their means together and below together. The bottom
line divides out the spreads, so $r$ does not depend on units. It always lies between $-1$ and $+1$ (Chapter 3 proves
this with the Cauchy-Schwarz inequality), equals $\pm1$ exactly when the points lie on a line, and is near 0 when
there is no *linear* trend. For the flats, area and price have $r=0.942$: bigger flats cost more, quite reliably. Area
and rooms have $r=0.834$, which matters for modelling: two strongly correlated features carry overlapping
information, and Chapter 4 shows that this makes their separate weights hard to pin down.

A **correlation matrix** lists $r$ for every pair of columns. It is a quick map of which features move together and
which relate to the label. Two warnings. First, correlation measures only straight-line association: a perfect
U-shaped relation can have $r=0$. Second, as Chapter 1 stressed, correlation says nothing about cause.

### Anscombe's quartet

In 1973 the statistician Francis Anscombe published four small datasets, now called **Anscombe's quartet**, to make
a point that is easy to forget. The program types them in and computes their summaries. All four have the same mean
of $x$ (9.00), the same variance of $x$ (11.00), the same mean of $y$ (7.50), nearly the same variance of $y$ (4.12 to
4.13), the same correlation (0.816 to 0.817) and the same least-squares line, $y=3.00+0.500x$. By the numbers they are
the same dataset. Now look at them.

<figure class="mars-fig" markdown="0">
<svg viewBox="0 0 640 200" role="img" aria-label="Anscombe's quartet: four small scatter plots, each with the same orange fitted line. I: points scattered evenly around the line. II: points on a smooth curve that rises and falls. III: points on a straight line except one high outlier. IV: all points at the same x except one far to the right, which alone sets the slope.">
  <rect x="15" y="20" width="140" height="150" fill="none" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="25" y="38" font-size="13" font-weight="bold" fill="currentColor">I</text>
  <line x1="26.6" y1="135.9" x2="143.4" y2="59.9" stroke="#eea66f" stroke-width="2"/>
  <circle cx="74.1" cy="104.6" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="59.5" cy="115.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="95.9" cy="109.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="66.8" cy="97.3" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="81.4" cy="101.9" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="103.2" cy="86.4" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="44.9" cy="112.2" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="30.3" cy="140.5" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="88.6" cy="78.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="52.2" cy="135.2" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="37.6" cy="127.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <rect x="170" y="20" width="140" height="150" fill="none" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="180" y="38" font-size="13" font-weight="bold" fill="currentColor">II</text>
  <line x1="181.6" y1="135.9" x2="298.4" y2="59.9" stroke="#eea66f" stroke-width="2"/>
  <circle cx="229.1" cy="94.2" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="214.5" cy="103.7" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="250.9" cy="98.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="221.8" cy="97.7" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="236.4" cy="93.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="258.2" cy="104.1" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="199.9" cy="122.8" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="185.3" cy="151.6" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="243.6" cy="94.3" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="207.2" cy="112.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="192.6" cy="136.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <rect x="325" y="20" width="140" height="150" fill="none" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="335" y="38" font-size="13" font-weight="bold" fill="currentColor">III</text>
  <line x1="336.6" y1="135.9" x2="453.4" y2="59.9" stroke="#eea66f" stroke-width="2"/>
  <circle cx="384.1" cy="110.1" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="369.5" cy="116.7" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="405.9" cy="60.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="376.8" cy="113.5" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="391.4" cy="106.8" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="413.2" cy="97.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="354.9" cy="123.2" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="340.3" cy="129.8" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="398.6" cy="103.6" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="362.2" cy="120.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="347.6" cy="126.6" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <rect x="480" y="20" width="140" height="150" fill="none" stroke="currentColor" stroke-opacity="0.5"/>
  <text x="490" y="38" font-size="13" font-weight="bold" fill="currentColor">IV</text>
  <line x1="491.6" y1="135.9" x2="608.4" y2="59.9" stroke="#eea66f" stroke-width="2"/>
  <circle cx="524.5" cy="118.5" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="524.5" cy="126.3" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="524.5" cy="107.8" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="524.5" cy="97.0" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="524.5" cy="100.5" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="524.5" cy="114.1" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="524.5" cy="131.1" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="604.7" cy="62.2" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="524.5" cy="128.2" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="524.5" cy="105.9" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <circle cx="524.5" cy="115.5" r="3.5" fill="#9cc9ea" stroke="currentColor"/>
  <text x="85" y="192" font-size="12" text-anchor="middle" fill="currentColor">noisy line</text>
  <text x="240" y="192" font-size="12" text-anchor="middle" fill="currentColor">a smooth curve</text>
  <text x="395" y="192" font-size="12" text-anchor="middle" fill="currentColor">a line and an outlier</text>
  <text x="550" y="192" font-size="12" text-anchor="middle" fill="currentColor">one point decides</text>
</svg>
<figcaption>Anscombe's quartet, plotted from the numbers in the program. The four datasets share their means,
variances, correlation and fitted line, and they are completely different.</figcaption>
</figure>

Set I is what the summary suggests: a noisy straight-line relation. Set II is a smooth curve; a straight line is the
wrong model, and a quadratic would fit it almost perfectly. Set III is an exact line with one outlier that tilts the
fit. Set IV has all points at $x=8$ except one at $x=19$; that single point alone determines the slope, and without
it there is no relation at all. A model fitted without looking would treat all four the same way. The lesson: **plot
the data**, every feature against the label and the important features against each other, before you trust any
summary or any model.

## Check yourself

??? question "1. Classify each feature as numeric, categorical, ordinal, text or other: (a) postcode, (b) shoe size, (c) T-shirt size S, M, L, XL, (d) a product review, (e) blood type, (f) the year a house was built."

    (a) Categorical: postcodes are labels, even when written with digits; 90210 is not "bigger" than 10001 in any
    useful sense. (b) Numeric (a count-like measurement with meaningful differences). (c) Ordinal: ordered, with no
    defined distance. (d) Text. (e) Categorical. (f) Numeric, but often better turned into "age of the house at the
    time of sale", an engineered feature.

??? question "2. The values 3, 5, 6, 7, 8, 9, 40 are given. Compute the mean and median, then the quartiles, IQR and Tukey's fences (use Q1 = 5.5 and Q3 = 8.5). Is 40 an outlier by Tukey's rule? By the 3-standard-deviation rule?"

    Mean $78/7\approx11.14$, median 7. IQR $=8.5-5.5=3$, fences $[5.5-4.5,\,8.5+4.5]=[1,13]$, so 40 is flagged. The
    population standard deviation is $\sqrt{\tfrac17\sum(x_i-11.14)^2}\approx11.92$, so the z-score of 40 is
    $(40-11.14)/11.92\approx2.42$: not flagged. With $n=7$, no z-score can exceed $\sqrt6\approx2.45$ anyway, so the
    3-sigma rule could never flag anything in a list this short.

??? question "3. Write the code: a function that imputes missing values (None) in a numeric column with the training median, and applies the same value to a test column."

    ```python
    import statistics

    def fit_median(train_col):
        return statistics.median(v for v in train_col if v is not None)

    def impute(col, fill):
        return [fill if v is None else v for v in col]

    train = [52, None, 40, 98, 63]
    test = [None, 70]
    m = fit_median(train)          # median of 40, 52, 63, 98 = 57.5
    print(impute(train, m), impute(test, m))
    # [52, 57.5, 40, 98, 63] [57.5, 70]
    ```

    The fill value is learned once, from training data, and reused: the test column's own values never influence
    it.

??? question "4. A colour feature takes values red, green, blue. Encoded as 0, 1, 2, what is the distance between red and blue compared with red and green? What is it after one-hot encoding?"

    As numbers: red to blue is $|0-2|=2$, red to green is 1, so the encoding claims red is twice as far from blue as
    from green. One-hot: red $(1,0,0)$, green $(0,1,0)$, blue $(0,0,1)$; every pair differs in two places, distance
    $\sqrt2$ for all pairs. One-hot carries only "same or different", which is all a colour name means here.

??? question "5. With one-hot district columns (east, north, south) and an intercept column of ones, show that the columns are linearly dependent. Which simple change fixes it?"

    In every row exactly one district column is 1, so east + north + south = 1 = the intercept column. One column is
    a combination of the others, so many different weight settings give identical predictions: adding $c$ to each
    district weight and subtracting $c$ from the intercept changes nothing. Drop one district (say east) and the
    dependence goes away; the remaining weights then measure the difference from east.

??? question "6. You hash 10 000 distinct words into 2^20 buckets. About how many colliding pairs do you expect? How many buckets would you need for an expected 1 colliding pair?"

    $\binom{10000}{2}/2^{20}=49\,995\,000/1\,048\,576\approx47.7$ pairs. For an expectation of 1 you need
    $b\approx\binom{10000}2\approx5\times10^7$ buckets. In practice 48 collisions among 10 000 words cost little,
    which is why $2^{20}$ is a common choice.

??? question "7. A feature has training mean 50 and standard deviation 10, and a test value of 75. What is its standardised value? A colleague standardises the test set with its own mean 60 and standard deviation 8. What value do they get, and why is that wrong?"

    With training values, $z=(75-50)/10=2.5$. With the test set's own values, $(75-60)/8=1.875$. The same raw value
    must always map to the same feature value, or the model, which learned what $z=2.5$ means from training data, sees
    a different input. Also, the test set's statistics are information the model should not have.

??? question "8. For the quadratic bowl with lambda_1 = 1 and lambda_2 = 100, what is the largest step size that does not blow up? With the step 1/lambda_2, by what factor does the error in direction 1 shrink per step, and about how many steps reduce it a thousandfold?"

    The step must satisfy $\eta<2/\lambda_2=0.02$. With $\eta=0.01$, direction 1 shrinks by $1-0.01=0.99$ per step.
    To shrink it by $10^{-3}$ we need $0.99^t\le10^{-3}$, so $t\ge\ln(1000)/(-\ln0.99)\approx6.908/0.01005\approx687.3$, so 688
    steps. That is about $\kappa\ln(1000)=100\times6.91\approx691$, as the rule of thumb says.

??? question "9. Write the code: encode an hour of the day as a cyclic feature, and check that the distance from 23 to 0 equals the distance from 6 to 7."

    ```python
    import math

    def cyclic(hour, period=24):
        a = 2 * math.pi * hour / period
        return (math.sin(a), math.cos(a))

    print(math.dist(cyclic(23), cyclic(0)))   # 0.2610...
    print(math.dist(cyclic(6), cyclic(7)))    # 0.2610...
    print(math.dist(cyclic(0), cyclic(12)))   # 2.0
    ```

    Both one-hour gaps give $2\sin(\pi/24)\approx0.2611$; opposite hours are 2 apart, the diameter of the unit circle.

??? question "10. A model predicts whether a loan will be repaid. Its most important feature is 'number of late-payment letters sent'. What would you check?"

    When the letters are sent. If they are sent after the loan starts going wrong, the feature is a consequence of
    the label (target leakage): at the time of the lending decision it is zero for everyone. Check the timestamp of
    every feature against the time of prediction, and rebuild the feature using only information from before that
    time.

??? question "11. Explain why selecting features on the whole dataset and then cross-validating gave 0.92 accuracy on pure noise, while selecting inside each fold gave 0.46."

    With 5000 random features and only 50 labels, some features match the labels well by chance. Choosing the best
    20 using all 50 labels picks features that happen to agree with the labels of the very examples later used for
    testing in each fold, so the "test" points are predicted with information that came from them. Selecting inside
    each fold uses only that fold's training labels; the chosen features then carry no real information about the
    held-out labels, and accuracy is at chance, which is the truth.

??? question "12. Prove that a perfect U-shaped relation can have correlation zero: take x = -2, -1, 0, 1, 2 and y = x^2."

    $\bar x=0$ and $y=4,1,0,1,4$ with $\bar y=2$. The top line of $r$ is $\sum x_i(y_i-2)=(-2)(2)+(-1)(-1)+0+(1)(-1)+(2)(2)
    =-4+1+0-1+4=0$, so $r=0$, although $y$ is completely determined by $x$. Correlation detects only the straight-line
    part of a relation; here, by symmetry, there is none.

## What you learned

- A dataset is a table: rows are examples, feature columns form the matrix $X$, the label column is $y$; features are
  numeric, categorical, ordinal, text, images or times, and the kind decides the encoding.
- Duplicates, missing values and outliers are found automatically and decided with knowledge; the median and the
  IQR are robust, while the mean and the z-score can be fooled (no z-score exceeds $\sqrt{n-1}$).
- One-hot encoding represents categories without inventing order; ordinal codes keep a real order; the hashing trick
  avoids a vocabulary at the cost of about $\binom m2/b$ collisions, and random signs make them cancel on average.
- Standardisation and min-max scaling make features comparable; gradient descent needs it, because its step count
  grows with the condition number of the loss.
- Logs, ratios, products and cyclic encodings give a model shapes it could not form by itself.
- Splits must mimic the future: stratify rare classes, split by time for forecasting and by group for new units,
  and fit every data-dependent step inside the training side to avoid leakage.
- Always summarise and plot before modelling: Anscombe's four datasets share every summary number and nothing else.

**Next:** [Chapter 3](03-The-Math-Toolkit.md), the math toolkit: vectors, matrices, derivatives, probability,
likelihood, eigenvectors and entropy, each built from scratch in NumPy.

## Further reading

- S. S. Stevens, "On the Theory of Scales of Measurement", *Science*, 1946.
- D. B. Rubin, "Inference and Missing Data", *Biometrika*, 1976; R. J. A. Little and D. B. Rubin, *Statistical
  Analysis with Missing Data*, 3rd ed., 2019.
- J. W. Tukey, *Exploratory Data Analysis*, 1977: box plots, fences and the habit of looking.
- F. J. Anscombe, "Graphs in Statistical Analysis", *The American Statistician*, 1973.
- K. Weinberger, A. Dasgupta, J. Langford, A. Smola and J. Attenberg, "Feature Hashing for Large Scale Multitask
  Learning", ICML 2009.
- S. Kaufman, S. Rosset, C. Perlich and O. Stitelman, "Leakage in Data Mining: Formulation, Detection, and
  Avoidance", *ACM Transactions on Knowledge Discovery from Data*, 2012.
- T. Hastie, R. Tibshirani and J. Friedman, *The Elements of Statistical Learning*, 2nd ed., 2009. Section 7.10.2,
  the wrong and the right way to do cross-validation.
- K. P. Murphy, *Probabilistic Machine Learning: An Introduction*, 2022, Chapter 1 (data and preprocessing).
- On this site: [hash tables](../../data-structures/hash-table.md) and
  [Chapter 7 of the Algorithms book](../algorithms/07-Searching-and-Hashing.md) (hashing); for statistics:
  [math.akadian.ca/books/statistics](https://math.akadian.ca/books/statistics/).
