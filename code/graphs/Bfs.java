import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

public class Bfs {
    /** Fewest-edges distance from start to every vertex (-1 if unreachable); fills parent[]. */
    static int[] bfs(List<List<Integer>> adj, int start, int[] parent) {
        int[] dist = new int[adj.size()];
        Arrays.fill(dist, -1);
        Arrays.fill(parent, -1);
        dist[start] = 0;
        ArrayDeque<Integer> q = new ArrayDeque<>();
        q.add(start);
        while (!q.isEmpty()) {
            int u = q.poll();                         // the oldest vertex in the queue: nearest first
            for (int v : adj.get(u)) {
                if (dist[v] == -1) {                  // first time we reach v: this is the shortest way
                    dist[v] = dist[u] + 1;
                    parent[v] = u;
                    q.add(v);
                }
            }
        }
        return dist;
    }

    /** Walks the parents back from target and reverses: the shortest path from the start. */
    static List<Integer> path(int[] parent, int target) {
        List<Integer> out = new ArrayList<>();
        for (; target != -1; target = parent[target]) out.add(target);
        Collections.reverse(out);
        return out;
    }

    static List<List<Integer>> build(int n, int[][] edges) {
        List<List<Integer>> adj = new ArrayList<>();
        for (int i = 0; i < n; i++) adj.add(new ArrayList<>());
        for (int[] e : edges) { adj.get(e[0]).add(e[1]); adj.get(e[1]).add(e[0]); }   // undirected
        return adj;
    }

    public static void main(String[] args) {
        List<List<Integer>> adj = build(8, new int[][]{{0, 1}, {0, 2}, {1, 3}, {2, 3}, {3, 4}, {4, 5}, {2, 5}, {6, 7}});
        int[] parent = new int[8];
        int[] dist = bfs(adj, 0, parent);
        System.out.println(Arrays.toString(dist));
        System.out.println(path(parent, 4) + " " + path(parent, 5));
        List<Integer> unreachable = new ArrayList<>();
        for (int v = 0; v < 8; v++) if (dist[v] == -1) unreachable.add(v);
        System.out.println(unreachable);
    }
}
