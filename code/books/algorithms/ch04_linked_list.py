"""Chapter 4: singly and doubly linked lists, built from nodes and references."""
import random


class Node:
    __slots__ = ("value", "next")

    def __init__(self, value, next=None):
        self.value = value
        self.next = next


class SinglyLinkedList:
    def __init__(self):
        self.head = None            # first node, or None when empty
        self.size = 0

    def push_front(self, x):        # O(1)
        self.head = Node(x, self.head)
        self.size += 1

    def pop_front(self):            # O(1)
        if self.head is None:
            raise IndexError("pop from empty list")
        node = self.head
        self.head = node.next
        self.size -= 1
        return node.value

    def insert_after(self, node, x):   # O(1) once you have the node
        node.next = Node(x, node.next)
        self.size += 1

    def find(self, x):              # O(n): must walk from the head
        node = self.head
        while node is not None and node.value != x:
            node = node.next
        return node

    def remove(self, x):            # O(n) to find it, O(1) to unlink it
        prev, node = None, self.head
        while node is not None and node.value != x:
            prev, node = node, node.next
        if node is None:
            return False
        if prev is None:
            self.head = node.next
        else:
            prev.next = node.next
        self.size -= 1
        return True

    def reverse(self):              # O(n) time, O(1) extra space
        prev, node = None, self.head
        while node is not None:
            node.next, prev, node = prev, node, node.next
        self.head = prev

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.value
            node = node.next


class DNode:
    __slots__ = ("value", "prev", "next")

    def __init__(self, value=None):
        self.value, self.prev, self.next = value, None, None


class DoublyLinkedList:
    """Circular, with one sentinel node: no special cases for the ends."""

    def __init__(self):
        self.nil = DNode()          # the sentinel: nil.next is first, nil.prev is last
        self.nil.next = self.nil.prev = self.nil
        self.size = 0

    def insert_after(self, node, x):    # O(1)
        new = DNode(x)
        new.prev, new.next = node, node.next
        node.next.prev = new
        node.next = new
        self.size += 1
        return new

    def push_front(self, x):
        return self.insert_after(self.nil, x)

    def push_back(self, x):
        return self.insert_after(self.nil.prev, x)

    def unlink(self, node):             # O(1), given the node itself
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1
        return node.value

    def pop_front(self):
        if self.size == 0:
            raise IndexError("pop from empty list")
        return self.unlink(self.nil.next)

    def pop_back(self):
        if self.size == 0:
            raise IndexError("pop from empty list")
        return self.unlink(self.nil.prev)

    def __iter__(self):
        node = self.nil.next
        while node is not self.nil:
            yield node.value
            node = node.next


if __name__ == "__main__":
    s = SinglyLinkedList()
    for x in [4, 3, 2, 1]:
        s.push_front(x)
    print("singly:", list(s))
    s.insert_after(s.find(2), 25)
    print("after insert_after(find(2), 25):", list(s))
    s.remove(3)
    print("after remove(3):", list(s))
    s.reverse()
    print("after reverse():", list(s))

    d = DoublyLinkedList()
    for x in [1, 2, 3]:
        d.push_back(x)
    middle = d.nil.next.next            # the node holding 2
    d.unlink(middle)
    d.push_front(0)
    print("doubly:", list(d), " pop_back ->", d.pop_back(), " now", list(d))

    # Random operations, checked against Python's list as the reference.
    rng = random.Random(4)
    s, ref = SinglyLinkedList(), []
    for step in range(3000):
        op, x = rng.choice(["push", "pop", "remove", "reverse"]), rng.randrange(20)
        if op == "push":
            s.push_front(x); ref.insert(0, x)
        elif op == "pop" and ref:
            assert s.pop_front() == ref.pop(0)
        elif op == "remove":
            assert s.remove(x) == (x in ref)
            if x in ref:
                ref.remove(x)
        elif op == "reverse":
            s.reverse(); ref.reverse()
        assert list(s) == ref and s.size == len(ref)
    d, ref = DoublyLinkedList(), []
    for step in range(3000):
        op, x = rng.choice(["pushf", "pushb", "popf", "popb"]), rng.randrange(20)
        if op == "pushf":
            d.push_front(x); ref.insert(0, x)
        elif op == "pushb":
            d.push_back(x); ref.append(x)
        elif op == "popf" and ref:
            assert d.pop_front() == ref.pop(0)
        elif op == "popb" and ref:
            assert d.pop_back() == ref.pop()
        assert list(d) == ref and d.size == len(ref)
    print("3000 random operations on each list agree with Python's list")
