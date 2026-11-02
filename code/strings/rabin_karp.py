def rabin_karp(text, p, mod=1_000_000_007, base=256):
    """Every position where p starts in text, comparing rolling hashes first and letters only when the hashes
    agree. Returns the positions and the number of false alarms (equal hashes, different letters)."""
    n, m = len(text), len(p)
    if m > n:
        return [], 0
    high = pow(base, m - 1, mod)             # the weight of the window's first letter
    hp = ht = 0
    for i in range(m):                       # hash of p and of the first window
        hp = (hp * base + ord(p[i])) % mod
        ht = (ht * base + ord(text[i])) % mod
    found, false_alarms = [], 0
    for s in range(n - m + 1):
        if hp == ht:
            if text[s:s + m] == p:           # check the letters: equal hashes do not prove a match
                found.append(s)
            else:
                false_alarms += 1
        if s + m < n:                        # roll: drop text[s], add text[s+m]
            ht = ((ht - ord(text[s]) * high) * base + ord(text[s + m])) % mod
    return found, false_alarms


if __name__ == "__main__":
    text = "dust storms on mars can cover all of mars for months"
    print(*rabin_karp(text, "mars"))
    print(*rabin_karp(text, "mars", mod=13))
    print(*rabin_karp("abracadabra", "abra"))
