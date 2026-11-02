class Node:
    def __init__(self, key):
        self.key = key
        self.left = None                     # keys smaller than this one
        self.right = None                    # keys larger than this one


def insert(root, key):
    """Inserts key (if new) and returns the root of the tree."""
    if root is None:
        return Node(key)
    if key < root.key:
        root.left = insert(root.left, key)
    elif key > root.key:
        root.right = insert(root.right, key)
    return root


def contains(root, key):
    while root is not None:                  # go left or right, like a binary search
        if key == root.key:
            return True
        root = root.left if key < root.key else root.right
    return False


def delete(root, key):
    """Removes key (if present) and returns the root of the tree."""
    if root is None:
        return None
    if key < root.key:
        root.left = delete(root.left, key)
    elif key > root.key:
        root.right = delete(root.right, key)
    else:
        if root.left is None:                # zero or one child: lift the child up
            return root.right
        if root.right is None:
            return root.left
        succ = root.right                    # two children: copy in the next larger key ...
        while succ.left is not None:
            succ = succ.left
        root.key = succ.key
        root.right = delete(root.right, succ.key)   # ... and delete it from the right subtree
    return root


def inorder(root, out):
    """Left subtree, node, right subtree: visits the keys in sorted order."""
    if root is not None:
        inorder(root.left, out)
        out.append(root.key)
        inorder(root.right, out)
    return out


def height(root):
    return 0 if root is None else 1 + max(height(root.left), height(root.right))


if __name__ == "__main__":
    root = None
    for k in [50, 30, 70, 20, 40, 60, 80, 35]:
        root = insert(root, k)
    print(inorder(root, []), height(root))
    print(contains(root, 60), contains(root, 65))
    for k in [20, 30, 50]:                   # a leaf, a node with two children, the root
        root = delete(root, k)
        print(inorder(root, []), "root", root.key)
    chain = None
    for k in range(1, 8):                    # sorted input makes a tall, thin tree
        chain = insert(chain, k)
    print("height after inserting 1..7 in order:", height(chain))
