import java.util.HashMap;
import java.util.Map;
import java.util.PriorityQueue;

public class Huffman {
    static int[] left, right;
    static char[] letters;
    static Map<Character, String> codes;

    /** Huffman coding: the prefix-free binary code with the fewest total bits for these letter counts.
     *  Ties are broken by creation order, so the result is the same in every language. */
    static Map<Character, String> huffman(char[] ls, int[] freq) {
        int n = ls.length;
        letters = ls;
        left = new int[2 * n];
        right = new int[2 * n];
        // entries {count, id}; ids 0..n-1 are the letters
        PriorityQueue<long[]> heap = new PriorityQueue<>((x, y) -> x[0] != y[0] ? Long.compare(x[0], y[0]) : Long.compare(x[1], y[1]));
        for (int i = 0; i < n; i++) heap.add(new long[]{freq[i], i});
        int nextId = n;
        while (heap.size() > 1) {                     // join the two rarest trees into one
            long[] a = heap.poll(), b = heap.poll();
            left[nextId] = (int) a[1];
            right[nextId] = (int) b[1];
            heap.add(new long[]{a[0] + b[0], nextId});
            nextId++;
        }
        codes = new HashMap<>();
        walk((int) heap.peek()[1], "");
        return codes;
    }

    static void walk(int node, String path) {         // left edge = 0, right edge = 1
        if (node < letters.length) codes.put(letters[node], path.isEmpty() ? "0" : path);
        else { walk(left[node], path + "0"); walk(right[node], path + "1"); }
    }

    public static void main(String[] args) {
        char[] ls = {'a', 'b', 'c', 'd', 'e', 'f'};
        int[] freq = {45, 13, 12, 16, 9, 5};
        Map<Character, String> c = huffman(ls, freq);
        int total = 0, all = 0;
        for (int i = 0; i < ls.length; i++) {
            System.out.println(ls[i] + " " + c.get(ls[i]));
            total += freq[i] * c.get(ls[i]).length();
            all += freq[i];
        }
        System.out.println("total bits: " + total + " fixed 3-bit code: " + 3 * all);
        StringBuilder sb = new StringBuilder();
        for (char ch : "face".toCharArray()) sb.append(c.get(ch));
        System.out.println("face -> " + sb);
    }
}
