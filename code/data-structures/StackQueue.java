import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class StackQueue {
    /** Last in, first out, on a growing array: push and pop at the end are O(1) amortized. */
    static class Stack<T> {
        private final ArrayList<T> items = new ArrayList<>();
        void push(T x) { items.add(x); }
        T pop() { return items.remove(items.size() - 1); }
        T peek() { return items.get(items.size() - 1); }
        boolean empty() { return items.isEmpty(); }
    }

    /** First in, first out, in a ring buffer that doubles when full: every operation is O(1) amortized. */
    static class Queue<T> {
        private Object[] buf = new Object[4];
        private int head = 0, size = 0;               // head: index of the front item

        void enqueue(T x) {
            if (size == buf.length) {                 // full: copy into a buffer twice as big
                Object[] bigger = new Object[2 * buf.length];
                for (int i = 0; i < size; i++) bigger[i] = buf[(head + i) % buf.length];
                buf = bigger;
                head = 0;
            }
            buf[(head + size) % buf.length] = x;
            size++;
        }

        @SuppressWarnings("unchecked")
        T dequeue() {
            T x = (T) buf[head];
            buf[head] = null;
            head = (head + 1) % buf.length;
            size--;
            return x;
        }

        boolean empty() { return size == 0; }
    }

    /** True if every bracket in s is closed by the right kind, in the right order. */
    static boolean balanced(String s) {
        Map<Character, Character> pairs = Map.of(')', '(', ']', '[', '}', '{');
        Stack<Character> st = new Stack<>();
        for (char ch : s.toCharArray()) {
            if (ch == '(' || ch == '[' || ch == '{') st.push(ch);       // remember the opener
            else if (pairs.containsKey(ch)) {
                if (st.empty() || st.pop() != pairs.get(ch)) return false;   // nothing to close, or wrong kind
            }
        }
        return st.empty();                            // every opener was closed
    }

    public static void main(String[] args) {
        for (String s : new String[]{"([]{})", "([)]", "((", "a[b(c)d]e", ""})
            System.out.println("'" + s + "' " + (balanced(s) ? "True" : "False"));
        Queue<Integer> q = new Queue<>();
        for (int x = 1; x <= 6; x++) q.enqueue(x);
        List<Integer> out = new ArrayList<>(List.of(q.dequeue(), q.dequeue()));
        q.enqueue(7);
        while (!q.empty()) out.add(q.dequeue());
        System.out.println(out);
    }
}
