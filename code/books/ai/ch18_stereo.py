# Chapter 18: depth from a rectified stereo pair, from scratch.
# A synthetic scene (textured far terrain and a near rock), block matching with the sum of absolute
# differences, depth Z = f B / d, and how the depth error grows with distance.
import numpy as np

f_px, B = 200.0, 0.20                            # focal length in pixels, baseline in metres (illustrative)
H, W = 60, 100
Z_far, Z_rock = 8.0, 2.0
d_far, d_rock = f_px * B / Z_far, f_px * B / Z_rock   # true disparities: 5 and 20 pixels
d_far, d_rock = int(round(d_far)), int(round(d_rock))

rng = np.random.default_rng(0)
tex_far = rng.random((H, W + 40))                # random-dot textures painted on each surface
tex_rock = rng.random((H, W + 40))
rows, cols = np.mgrid[0:H, 0:W]
rock_left = (rows >= 20) & (rows < 40) & (cols >= 50) & (cols < 70)      # the rock in the left image
left = np.where(rock_left, tex_rock[rows, cols], tex_far[rows, cols])
# A point at left column c appears at column c - d in the right image (rectified cameras: same row).
rock_right = (rows >= 20) & (rows < 40) & (cols >= 50 - d_rock) & (cols < 70 - d_rock)
right = np.where(rock_right, tex_rock[rows, np.clip(cols + d_rock, 0, W + 39)],
                 tex_far[rows, np.clip(cols + d_far, 0, W + 39)])
true_d = np.where(rock_left, d_rock, d_far)


def box_sum(a, r):
    """Sum of a over the (2r+1) x (2r+1) window around each pixel, via 2-D cumulative sums."""
    p = np.pad(a, ((r + 1, r), (r + 1, r)), mode="edge")
    c = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    return c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]


D_MAX, RAD = 30, 3                               # search disparities 0..30, 7 x 7 windows
cost = np.full((D_MAX + 1, H, W), np.inf)
for d in range(D_MAX + 1):
    diff = np.full((H, W), 1.0)                  # columns with no partner cost the maximum
    diff[:, d:] = np.abs(left[:, d:] - right[:, :W - d])
    cost[d] = box_sum(diff, RAD)
disp = cost.argmin(0)                            # winner takes all: the best disparity per pixel

valid = (cols >= D_MAX + RAD) & (cols < W - RAD) & (rows >= RAD) & (rows < H - RAD)
ok = np.abs(disp - true_d) <= 1
print(f"1. scene: far terrain at {Z_far} m (disparity {d_far} px), rock at {Z_rock} m (disparity {d_rock} px)")
print(f"   f = {f_px:.0f} px, baseline B = {B} m, images {H} x {W}, windows 7 x 7")
print(f"\n2. block matching on {valid.sum()} interior pixels")
print(f"   within 1 px of the true disparity: {ok[valid].mean():.3f}")
print(f"   median disparity on the rock {np.median(disp[valid & rock_left]):.0f}, "
      f"on the terrain {np.median(disp[valid & ~rock_left]):.0f}")
bad = valid & ~ok
near_edge = np.zeros_like(bad)
for dc in range(-RAD - d_rock, RAD + 1):          # within a window of the rock's left or right boundary
    for edge in (50, 70):
        near_edge |= (cols == edge + dc)
print(f"   wrong pixels: {bad.sum()}, of which {(bad & near_edge).sum()} lie near the rock's left or right side")

print("\n3. row 30 of the disparity map (the rock covers columns 50..69; terrain at 35..49 is hidden from the right camera)")
print("   column   " + " ".join(f"{c:3d}" for c in range(33, 76, 3)))
print("   found    " + " ".join(f"{disp[30, c]:3d}" for c in range(33, 76, 3)))
print("   true     " + " ".join(f"{true_d[30, c]:3d}" for c in range(33, 76, 3)))

Z = np.where(disp > 0, f_px * B / np.maximum(disp, 1), np.inf)
print(f"\n4. depth on the rock: median {np.median(Z[valid & rock_left & ok]):.2f} m; "
      f"on the terrain: median {np.median(Z[valid & ~rock_left & ok]):.2f} m")

print("\n5. depth error for a 1-pixel disparity error, dZ = Z^2 / (f B)")
print(f"   {'Z (m)':>6s}{'d (px)':>8s}{'dZ (m)':>8s}")
for z in (1, 2, 4, 8, 16):
    print(f"   {z:6d}{f_px * B / z:8.1f}{z * z / (f_px * B):8.3f}")
