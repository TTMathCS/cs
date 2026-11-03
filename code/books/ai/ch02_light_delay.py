"""Chapter 2: how long a radio signal takes between Earth and Mars, and why it matters.

1. Light time from a simple model: circular, coplanar orbits.
2. Light time at the real extremes, from perihelion and aphelion distances.
3. A thought experiment: a rover that must wait for Earth after every 1 m step,
   against a rover that decides each step itself.
Python with NumPy.
"""
import numpy as np

C_KM_S = 299_792.458          # speed of light, km/s
AU_KM = 149_597_870.7         # astronomical unit, km

# Semi-major axes in AU and orbital periods in days.
A_EARTH, P_EARTH = 1.000, 365.256
A_MARS, P_MARS = 1.5237, 686.98

# Real extremes (km): perihelion and aphelion of each orbit.
EARTH_PERI, EARTH_APH = 147.10e6, 152.10e6
MARS_PERI, MARS_APH = 206.62e6, 249.23e6


def minutes(km):
    return km / C_KM_S / 60


def main():
    synodic = 1 / (1 / P_EARTH - 1 / P_MARS)
    t = np.linspace(0, synodic, 100_001)                 # days
    angle = 2 * np.pi * t * (1 / P_EARTH - 1 / P_MARS)   # Earth's lead over Mars
    d = AU_KM * np.sqrt(A_EARTH ** 2 + A_MARS ** 2
                        - 2 * A_EARTH * A_MARS * np.cos(angle))
    lt = minutes(d)
    print("circular-orbit model:")
    print(f"  synodic period {synodic:.0f} days")
    print(f"  distance {d.min() / 1e6:.1f} to {d.max() / 1e6:.1f} million km")
    print(f"  one-way light time {lt.min():.1f} to {lt.max():.1f} minutes")
    print(f"  fraction of the time above 10 minutes: {np.mean(lt > 10):.2f}")

    near, far = MARS_PERI - EARTH_APH, MARS_APH + EARTH_APH
    print("real orbits (eccentric), extreme cases:")
    print(f"  closest possible about {near / 1e6:.1f} million km:"
          f" {minutes(near):.1f} minutes one way")
    print(f"  farthest possible about {far / 1e6:.1f} million km:"
          f" {minutes(far):.1f} minutes one way")
    print(f"  round trip: {2 * minutes(near):.0f} to {2 * minutes(far):.0f} minutes")

    print("\nthought experiment: 4 hours of driving, 1 minute to drive and image 1 m")
    window = 240
    for delay in (3, 12.5, 22):
        per_step = 1 + 2 * delay
        print(f"  wait for Earth after each metre (one-way {delay:4.1f} min):"
              f" {int(window // per_step):3d} m")
    print(f"  decide each metre on board:                    {window:3d} m")


if __name__ == "__main__":
    main()
