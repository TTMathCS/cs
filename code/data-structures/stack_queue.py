class Stack:
    """Last in, first out, on a growing list: push and pop at the end are O(1)."""
    def __init__(self):
        self.items = []

    def push(self, x):
        self.items.append(x)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[-1]

    def empty(self):
        return not self.items


class Queue:
    """First in, first out, in a ring buffer that doubles when full: every operation is O(1) amortized."""
    def __init__(self):
        self.buf = [None] * 4
        self.head = 0                        # index of the front item
        self.size = 0

    def enqueue(self, x):
        if self.size == len(self.buf):       # full: copy into a buffer twice as big
            self.buf = [self.buf[(self.head + i) % len(self.buf)] for i in range(self.size)] + [None] * self.size
            self.head = 0
        self.buf[(self.head + self.size) % len(self.buf)] = x
        self.size += 1

    def dequeue(self):
        x = self.buf[self.head]
        self.buf[self.head] = None
        self.head = (self.head + 1) % len(self.buf)
        self.size -= 1
        return x

    def empty(self):
        return self.size == 0


def balanced(s):
    """True if every bracket in s is closed by the right kind, in the right order."""
    pairs = {")": "(", "]": "[", "}": "{"}
    st = Stack()
    for ch in s:
        if ch in "([{":
            st.push(ch)                      # remember the opener
        elif ch in pairs:
            if st.empty() or st.pop() != pairs[ch]:
                return False                 # nothing to close, or the wrong kind
    return st.empty()                        # every opener was closed


if __name__ == "__main__":
    for s in ["([]{})", "([)]", "((", "a[b(c)d]e", ""]:
        print(repr(s), balanced(s))
    q = Queue()
    for x in range(1, 7):
        q.enqueue(x)
    out = [q.dequeue(), q.dequeue()]
    q.enqueue(7)
    while not q.empty():
        out.append(q.dequeue())
    print(out)
