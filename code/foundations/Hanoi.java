import java.util.ArrayList;
import java.util.List;

public class Hanoi {
    record Move(int disc, char from, char to) {}

    /** Moves n discs from source to target, never putting a disc on a smaller one. */
    static void hanoi(int n, char source, char target, char spare, List<Move> moves) {
        if (n == 0) return;                           // base case: nothing to move
        hanoi(n - 1, source, spare, target, moves);   // 1. move the n-1 smaller discs out of the way
        moves.add(new Move(n, source, target));       // 2. move the biggest disc
        hanoi(n - 1, spare, target, source, moves);   // 3. move the n-1 smaller discs on top of it
    }

    /** n! = n * (n-1)!, with 0! = 1. */
    static long factorial(int n) { return n == 0 ? 1 : n * factorial(n - 1); }

    public static void main(String[] args) {
        List<Move> moves = new ArrayList<>();
        hanoi(3, 'A', 'C', 'B', moves);
        for (Move m : moves) System.out.println("disc " + m.disc() + ": " + m.from() + " -> " + m.to());
        for (int n : new int[]{1, 2, 3, 10, 20}) {
            List<Move> m = new ArrayList<>();
            hanoi(n, 'A', 'C', 'B', m);
            System.out.println(n + " discs: " + m.size() + " moves");
        }
        System.out.println(factorial(10));
    }
}
