# Chapter 8: a conflict-driven clause-learning (CDCL) SAT solver from scratch:
# two watched literals, first-UIP clause learning, non-chronological backjumping,
# VSIDS-style variable activity, phase saving and restarts. Compared with plain DPLL.
import random
import sys
from itertools import combinations

sys.setrecursionlimit(10000)


class CDCL:
    def __init__(self, n, clauses):
        self.n = n
        self.clauses = [list(c) for c in clauses]
        self.value = [None] * (n + 1)          # True / False / None per variable
        self.level = [0] * (n + 1)
        self.reason = [None] * (n + 1)         # index of the clause that forced the variable
        self.trail, self.trail_lim = [], []    # assigned literals in order; trail index where each level starts
        self.watches = {}                      # literal -> indices of clauses watching it
        self.activity = [0.0] * (n + 1)
        self.inc = 1.0
        self.phase = [False] * (n + 1)
        self.qhead = 0
        self.stats = {"decisions": 0, "propagations": 0, "conflicts": 0, "learned": 0, "max_backjump": 0}
        self.ok = True
        for i, c in enumerate(self.clauses):
            if len(c) == 0:
                self.ok = False
            elif len(c) == 1:
                if not self.enqueue(c[0], None):
                    self.ok = False
            else:
                self.watch(c[0], i)
                self.watch(c[1], i)

    def watch(self, lit, i):
        self.watches.setdefault(lit, []).append(i)

    def lit_value(self, lit):
        v = self.value[abs(lit)]
        return None if v is None else (v == (lit > 0))

    def enqueue(self, lit, reason):
        val = self.lit_value(lit)
        if val is not None:
            return val
        v = abs(lit)
        self.value[v] = lit > 0
        self.level[v] = len(self.trail_lim)
        self.reason[v] = reason
        self.trail.append(lit)
        return True

    def propagate(self):
        """Unit propagation with two watched literals. Returns the index of a conflicting clause, or None."""
        while self.qhead < len(self.trail):
            p = self.trail[self.qhead]          # p just became true, so -p is false
            self.qhead += 1
            false_lit = -p
            ws = self.watches.get(false_lit, [])
            self.watches[false_lit] = []
            for k, i in enumerate(ws):
                c = self.clauses[i]
                if c[0] == false_lit:           # keep the false watched literal in position 1
                    c[0], c[1] = c[1], c[0]
                if self.lit_value(c[0]) is True:
                    self.watches[false_lit].append(i)
                    continue
                for j in range(2, len(c)):      # look for a new literal to watch
                    if self.lit_value(c[j]) is not False:
                        c[1], c[j] = c[j], c[1]
                        self.watch(c[1], i)
                        break
                else:
                    self.watches[false_lit].append(i)
                    if self.lit_value(c[0]) is False:   # every literal false: conflict
                        self.watches[false_lit].extend(ws[k + 1:])
                        self.qhead = len(self.trail)
                        return i
                    self.stats["propagations"] += 1
                    self.enqueue(c[0], i)        # unit clause: c[0] is forced
        return None

    def analyze(self, confl):
        """First-UIP learning: resolve the conflict clause with reasons of current-level literals
        until exactly one literal of the current level is left."""
        learnt, seen, counter, p = [None], set(), 0, None
        index = len(self.trail) - 1
        cur = len(self.trail_lim)
        while True:
            for q in self.clauses[confl]:
                if p is not None and q == p:
                    continue
                v = abs(q)
                if v not in seen and self.level[v] > 0:
                    seen.add(v)
                    self.bump(v)
                    if self.level[v] == cur:
                        counter += 1
                    else:
                        learnt.append(q)
            while abs(self.trail[index]) not in seen:
                index -= 1
            p = self.trail[index]
            index -= 1
            confl = self.reason[abs(p)]
            seen.discard(abs(p))
            counter -= 1
            if counter == 0:
                break
        learnt[0] = -p                           # the asserting literal: the negation of the UIP
        back = max((self.level[abs(l)] for l in learnt[1:]), default=0)
        return learnt, back

    def bump(self, v):
        self.activity[v] += self.inc
        if self.activity[v] > 1e100:
            self.activity = [a * 1e-100 for a in self.activity]
            self.inc *= 1e-100

    def backjump(self, level):
        if len(self.trail_lim) <= level:
            return
        start = self.trail_lim[level]
        for lit in self.trail[start:]:
            v = abs(lit)
            self.phase[v] = self.value[v]
            self.value[v] = None
            self.reason[v] = None
        del self.trail[start:]
        del self.trail_lim[level:]
        self.qhead = len(self.trail)

    def pick(self):
        best, best_a = None, -1.0
        for v in range(1, self.n + 1):
            if self.value[v] is None and self.activity[v] > best_a:
                best, best_a = v, self.activity[v]
        return best

    def solve(self, max_conflicts=10 ** 6):
        if not self.ok or self.propagate() is not None:
            return None
        restart_at, restart_gap = 100, 100
        while True:
            confl = self.propagate()
            if confl is not None:
                self.stats["conflicts"] += 1
                if not self.trail_lim:
                    return None                  # conflict at level 0: unsatisfiable
                learnt, back = self.analyze(confl)
                self.stats["max_backjump"] = max(self.stats["max_backjump"], len(self.trail_lim) - back)
                self.backjump(back)
                if len(learnt) == 1:
                    self.enqueue(learnt[0], None)
                else:
                    # watch the asserting literal and the literal of the highest remaining level
                    j = max(range(1, len(learnt)), key=lambda k: self.level[abs(learnt[k])])
                    learnt[1], learnt[j] = learnt[j], learnt[1]
                    self.clauses.append(learnt)
                    i = len(self.clauses) - 1
                    self.watch(learnt[0], i)
                    self.watch(learnt[1], i)
                    self.enqueue(learnt[0], i)
                self.stats["learned"] += 1
                self.inc /= 0.95                 # VSIDS: recent conflicts count more
                if self.stats["conflicts"] >= max_conflicts:
                    return "unknown"
                if self.stats["conflicts"] >= restart_at:
                    self.backjump(0)             # restart, keeping learned clauses and activities
                    restart_gap = int(restart_gap * 1.5)
                    restart_at += restart_gap
            else:
                v = self.pick()
                if v is None:
                    return [None] + self.value[1:]
                self.stats["decisions"] += 1
                self.trail_lim.append(len(self.trail))
                self.enqueue(v if self.phase[v] else -v, None)


