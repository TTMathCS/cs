def z_array(s):
    """z[i] = the length of the longest stretch starting at i that equals the start of s (z[0] = len(s))."""
    n = len(s)
    z = [0] * n
    if n:
        z[0] = n
    l = r = 0                                # s[l:r] is the rightmost stretch found that equals a prefix
    for i in range(1, n):
        if i < r:                            # inside a known stretch: reuse the value from the copy at the start
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:   # then try to extend by direct comparison
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    return z


def z_search(text, p, sep="\0"):
    """Every position where p starts in text: z-values of p + separator + text that reach len(p)."""
    z = z_array(p + sep + text)
    m = len(p)
    return [i - m - 1 for i in range(m + 1, len(z)) if z[i] >= m]


if __name__ == "__main__":
    print(z_array("aabxaab"))
    print(z_array("aaaaa"))
    print(z_search("the red planet has red dust", "red"))
