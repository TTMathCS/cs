public class BinarySearch {
    /** Returns an index of target in the sorted array a, or -1 if it is not there. */
    static int binarySearch(int[] a, int target) {
        int lo = 0, hi = a.length - 1;                // the target, if present, is in a[lo..hi]
        while (lo <= hi) {
            int mid = lo + (hi - lo) / 2;             // not (lo + hi) / 2, which can overflow
            if (a[mid] == target) return mid;
            if (a[mid] < target) lo = mid + 1;        // everything up to mid is too small
            else hi = mid - 1;                        // everything from mid on is too big
        }
        return -1;
    }

    /** Returns the first index i with a[i] >= target (a.length if there is none). */
    static int lowerBound(int[] a, int target) {
        int lo = 0, hi = a.length;                    // the answer is in [lo, hi]
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (a[mid] < target) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    public static void main(String[] args) {
        int[] a = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};
        System.out.println(binarySearch(a, 23) + " " + binarySearch(a, 2) + " " + binarySearch(a, 91) + " " + binarySearch(a, 7));
        int[] b = {1, 3, 3, 3, 7, 9};
        System.out.println(lowerBound(b, 3) + " " + lowerBound(b, 4) + " " + lowerBound(b, 0) + " " + lowerBound(b, 10));
        System.out.println(lowerBound(b, 4) - lowerBound(b, 3));   // how many 3s
    }
}
