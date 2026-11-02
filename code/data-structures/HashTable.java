import java.util.ArrayList;
import java.util.List;
import java.util.TreeSet;

public class HashTable {
    /** A hash table with separate chaining: each bucket holds a short list of (key, value) pairs. */
    static class HashMap {
        record Entry(String key, int value) {}
        List<List<Entry>> buckets = newBuckets(8);
        int size = 0;

        static List<List<Entry>> newBuckets(int n) {
            List<List<Entry>> b = new ArrayList<>();
            for (int i = 0; i < n; i++) b.add(new ArrayList<>());
            return b;
        }

        List<Entry> bucket(String key) { return buckets.get((int) (hashStr(key) % buckets.size())); }

        void put(String key, int value) {
            List<Entry> b = bucket(key);
            for (int i = 0; i < b.size(); i++)
                if (b.get(i).key().equals(key)) { b.set(i, new Entry(key, value)); return; }  // replace
            b.add(new Entry(key, value));
            size++;
            if (size > 0.75 * buckets.size()) resize(2 * buckets.size());   // too full: double the buckets
        }

        int get(String key, int dflt) {
            for (Entry e : bucket(key)) if (e.key().equals(key)) return e.value();
            return dflt;
        }

        void resize(int n) {
            List<List<Entry>> old = buckets;
            buckets = newBuckets(n);
            for (List<Entry> b : old)
                for (Entry e : b) buckets.get((int) (hashStr(e.key()) % n)).add(e);
        }
    }

    /** Polynomial string hash, the same as Java's String.hashCode, read as an unsigned 32-bit number. */
    static long hashStr(String s) {
        long h = 0;
        for (char ch : s.toCharArray()) h = (31 * h + ch) & 0xFFFFFFFFL;
        return h;
    }

    public static void main(String[] args) {
        String text = "the quick brown fox jumps over the lazy dog the end";
        HashMap m = new HashMap();
        for (String w : text.split(" ")) m.put(w, m.get(w, 0) + 1);
        for (String w : new TreeSet<>(List.of(text.split(" ")))) System.out.println(w + " " + m.get(w, 0));
        System.out.println("buckets: " + m.buckets.size() + " keys: " + m.size + " missing: " + m.get("cat", 0));
        System.out.println(hashStr("abc"));
    }
}