# ---- plain DPLL (unit propagation + branching), recursive, for comparison
def dpll(clauses, stats):
    def simplify(cl, lit):
        out = []
        for c in cl:
            if lit in c:
                continue
            out.append([l for l in c if l != -lit] if -lit in c else c)
        return out

    def go(cl):
        while True:
            if any(not c for c in cl):
                stats["conflicts"] += 1
                return False
            unit = next((c[0] for c in cl if len(c) == 1), None)
            if unit is None:
                break
            cl = simplify(cl, unit)
        if not cl:
            return True
        counts = {}
        for c in cl:
            for l in c:
                counts[abs(l)] = counts.get(abs(l), 0) + 1
        v = max(counts, key=counts.get)
        for lit in (v, -v):
            stats["decisions"] += 1
            if go(simplify(cl, lit)):
                return True
        return False

    return go(clauses)


def random_3sat(n, m, rng):
    return [[v if rng.random() < 0.5 else -v for v in rng.sample(range(1, n + 1), 3)] for _ in range(m)]


def satisfied(clauses, model):
    return all(any(model[abs(l)] == (l > 0) for l in c) for c in clauses)


def pigeonhole(holes):
    var = lambda i, j: i * holes + j + 1
    cl = [[var(i, j) for j in range(holes)] for i in range(holes + 1)]
    for j in range(holes):
        for a, b in combinations(range(holes + 1), 2):
            cl.append([-var(a, j), -var(b, j)])
    return cl


rng = random.Random(2001)
print("random 3-SAT at 4.26 clauses per variable (3 formulas per size)")
print("   n   result   DPLL decisions   CDCL decisions  conflicts  learned  longest backjump")
for n in (50, 75, 100):
    for _ in range(3):
        cl = random_3sat(n, round(4.26 * n), rng)
        st = {"decisions": 0, "conflicts": 0}
        d_ans = dpll(cl, st)
        s = CDCL(n, cl)
        res = s.solve()
        if res is not None:
            assert satisfied(cl, res)
        assert (res is not None) == d_ans
        print(f"{n:4d}   {'SAT' if res else 'UNSAT':6s}   {st['decisions']:14d}   {s.stats['decisions']:14d}"
              f"  {s.stats['conflicts']:9d}  {s.stats['learned']:7d}  {s.stats['max_backjump']:16d}")

print("\npigeonhole (unsatisfiable): CDCL conflicts")
for h in range(4, 8):
    s = CDCL(h * (h + 1), pigeonhole(h))
    res = s.solve()
    print(f"  holes {h}: unsatisfiable {res is None}, conflicts {s.stats['conflicts']}")


def hidden_core(k, rng):
    """k irrelevant variables in 3k random all-positive 3-clauses (easy to satisfy), plus a small
    unsatisfiable core (5 pigeons, 4 holes) on 20 other variables numbered after them."""
    ys = [rng.sample(range(1, k + 1), 3) for _ in range(3 * k)]
    core = [[l + k if l > 0 else l - k for l in c] for c in pigeonhole(4)]
    return k + 20, ys + core


print("\nirrelevant variables plus a small unsatisfiable core")
print("   k   DPLL decisions   CDCL decisions   CDCL conflicts   longest backjump")
for k in (10, 20, 30):
    n, cl = hidden_core(k, rng)
    st = {"decisions": 0, "conflicts": 0}
    assert not dpll(cl, st)
    s = CDCL(n, cl)
    assert s.solve() is None
    print(f"{k:4d}   {st['decisions']:14d}   {s.stats['decisions']:14d}   {s.stats['conflicts']:14d}"
          f"   {s.stats['max_backjump']:16d}")
