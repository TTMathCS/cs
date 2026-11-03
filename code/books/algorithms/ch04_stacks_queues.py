"""Chapter 4: stacks and queues at work.

balanced()      bracket matching with a stack
to_rpn()        Dijkstra's shunting-yard: infix to postfix, with a trace
eval_rpn()      evaluate postfix with a stack
RingQueue       a queue in a circular buffer that doubles when full
TwoStackQueue   a queue made of two stacks, counting its elementary moves
"""
import operator
import random
from collections import deque

PAIRS = {")": "(", "]": "[", "}": "{"}


def balanced(text):
    stack = []
    for ch in text:
        if ch in "([{":
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack                     # every opener must be closed


PREC = {"+": 1, "-": 1, "*": 2, "/": 2, "^": 3}
RIGHT = {"^"}                            # 2^3^2 means 2^(3^2)
OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul,
       "/": operator.truediv, "^": operator.pow}


def to_rpn(tokens, trace=False):
    out, stack = [], []
    if trace:
        print(f"  {'token':<6} {'output':<26} stack")
    for t in tokens:
        if t in PREC:
            while (stack and stack[-1] != "(" and
                   (PREC[stack[-1]] > PREC[t] or
                    (PREC[stack[-1]] == PREC[t] and t not in RIGHT))):
                out.append(stack.pop())
            stack.append(t)
        elif t == "(":
            stack.append(t)
        elif t == ")":
            while stack[-1] != "(":
                out.append(stack.pop())
            stack.pop()                  # discard the "("
        else:
            out.append(t)                # a number goes straight to the output
        if trace:
            print(f"  {t:<6} {' '.join(out):<26} {' '.join(stack)}".rstrip())
    while stack:
        out.append(stack.pop())
    if trace:
        print(f"  {'end':<6} {' '.join(out)}")
    return out


def eval_rpn(rpn):
    stack = []
    for t in rpn:
        if t in OPS:
            b, a = stack.pop(), stack.pop()      # the right operand is on top
            stack.append(OPS[t](a, b))
        else:
            stack.append(float(t))
    assert len(stack) == 1
    return stack[0]


class RingQueue:
    def __init__(self, cap=4):
        self.buf = [None] * cap
        self.head = 0                    # index of the front item
        self.n = 0

    def enqueue(self, x):
        if self.n == len(self.buf):      # full: copy into a block twice as big
            self.buf = [self.buf[(self.head + i) % len(self.buf)] for i in range(self.n)] \
                       + [None] * self.n
            self.head = 0
        self.buf[(self.head + self.n) % len(self.buf)] = x
        self.n += 1

    def dequeue(self):
        if self.n == 0:
            raise IndexError("dequeue from empty queue")
        x = self.buf[self.head]
        self.buf[self.head] = None
        self.head = (self.head + 1) % len(self.buf)
        self.n -= 1
        return x


class TwoStackQueue:
    def __init__(self):
        self.inbox, self.outbox = [], []
        self.moves = 0                   # pushes and pops on the two stacks

    def enqueue(self, x):
        self.inbox.append(x)
        self.moves += 1

    def dequeue(self):
        if not self.outbox:              # refill: reverses the order, oldest on top
            while self.inbox:
                self.outbox.append(self.inbox.pop())
                self.moves += 2
        self.moves += 1
        return self.outbox.pop()


if __name__ == "__main__":
    for text in ["{[()()]}", "([)]", "((a + b) * c", "f(a[i], {k: v})"]:
        print(f"balanced({text!r}) = {balanced(text)}")

    print()
    expr = "2 * ( 3 + 4 ) - 10 / 5 ^ 2"
    print("Shunting-yard on:", expr)
    rpn = to_rpn(expr.split(), trace=True)
    print("value:", eval_rpn(rpn), "  check:", 2 * (3 + 4) - 10 / 5 ** 2)
    print("2 ^ 3 ^ 2 ->", " ".join(to_rpn("2 ^ 3 ^ 2".split())), "=", eval_rpn(to_rpn("2 ^ 3 ^ 2".split())))

    print()
    rng = random.Random(5)
    q, tq, ref = RingQueue(), TwoStackQueue(), deque()
    ops = 0
    for step in range(100_000):
        if rng.random() < 0.55 or not ref:
            x = rng.randrange(10**6)
            q.enqueue(x); tq.enqueue(x); ref.append(x)
        else:
            assert q.dequeue() == tq.dequeue() == ref.popleft()
        ops += 1
    print(f"RingQueue and TwoStackQueue agree with deque over {ops:,} operations")
    print(f"two-stack queue: {tq.moves:,} stack moves, {tq.moves / ops:.2f} per operation")
    print(f"ring buffer capacity at the end: {len(q.buf):,} for {q.n:,} items")
