import java.util.HashMap;
import java.util.Map;

public class SlidingWindow {
    /** The largest sum of k consecutive values of a. */
    static int maxSumWindow(int[] a, int k) {
        int window = 0;
        for (int i = 0; i < k; i++) window += a[i];
        int best = window;
        for (int i = k; i < a.length; i++) {
            window += a[i] - a[i - k];                // slide right: add the new value, drop the old one
            best = Math.max(best, window);
        }
        return best;
    }

    /** The length of the longest stretch of s with no repeated character. */
    static int longestUnique(String s) {
        Map<Character, Integer> last = new HashMap<>();   // where each character was last seen
        int left = 0, best = 0;                       // the window is s[left..right]
        for (int right = 0; right < s.length(); right++) {
            char ch = s.charAt(right);
            Integer seen = last.get(ch);
            if (seen != null && seen >= left) left = seen + 1;   // repeat inside the window: shrink past it
            last.put(ch, right);
            best = Math.max(best, right - left + 1);
        }
        return best;
    }

    /** The length of the shortest stretch of positive values with sum >= target (0 if none). */
    static int shortestWithSum(int[] a, int target) {
        int left = 0, total = 0, best = a.length + 1;
        for (int right = 0; right < a.length; right++) {
            total += a[right];                        // grow on the right ...
            while (total >= target) {                 // ... and shrink from the left while it still works
                best = Math.min(best, right - left + 1);
                total -= a[left++];
            }
        }
        return best > a.length ? 0 : best;
    }

    public static void main(String[] args) {
        System.out.println(maxSumWindow(new int[]{2, 1, 5, 1, 3, 2}, 3));
        System.out.println(longestUnique("abcabcbb") + " " + longestUnique("bbbbb") + " " + longestUnique("pwwkew") + " " + longestUnique(""));
        System.out.println(shortestWithSum(new int[]{2, 3, 1, 2, 4, 3}, 7) + " " + shortestWithSum(new int[]{1, 1, 1}, 5));
    }
}
