"""Materials from formulas: hash, gradient noise, fBm, Voronoi cells and slab joints, then a basalt floor.
Only numpy is needed; the picture is written as a PNG by hand (zlib), so nothing else has to be installed.
Run:  python3 materials.py      -> basalt.png (a 1.8 m x 1.2 m piece of the floor) and the worked numbers."""
import struct
import zlib

import numpy as np


def fade(t):
    """Perlin's 2002 curve 6t^5 - 15t^4 + 10t^3: 0 at t = 0, 1 at t = 1, flat (slope and bend 0) at both ends."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def hash2(ix, iy, seed=0):
    """a whole-number hash of a lattice corner: the same corner always gives the same 32-bit number"""
    h = (ix.astype(np.uint32) * np.uint32(73856093)) ^ (iy.astype(np.uint32) * np.uint32(19349663)) ^ np.uint32(seed)
    h ^= h >> np.uint32(13)
    h *= np.uint32(0x5BD1E995)
    h ^= h >> np.uint32(15)
    return h


def gradient_noise(x, y, seed=0):
    """2D gradient (Perlin) noise, about -1..1: a random unit gradient at every lattice corner, blended with fade()"""
    ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    fx, fy = x - ix, y - iy

    def corner(dx, dy):
        a = hash2(ix + dx, iy + dy, seed).astype(np.float64) / 2**32 * 2 * np.pi    # a random direction
        return np.cos(a) * (fx - dx) + np.sin(a) * (fy - dy)                         # gradient . offset

    u, v = fade(fx), fade(fy)
    bottom = corner(0, 0) + u * (corner(1, 0) - corner(0, 0))
    top = corner(0, 1) + u * (corner(1, 1) - corner(0, 1))
    return (bottom + v * (top - bottom)) * np.sqrt(2)      # 2D gradient noise stays within about +-1/sqrt(2)


def fbm(x, y, detail=4, roughness=0.5, lacunarity=2.0, seed=0):
    """fractal Brownian motion as Blender's Noise Texture adds it up: octaves 0..detail, each one `lacunarity`
    times finer and `roughness` times weaker, then squeezed into 0..1 (here detail is a whole number)"""
    total, amp, maxamp, f = 0.0, 1.0, 0.0, 1.0
    for _ in range(int(detail) + 1):
        total = total + amp * gradient_noise(x * f, y * f, seed)
        maxamp += amp
        amp *= roughness
        f *= lacunarity
    return 0.5 * total / maxamp + 0.5


def voronoi_f1(x, y, seed=1):
    """Worley's cell noise: the distance to the nearest of one random point per unit square (looks at the 3 x 3
    squares around), as Blender's Voronoi Texture with Randomness 1 and the F1 feature"""
    ix, iy = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    best = np.full(np.shape(x), 9.0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            h = hash2(ix + dx, iy + dy, seed)
            px = ix + dx + (h & np.uint32(0xFFFF)).astype(np.float64) / 65536
            py = iy + dy + (h >> np.uint32(16)).astype(np.float64) / 65536
            best = np.minimum(best, np.hypot(x - px, y - py))
    return best


def slab_joint(x, y, width=1.2, row=0.6, joint=0.003, offset=0.5):
    """1 on a joint between slabs, else 0: Blender's Brick Texture (every other row shifted by offset * width)"""
    r = np.floor(y / row)
    shift = np.where(r % 2 == 0, offset * width, 0.0)
    b = np.floor((x + shift) / width)
    u, v = x + shift - b * width, y - r * row
    d = np.minimum(np.minimum(u, v), np.minimum(width - u, row - v))
    return (d < joint).astype(np.float64)


def basalt(x, y):
    """the Crown's polished basalt floor (Art repo crown_rooms.py basalt()), colour and roughness, x, y in metres"""
    t = 0.6 * voronoi_f1(x * 260, y * 260) + 0.5 * fbm(x * 0.7, y * 0.7, detail=6)    # fine grains, slow clouds
    t = np.clip(t, 0, 1)
    dark, light = np.array([0.018, 0.018, 0.019]), np.array([0.06, 0.058, 0.056])
    colour = dark + t[..., None] * (light - dark)                                      # the colour ramp
    colour *= np.where(slab_joint(x, y)[..., None] > 0, 0.4, 1.0)                     # darker joints
    rough = 0.13 + 0.14 * fbm(x * 3, y * 3, detail=8)                                  # 0.13 .. 0.27
    return colour, rough


def to_srgb(c):
    """linear light (what the formulas work in) to the sRGB numbers a screen expects"""
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)


def write_png(path, rgb):
    """rgb: an h x w x 3 array of 0..1"""
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + row.tobytes() for row in (rgb * 255 + 0.5).astype(np.uint8))
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


if __name__ == "__main__":
    print("fade(0.3) =", round(float(fade(0.3)), 5))
    print("value noise between 0.2 and 0.8 at t = 0.3:", round(0.2 + 0.6 * float(fade(0.3)), 5))
    print("fBm of octaves 0.4, -0.2, 0.6 (roughness 0.5):", round(0.5 * (0.4 - 0.1 + 0.15) / 1.75 + 0.5, 5))
    print("slab joint at (2.0, 0.9):", int(slab_joint(np.array(2.0), np.array(0.9))),
          " at (2.0, 1.199):", int(slab_joint(np.array(2.0), np.array(1.199))))
    n = gradient_noise(np.linspace(0, 50, 200001), np.full(200001, 0.37))
    print("gradient noise on a line: min %.2f, max %.2f, mean %.2f" % (n.min(), n.max(), n.mean()))
    # 1.8 m x 1.2 m of floor at 2 mm a pixel: 900 x 600 pixels
    ys, xs = np.mgrid[0:600, 0:900] * 0.002
    colour, rough = basalt(xs + 0.3, ys + 0.3)
    write_png("basalt.png", to_srgb(colour * 6))        # x6: as if lit brightly, so the dark stone shows
    print("roughness on this piece: %.3f .. %.3f" % (rough.min(), rough.max()))
    print("wrote basalt.png")
