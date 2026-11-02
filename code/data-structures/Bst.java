import java.util.ArrayList;
import java.util.List;

public class Bst {
    static class Node {
        int key;
        Node left, right;                             // smaller keys on the left, larger on the right
        Node(int key) { this.key = key; }
    }

    /** Inserts key (if new) and returns the root of the tree. */
    static Node insert(Node root, int key) {
        if (root == null) return new Node(key);
        if (key < root.key) root.left = insert(root.left, key);
        else if (key > root.key) root.right = insert(root.right, key);
        return root;
    }

    static boolean contains(Node root, int key) {
        while (root != null) {                        // go left or right, like a binary search
            if (key == root.key) return true;
            root = key < root.key ? root.left : root.right;
        }
        return false;
    }

    /** Removes key (if present) and returns the root of the tree. */
    static Node delete(Node root, int key) {
        if (root == null) return null;
        if (key < root.key) root.left = delete(root.left, key);
        else if (key > root.key) root.right = delete(root.right, key);
        else {
            if (root.left == null) return root.right; // zero or one child: lift the child up
            if (root.right == null) return root.left;
            Node succ = root.right;                   // two children: copy in the next larger key ...
            while (succ.left != null) succ = succ.left;
            root.key = succ.key;
            root.right = delete(root.right, succ.key);   // ... and delete it from the right subtree
        }
        return root;
    }

    /** Left subtree, node, right subtree: visits the keys in sorted order. */
    static List<Integer> inorder(Node root, List<Integer> out) {
        if (root != null) { inorder(root.left, out); out.add(root.key); inorder(root.right, out); }
        return out;
    }

    static int height(Node root) { return root == null ? 0 : 1 + Math.max(height(root.left), height(root.right)); }

    public static void main(String[] args) {
        Node root = null;
        for (int k : new int[]{50, 30, 70, 20, 40, 60, 80, 35}) root = insert(root, k);
        System.out.println(inorder(root, new ArrayList<>()) + " " + height(root));
        System.out.println((contains(root, 60) ? "True" : "False") + " " + (contains(root, 65) ? "True" : "False"));
        for (int k : new int[]{20, 30, 50}) {         // a leaf, a node with two children, the root
            root = delete(root, k);
            System.out.println(inorder(root, new ArrayList<>()) + " root " + root.key);
        }
        Node chain = null;
        for (int k = 1; k <= 7; k++) chain = insert(chain, k);   // sorted input makes a tall, thin tree
        System.out.println("height after inserting 1..7 in order: " + height(chain));
    }
}
