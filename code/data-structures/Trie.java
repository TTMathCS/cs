import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class Trie {
    static class Node {
        final Map<Character, Node> children = new TreeMap<>();   // letter -> next node, kept in order
        boolean end;                                  // does a word end here?
        int count;                                    // how many words pass through here
    }

    final Node root = new Node();

    /** A prefix tree of words: insert, look up and count by prefix in O(length of the word). */
    void insert(String word) {
        Node node = root;
        for (char ch : word.toCharArray()) {
            node = node.children.computeIfAbsent(ch, c -> new Node());
            node.count++;
        }
        node.end = true;
    }

    Node walk(String s) {
        Node node = root;
        for (char ch : s.toCharArray()) {
            node = node.children.get(ch);
            if (node == null) return null;
        }
        return node;
    }

    boolean contains(String word) { Node n = walk(word); return n != null && n.end; }

    int countPrefix(String prefix) { Node n = walk(prefix); return n == null ? 0 : n.count; }

    /** All stored words that start with prefix, in alphabetical order. */
    List<String> withPrefix(String prefix) {
        List<String> out = new ArrayList<>();
        Node n = walk(prefix);
        if (n != null) dfs(n, new StringBuilder(prefix), out);
        return out;
    }

    void dfs(Node node, StringBuilder path, List<String> out) {
        if (node.end) out.add(path.toString());
        for (Map.Entry<Character, Node> e : node.children.entrySet()) {
            path.append(e.getKey());
            dfs(e.getValue(), path, out);
            path.deleteCharAt(path.length() - 1);
        }
    }

    static String py(boolean b) { return b ? "True" : "False"; }

    static String show(List<String> xs) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < xs.size(); i++) sb.append(i > 0 ? ", " : "").append("'").append(xs.get(i)).append("'");
        return sb.append("]").toString();
    }

    public static void main(String[] args) {
        Trie t = new Trie();
        for (String w : new String[]{"mars", "marble", "march", "mare", "moon", "moonlight", "map"}) t.insert(w);
        System.out.println(py(t.contains("mars")) + " " + py(t.contains("mar")) + " " + py(t.contains("moonlit")));
        System.out.println(t.countPrefix("mar") + " " + t.countPrefix("moon") + " " + t.countPrefix("x"));
        System.out.println(show(t.withPrefix("mar")));
        System.out.println(show(t.withPrefix("mo")));
    }
}
