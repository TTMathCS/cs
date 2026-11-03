# Glossary

*Short definitions of the terms this book uses, from A to Z, each with a link to the chapter that teaches it.*

## A

**Accuracy**
The fraction of examples a classifier labels correctly. On imbalanced data it misleads, because predicting the common class every time already scores high, so always compare it with that trivial baseline.
See [Chapter 7](07-Evaluating-Models.md#71-accuracy-and-why-it-lies-on-imbalanced-data).

**Activation function**
The fixed non-linear function an artificial neuron applies to its weighted sum, such as the sigmoid, tanh or ReLU. Without it a stack of layers would collapse into one linear map, since a composition of linear maps is linear.
See [Chapter 15](15-Neural-Networks-and-Backpropagation.md#151-from-the-perceptron-to-layers-why-xor-needs-a-hidden-layer) and [Chapter 15](15-Neural-Networks-and-Backpropagation.md#152-activation-functions-and-why-non-linearity-matters).

**AdaBoost**
The boosting algorithm of Freund and Schapire: train weak learners such as decision stumps in sequence, raising the weights of the examples each one gets wrong, and combine them in a weighted vote. It can be read as minimising the exponential loss by forward stagewise additive modelling.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#114-boosting-adaboost-and-the-exponential-loss-view).

**AdaGrad**
An adaptive optimiser that divides each parameter's step by the square root of the sum of all its past squared gradients. Rarely updated parameters keep large steps, but because the sum only grows, steps shrink and can become too small in long training.
See [Chapter 5](05-Optimization.md#55-adaptive-methods-adagrad-rmsprop-adam).

**Adam**
Adaptive moment estimation: an optimiser that keeps a moving average of the gradients (momentum) and of the squared gradients (as in RMSProp), corrects both for their start at zero, and steps each parameter by the ratio. It is the default optimiser for most deep networks.
See [Chapter 5](05-Optimization.md#55-adaptive-methods-adagrad-rmsprop-adam) and [Chapter 16](16-Training-Deep-Networks.md#165-optimizers-in-practice-learning-rates-schedules-clipping).

**AdamW**
Adam with decoupled weight decay: the decay $\alpha\lambda w$ is subtracted separately from the adaptive step instead of being added to the gradient, where Adam's scaling would distort it. Most large models are trained with it.
See [Chapter 5](05-Optimization.md#55-adaptive-methods-adagrad-rmsprop-adam) and [Chapter 16](16-Training-Deep-Networks.md#164-regularization-weight-decay-dropout-augmentation).

**Adversarial example**
An input changed by a perturbation too small for people to notice that makes a model give a wrong answer. Perturbations found for one network often fool others, and high dimension makes such perturbations easy to find.
See [Chapter 22](22-Machine-Learning-in-Practice.md#225-robustness-adversarial-examples).

**Agglomerative hierarchical clustering**
Clustering from the bottom up: start with every point in its own cluster and repeatedly merge the two closest clusters, where "closest" is set by the linkage. The merges form a tree drawn as a dendrogram.
See [Chapter 13](13-Clustering.md#135-hierarchical-clustering-linkages-dendrograms).

**AIC (Akaike information criterion)**
An estimate of test performance from training likelihood plus a charge for the number of parameters, derived by the same optimism reasoning as Mallows' $C_p$. Lower is better.
See [Chapter 8](08-Overfitting-and-Regularization.md#86-effective-degrees-of-freedom-and-the-elastic-net).

**Area under the ROC curve (AUC)**
A one-number summary of the ROC curve. It equals the probability that the model scores a random positive above a random negative, the Mann-Whitney U statistic scaled to $[0,1]$; 0.5 is random ranking and 1 is perfect.
See [Chapter 7](07-Evaluating-Models.md#73-roc-curves-auc-and-precision-recall-curves).

**Attention**
A mechanism that lets each output look at all positions of an input: compare a query with every key, turn the scores into weights with a softmax, and return the weighted average of the values. It removed the fixed-vector bottleneck of sequence-to-sequence models.
See [Chapter 18](18-Sequence-Models.md#186-attention-from-scratch) and [Chapter 19](19-Transformers.md#192-scaled-dot-product-attention-derived).

**Autoencoder**
A neural network trained to reproduce its input through a narrow middle: an encoder maps the input to a short code and a decoder maps the code back. The bottleneck forces a compact description, and a linear autoencoder finds the same subspace as PCA.
See [Chapter 14](14-Dimensionality-Reduction.md#146-autoencoders-preview) and [Chapter 20](20-Generative-Models.md#202-autoencoders-and-variational-autoencoders).

**Automatic differentiation**
Computing exact derivatives of a program by recording the computational graph as it runs and applying the chain rule to each elementary operation. Reverse mode, which is backpropagation, gives the gradient of one output with respect to all inputs in about the cost of two forward passes.
See [Chapter 15](15-Neural-Networks-and-Backpropagation.md#155-a-tiny-automatic-differentiation-engine-from-scratch) and [Chapter 22](22-Machine-Learning-in-Practice.md#227-tools-in-the-real-world).

**Autoregressive model**
A generative model that writes the joint distribution as a product of conditionals, $p(x)=\prod_ip(x_i\mid x_{<i})$, and learns each conditional with one shared network. It gives exact likelihoods and simple sampling, one token at a time.
See [Chapter 20](20-Generative-Models.md#206-autoregressive-models).

## B

**Backpropagation**
The algorithm that computes the gradient of a network's loss with respect to every weight by applying the chain rule backwards from the output, layer by layer. It costs about twice a forward pass whatever the number of weights, which is why neural networks are practical.
See [Chapter 1](01-What-Is-Machine-Learning.md#17-a-short-honest-history) and [Chapter 15](15-Neural-Networks-and-Backpropagation.md#154-backpropagation-and-computational-graphs).

**Backpropagation through time (BPTT)**
Backpropagation applied to a recurrent network unrolled over the steps of a sequence, with the shared weights receiving gradient from every step. It costs time and memory proportional to the sequence length.
See [Chapter 18](18-Sequence-Models.md#183-recurrent-networks-backprop-through-time).

**Bag of words**
A representation of text as the vector of its word counts, ignoring word order. It is crude ("dog bites man" equals "man bites dog") but was the standard for text classification for decades.
See [Chapter 2](02-Data-and-Features.md#23-encoding-one-hot-ordinal-hashing) and [Chapter 12](12-Probabilistic-Models.md#122-naive-bayes-for-text-spam-laplace-smoothing).

**Bagging**
Bootstrap aggregating: train the same learner on many bootstrap samples of the training set and average (or vote) their predictions. It reduces variance, which suits high-variance learners such as deep decision trees.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#113-bagging-and-random-forests-out-of-bag-error).

**Batch normalisation**
A layer that normalises each unit's pre-activations to mean 0 and variance 1 over the current mini-batch, then applies a learned scale $\gamma$ and shift $\beta$. At test time it uses running averages; it makes deep networks train faster, although why is still debated.
See [Chapter 16](16-Training-Deep-Networks.md#163-normalization-batch-norm-and-layer-norm).

**Bayes error**
The error of the Bayes classifier, the lowest error any rule can reach on a problem because the labels themselves are noisy. As data grows, the 1-nearest-neighbour error tends to at most twice the Bayes error.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#91-k-nn-revisited-choosing-k-distance-metrics-scaling) and [Chapter 21](21-Learning-Theory.md#215-the-bias-complexity-trade-off-and-structural-risk-minimisation).

**Bayes' rule**
The formula $P(A\mid B)=P(B\mid A)P(A)/P(B)$ that turns a prior and a likelihood into a posterior. Generative classifiers use it to turn $P(y)$ and $p(x\mid y)$ into $P(y\mid x)$.
See [Chapter 3](03-The-Math-Toolkit.md#34-probability) and [Chapter 12](12-Probabilistic-Models.md#121-generative-vs-discriminative).

**Bayesian linear regression**
Linear regression with a Gaussian prior on the weights: the posterior over weights is Gaussian, and predictions come with an uncertainty that grows away from the data. Its MAP estimate is ridge regression.
See [Chapter 12](12-Probabilistic-Models.md#124-bayesian-linear-regression-posterior-and-predictive-derived).

**Beam search**
A decoding method that keeps the $B$ best partial outputs by total log-probability at each step, extends each by every token, and keeps the best $B$ of those. With $B=1$ it is greedy decoding.
See [Chapter 18](18-Sequence-Models.md#185-sequence-to-sequence).

**BERT**
An encoder-only transformer pretrained as a masked language model: about 15 percent of tokens are hidden and the model predicts them from both sides. It is then fine-tuned for tasks such as classification and question answering.
See [Chapter 19](19-Transformers.md#197-pretraining-gpt-bert-vision-transformers).

**Bias (of an estimator or model)**
How far the average fitted model, over many training sets, is from the truth: a systematic error. A straight line fitted to a sine curve has high bias however much data it sees.
See [Chapter 8](08-Overfitting-and-Regularization.md#82-the-bias-variance-decomposition).

**Bias-variance decomposition**
The identity that the expected squared test error at a point equals noise plus squared bias plus variance. Simple models have high bias, flexible ones high variance, and the best model balances the two (the bias-variance trade-off).
See [Chapter 8](08-Overfitting-and-Regularization.md#82-the-bias-variance-decomposition).

**Boosting**
Building a strong model as a sequence of weak learners, each one concentrating on the mistakes of those before. AdaBoost and gradient boosting are the main forms.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#114-boosting-adaboost-and-the-exponential-loss-view) and [Chapter 11](11-Decision-Trees-and-Ensembles.md#115-gradient-boosting-friedman-2001-from-scratch-for-regression).

**Bootstrap**
Estimating the uncertainty of a statistic by resampling: draw many samples of the same size with replacement from the data, recompute the statistic on each, and read the spread. Its 2.5th and 97.5th percentiles give a percentile bootstrap interval.
See [Chapter 7](07-Evaluating-Models.md#77-comparing-models-intervals-the-bootstrap-and-tests) and [Chapter 11](11-Decision-Trees-and-Ensembles.md#113-bagging-and-random-forests-out-of-bag-error).

**Brier score**
The mean squared error of predicted probabilities, $\frac1n\sum(p_i-y_i)^2$. It is a proper scoring rule that rewards both ranking and calibration, and unlike the expected calibration error it needs no bins.
See [Chapter 7](07-Evaluating-Models.md#76-calibration-reliability-diagrams-and-the-brier-score).

**Byte-pair encoding (BPE)**
A subword tokenizer that starts from single characters (or bytes) and repeatedly merges the most frequent adjacent pair into a new token until the vocabulary reaches the desired size. It began as a compression method.
See [Chapter 19](19-Transformers.md#196-tokenization-byte-pair-encoding-from-scratch).

## C

**Calibration**
The property that predicted probabilities mean what they say: of the examples given probability 0.8, about 80 percent are positive. It is checked with a reliability diagram and fixed afterwards with Platt scaling, isotonic regression or temperature scaling.
See [Chapter 7](07-Evaluating-Models.md#76-calibration-reliability-diagrams-and-the-brier-score).

**CART**
Classification and regression trees (Breiman and others, 1984): grow a binary tree greedily, at each node choosing the split that most reduces impurity or squared error, then prune it back by cost-complexity.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#112-growing-a-tree-from-scratch-cart-pruning).

**Catastrophic forgetting**
The tendency of a network trained on task A and then on task B to forget A, because gradient descent on B moves the weights wherever B's loss wants. Avoiding it is the problem of continual learning.
See [Chapter 23](23-Where-Machine-Learning-Goes.md#236-open-problems).

**Causal mask**
In a decoder's self-attention, setting the scores of all later positions to $-\infty$ before the softmax, so that each position sees only the past. It lets a language model train on every position of a sequence in parallel.
See [Chapter 19](19-Transformers.md#194-the-transformer-block).

**Central limit theorem**
The result that a sum of many small independent effects with finite variances is approximately Gaussian, whatever their own distributions. It is the main reason Gaussian noise models are common.
See [Chapter 3](03-The-Math-Toolkit.md#34-probability).

**Chain rule**
The rule for differentiating a composition: if $z=f(g(x))$ then $dz/dx=f'(g(x))\,g'(x)$. Backpropagation is the chain rule applied systematically through a network.
See [Chapter 3](03-The-Math-Toolkit.md#33-derivatives-gradients-and-the-chain-rule) and [Chapter 15](15-Neural-Networks-and-Backpropagation.md#154-backpropagation-and-computational-graphs).

**Classification**
Supervised learning in which the label is one of a finite set of classes, such as spam or not spam. Compare regression, where the label is a number.
See [Chapter 1](01-What-Is-Machine-Learning.md#12-kinds-of-learning) and [Chapter 6](06-Classification-and-Logistic-Regression.md#61-from-numbers-to-classes).

**Coefficient of determination ($R^2$)**
$R^2=1-\mathrm{MSE}/\mathrm{Var}(y)$: the fraction of the squared error of always predicting the mean that a model removes. It is 1 for a perfect fit and can be negative on test data for a model worse than the mean.
See [Chapter 4](04-Linear-Regression.md#46-reading-coefficients-r-squared-residual-plots) and [Chapter 7](07-Evaluating-Models.md#74-regression-metrics).

**Computational graph**
A directed acyclic graph whose nodes are intermediate values of a computation and whose edges say which values each was computed from. Reverse-mode differentiation visits it in reverse topological order.
See [Chapter 15](15-Neural-Networks-and-Backpropagation.md#154-backpropagation-and-computational-graphs).

**Condition number**
The ratio of largest to smallest stretch of a matrix ($\sigma_{\max}/\sigma_{\min}$), or of largest to smallest curvature of a loss ($\kappa=L/\mu$). A large value means badly scaled features, slow gradient descent and loss of precision in solving; forming $X^\top X$ squares it.
See [Chapter 2](02-Data-and-Features.md#24-scaling-standardisation-and-min-max), [Chapter 3](03-The-Math-Toolkit.md#36-eigenvectors-and-the-svd-in-one-picture), [Chapter 4](04-Linear-Regression.md#47-qr-and-svd-solutions-conditioning-and-why-not-invert-xt-x) and [Chapter 5](05-Optimization.md#52-how-fast-gradient-descent-converges).

**Confounder**
A hidden cause that drives two variables at once and makes them correlated without either causing the other, as hot weather drives both ice-cream sales and swimming.
See [Chapter 1](01-What-Is-Machine-Learning.md#16-what-machine-learning-cannot-do).

**Confusion matrix**
The table of counts of true positives, false positives, false negatives and true negatives for a classifier at a given threshold. Precision, recall and most other classification measures are computed from it.
See [Chapter 7](07-Evaluating-Models.md#72-the-confusion-matrix-precision-recall-and-f1).

**Conjugate prior**
A prior that, combined with a given likelihood, gives a posterior in the same family, so updating is just changing parameters. The beta prior with a binomial likelihood is the standard example, where updating adds counts.
See [Chapter 12](12-Probabilistic-Models.md#123-mle-vs-map-vs-full-bayes-conjugate-priors-beta-binomial-worked).

**Contrastive learning**
Self-supervised learning that makes two views of the same example, such as two random crops, and trains an encoder to place their embeddings close while pushing embeddings of different examples apart, usually with the InfoNCE loss.
See [Chapter 23](23-Where-Machine-Learning-Goes.md#232-self-supervised-and-contrastive-learning-foundation-models).

**Convex function**
A function whose graph lies below every chord: $f(tx+(1-t)y)\le tf(x)+(1-t)f(y)$. Every local minimum of a convex function is global, which is why convex losses can be minimised reliably.
See [Chapter 5](05-Optimization.md#51-loss-landscapes-and-convexity).

**Convolution**
Sliding a small filter over an input and taking, at each position, the sum of products of the filter and the patch beneath it. Strictly that is cross-correlation; true convolution flips the filter first, but deep-learning libraries use the name for both.
See [Chapter 17](17-Convolutional-Networks.md#172-convolution-from-scratch-filters-edges-stride-padding).

**Convolutional neural network (CNN)**
A network whose layers are convolutions, building in locality (each unit sees a small window) and weight sharing (every window uses the same filter). It needs far fewer weights than a fully connected network on images and is equivariant to shifts.
See [Chapter 17](17-Convolutional-Networks.md#171-images-as-arrays-why-fully-connected-fails).

**Coordinate descent**
Minimising over one weight at a time with the others held fixed, cycling through the weights. For the lasso each one-weight problem is solved exactly by soft-thresholding, which makes it the standard lasso algorithm.
See [Chapter 8](08-Overfitting-and-Regularization.md#84-the-lasso).

**Covariance matrix**
The matrix whose entries are the covariances between pairs of features. For centred data, $u^\top\Sigma u$ is the variance along direction $u$, so its top eigenvectors are the principal components.
See [Chapter 3](03-The-Math-Toolkit.md#36-eigenvectors-and-the-svd-in-one-picture) and [Chapter 14](14-Dimensionality-Reduction.md#142-principal-component-analysis-maximum-variance-and-the-svd).

**Covariate shift**
Distribution shift in which the inputs move but the labelling rule stays the same, $Q(x)\ne P(x)$ with $Q(y\mid x)=P(y\mid x)$. Importance weighting the training loss by $Q(x)/P(x)$ corrects for it.
See [Chapter 22](22-Machine-Learning-in-Practice.md#222-distribution-shift-covariate-label-concept-detecting-it).

**Cross-entropy loss (log loss)**
The classification loss $-\log$ of the probability the model gave the true class, averaged over examples. Minimising it is the same as maximising the likelihood, and it is the standard loss from logistic regression to language models.
See [Chapter 3](03-The-Math-Toolkit.md#37-information-entropy-cross-entropy-kl-divergence) and [Chapter 6](06-Classification-and-Logistic-Regression.md#63-logistic-regression).

**Cross-validation**
Estimating test performance by splitting the data into $k$ folds, training on $k-1$ and evaluating on the remaining one, and averaging over the folds. Folds may be stratified by class, grouped by source, or arranged forward in time.
See [Chapter 1](01-What-Is-Machine-Learning.md#14-training-validation-and-test-data) and [Chapter 7](07-Evaluating-Models.md#75-cross-validation).

**Curse of dimensionality**
The ways high dimension defeats methods that rely on nearby points: neighbourhoods stop being small, volume lies near the edge, all distances become about equal, and the data needed grows exponentially. Real data escapes it only through low intrinsic dimension.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#92-the-curse-of-dimensionality-shown-by-computation).

## D

**Data augmentation**
Adding modified copies of training examples, such as shifted, flipped or slightly rotated images or inputs with a little noise. It acts as a regulariser by teaching the model which changes should not matter.
See [Chapter 8](08-Overfitting-and-Regularization.md#85-early-stopping-data-augmentation-and-model-selection) and [Chapter 16](16-Training-Deep-Networks.md#164-regularization-weight-decay-dropout-augmentation).

**Data leakage**
Information that will not be available when the model is used finding its way into training or evaluation, for example a feature that is a consequence of the label, preprocessing fitted on all the data, or the same patient on both sides of a split. It is the most common reason a model that scores brilliantly in development fails in use.
See [Chapter 2](02-Data-and-Features.md#26-splitting-well) and [Chapter 22](22-Machine-Learning-in-Practice.md#221-from-notebook-to-system-pipelines-reproducibility-versioning-data).

**DBSCAN**
Density-based clustering with two parameters, a radius $\varepsilon$ and a count minPts: clusters are groups of core points that reach each other through dense neighbourhoods, plus their border points, and points in sparse regions are labelled noise. It finds clusters of any shape.
See [Chapter 13](13-Clustering.md#136-density-based-clustering-dbscan).

**Decision boundary**
The set of inputs where a classifier switches from one class to another. For a linear classifier it is a hyperplane; adding features such as products lets a linear model draw curved boundaries in the original space.
See [Chapter 6](06-Classification-and-Logistic-Regression.md#61-from-numbers-to-classes) and [Chapter 6](06-Classification-and-Logistic-Regression.md#66-decision-boundaries).

**Decision tree**
A model that predicts by asking a sequence of questions about single features, such as "is $x_3\le2.7$?", following branches from the root to a leaf that holds the prediction. It cuts the input space into axis-aligned boxes.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#111-trees-as-twenty-questions-gini-impurity-and-entropy-information-gain).

**Demographic parity**
A fairness criterion requiring equal selection rates $\Pr[\hat y=1\mid g]$ across groups, whatever the true labels.
See [Chapter 22](22-Machine-Learning-in-Practice.md#223-fairness-measured-technically).

**Denoising diffusion probabilistic model (DDPM)**
A diffusion model in which a fixed forward process adds Gaussian noise over many steps and a network is trained to predict the added noise, a simplified form of the ELBO. Sampling runs the learned reverse process from pure noise.
See [Chapter 20](20-Generative-Models.md#205-diffusion-models).

**Differential privacy**
A guarantee that an algorithm's output distribution changes by at most a factor $e^\varepsilon$ when any one person's record is added or removed, so the output reveals little about any individual. It survives post-processing and composes by adding the budgets.
See [Chapter 22](22-Machine-Learning-in-Practice.md#226-privacy-preserving-learning).

**Dimensionality reduction**
Describing each data point by fewer numbers while keeping what matters, for seeing, compressing, denoising or helping other models. PCA is the linear method; Isomap, t-SNE, UMAP and autoencoders are non-linear ones.
See [Chapter 1](01-What-Is-Machine-Learning.md#12-kinds-of-learning) and [Chapter 14](14-Dimensionality-Reduction.md#141-why-fewer-dimensions-seeing-compressing-denoising).

**Discriminative model**
A model that learns $P(y\mid x)$ directly, or just a decision boundary, without modelling how the inputs are distributed. Logistic regression is the standard example.
See [Chapter 12](12-Probabilistic-Models.md#121-generative-vs-discriminative).

**Distribution shift**
A difference between the distribution a model was trained on and the one it meets in use, which breaks the i.i.d. assumption behind every guarantee. Its main kinds are covariate shift, label shift and concept shift.
See [Chapter 22](22-Machine-Learning-in-Practice.md#222-distribution-shift-covariate-label-concept-detecting-it).

**Dot product**
The sum of the products of two vectors' entries, $u\cdot v=\sum_ju_jv_j$. It equals $\lVert u\rVert\lVert v\rVert\cos\theta$, so it measures how much two vectors point the same way.
See [Chapter 3](03-The-Math-Toolkit.md#31-vectors-and-dot-products).

**Double descent**
The observation that, as model size grows past the point where the model can fit the training data exactly, test error can fall again after its classical U-shaped peak. It is one of the things classical learning theory does not explain.
See [Chapter 8](08-Overfitting-and-Regularization.md#82-the-bias-variance-decomposition) and [Chapter 21](21-Learning-Theory.md#216-what-theory-does-not-explain).

**Dropout**
A regulariser that, during training, sets each hidden unit to zero with probability $p$ independently for every example and step, so units cannot rely on each other. Inverted dropout scales survivors by $1/(1-p)$ so nothing changes at test time.
See [Chapter 16](16-Training-Deep-Networks.md#164-regularization-weight-decay-dropout-augmentation) and [Chapter 17](17-Convolutional-Networks.md#175-architectures-lenet-alexnet-vgg-resnet).

## E

**Early stopping**
Keeping the weights from the training step with the best validation error instead of training to the end. For gradient descent on least squares, running $t$ steps is roughly ridge regression with $\lambda=1/(\alpha t)$.
See [Chapter 8](08-Overfitting-and-Regularization.md#85-early-stopping-data-augmentation-and-model-selection) and [Chapter 16](16-Training-Deep-Networks.md#164-regularization-weight-decay-dropout-augmentation).

**Eigenvector**
A nonzero vector $v$ that a square matrix maps to a multiple of itself, $Av=\lambda v$; the factor $\lambda$ is its eigenvalue. A symmetric matrix has real eigenvalues and orthogonal eigenvectors.
See [Chapter 3](03-The-Math-Toolkit.md#36-eigenvectors-and-the-svd-in-one-picture).

**Elastic net**
Regression with both an L1 and an L2 penalty. It keeps the lasso's exact zeros but adds the grouping effect, giving correlated features nearly equal weights, and has a unique solution.
See [Chapter 8](08-Overfitting-and-Regularization.md#86-effective-degrees-of-freedom-and-the-elastic-net).

**Embedding**
A placement of objects in a vector space where geometry carries meaning, such as a low-dimensional map of data or a learned vector for each token in a vocabulary.
See [Chapter 14](14-Dimensionality-Reduction.md#141-why-fewer-dimensions-seeing-compressing-denoising) and [Chapter 18](18-Sequence-Models.md#181-text-time-series-and-audio-as-sequences).

**Emergent ability**
A capability that is near chance for smaller models and rises sharply beyond some size, not predictable by extrapolating from smaller ones. Part of the effect comes from all-or-nothing metrics such as exact match.
See [Chapter 23](23-Where-Machine-Learning-Goes.md#233-in-context-learning-and-emergent-behaviour).

**Empirical risk minimisation (ERM)**
The learning rule that picks the hypothesis with the smallest training error in its class. Regularised ERM adds a penalty, as in ridge regression and SVMs.
See [Chapter 10](10-Support-Vector-Machines.md#103-soft-margin-and-hinge-loss) and [Chapter 21](21-Learning-Theory.md#211-the-question-why-does-a-model-that-fits-training-data-work-on-new-data).

**Entropy**
The expected surprise of a distribution, $H=-\sum_ip_i\log p_i$: 0 when one outcome is certain and largest, $\log k$, when $k$ outcomes are equally likely. Decision trees use it as an impurity measure.
See [Chapter 3](03-The-Math-Toolkit.md#37-information-entropy-cross-entropy-kl-divergence) and [Chapter 11](11-Decision-Trees-and-Ensembles.md#111-trees-as-twenty-questions-gini-impurity-and-entropy-information-gain).

**Epoch**
One pass over all the training examples. Mini-batch training shuffles the data each epoch and walks through it in batches.
See [Chapter 5](05-Optimization.md#53-stochastic-and-mini-batch-gradient-descent).

**Equal opportunity**
A fairness criterion requiring equal true positive rates across groups: among people who really are positive, each group is selected at the same rate.
See [Chapter 22](22-Machine-Learning-in-Practice.md#223-fairness-measured-technically).

**Equalised odds**
A fairness criterion requiring both the true positive rate and the false positive rate to be equal across groups.
See [Chapter 22](22-Machine-Learning-in-Practice.md#223-fairness-measured-technically).

**Equivariance**
The property that transforming the input transforms the output the same way, $F(T x)=T F(x)$. Convolution is equivariant to shifts; self-attention without positions and graph layers are equivariant to permutations.
See [Chapter 17](17-Convolutional-Networks.md#173-pooling-receptive-fields-translation-equivariance), [Chapter 19](19-Transformers.md#193-multi-head-attention-positional-encodings) and [Chapter 23](23-Where-Machine-Learning-Goes.md#235-graph-neural-networks-geometric-deep-learning-and-ml-for-science).

**Euclidean distance**
The straight-line distance between two points, the square root of the sum of squared coordinate differences, $\lVert a-b\rVert_2$.
See [Chapter 1](01-What-Is-Machine-Learning.md#13-a-first-learner-from-scratch) and [Chapter 3](03-The-Math-Toolkit.md#31-vectors-and-dot-products).

**Evidence lower bound (ELBO)**
A lower bound on the log-likelihood obtained from Jensen's inequality with any distribution over the hidden variables; it is tight when that distribution is the true posterior. EM maximises it by coordinate ascent, and variational autoencoders maximise it by gradient.
See [Chapter 13](13-Clustering.md#134-gaussian-mixtures-and-the-em-algorithm) and [Chapter 20](20-Generative-Models.md#202-autoencoders-and-variational-autoencoders).

**Expectation-maximization (EM)**
An algorithm for fitting models with hidden variables that alternates an E step (compute the posterior over the hidden variables, such as responsibilities) and an M step (refit the parameters to it). Each round never decreases the likelihood.
See [Chapter 13](13-Clustering.md#134-gaussian-mixtures-and-the-em-algorithm) and [Chapter 14](14-Dimensionality-Reduction.md#144-probabilistic-pca-and-factor-analysis).

**Explained variance ratio**
The share of total variance along one principal component, $\lambda_j/\sum_m\lambda_m$. Its running sum is used to decide how many components to keep.
See [Chapter 14](14-Dimensionality-Reduction.md#143-how-many-components-explained-variance).

**Exploding gradient**
Gradients that grow exponentially as they are passed back through many layers or time steps, so that one step can throw the weights far away. Gradient clipping and careful initialisation control it.
See [Chapter 16](16-Training-Deep-Networks.md#161-vanishing-and-exploding-gradients-shown) and [Chapter 18](18-Sequence-Models.md#183-recurrent-networks-backprop-through-time).

## F

**F1 score**
The harmonic mean of precision and recall, $2PR/(P+R)$. It is high only when both are high; for several classes it is macro-averaged (each class equal) or micro-averaged (pooled counts).
See [Chapter 7](07-Evaluating-Models.md#72-the-confusion-matrix-precision-recall-and-f1).

**False positive and false negative**
The two kinds of mistake of a binary classifier: predicting positive for a true negative (a false alarm), and predicting negative for a true positive (a miss).
See [Chapter 7](07-Evaluating-Models.md#72-the-confusion-matrix-precision-recall-and-f1).

**Fast gradient sign method (FGSM)**
A one-step attack that moves every input coordinate by $\varepsilon$ in the direction of the sign of the loss gradient, the worst change of that size to first order. It shows how easily adversarial examples are found.
See [Chapter 22](22-Machine-Learning-in-Practice.md#225-robustness-adversarial-examples).

**Feature**
One measured quantity that describes an example, such as length or price. The features of one example form its feature vector, and stacking those as rows gives the feature matrix.
See [Chapter 1](01-What-Is-Machine-Learning.md#12-kinds-of-learning) and [Chapter 2](02-Data-and-Features.md#21-rows-columns-labels).

**Feature engineering**
Building new features from the raw ones using knowledge of the problem, such as logs of skewed quantities, ratios, products (interactions), points on a circle for cyclic values, or bins.
See [Chapter 2](02-Data-and-Features.md#25-feature-engineering-and-interactions).

**Feature map (convolution)**
The output array of one convolutional filter: how strongly the filter's pattern appears at each position of the input.
See [Chapter 17](17-Convolutional-Networks.md#172-convolution-from-scratch-filters-edges-stride-padding).

**Federated learning**
Training one model across many devices or institutions without collecting their data. In federated averaging each client trains on its own data and the server averages the updated weights, often with secure aggregation and differential privacy.
See [Chapter 22](22-Machine-Learning-in-Practice.md#226-privacy-preserving-learning).

**Filter (kernel)**
A small array of weights slid over an image in a convolution. Learned filters detect patterns such as edges at the first layer and more complex parts deeper.
See [Chapter 17](17-Convolutional-Networks.md#172-convolution-from-scratch-filters-edges-stride-padding).

**Fine-tuning**
Starting from a pretrained model, replacing or adding a small output layer and training on the new task's data, usually with a small learning rate so the useful features are adjusted rather than destroyed.
See [Chapter 17](17-Convolutional-Networks.md#176-transfer-learning-what-filters-learn) and [Chapter 19](19-Transformers.md#197-pretraining-gpt-bert-vision-transformers).

**FlashAttention**
An exact attention algorithm that processes queries, keys and values in blocks held in fast on-chip memory, with a running softmax, so the full $n\times n$ score matrix is never stored. It saves memory and time without changing the result.
See [Chapter 19](19-Transformers.md#198-the-cost-of-attention-efficient-attention).

**Foundation model**
A model trained on broad data, usually self-supervised and at scale, that is then adapted to many downstream tasks by fine-tuning, a linear probe or simply prompting.
See [Chapter 23](23-Where-Machine-Learning-Goes.md#232-self-supervised-and-contrastive-learning-foundation-models).

**Fundamental theorem of statistical learning**
The result that, for binary classification with zero-one loss, uniform convergence, agnostic PAC learnability, PAC learnability and success of ERM are all equivalent to finite VC dimension, with a sample complexity governed by the VC dimension.
See [Chapter 21](21-Learning-Theory.md#213-the-vc-dimension).

## G

**GAN (generative adversarial network)**
A generative model trained as a game: a generator maps noise to samples, and a discriminator tries to tell them from real data. At the game's optimum the generator's distribution equals the data distribution; in practice training can circle instead of converging, or suffer mode collapse.
See [Chapter 20](20-Generative-Models.md#203-gans-the-minimax-game).

**Gaussian distribution**
The normal distribution $\mathcal N(\mu,\sigma^2)$, the bell curve with mean $\mu$ and variance $\sigma^2$. By the central limit theorem, sums of many small independent effects are close to it.
See [Chapter 3](03-The-Math-Toolkit.md#34-probability).

**Gaussian mixture model (GMM)**
A model in which each point comes from one of $k$ Gaussians, chosen with probabilities given by the mixing weights. Fitted by EM, it gives soft clusters shaped as ellipses.
See [Chapter 13](13-Clustering.md#134-gaussian-mixtures-and-the-em-algorithm).

**Gaussian process**
A prior on functions in which the values at any finite set of inputs are jointly Gaussian, with covariances given by a kernel. Conditioning on data gives predictions with error bars that grow away from the data.
See [Chapter 12](12-Probabilistic-Models.md#126-gaussian-processes-from-scratch).

**Generalisation**
Doing well on new data from the same source, not just on the training examples. The difference between test and training performance is the generalisation gap.
See [Chapter 1](01-What-Is-Machine-Learning.md#14-training-validation-and-test-data) and [Chapter 21](21-Learning-Theory.md#211-the-question-why-does-a-model-that-fits-training-data-work-on-new-data).

**Generalised linear model (GLM)**
A model with three parts: an exponential-family distribution for $y$, a linear score $w^\top x$, and a link function connecting the mean of $y$ to the score. Linear, logistic and Poisson regression are all GLMs.
See [Chapter 6](06-Classification-and-Logistic-Regression.md#67-generalised-linear-models-and-why-the-logistic-loss-is-convex).

**Generative model**
A model of how the data is produced: in classification, a class prior $P(y)$ with class-conditional distributions $p(x\mid y)$; in general, a distribution $p_\theta$ close to the data's that can be sampled from or evaluated.
See [Chapter 12](12-Probabilistic-Models.md#121-generative-vs-discriminative) and [Chapter 20](20-Generative-Models.md#201-what-it-means-to-model-a-distribution-sampling).

**Gini impurity**
$1-\sum_kp_k^2$: the probability that two members of a group drawn at random have different classes. CART uses it to choose splits.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#111-trees-as-twenty-questions-gini-impurity-and-entropy-information-gain).

**GPT**
Generative pretrained transformer: a decoder-only transformer trained as a causal language model on large text, then fine-tuned or prompted. Larger GPT models showed in-context learning.
See [Chapter 19](19-Transformers.md#197-pretraining-gpt-bert-vision-transformers).

**Gradient**
The vector of a function's partial derivatives, $\nabla L$. It points in the direction of steepest increase, so stepping against it decreases the loss fastest.
See [Chapter 3](03-The-Math-Toolkit.md#33-derivatives-gradients-and-the-chain-rule) and [Chapter 5](05-Optimization.md#51-loss-landscapes-and-convexity).

**Gradient boosting**
Gradient descent in function space: each new tree is fitted to the pseudo-residuals, the negative gradients of the loss at the current predictions, and added with a small learning rate. With trees it is the strongest default for tabular data.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#115-gradient-boosting-friedman-2001-from-scratch-for-regression).

**Gradient clipping**
Capping the length of the whole gradient at a threshold $c$, rescaling it to length $c$ when it is longer, so that one enormous gradient cannot destroy training.
See [Chapter 16](16-Training-Deep-Networks.md#165-optimizers-in-practice-learning-rates-schedules-clipping).

**Gradient descent**
Minimising a loss by repeatedly stepping against the gradient, $w\leftarrow w-\alpha\nabla L(w)$, with step size or learning rate $\alpha$. On convex smooth losses it converges, linearly when the loss is strongly convex.
See [Chapter 3](03-The-Math-Toolkit.md#33-derivatives-gradients-and-the-chain-rule), [Chapter 4](04-Linear-Regression.md#44-gradient-descent-from-scratch) and [Chapter 5](05-Optimization.md#51-loss-landscapes-and-convexity).

**Graph Laplacian**
The matrix $L=D-W$ of a weighted graph, with $D$ the diagonal of degrees. Its quadratic form $f^\top Lf$ sums $w_{ij}(f_i-f_j)^2$ over edges, and its smallest eigenvectors reveal connected groups, which spectral clustering uses.
See [Chapter 13](13-Clustering.md#137-spectral-clustering).

**Graph neural network**
A network that works on graphs, updating each node's vector from its neighbours' by message passing, in a way that is equivariant to renumbering the nodes. Its power to tell graphs apart is at most that of the 1-dimensional Weisfeiler-Lehman test.
See [Chapter 23](23-Where-Machine-Learning-Goes.md#235-graph-neural-networks-geometric-deep-learning-and-ml-for-science).

## H

**Hashing trick**
Encoding a categorical value or word by sending it to column $h(\text{value})\bmod b$ for a hash function $h$ and a fixed number of buckets $b$, with no vocabulary. Collisions add some noise; a second hash for the sign makes them cancel on average.
See [Chapter 2](02-Data-and-Features.md#23-encoding-one-hot-ordinal-hashing).

**He initialisation**
Initialising weights with variance $2/n_{\text{in}}$, which keeps activation variance constant through ReLU layers, since ReLU zeroes half its inputs.
See [Chapter 15](15-Neural-Networks-and-Backpropagation.md#157-training-an-mlp-from-scratch-on-two-spirals) and [Chapter 16](16-Training-Deep-Networks.md#162-initialization-xavier-and-he-derived-from-variance).

**Hessian**
The matrix of second derivatives of a function. Its eigenvalues give the curvature in each direction: all positive at a strict local minimum, of mixed signs at a saddle point.
See [Chapter 4](04-Linear-Regression.md#44-gradient-descent-from-scratch) and [Chapter 5](05-Optimization.md#51-loss-landscapes-and-convexity).

**Hidden layer**
A layer of a network that is neither input nor output, whose values are not given by the data. Hidden layers learn new features in which the problem becomes easy for the last layer, which is how a network solves XOR.
See [Chapter 15](15-Neural-Networks-and-Backpropagation.md#151-from-the-perceptron-to-layers-why-xor-needs-a-hidden-layer).

**Hierarchical clustering**
Clustering that builds a whole tree of nested groupings, usually agglomeratively by merging the closest clusters, drawn as a dendrogram. The linkage decides which clusters are closest.
See [Chapter 13](13-Clustering.md#135-hierarchical-clustering-linkages-dendrograms).

**Hinge loss**
The loss $\max(0,1-m)$ of the margin $m=yf(x)$: zero for confidently correct points and rising linearly otherwise. The soft-margin SVM is regularised empirical risk minimisation with it.
See [Chapter 10](10-Support-Vector-Machines.md#103-soft-margin-and-hinge-loss).

**Hoeffding's inequality**
The bound that the mean of $m$ independent variables in $[0,1]$ is more than $\varepsilon$ from its expectation with probability at most $2e^{-2m\varepsilon^2}$. It is the basic tool behind finite-class generalisation bounds.
See [Chapter 21](21-Learning-Theory.md#212-pac-learning-and-the-finite-class-bound).

**Hyperparameter**
A setting chosen by the person rather than learned from training data by the fit itself, such as $k$ in k-NN, a penalty strength or a learning rate. It is chosen on validation data or by cross-validation.
See [Chapter 7](07-Evaluating-Models.md#75-cross-validation).

**Hyperplane**
The set of points with $w\cdot x+b=0$: a line in two dimensions, a plane in three. It is the decision boundary of every linear classifier, with $w$ its normal vector.
See [Chapter 6](06-Classification-and-Logistic-Regression.md#61-from-numbers-to-classes) and [Chapter 10](10-Support-Vector-Machines.md#101-the-widest-margin-geometry-of-the-margin-derived).

**Hypothesis class**
The family of rules a learner chooses from, such as all straight lines or all trees of depth five. Its richness controls the bias-complexity trade-off.
See [Chapter 1](01-What-Is-Machine-Learning.md#15-the-workflow) and [Chapter 21](21-Learning-Theory.md#211-the-question-why-does-a-model-that-fits-training-data-work-on-new-data).

## I

**i.i.d. (independently and identically distributed)**
The assumption that each example is a fresh, independent draw from the same distribution. Every generalisation guarantee rests on it, and distribution shift is what happens when it fails.
See [Chapter 21](21-Learning-Theory.md#211-the-question-why-does-a-model-that-fits-training-data-work-on-new-data).

**Implicit bias (implicit regularisation)**
The preference of an optimisation algorithm for some solutions among the many that fit the data. Gradient descent on logistic loss of separable data heads towards the maximum-margin direction, and on overparameterised models it finds solutions that often generalise.
See [Chapter 6](06-Classification-and-Logistic-Regression.md#64-the-gradient-and-training-from-scratch) and [Chapter 21](21-Learning-Theory.md#216-what-theory-does-not-explain).

**Importance weight**
The ratio $w(x)=Q(x)/P(x)$ of deployment to training density. Weighting the training loss by it corrects for covariate shift, at the cost of a smaller effective sample size.
See [Chapter 22](22-Machine-Learning-in-Practice.md#222-distribution-shift-covariate-label-concept-detecting-it).

**Impossibility theorem for fairness**
The result of Kleinberg, Mullainathan and Raghavan (2016) that a score calibrated within groups and balanced for both classes is possible only if the groups have equal base rates or the score is perfect.
See [Chapter 22](22-Machine-Learning-in-Practice.md#223-fairness-measured-technically).

**Impurity importance**
A feature importance that adds up the impurity reductions of every split on a feature over all trees. It is biased towards features with many possible split points, even pure noise.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#117-feature-importance-and-its-pitfalls).

**Imputation**
Filling missing values, for example with the column's mean, median or mode, or with a model's prediction. The values must be computed from the training set only, and a missing-value indicator can record what was filled.
See [Chapter 2](02-Data-and-Features.md#22-cleaning-missing-values-outliers-duplicates).

**In-context learning**
A language model's ability to perform a new task from a few examples placed in its prompt, with no change to its weights. The "learning" happens inside the forward pass; for linear regression tasks, linear self-attention can implement a step of gradient descent.
See [Chapter 19](19-Transformers.md#197-pretraining-gpt-bert-vision-transformers) and [Chapter 23](23-Where-Machine-Learning-Goes.md#233-in-context-learning-and-emergent-behaviour).

**Inductive bias**
A learner's built-in preference for some answers over others, such as "close means similar" for nearest neighbours or locality and weight sharing for CNNs. By the no-free-lunch theorem, no learner works without one.
See [Chapter 1](01-What-Is-Machine-Learning.md#16-what-machine-learning-cannot-do) and [Chapter 17](17-Convolutional-Networks.md#171-images-as-arrays-why-fully-connected-fails).

**Information gain**
The reduction in entropy of the class labels from splitting on a test, which equals the mutual information between the test's answer and the class. It favours tests with many outcomes, which the gain ratio corrects.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#111-trees-as-twenty-questions-gini-impurity-and-entropy-information-gain).

**Intersection over union (IoU)**
The area of overlap of a predicted and a true box (or mask) divided by the area of their union. Detection counts a prediction as correct when IoU exceeds a threshold such as 0.5.
See [Chapter 17](17-Convolutional-Networks.md#177-beyond-classification-detection-segmentation-u-net-2015).

**Intrinsic dimension**
The number of directions of real variation in data, which can be far fewer than the number of coordinates, as for images lying near a thin curved manifold. It is what decides whether nearest neighbours work.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#92-the-curse-of-dimensionality-shown-by-computation) and [Chapter 14](14-Dimensionality-Reduction.md#141-why-fewer-dimensions-seeing-compressing-denoising).

**Isomap**
A non-linear embedding that replaces straight-line distances by geodesic distances, shortest paths through a nearest-neighbour graph, and then applies classical MDS. Too many neighbours cause short circuits across folds.
See [Chapter 14](14-Dimensionality-Reduction.md#145-non-linear-methods-mds-isomap-t-sne-umap).

## J

**Jensen-Shannon divergence**
A symmetric divergence between distributions $p$ and $q$, the average KL divergence of each from their mixture $(p+q)/2$. The original GAN objective with the best discriminator minimises it.
See [Chapter 20](20-Generative-Models.md#203-gans-the-minimax-game).

## K

**k-d tree**
A binary tree that splits space by one coordinate at a time, at the median, for fast nearest-neighbour search: search the near side first and visit the far side only if it could hold a closer point. It works well in low dimensions.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#93-fast-neighbour-search-k-d-trees-and-approximate-search).

**k-fold cross-validation**
Splitting data into $k$ folds and training $k$ times, each time validating on one fold and training on the rest, so every example is used for validation exactly once.
See [Chapter 7](07-Evaluating-Models.md#75-cross-validation).

**k-means**
Clustering into $k$ groups that minimises the within-cluster sum of squares. Lloyd's algorithm alternates assigning each point to its nearest centre and moving each centre to the mean of its points; it always stops, but possibly at a poor local minimum.
See [Chapter 13](13-Clustering.md#132-k-means-lloyds-algorithm-and-k-means).

**k-means++**
A seeding for k-means that picks each new starting centre with probability proportional to its squared distance from the centres already chosen. Its expected cost is within a factor $8(\ln k+2)$ of the optimum.
See [Chapter 13](13-Clustering.md#132-k-means-lloyds-algorithm-and-k-means).

**k-nearest neighbours (k-NN)**
Predict for a new point from its $k$ closest training points: majority vote for classification, average for regression. It is lazy, low in bias and high in variance for small $k$, and needs scaled features and a sensible distance.
See [Chapter 1](01-What-Is-Machine-Learning.md#13-a-first-learner-from-scratch) and [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#91-k-nn-revisited-choosing-k-distance-metrics-scaling).

**Karush-Kuhn-Tucker (KKT) conditions**
The conditions that characterise the optimum of a convex constrained problem: stationarity of the Lagrangian, primal feasibility, dual feasibility and complementary slackness. For SVMs they show the solution depends only on the support vectors.
See [Chapter 10](10-Support-Vector-Machines.md#104-lagrange-duality-kkt-conditions-support-vectors).

**Kernel**
A function $k(x,z)$ that measures similarity. In kernel density estimation and smoothing it is a bump that weights points by distance; in kernel methods it is a dot product in some feature space, $k(x,z)=\varphi(x)\cdot\varphi(z)$.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#94-kernel-density-estimation-and-kernel-regression) and [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#95-the-kernel-trick-positive-definite-kernels-mercer-stated).

**Kernel density estimation (KDE)**
Estimating a density by placing a small bump (a kernel) of width $h$ on every data point and averaging. The bandwidth $h$ trades bias against variance.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#94-kernel-density-estimation-and-kernel-regression).

**Kernel ridge regression**
Ridge regression with dot products replaced by a kernel: the prediction is $\sum_i\alpha_ik(x_i,x)$ with $\alpha=(K+\lambda I)^{-1}y$. It fits non-linear functions at the cost of solving an $n\times n$ system.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#96-kernel-ridge-regression-from-scratch).

**Kernel trick**
Replacing every dot product in an algorithm by a kernel $k(x,z)$, which runs the algorithm in a large feature space without ever computing the features.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#95-the-kernel-trick-positive-definite-kernels-mercer-stated).

**KL divergence (Kullback-Leibler divergence)**
$D_{\mathrm{KL}}(P\|Q)=\sum_iP_i\log(P_i/Q_i)$: the extra expected surprise from using model $Q$ when the truth is $P$, equal to cross-entropy minus entropy. It is never negative and not symmetric.
See [Chapter 3](03-The-Math-Toolkit.md#37-information-entropy-cross-entropy-kl-divergence).

## L

**$L$-smooth function**
A differentiable function whose gradient never changes faster than $L$ times the distance moved, $\lVert\nabla f(x)-\nabla f(y)\rVert\le L\lVert x-y\rVert$; for twice-differentiable functions, Hessian eigenvalues at most $L$.
See [Chapter 5](05-Optimization.md#52-how-fast-gradient-descent-converges).

**L1 norm**
The sum of the absolute values of a vector's entries, $\lVert u\rVert_1=\sum_j|u_j|$, whose distance is the Manhattan distance. As a penalty it drives weights exactly to zero, which is the lasso.
See [Chapter 3](03-The-Math-Toolkit.md#31-vectors-and-dot-products) and [Chapter 8](08-Overfitting-and-Regularization.md#84-the-lasso).

**Label**
The right answer attached to an example in supervised learning, also called the target and written $y$.
See [Chapter 1](01-What-Is-Machine-Learning.md#12-kinds-of-learning) and [Chapter 2](02-Data-and-Features.md#21-rows-columns-labels).

**Label shift**
Distribution shift in which the share of each class changes but each class looks the same, $Q(y)\ne P(y)$ with $Q(x\mid y)=P(x\mid y)$. Also called prior shift.
See [Chapter 22](22-Machine-Learning-in-Practice.md#222-distribution-shift-covariate-label-concept-detecting-it).

**Language model**
A model that gives a probability to every sequence of tokens by predicting each next token from the ones before. Its loss is the sum of the cross-entropies of the next-token predictions.
See [Chapter 18](18-Sequence-Models.md#181-text-time-series-and-audio-as-sequences) and [Chapter 19](19-Transformers.md#197-pretraining-gpt-bert-vision-transformers).

**Laplace smoothing**
Adding one (or $\alpha$) to every count before estimating probabilities, so that no word seen zero times gets probability zero. It is the posterior mean under a uniform prior.
See [Chapter 12](12-Probabilistic-Models.md#122-naive-bayes-for-text-spam-laplace-smoothing).

**Lasso**
Least squares plus $\lambda$ times the L1 norm of the weights. It shrinks weights and sets many exactly to zero, so it also selects features; coordinate descent with soft-thresholding solves it.
See [Chapter 8](08-Overfitting-and-Regularization.md#84-the-lasso).

**Latent variable**
A hidden variable that is not observed but helps explain the data, such as which mixture component produced a point or the code of a variational autoencoder.
See [Chapter 13](13-Clustering.md#134-gaussian-mixtures-and-the-em-algorithm), [Chapter 14](14-Dimensionality-Reduction.md#144-probabilistic-pca-and-factor-analysis) and [Chapter 20](20-Generative-Models.md#202-autoencoders-and-variational-autoencoders).

**Layer normalisation**
Normalising the features of one example to mean 0 and variance 1, then applying a learned scale and shift, instead of normalising over the batch. It works the same at training and test time and is the norm used in transformers.
See [Chapter 16](16-Training-Deep-Networks.md#163-normalization-batch-norm-and-layer-norm) and [Chapter 19](19-Transformers.md#194-the-transformer-block).

**Learning rate**
The step size $\alpha$ of gradient descent. Too large and training diverges; too small and it crawls. In practice it follows a schedule and is found with a range test.
See [Chapter 3](03-The-Math-Toolkit.md#33-derivatives-gradients-and-the-chain-rule), [Chapter 5](05-Optimization.md#51-loss-landscapes-and-convexity) and [Chapter 16](16-Training-Deep-Networks.md#165-optimizers-in-practice-learning-rates-schedules-clipping).

**Learning-rate schedule**
The learning rate as a function of the step number, such as step decay, inverse square root or cosine decay, usually after a linear warmup.
See [Chapter 5](05-Optimization.md#57-learning-rate-schedules-warmup-and-non-convex-landscapes) and [Chapter 16](16-Training-Deep-Networks.md#165-optimizers-in-practice-learning-rates-schedules-clipping).

**Least squares**
Fitting a model by minimising the sum of squared residuals. It is easy to solve, and it is the maximum likelihood fit when the noise is Gaussian.
See [Chapter 4](04-Linear-Regression.md#41-fitting-a-line).

**Leave-one-out cross-validation**
Cross-validation with as many folds as examples: predict each point from a model trained on all the others. For linear smoothers it needs no refitting, since each left-out residual is $e_i/(1-h_{ii})$.
See [Chapter 1](01-What-Is-Machine-Learning.md#13-a-first-learner-from-scratch) and [Chapter 7](07-Evaluating-Models.md#75-cross-validation).

**Likelihood**
The probability (or density) of the observed data under a model, read as a function of the parameters. It ranks parameter values by how well they explain the data.
See [Chapter 3](03-The-Math-Toolkit.md#35-likelihood-and-maximum-likelihood).

**Linear discriminant analysis (LDA)**
Gaussian discriminant analysis with one covariance shared by all classes, which gives linear decision boundaries. Its posterior has exactly the form of logistic regression.
See [Chapter 12](12-Probabilistic-Models.md#125-gaussian-discriminant-analysis-ldaqda).

**Linear regression**
Predicting a number as a weighted sum of features plus an intercept, $\hat y=w\cdot x+w_0$, usually fitted by least squares.
See [Chapter 4](04-Linear-Regression.md#41-fitting-a-line) and [Chapter 4](04-Linear-Regression.md#43-many-features-the-design-matrix-polynomial-features).

**Linkage**
The rule for the distance between two clusters in hierarchical clustering: single (closest pair), complete (farthest pair), average (mean over pairs) or Ward's (increase in within-cluster sum of squares).
See [Chapter 13](13-Clustering.md#135-hierarchical-clustering-linkages-dendrograms).

**Locality-sensitive hashing (LSH)**
Approximate nearest-neighbour search with hash functions designed so that close points collide more often than far ones; only points in the query's buckets are compared.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#93-fast-neighbour-search-k-d-trees-and-approximate-search).

**Log-likelihood**
The logarithm of the likelihood. It has its maximum at the same place, turns products over examples into sums, and its negative is the usual training loss.
See [Chapter 3](03-The-Math-Toolkit.md#35-likelihood-and-maximum-likelihood).

**Logistic regression**
A linear classifier that turns the score $w\cdot x+b$ into a probability with the sigmoid, so the log-odds of class 1 are linear in the features. It is fitted by minimising the cross-entropy loss, which is convex.
See [Chapter 6](06-Classification-and-Logistic-Regression.md#63-logistic-regression).

**Logit**
The log-odds $\log(p/(1-p))$, the inverse of the sigmoid. In networks, "logits" also means the raw output scores that go into a softmax or sigmoid.
See [Chapter 6](06-Classification-and-Logistic-Regression.md#63-logistic-regression) and [Chapter 15](15-Neural-Networks-and-Backpropagation.md#153-forward-pass-in-matrices).

**Long short-term memory (LSTM)**
A recurrent cell with a separate cell state updated mostly by addition, controlled by forget, input and output gates. Because memory flows through addition, gradients survive over long sequences.
See [Chapter 18](18-Sequence-Models.md#184-lstm-and-gru-gates-explained).

**Loss function**
A number measuring how badly a model does on one example, such as the squared difference between prediction and truth. Training minimises its average over the training set.
See [Chapter 1](01-What-Is-Machine-Learning.md#15-the-workflow).

## M

**Machine learning**
Building programs that learn rules from examples instead of having the rules written by hand: a program learns from experience $E$ at task $T$ if its performance $P$ improves with $E$.
See [Chapter 1](01-What-Is-Machine-Learning.md#11-programs-that-learn-from-examples-instead-of-rules).

**Manifold hypothesis**
The belief that real high-dimensional data, such as photographs, lies near a much lower-dimensional curved surface (a manifold). It explains why methods that suffer from the curse of dimensionality can still work.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#92-the-curse-of-dimensionality-shown-by-computation) and [Chapter 14](14-Dimensionality-Reduction.md#141-why-fewer-dimensions-seeing-compressing-denoising).

**MAP estimate (maximum a posteriori)**
The parameter value with the highest posterior probability: maximum likelihood plus a penalty equal to minus the log prior. With a Gaussian prior on the weights it is ridge regression.
See [Chapter 8](08-Overfitting-and-Regularization.md#83-ridge-regression) and [Chapter 12](12-Probabilistic-Models.md#123-mle-vs-map-vs-full-bayes-conjugate-priors-beta-binomial-worked).

**Margin**
The distance between a classifier's boundary and the nearest training point, or for one example its signed confidence $yf(x)$. Wide margins give generalisation bounds that do not depend on the dimension.
See [Chapter 10](10-Support-Vector-Machines.md#101-the-widest-margin-geometry-of-the-margin-derived) and [Chapter 21](21-Learning-Theory.md#214-rademacher-complexity-and-margins).

**Marginal likelihood (evidence)**
The probability of the data under a model with its parameters integrated out. Maximising it chooses hyperparameters and acts as an automatic Occam's razor, since too simple and too flexible models both score low.
See [Chapter 12](12-Probabilistic-Models.md#124-bayesian-linear-regression-posterior-and-predictive-derived) and [Chapter 12](12-Probabilistic-Models.md#126-gaussian-processes-from-scratch).

**Markov chain**
A sequence of random states in which each next state depends only on the current one, through a transition distribution. Under ergodicity its distribution converges to a stationary distribution.
See [Chapter 12](12-Probabilistic-Models.md#127-sampling-monte-carlo-mcmc-metropolis-hastings-from-scratch).

**Markov chain Monte Carlo (MCMC)**
Sampling from a hard distribution, such as a posterior, by running a Markov chain whose stationary distribution is that target and using its states as samples. Metropolis-Hastings, Gibbs sampling and Hamiltonian Monte Carlo are the main methods.
See [Chapter 12](12-Probabilistic-Models.md#127-sampling-monte-carlo-mcmc-metropolis-hastings-from-scratch).

**Maximum likelihood estimate (MLE)**
The parameter value that makes the observed data most probable. For a coin it is the fraction of heads; for linear regression with Gaussian noise it is least squares; most losses in this book are negative log-likelihoods.
See [Chapter 3](03-The-Math-Toolkit.md#35-likelihood-and-maximum-likelihood) and [Chapter 12](12-Probabilistic-Models.md#123-mle-vs-map-vs-full-bayes-conjugate-priors-beta-binomial-worked).

**Mean absolute error (MAE)**
The average absolute residual, $\frac1n\sum|e_i|$, in the units of $y$ and less dominated by a few large errors than MSE. The median minimises it.
See [Chapter 7](07-Evaluating-Models.md#74-regression-metrics).

**Mean squared error (MSE)**
The average squared residual, $\frac1n\sum(y_i-\hat y_i)^2$. The mean minimises it; its square root, RMSE, is in the units of $y$.
See [Chapter 3](03-The-Math-Toolkit.md#33-derivatives-gradients-and-the-chain-rule), [Chapter 4](04-Linear-Regression.md#41-fitting-a-line) and [Chapter 7](07-Evaluating-Models.md#74-regression-metrics).

**Mechanistic interpretability**
Explaining how a model computes from the inside: which internal directions represent which concepts (features) and which weights connect them into computations (circuits), checked by intervening on activations.
See [Chapter 23](23-Where-Machine-Learning-Goes.md#234-mechanistic-interpretability).

**Metropolis-Hastings algorithm**
An MCMC method: from the current state, propose a move from a proposal distribution and accept it with probability $\min(1,\frac{\pi(x')q(x\mid x')}{\pi(x)q(x'\mid x)})$, otherwise stay. Only ratios of $\pi$ appear, so it needs the target only up to a constant.
See [Chapter 12](12-Probabilistic-Models.md#127-sampling-monte-carlo-mcmc-metropolis-hastings-from-scratch).

**Min-max scaling**
Rescaling a feature so its smallest training value maps to 0 and its largest to 1, $x'=(x-\min)/(\max-\min)$. A single outlier squeezes all other values into a small part of the range.
See [Chapter 2](02-Data-and-Features.md#24-scaling-standardisation-and-min-max).

**Mini-batch gradient descent**
Stochastic gradient descent that averages the gradients of a random batch of examples, such as 32 or 256, at each step. The estimate is still unbiased, with less noise than one example, and suits parallel hardware.
See [Chapter 5](05-Optimization.md#53-stochastic-and-mini-batch-gradient-descent).

**Missing at random (MAR)**
Missingness that depends on other recorded columns but not on the missing value itself, so the other columns help to fill the gap. Compare missing completely at random (no dependence at all) and missing not at random (depends on the value itself).
See [Chapter 2](02-Data-and-Features.md#22-cleaning-missing-values-outliers-duplicates).

**Mode collapse**
A GAN failure in which the generator produces only a few kinds of output that the discriminator currently accepts, instead of the full variety of the data.
See [Chapter 20](20-Generative-Models.md#203-gans-the-minimax-game).

**Momentum**
An optimiser that keeps a velocity accumulating past gradients and steps along it, like a heavy ball rolling downhill. It damps zigzags across narrow valleys and turns a condition number $\kappa$ into roughly $\sqrt\kappa$ for quadratics.
See [Chapter 5](05-Optimization.md#54-momentum-and-nesterov) and [Chapter 16](16-Training-Deep-Networks.md#165-optimizers-in-practice-learning-rates-schedules-clipping).

**Multi-head attention**
Running several attention operations, called heads, in parallel with their own smaller projections, then concatenating and mixing their outputs. Different heads can attend to different kinds of relation.
See [Chapter 19](19-Transformers.md#193-multi-head-attention-positional-encodings).

**Multidimensional scaling (MDS)**
Finding points in a low-dimensional space whose distances match a given table of distances. Classical MDS does it with one eigen-decomposition of the double-centred squared-distance matrix.
See [Chapter 14](14-Dimensionality-Reduction.md#145-non-linear-methods-mds-isomap-t-sne-umap).

**Multilayer perceptron (MLP)**
A fully connected feed-forward network: layers of units, each computing an activation of a weight matrix times the previous layer plus a bias.
See [Chapter 15](15-Neural-Networks-and-Backpropagation.md#153-forward-pass-in-matrices).

## N

**Naive Bayes**
A generative classifier that assumes the features are independent given the class. For text it multiplies per-word probabilities estimated by counting, with Laplace smoothing, and is a linear classifier in the word counts.
See [Chapter 12](12-Probabilistic-Models.md#122-naive-bayes-for-text-spam-laplace-smoothing).

**Negative sampling**
A fast training trick for word2vec: replace the softmax over the whole vocabulary by a few yes-or-no logistic questions, one for the true context word and a few for randomly drawn words.
See [Chapter 18](18-Sequence-Models.md#182-word-embeddings-word2vec).

**Nested cross-validation**
Two loops of cross-validation: the inner loop chooses hyperparameters using only the outer training data, and the outer loop evaluates the whole procedure, so the reported score is not biased by the tuning.
See [Chapter 7](07-Evaluating-Models.md#75-cross-validation).

**Neural tangent kernel**
The kernel $\nabla_\theta f(x)\cdot\nabla_\theta f(x')$ that governs gradient descent on a network in function space. For very wide networks it hardly changes during training, so they behave like kernel regression.
See [Chapter 21](21-Learning-Theory.md#216-what-theory-does-not-explain).

**Newton's method**
Optimisation by stepping to the minimum of the local quadratic model, $w\leftarrow w-H^{-1}\nabla f$. It converges quadratically near the minimum and is unaffected by conditioning, but forming the Hessian is too costly for large networks.
See [Chapter 5](05-Optimization.md#56-newtons-method-and-second-order-ideas).

**No-free-lunch theorem**
The result that, averaged over all possible target functions, every learner has the same accuracy, exactly $1/2$ for two classes, on inputs outside the training set. A learner beats chance only through an inductive bias that fits the problems it meets.
See [Chapter 1](01-What-Is-Machine-Learning.md#16-what-machine-learning-cannot-do).

**Noise floor**
The error no model can beat because of noise in the labels, $\sigma^2$ for squared error. For SGD with a constant step it also names the level at which the loss keeps bouncing.
See [Chapter 5](05-Optimization.md#53-stochastic-and-mini-batch-gradient-descent) and [Chapter 8](08-Overfitting-and-Regularization.md#81-underfitting-and-overfitting).

**Normal equations**
The linear system $X^\top Xw=X^\top y$ whose solution is the least-squares fit. They say that the residual is orthogonal to every column of $X$.
See [Chapter 4](04-Linear-Regression.md#42-solving-exactly-the-normal-equations).

**Normalizing flow**
A generative model that maps data to simple noise through a chain of invertible layers, so exact likelihoods follow from the change-of-variables formula with log-determinants of the Jacobians.
See [Chapter 20](20-Generative-Models.md#204-normalizing-flows-change-of-variables).

**Nucleus sampling (top-$p$)**
Sampling the next token from the smallest set of tokens whose probabilities add up to $p$, which adapts the number of candidates to how confident the model is.
See [Chapter 20](20-Generative-Models.md#206-autoregressive-models).

## O

**One-hot encoding**
Encoding a categorical feature with one 0/1 column per category, 1 for the example's category and 0 elsewhere. The list of categories comes from the training set.
See [Chapter 2](02-Data-and-Features.md#23-encoding-one-hot-ordinal-hashing).

**Out-of-bag estimate**
In bagging, the error of each training point predicted only by the models whose bootstrap samples left it out. It behaves much like cross-validation and comes free with training.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#113-bagging-and-random-forests-out-of-bag-error).

**Outlier**
A value far from the others. Some are errors to fix, others real and important; find them automatically with rules such as Tukey's fences, but decide about them with knowledge.
See [Chapter 2](02-Data-and-Features.md#22-cleaning-missing-values-outliers-duplicates).

**Overfitting**
Learning details of the training set that do not carry over to new data, shown by low training error with much higher test error. Regularisation, more data and simpler models reduce it.
See [Chapter 1](01-What-Is-Machine-Learning.md#14-training-validation-and-test-data) and [Chapter 8](08-Overfitting-and-Regularization.md#81-underfitting-and-overfitting).

## P

**p-value**
The probability, if there were no real difference, of seeing a difference at least as large as the one observed. Small values are evidence against "no difference".
See [Chapter 7](07-Evaluating-Models.md#77-comparing-models-intervals-the-bootstrap-and-tests).

**PAC learning**
Probably approximately correct learning: a class is learnable if some algorithm, given enough examples $m_{\mathcal H}(\varepsilon,\delta)$, returns with probability at least $1-\delta$ a hypothesis with error at most $\varepsilon$. A finite class needs about $(\ln|\mathcal H|+\ln(1/\delta))/\varepsilon$ examples.
See [Chapter 21](21-Learning-Theory.md#212-pac-learning-and-the-finite-class-bound).

**Perceptron**
Rosenblatt's linear classifier that learns from mistakes: whenever an example is misclassified, add $y_ix_i$ to the weights. On data separable with margin $\gamma$ and radius $R$ it makes at most $(R/\gamma)^2$ updates (Novikoff).
See [Chapter 1](01-What-Is-Machine-Learning.md#17-a-short-honest-history) and [Chapter 6](06-Classification-and-Logistic-Regression.md#62-the-perceptron).

**Permutation importance**
The drop in a model's held-out score when one feature's values are shuffled, breaking its link to the target. It is more honest than impurity importance, but correlated features share or hide credit.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#117-feature-importance-and-its-pitfalls).

**Perplexity**
$2$ to the power of the entropy (or of the bits per token): the effective number of equally likely choices. In t-SNE it sets each point's neighbourhood size; for language models lower is better.
See [Chapter 14](14-Dimensionality-Reduction.md#145-non-linear-methods-mds-isomap-t-sne-umap) and [Chapter 20](20-Generative-Models.md#206-autoregressive-models).

**Pooling**
Shrinking a feature map by summarising small blocks, with their maximum (max pooling) or mean (average pooling). Global pooling summarises the whole map, one number per channel.
See [Chapter 17](17-Convolutional-Networks.md#173-pooling-receptive-fields-translation-equivariance).

**Positional encoding**
Information about each token's position added to its embedding, such as sinusoids of different frequencies, since self-attention by itself ignores order.
See [Chapter 19](19-Transformers.md#193-multi-head-attention-positional-encodings).

**Positive definite kernel**
A symmetric function whose Gram matrix is positive semidefinite for every finite set of points. Exactly these functions are dot products in some feature space (a reproducing kernel Hilbert space).
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#95-the-kernel-trick-positive-definite-kernels-mercer-stated).

**Posterior**
The distribution of unknowns after seeing data, proportional to the prior times the likelihood by Bayes' rule.
See [Chapter 8](08-Overfitting-and-Regularization.md#83-ridge-regression), [Chapter 12](12-Probabilistic-Models.md#121-generative-vs-discriminative) and [Chapter 12](12-Probabilistic-Models.md#123-mle-vs-map-vs-full-bayes-conjugate-priors-beta-binomial-worked).

**Precision (classification)**
Of the examples predicted positive, the fraction that really are positive, $TP/(TP+FP)$. It falls when there are many false alarms.
See [Chapter 7](07-Evaluating-Models.md#72-the-confusion-matrix-precision-recall-and-f1).

**Precision-recall curve**
Precision plotted against recall as the threshold sweeps. It is much more sensitive to false alarms than the ROC curve when positives are rare.
See [Chapter 7](07-Evaluating-Models.md#73-roc-curves-auc-and-precision-recall-curves).

**Pretraining**
Training a model on a large general task, such as predicting the next or a hidden token, before adapting it to specific tasks by fine-tuning or prompting.
See [Chapter 19](19-Transformers.md#197-pretraining-gpt-bert-vision-transformers) and [Chapter 23](23-Where-Machine-Learning-Goes.md#232-self-supervised-and-contrastive-learning-foundation-models).

**Principal component analysis (PCA)**
Finding the orthogonal directions of greatest variance in centred data, the top eigenvectors of the covariance matrix (or right singular vectors of the data). Projecting onto the top $k$ also minimises the squared reconstruction error.
See [Chapter 14](14-Dimensionality-Reduction.md#142-principal-component-analysis-maximum-variance-and-the-svd).

**Prior**
The distribution over unknowns before seeing data: a class prior $P(y)$ in a generative classifier, or a distribution over parameters in Bayesian inference.
See [Chapter 8](08-Overfitting-and-Regularization.md#83-ridge-regression), [Chapter 12](12-Probabilistic-Models.md#121-generative-vs-discriminative) and [Chapter 12](12-Probabilistic-Models.md#123-mle-vs-map-vs-full-bayes-conjugate-priors-beta-binomial-worked).

**Pruning**
Cutting back a fully grown decision tree to reduce overfitting, usually by cost-complexity pruning with the penalty chosen by validation.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#112-growing-a-tree-from-scratch-cart-pruning).

**Pseudo-residual**
The negative gradient of the loss with respect to the current prediction at each training point. Gradient boosting fits each new tree to them; for squared error they are the ordinary residuals.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#115-gradient-boosting-friedman-2001-from-scratch-for-regression).

## Q

**QR decomposition**
Writing $X=QR$ with $Q$ having orthonormal columns and $R$ upper triangular. Least squares then reduces to $Rw=Q^\top y$, solved by back substitution without forming $X^\top X$.
See [Chapter 4](04-Linear-Regression.md#47-qr-and-svd-solutions-conditioning-and-why-not-invert-xt-x).

**Quadratic discriminant analysis (QDA)**
Gaussian discriminant analysis with a separate covariance for each class, which gives quadratic decision boundaries at the cost of many more parameters.
See [Chapter 12](12-Probabilistic-Models.md#125-gaussian-discriminant-analysis-ldaqda).

**Quasi-Newton method**
An optimiser that builds an approximation of the inverse Hessian from the gradients it computes anyway, satisfying the secant condition. BFGS and L-BFGS are the standard examples.
See [Chapter 5](05-Optimization.md#56-newtons-method-and-second-order-ideas).

**Query, key and value**
The three roles in attention: a query is compared with keys to give weights, and the weights average the values. In self-attention each position computes all three by its own linear maps.
See [Chapter 18](18-Sequence-Models.md#186-attention-from-scratch) and [Chapter 19](19-Transformers.md#192-scaled-dot-product-attention-derived).

## R

**Rademacher complexity**
How well a class of functions can correlate with random $\pm1$ signs on a sample: a measure of richness that gives generalisation bounds for real-valued classes and margins.
See [Chapter 21](21-Learning-Theory.md#214-rademacher-complexity-and-margins).

**Random forest**
Bagged decision trees that also consider only a random subset of features at each split, which decorrelates the trees so averaging removes more variance. It is a strong default with little tuning.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#113-bagging-and-random-forests-out-of-bag-error).

**RBF kernel (Gaussian kernel)**
The kernel $\exp(-\gamma\lVert x-z\rVert^2)$, whose similarity falls with distance. It is a valid kernel with an infinite-dimensional feature space, and $\gamma$ sets its width.
See [Chapter 9](09-Nearest-Neighbours-and-Kernels.md#95-the-kernel-trick-positive-definite-kernels-mercer-stated) and [Chapter 10](10-Support-Vector-Machines.md#105-kernel-svms-rbf-kernel).

**Recall (sensitivity, true positive rate)**
Of the examples that really are positive, the fraction the classifier finds, $TP/(TP+FN)$.
See [Chapter 7](07-Evaluating-Models.md#72-the-confusion-matrix-precision-recall-and-f1).

**Receptive field**
The set of input pixels that can affect a unit. It grows with each convolution or pooling layer, so deep units see large regions.
See [Chapter 17](17-Convolutional-Networks.md#173-pooling-receptive-fields-translation-equivariance).

**Rectified linear unit (ReLU)**
The activation $\max(0,a)$, with derivative 1 for positive inputs and 0 for negative ones. It does not saturate for positive inputs, which made deep networks easier to train, but units can die.
See [Chapter 15](15-Neural-Networks-and-Backpropagation.md#152-activation-functions-and-why-non-linearity-matters).

**Recurrent neural network (RNN)**
A network that reads a sequence one step at a time, updating a hidden state with the same weights at every step. It is trained by backpropagation through time and suffers from vanishing gradients over long spans.
See [Chapter 18](18-Sequence-Models.md#183-recurrent-networks-backprop-through-time).

**Regression**
Supervised learning in which the label is a number, such as a price or a temperature. Compare classification.
See [Chapter 1](01-What-Is-Machine-Learning.md#12-kinds-of-learning) and [Chapter 4](04-Linear-Regression.md#41-fitting-a-line).

**Regularisation**
Anything that reduces overfitting by limiting a model's effective flexibility, most directly a penalty on the weights added to the training loss, but also early stopping, dropout and data augmentation.
See [Chapter 8](08-Overfitting-and-Regularization.md#83-ridge-regression) and [Chapter 16](16-Training-Deep-Networks.md#164-regularization-weight-decay-dropout-augmentation).

**Reinforcement learning**
Learning in which an agent takes actions in an environment, sees the new state and receives a reward, and learns a policy that maximises total reward, with no examples of right answers.
See [Chapter 1](01-What-Is-Machine-Learning.md#12-kinds-of-learning).

**Reliability diagram**
A plot of observed frequency of positives against mean predicted probability in bins. A calibrated model lies on the diagonal.
See [Chapter 7](07-Evaluating-Models.md#76-calibration-reliability-diagrams-and-the-brier-score).

**Reparameterisation trick**
Writing a random sample as a deterministic function of the parameters and outside noise, $z=\mu+\sigma\epsilon$, so gradients can flow through sampling. It is how variational autoencoders are trained.
See [Chapter 20](20-Generative-Models.md#202-autoencoders-and-variational-autoencoders).

**Residual**
The error of a fit on one example, $r_i=y_i-\hat y_i$. Residual plots against fitted values reveal curvature, funnels of growing noise and outliers.
See [Chapter 4](04-Linear-Regression.md#41-fitting-a-line) and [Chapter 7](07-Evaluating-Models.md#74-regression-metrics).

**Residual connection (skip connection)**
Adding a block's input to its output, $x+F(x)$, so the block only has to learn a change and doing nothing is easy. It lets gradients flow through very deep networks and made ResNets and transformers trainable.
See [Chapter 16](16-Training-Deep-Networks.md#166-residual-connections-and-why-depth-became-possible) and [Chapter 17](17-Convolutional-Networks.md#175-architectures-lenet-alexnet-vgg-resnet).

**ResNet**
The residual network of He and others (2015), built from residual blocks, which trained networks of over a hundred layers after plain deep networks had shown higher training error than shallow ones.
See [Chapter 16](16-Training-Deep-Networks.md#166-residual-connections-and-why-depth-became-possible) and [Chapter 17](17-Convolutional-Networks.md#175-architectures-lenet-alexnet-vgg-resnet).

**Ridge regression**
Least squares plus $\lambda$ times the squared length of the weights, solved by $(X^\top X+\lambda I)^{-1}X^\top y$, which always exists for $\lambda>0$. It shrinks weights, tames collinearity, and is the MAP estimate under a Gaussian prior.
See [Chapter 8](08-Overfitting-and-Regularization.md#83-ridge-regression).

**RMSProp**
An adaptive optimiser that divides each parameter's step by the square root of an exponential moving average of its squared gradients, so steps no longer shrink forever as in AdaGrad.
See [Chapter 5](05-Optimization.md#55-adaptive-methods-adagrad-rmsprop-adam).

**ROC curve**
The true positive rate plotted against the false positive rate as the decision threshold sweeps. The area under it is the AUC.
See [Chapter 7](07-Evaluating-Models.md#73-roc-curves-auc-and-precision-recall-curves).

## S

**Saddle point**
A stationary point that is a minimum in some directions and a maximum in others, like a mountain pass. A strict saddle has a direction of negative curvature that gradient methods can escape along; in high dimensions saddles are thought to be far more common than poor local minima.
See [Chapter 5](05-Optimization.md#51-loss-landscapes-and-convexity) and [Chapter 5](05-Optimization.md#57-learning-rate-schedules-warmup-and-non-convex-landscapes).

**Saliency map**
A picture of $|\partial(\text{class score})/\partial x|$ for each pixel of one input: which pixels would change the score most. It is a local explanation, and can mislead when the output is saturated.
See [Chapter 17](17-Convolutional-Networks.md#176-transfer-learning-what-filters-learn) and [Chapter 22](22-Machine-Learning-in-Practice.md#224-interpretability).

**Scaled dot-product attention**
Attention computed as $\operatorname{softmax}(QK^\top/\sqrt{d_k})V$. Dividing by $\sqrt{d_k}$ keeps the scores' variance near 1 so the softmax does not saturate as the dimension grows.
See [Chapter 19](19-Transformers.md#192-scaled-dot-product-attention-derived).

**Scaling laws**
Empirical power laws that predict a network's test loss from its number of parameters $N$, data $D$ and compute, such as $L=E+A/N^a+B/D^b$. They tell how to split a compute budget; the Chinchilla fit says parameters and data should grow at nearly the same rate, about 20 tokens per parameter.
See [Chapter 23](23-Where-Machine-Learning-Goes.md#231-scaling-laws).

**Score (of a density)**
The gradient of the log density with respect to the input, $\nabla_x\log p(x)$, which points towards more probable regions and does not need the normalising constant. Score-based generative models learn it and sample with Langevin dynamics.
See [Chapter 20](20-Generative-Models.md#207-score-matching-and-the-link-between-diffusion-and-score-based-models).

**Score matching**
Fitting a model to the score of the data distribution without knowing the density, by a loss that integration by parts makes computable. Denoising score matching learns the score of noise-blurred data by predicting the noise.
See [Chapter 20](20-Generative-Models.md#207-score-matching-and-the-link-between-diffusion-and-score-based-models).

**Self-attention**
Attention in which the positions of one sequence attend to each other, so each position's new representation is a weighted mixture of all positions, computed for all positions at once. It replaced recurrence in transformers.
See [Chapter 19](19-Transformers.md#191-attention-is-all-you-need-the-problem-it-solved) and [Chapter 19](19-Transformers.md#192-scaled-dot-product-attention-derived).

**Self-supervised learning**
Learning from unlabelled data by making labels from the data itself: hide part of each input and predict it, or recognise which views come from the same example. It is how language models and foundation models are pretrained.
See [Chapter 1](01-What-Is-Machine-Learning.md#12-kinds-of-learning) and [Chapter 23](23-Where-Machine-Learning-Goes.md#232-self-supervised-and-contrastive-learning-foundation-models).

**Sequence-to-sequence model**
An encoder that reads a source sequence and a decoder that generates a target sequence from it, as in translation. Without attention, the whole source must pass through one fixed vector.
See [Chapter 18](18-Sequence-Models.md#185-sequence-to-sequence).

**Shapley values (SHAP)**
Attributions of one prediction to the features, defined as each feature's average contribution over all orders of adding features, from cooperative game theory. They add up to the prediction minus the average prediction; Kernel SHAP estimates them and TreeSHAP computes them exactly for trees.
See [Chapter 22](22-Machine-Learning-in-Practice.md#224-interpretability).

**Shattering**
A class shatters a set of points if it can produce every one of the $2^n$ labellings of them. The VC dimension is the size of the largest set it can shatter.
See [Chapter 21](21-Learning-Theory.md#213-the-vc-dimension).

**Sigmoid**
The function $\sigma(z)=1/(1+e^{-z})$, which squashes any number into $(0,1)$ and is read as a probability. Its derivative is $\sigma(1-\sigma)$, at most $1/4$, and it saturates for large $|z|$.
See [Chapter 6](06-Classification-and-Logistic-Regression.md#63-logistic-regression) and [Chapter 15](15-Neural-Networks-and-Backpropagation.md#152-activation-functions-and-why-non-linearity-matters).

**Silhouette**
A per-point clustering score $s=(b-a)/\max(a,b)$, where $a$ is the mean distance to the point's own cluster and $b$ to the nearest other cluster. Near 1 is well placed, near 0 on a border, negative probably misassigned; its mean helps choose $k$.
See [Chapter 13](13-Clustering.md#133-choosing-k-the-elbow-and-the-silhouette).

**Singular value decomposition (SVD)**
Writing any matrix as $M=U\Sigma V^\top$ with orthonormal $U$ and $V$ and nonnegative singular values on the diagonal of $\Sigma$: a rotation, a stretch along the axes and another rotation. It gives PCA, least squares, the pseudo-inverse and best low-rank approximations.
See [Chapter 3](03-The-Math-Toolkit.md#36-eigenvectors-and-the-svd-in-one-picture), [Chapter 4](04-Linear-Regression.md#47-qr-and-svd-solutions-conditioning-and-why-not-invert-xt-x) and [Chapter 14](14-Dimensionality-Reduction.md#142-principal-component-analysis-maximum-variance-and-the-svd).

**Softmax**
The function $e^{z_k}/\sum_je^{z_j}$ that turns $K$ scores into positive probabilities summing to 1. Softmax regression is logistic regression for many classes.
See [Chapter 6](06-Classification-and-Logistic-Regression.md#65-many-classes-softmax-regression-and-one-vs-rest) and [Chapter 15](15-Neural-Networks-and-Backpropagation.md#153-forward-pass-in-matrices).

**Spectral clustering**
Clustering by building a similarity graph of the points, taking the eigenvectors of the smallest eigenvalues of its graph Laplacian as new coordinates, and running k-means on them. It finds clusters defined by connectedness, such as rings.
See [Chapter 13](13-Clustering.md#137-spectral-clustering).

**Spectral theorem**
A real symmetric matrix has real eigenvalues and an orthonormal set of eigenvectors, so it stretches space along perpendicular axes. Its largest eigenvalue is the largest value of $u^\top Au$ over unit vectors.
See [Chapter 3](03-The-Math-Toolkit.md#36-eigenvectors-and-the-svd-in-one-picture) and [Chapter 14](14-Dimensionality-Reduction.md#142-principal-component-analysis-maximum-variance-and-the-svd).

**Standardisation**
Rescaling a feature by subtracting its mean and dividing by its standard deviation, $z=(x-\mu)/\sigma$, using training-set statistics. Distance-based and gradient-trained learners need it; trees do not.
See [Chapter 2](02-Data-and-Features.md#24-scaling-standardisation-and-min-max).

**Stochastic gradient descent (SGD)**
Gradient descent that steps along the gradient of one random example (or a mini-batch) instead of the whole training set. The step is right on average but noisy, so a constant learning rate leaves it bouncing at a noise floor unless the rate decays.
See [Chapter 5](05-Optimization.md#53-stochastic-and-mini-batch-gradient-descent).

**Stratified split**
A split or cross-validation that samples each class separately so every part keeps the class proportions of the whole, which matters most with rare classes.
See [Chapter 2](02-Data-and-Features.md#26-splitting-well) and [Chapter 7](07-Evaluating-Models.md#75-cross-validation).

**Subword tokenization**
Splitting text into tokens between words and characters: frequent words are single tokens, rare words are split into pieces, and any string can still be written. Byte-pair encoding, WordPiece and unigram tokenizers do it.
See [Chapter 19](19-Transformers.md#196-tokenization-byte-pair-encoding-from-scratch).

**Superposition**
A layer with $m$ neurons representing more than $m$ features by giving them nearly orthogonal directions, which works when features are sparse. It explains polysemantic neurons.
See [Chapter 23](23-Where-Machine-Learning-Goes.md#234-mechanistic-interpretability).

**Supervised learning**
Learning from examples that come with their right answers (labels), with the goal of predicting the label of new inputs. Regression and classification are its two main kinds.
See [Chapter 1](01-What-Is-Machine-Learning.md#12-kinds-of-learning).

**Support vector machine (SVM)**
A classifier that chooses the separating hyperplane with the widest margin, softened by slack variables for overlapping classes and made non-linear with kernels. Its solution depends only on the support vectors.
See [Chapter 10](10-Support-Vector-Machines.md#101-the-widest-margin-geometry-of-the-margin-derived) and [Chapter 10](10-Support-Vector-Machines.md#103-soft-margin-and-hinge-loss).

**Support vectors**
The training points with nonzero dual multipliers, those on or inside the margin. The SVM's weight vector is a combination of them alone, and the others could be moved without changing the solution.
See [Chapter 10](10-Support-Vector-Machines.md#104-lagrange-duality-kkt-conditions-support-vectors).

**Surrogate loss**
A convex loss lying above the 0-1 loss, minimised instead because the 0-1 loss is not convex and has zero gradient almost everywhere. The hinge, logistic and exponential losses are surrogates.
See [Chapter 10](10-Support-Vector-Machines.md#103-soft-margin-and-hinge-loss).

## T

**t-SNE**
A visualisation method that turns distances into neighbour probabilities in the data and in a 2-D map, using a heavy-tailed Student t kernel in the map, and moves the map points to make the two match. It keeps neighbours together; cluster sizes and distances between clusters in its pictures mean little.
See [Chapter 14](14-Dimensionality-Reduction.md#145-non-linear-methods-mds-isomap-t-sne-umap).

**Teacher forcing**
Training a decoder by feeding it the true previous token at each step rather than its own prediction. It makes training stable and parallel but causes exposure bias.
See [Chapter 18](18-Sequence-Models.md#185-sequence-to-sequence).

**Temperature**
A number $\tau$ that divides the logits before a softmax: below 1 sharpens the distribution, above 1 flattens it. It controls the randomness of sampling and the sharpness of contrastive losses.
See [Chapter 19](19-Transformers.md#195-a-tiny-transformer-from-scratch), [Chapter 20](20-Generative-Models.md#206-autoregressive-models) and [Chapter 23](23-Where-Machine-Learning-Goes.md#232-self-supervised-and-contrastive-learning-foundation-models).

**Test set**
Data held back from all training and choices and used once at the end to estimate how the final model will do on new data.
See [Chapter 1](01-What-Is-Machine-Learning.md#14-training-validation-and-test-data) and [Chapter 7](07-Evaluating-Models.md#75-cross-validation).

**Token**
One unit of a text sequence, such as a word, a piece of a word or a character, represented as an index into a vocabulary.
See [Chapter 18](18-Sequence-Models.md#181-text-time-series-and-audio-as-sequences) and [Chapter 19](19-Transformers.md#196-tokenization-byte-pair-encoding-from-scratch).

**Training set**
The examples a model is fitted on.
See [Chapter 1](01-What-Is-Machine-Learning.md#14-training-validation-and-test-data) and [Chapter 7](07-Evaluating-Models.md#75-cross-validation).

**Transfer learning**
Reusing a network trained on one task, such as ImageNet classification, for another, either by feature extraction with frozen layers or by fine-tuning all of them.
See [Chapter 17](17-Convolutional-Networks.md#176-transfer-learning-what-filters-learn).

**Transformer**
A network built from blocks of multi-head self-attention and position-wise MLPs, each wrapped in a residual connection with layer normalisation. It processes all positions in parallel and is the architecture of modern language models.
See [Chapter 19](19-Transformers.md#191-attention-is-all-you-need-the-problem-it-solved) and [Chapter 19](19-Transformers.md#194-the-transformer-block).

**True risk**
A hypothesis's expected loss on a fresh example from the data distribution, also called its generalisation error. The learner cannot compute it, only estimate it.
See [Chapter 21](21-Learning-Theory.md#211-the-question-why-does-a-model-that-fits-training-data-work-on-new-data).

**Tukey's fences**
An outlier rule that flags values below $Q_1-1.5\,\mathrm{IQR}$ or above $Q_3+1.5\,\mathrm{IQR}$. Being based on quartiles, it is not fooled by the outliers it looks for.
See [Chapter 2](02-Data-and-Features.md#22-cleaning-missing-values-outliers-duplicates).

## U

**U-Net**
A segmentation network with an encoder that halves the size and doubles the channels, a decoder that does the reverse, and skip connections between matching levels that carry fine detail across.
See [Chapter 17](17-Convolutional-Networks.md#177-beyond-classification-detection-segmentation-u-net-2015).

**UMAP**
A non-linear embedding method, justified by topology, that in practice builds a weighted nearest-neighbour graph and lays it out in low dimension. It is much faster than exact t-SNE and scales to millions of points, with similar cautions about reading its pictures.
See [Chapter 14](14-Dimensionality-Reduction.md#145-non-linear-methods-mds-isomap-t-sne-umap).

**Underfitting**
A model too simple to capture the pattern, doing badly even on the training data: high bias.
See [Chapter 1](01-What-Is-Machine-Learning.md#14-training-validation-and-test-data) and [Chapter 8](08-Overfitting-and-Regularization.md#81-underfitting-and-overfitting).

**Uniform convergence**
The property that, with high probability, training error is close to true error for every hypothesis in the class at once, so whichever hypothesis the learner picks, its training error tells the truth.
See [Chapter 21](21-Learning-Theory.md#211-the-question-why-does-a-model-that-fits-training-data-work-on-new-data).

**Universal approximation theorem**
The result (Cybenko, 1989, for sigmoids) that a network with one hidden layer can approximate any continuous function on a cube as closely as desired, given enough units. It says such weights exist, not that training finds them or how many are needed.
See [Chapter 15](15-Neural-Networks-and-Backpropagation.md#156-universal-approximation).

**Unsupervised learning**
Learning from inputs without labels, to find structure such as clusters, low-dimensional descriptions or a density.
See [Chapter 1](01-What-Is-Machine-Learning.md#12-kinds-of-learning) and [Chapter 13](13-Clustering.md#131-what-a-cluster-is-distances).

## V

**Validation set**
Data held back from training and used to make choices, such as the learner, its hyperparameters or when to stop. Each choice uses up some of its honesty, which is why a separate test set is kept.
See [Chapter 1](01-What-Is-Machine-Learning.md#14-training-validation-and-test-data) and [Chapter 7](07-Evaluating-Models.md#75-cross-validation).

**Vanishing gradient**
Gradients that shrink exponentially as they are passed back through many layers or time steps, so early layers barely learn. Saturating activations, poor initialisation and plain recurrence cause it; ReLUs, careful initialisation, gating and residual connections relieve it.
See [Chapter 16](16-Training-Deep-Networks.md#161-vanishing-and-exploding-gradients-shown) and [Chapter 18](18-Sequence-Models.md#183-recurrent-networks-backprop-through-time).

**Variance**
For a random variable, the expected squared distance from its mean. For a learner, how much the fitted model changes from one training set to another; flexible models have high variance.
See [Chapter 3](03-The-Math-Toolkit.md#34-probability) and [Chapter 8](08-Overfitting-and-Regularization.md#82-the-bias-variance-decomposition).

**Variational autoencoder (VAE)**
A generative model with a latent Gaussian code and a decoder, trained with an encoder that approximates the posterior by maximising the ELBO: a reconstruction term minus the KL divergence of the code from the prior. The reparameterisation trick makes it trainable by gradient descent.
See [Chapter 14](14-Dimensionality-Reduction.md#146-autoencoders-preview) and [Chapter 20](20-Generative-Models.md#202-autoencoders-and-variational-autoencoders).

**Variational inference**
Approximating an intractable posterior by the closest member of a simple family, turning integration into optimisation of the ELBO.
See [Chapter 12](12-Probabilistic-Models.md#127-sampling-monte-carlo-mcmc-metropolis-hastings-from-scratch) and [Chapter 20](20-Generative-Models.md#202-autoencoders-and-variational-autoencoders).

**VC dimension**
The size of the largest set of points a hypothesis class can shatter. Half-spaces in $\mathbb R^d$ have VC dimension $d+1$; a class is PAC learnable exactly when its VC dimension is finite.
See [Chapter 21](21-Learning-Theory.md#213-the-vc-dimension).

**Vision transformer (ViT)**
A transformer applied to images by cutting them into patches and treating each patch as a token. It has none of a CNN's built-in locality and needs much data, but then matches or beats CNNs.
See [Chapter 19](19-Transformers.md#197-pretraining-gpt-bert-vision-transformers).

## W

**Warmup**
Starting training with a very small learning rate and raising it linearly over the first few hundred or thousand steps, before the main schedule. It stabilises early training, especially of transformers with Adam.
See [Chapter 5](05-Optimization.md#57-learning-rate-schedules-warmup-and-non-convex-landscapes) and [Chapter 16](16-Training-Deep-Networks.md#165-optimizers-in-practice-learning-rates-schedules-clipping).

**Weight decay**
The L2 penalty on weights as used in deep learning, which shrinks every weight a little at each step. With Adam it should be decoupled from the adaptive step (AdamW).
See [Chapter 8](08-Overfitting-and-Regularization.md#86-effective-degrees-of-freedom-and-the-elastic-net) and [Chapter 16](16-Training-Deep-Networks.md#164-regularization-weight-decay-dropout-augmentation).

**Weisfeiler-Lehman test**
A classical colour-refinement test for graph isomorphism that repeatedly relabels each node by its own label and the multiset of its neighbours' labels. Message-passing graph networks can tell apart at most the graphs that the 1-dimensional version can.
See [Chapter 23](23-Where-Machine-Learning-Goes.md#235-graph-neural-networks-geometric-deep-learning-and-ml-for-science).

**Within-cluster sum of squares (inertia)**
The total squared distance from each point to the centre of its cluster, the quantity k-means minimises. It always falls as $k$ grows, so it cannot choose $k$ alone.
See [Chapter 13](13-Clustering.md#132-k-means-lloyds-algorithm-and-k-means).

**Word embedding**
A learned vector for each word in which similar words are close and some relations are directions, as in "king minus man plus woman is near queen". word2vec, GloVe and the SVD of a PMI matrix give them.
See [Chapter 18](18-Sequence-Models.md#182-word-embeddings-word2vec).

**word2vec**
The 2013 method of Mikolov and colleagues that learns word vectors fast from billions of words, by training each word's vector to predict nearby words with negative sampling.
See [Chapter 18](18-Sequence-Models.md#182-word-embeddings-word2vec).

## X

**Xavier (Glorot) initialisation**
Initialising weights with variance $2/(n_{\text{in}}+n_{\text{out}})$, a compromise that keeps signal variance roughly constant both forwards and backwards through tanh layers.
See [Chapter 16](16-Training-Deep-Networks.md#162-initialization-xavier-and-he-derived-from-variance).

**XGBoost**
A gradient-boosting library that adds each tree by minimising a second-order Taylor approximation of the loss plus a penalty on the tree, so leaf values are Newton steps; it adds missing-value handling, approximate split finding and fast engineering.
See [Chapter 11](11-Decision-Trees-and-Ensembles.md#116-modern-boosted-trees-xgboost-lightgbm-and-why-they-win-on-tables).

**XOR (exclusive or)**
The labelling of $(0,0),(1,1)$ as 0 and $(0,1),(1,0)$ as 1, which no line separates. It stalled the perceptron in 1969 and is solved by an interaction feature or one hidden layer.
See [Chapter 6](06-Classification-and-Logistic-Regression.md#66-decision-boundaries) and [Chapter 15](15-Neural-Networks-and-Backpropagation.md#151-from-the-perceptron-to-layers-why-xor-needs-a-hidden-layer).

## Y

**YOLO and SSD**
One-stage object detectors that skip region proposals and predict boxes and classes for every cell of a coarse grid in one pass, trading some accuracy for speed.
See [Chapter 17](17-Convolutional-Networks.md#177-beyond-classification-detection-segmentation-u-net-2015).

## Z

**z-score**
The number of standard deviations a value lies from the mean, $z=(x-\bar x)/\sigma$. A rule flagging $|z|>3$ as outliers can be fooled by masking, since extreme values inflate $\sigma$.
See [Chapter 2](02-Data-and-Features.md#22-cleaning-missing-values-outliers-duplicates) and [Chapter 2](02-Data-and-Features.md#24-scaling-standardisation-and-min-max).

**Zero-one loss**
The loss that is 1 for a mistake and 0 otherwise, the error rate. It is not convex or continuous, so learners minimise a convex surrogate such as the hinge or logistic loss.
See [Chapter 10](10-Support-Vector-Machines.md#103-soft-margin-and-hinge-loss) and [Chapter 21](21-Learning-Theory.md#211-the-question-why-does-a-model-that-fits-training-data-work-on-new-data).
