import java.util.ArrayList;
import java.util.List;

public class SubsetsPermutations {
    static List<List<Integer>> out;
    static List<Integer> chosen;

    /** Every subset: for each item, first leave it out, then put it in. */
    static List<List<Integer>> subsets(int[] items) {
        out = new ArrayList<>(); chosen = new ArrayList<>();
        subsetsGo(items, 0);
        return out;
    }

    static void subsetsGo(int[] items, int i) {
        if (i == items.length) { out.add(new ArrayList<>(chosen)); return; }
        subsetsGo(items, i + 1);                      // without items[i]
        chosen.add(items[i]);                         // choose
        subsetsGo(items, i + 1);                      // with items[i]
        chosen.remove(chosen.size() - 1);             // un-choose (the "back" in backtracking)
    }

    /** Every ordering: fill the positions one by one with an item not used yet. */
    static List<List<Integer>> permutations(int[] items) {
        out = new ArrayList<>(); chosen = new ArrayList<>();
        permGo(items, new boolean[items.length]);
        return out;
    }

    static void permGo(int[] items, boolean[] used) {
        if (chosen.size() == items.length) { out.add(new ArrayList<>(chosen)); return; }
        for (int i = 0; i < items.length; i++)
            if (!used[i]) {
                used[i] = true; chosen.add(items[i]);
                permGo(items, used);
                chosen.remove(chosen.size() - 1); used[i] = false;
            }
    }

    /** Every subset (keeping the items' order) that adds up to target; all items positive.
     *  Prunes: stop as soon as the running sum is too big. */
    static List<List<Integer>> subsetSums(int[] items, int target) {
        out = new ArrayList<>(); chosen = new ArrayList<>();
        sumGo(items, target, 0, 0);
        return out;
    }

    static void sumGo(int[] items, int target, int i, int total) {
        if (total == target) { out.add(new ArrayList<>(chosen)); return; }
        if (i == items.length || total > target) return;   // nothing left, or already too much
        chosen.add(items[i]);
        sumGo(items, target, i + 1, total + items[i]);
        chosen.remove(chosen.size() - 1);
        sumGo(items, target, i + 1, total);
    }

    public static void main(String[] args) {
        System.out.println(subsets(new int[]{1, 2, 3}));
        System.out.println(permutations(new int[]{1, 2, 3}));
        System.out.println(subsetSums(new int[]{3, 34, 4, 12, 5, 2}, 9));
    }
}
