import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class BinaryHeap {
    /** A min-heap in an array list: a.get(0) is the smallest; the children of i are 2i+1 and 2i+2. */
    static class MinHeap {
        final ArrayList<Integer> a = new ArrayList<>();

        void push(int x) {
            a.add(x);                                 // put it at the bottom ...
            int i = a.size() - 1;
            while (i > 0) {                           // ... and sift it up while it beats its parent
                int parent = (i - 1) / 2;
                if (a.get(parent) <= a.get(i)) break;
                Collections.swap(a, parent, i);
                i = parent;
            }
        }

        int pop() {
            int top = a.get(0);
            int last = a.remove(a.size() - 1);
            if (!a.isEmpty()) {
                a.set(0, last);                       // move the last value to the root ...
                int i = 0, n = a.size();
                while (true) {                        // ... and sift it down below smaller children
                    int small = i, l = 2 * i + 1, r = 2 * i + 2;
                    if (l < n && a.get(l) < a.get(small)) small = l;
                    if (r < n && a.get(r) < a.get(small)) small = r;
                    if (small == i) break;
                    Collections.swap(a, i, small);
                    i = small;
                }
            }
            return top;
        }

        int peek() { return a.get(0); }
        int size() { return a.size(); }
    }

    public static void main(String[] args) {
        MinHeap h = new MinHeap();
        for (int x : new int[]{5, 3, 8, 1, 9, 2, 7}) h.push(x);
        System.out.println(h.a);                      // the heap as stored
        List<Integer> out = new ArrayList<>();
        while (h.size() > 0) out.add(h.pop());        // comes out sorted
        System.out.println(out);
        MinHeap top = new MinHeap();                  // the 3 largest of a stream, keeping only 3 values
        for (int x : new int[]{12, 3, 45, 7, 33, 21, 9, 40}) {
            top.push(x);
            if (top.size() > 3) top.pop();            // drop the smallest of the 4
        }
        List<Integer> best = new ArrayList<>(top.a);
        best.sort(Collections.reverseOrder());
        System.out.println(best);
    }
}
