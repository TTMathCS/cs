"""Chapter 17: pieces of detection and segmentation from scratch: intersection
over union, non-maximum suppression, and the transposed convolution that
U-Net-style decoders use to upsample (checked to be the adjoint of a strided conv)."""
import numpy as np


def iou(a, b):
    """Boxes as (x1, y1, x2, y2). Area of overlap / area of union."""
    w = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    h = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = w * h
    area = lambda r: (r[2] - r[0]) * (r[3] - r[1])
    return inter / (area(a) + area(b) - inter)


def nms(boxes, scores, threshold=0.5):
    """Greedy non-maximum suppression: keep the best box, drop boxes that overlap
    it by more than the threshold, repeat."""
    order = [int(i) for i in np.argsort(scores)[::-1]]
    keep = []
    while order:
        best = order.pop(0)
        keep.append(best)
        order = [i for i in order if iou(boxes[best], boxes[i]) <= threshold]
    return keep


print("1. intersection over union")
A, B = (0, 0, 4, 4), (2, 2, 6, 6)
print(f"   A={A} B={B}: overlap 4, union 28, IoU = {iou(A, B):.4f}")
print(f"   A with itself: {iou(A, A):.1f}; A with (5, 5, 7, 7): {iou(A, (5, 5, 7, 7)):.1f}")

print()
print("2. non-maximum suppression (threshold 0.5)")
boxes = [(10, 10, 50, 50), (12, 12, 52, 52), (8, 11, 48, 49), (60, 60, 90, 95), (62, 58, 92, 93)]
scores = [0.90, 0.75, 0.80, 0.70, 0.85]
for i, (bx, s) in enumerate(zip(boxes, scores)):
    print(f"   box {i}: {bx} score {s:.2f}")
print(f"   kept: {nms(boxes, scores)}   (one box per object)")

print()
print("3. a strided convolution shrinks; its transpose grows")
k = np.array([1.0, 2.0, 1.0])
n, s = 8, 2
m = (n - len(k)) // s + 1
C = np.zeros((m, n))                       # the strided conv as a matrix
for i in range(m):
    C[i, i * s:i * s + len(k)] = k
print(f"   1-D conv, kernel {k}, stride {s}: maps length {n} -> {m}; matrix C is {C.shape}")
print("   C =")
for row in C:
    print("      " + " ".join(f"{v:2.0f}" for v in row))


def conv_transpose_1d(y, k, s, n):
    """Each input value stamps a scaled copy of the kernel into the output."""
    out = np.zeros(n)
    for i, v in enumerate(y):
        out[i * s:i * s + len(k)] += v * k
    return out


rng = np.random.default_rng(0)
x, y = rng.normal(size=n), rng.normal(size=m)
print(f"   transposed conv of [1, 0, 0] = {conv_transpose_1d(np.array([1.0, 0, 0]), k, s, n)}")
print(f"   equals C^T y for random y? {np.allclose(conv_transpose_1d(y, k, s, n), C.T @ y)}")
print(f"   <Cx, y> = {np.dot(C @ x, y):.6f},  <x, C^T y> = {np.dot(x, C.T @ y):.6f}")

print()
print("4. segmentation scores on a 6 x 6 mask")
truth = np.zeros((6, 6), bool); truth[1:5, 1:4] = True       # 12 pixels
pred = np.zeros((6, 6), bool); pred[2:5, 1:5] = True         # 12 pixels
tp = np.sum(truth & pred)
print(f"   true pixels {truth.sum()}, predicted {pred.sum()}, both {tp}")
print(f"   pixel IoU = {tp / np.sum(truth | pred):.3f}, Dice = {2 * tp / (truth.sum() + pred.sum()):.3f}")
