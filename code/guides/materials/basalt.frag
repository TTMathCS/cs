#version 300 es
// The basalt pattern of materials.py as a WebGL2 fragment shader: the graphics card runs main() once for every
// pixel, at the same time on thousands of cores. vPos is the point on the floor in metres.
precision highp float;
precision highp int;
in vec2 vPos;
out vec4 outColor;

uint hash2(ivec2 p, uint seed) {                 // the same integer hash as the Python (wraps at 2^32)
    uint h = (uint(p.x) * 73856093u) ^ (uint(p.y) * 19349663u) ^ seed;
    h ^= h >> 13u; h *= 0x5BD1E995u; h ^= h >> 15u;
    return h;
}
float fade(float t) { return t * t * t * (t * (t * 6.0 - 15.0) + 10.0); }

float gradientNoise(vec2 p, uint seed) {         // about -1..1
    ivec2 i = ivec2(floor(p)); vec2 f = p - floor(p);
    float c[4];
    for (int k = 0; k < 4; k++) {
        ivec2 o = ivec2(k & 1, k >> 1);
        float a = float(hash2(i + o, seed)) / 4294967296.0 * 6.28318530718;
        c[k] = dot(vec2(cos(a), sin(a)), f - vec2(o));
    }
    vec2 u = vec2(fade(f.x), fade(f.y));
    return mix(mix(c[0], c[1], u.x), mix(c[2], c[3], u.x), u.y) * 1.41421356;
}

float fbm(vec2 p, int detail) {                  // octaves 0..detail, roughness 0.5, lacunarity 2, into 0..1
    float total = 0.0, amp = 1.0, maxamp = 0.0, f = 1.0;
    for (int k = 0; k <= detail; k++) { total += amp * gradientNoise(p * f, 0u); maxamp += amp; amp *= 0.5; f *= 2.0; }
    return 0.5 * total / maxamp + 0.5;
}

float voronoiF1(vec2 p) {                        // distance to the nearest of one random point per unit square
    ivec2 i = ivec2(floor(p)); float best = 9.0;
    for (int dy = -1; dy <= 1; dy++) for (int dx = -1; dx <= 1; dx++) {
        ivec2 c = i + ivec2(dx, dy); uint h = hash2(c, 1u);
        vec2 q = vec2(c) + vec2(float(h & 0xFFFFu), float(h >> 16u)) / 65536.0;
        best = min(best, distance(p, q));
    }
    return best;
}

float slabJoint(vec2 p) {                        // 1 on the 3 mm joint between 1.2 m x 0.6 m slabs
    float r = floor(p.y / 0.6), shift = mod(r, 2.0) == 0.0 ? 0.6 : 0.0;
    float b = floor((p.x + shift) / 1.2);
    vec2 uv = vec2(p.x + shift - b * 1.2, p.y - r * 0.6);
    float d = min(min(uv.x, uv.y), min(1.2 - uv.x, 0.6 - uv.y));
    return d < 0.003 ? 1.0 : 0.0;
}

void main() {
    float t = clamp(0.6 * voronoiF1(vPos * 260.0) + 0.5 * fbm(vPos * 0.7, 6), 0.0, 1.0);
    vec3 colour = mix(vec3(0.018, 0.018, 0.019), vec3(0.06, 0.058, 0.056), t);   // linear light
    colour *= slabJoint(vPos) > 0.5 ? 0.4 : 1.0;
    float roughness = 0.13 + 0.14 * fbm(vPos * 3.0, 8);                          // would go to the lighting
    vec3 shown = colour * 6.0;                                                    // as bright as the Python picture
    outColor = vec4(pow(shown, vec3(1.0 / 2.2)), 1.0);                            // near enough to sRGB for a test
}
