"""Chapter 1: a Turing machine simulator, and a machine that adds 1 in binary.

A machine is a table: (state, symbol read) -> (symbol to write, move, next state).
The tape is a dict from position to symbol; blank cells hold '_'.
"""


def run(table, tape_text, state="right", head=0, halt="done", max_steps=1000, show=True):
    tape = {i: ch for i, ch in enumerate(tape_text)}
    steps = 0
    while state != halt:
        if steps >= max_steps:
            raise RuntimeError("no halt within max_steps")
        sym = tape.get(head, "_")
        if show:
            lo, hi = min(min(tape), head), max(max(tape), head)
            cells = "".join(f"[{tape.get(i, '_')}]" if i == head else tape.get(i, "_")
                            for i in range(lo, hi + 1))
            print(f"  step {steps:>2}  state {state:<6} tape {cells}")
        write, move, state = table[(state, sym)]
        tape[head] = write
        head += 1 if move == "R" else -1
        steps += 1
    lo, hi = min(tape), max(tape)
    return "".join(tape.get(i, "_") for i in range(lo, hi + 1)).strip("_"), steps


# Binary increment: walk right to the end of the number, then add 1 from the right.
INCREMENT = {
    ("right", "0"): ("0", "R", "right"),
    ("right", "1"): ("1", "R", "right"),
    ("right", "_"): ("_", "L", "carry"),
    ("carry", "1"): ("0", "L", "carry"),   # 1 + carry = 0, carry on
    ("carry", "0"): ("1", "L", "done"),    # 0 + carry = 1, finished
    ("carry", "_"): ("1", "L", "done"),    # ran off the left end: new digit
}

if __name__ == "__main__":
    print("Incrementing 1011 (eleven):")
    result, steps = run(INCREMENT, "1011")
    print(f"  result {result} after {steps} steps")
    print()
    for word in ["0", "1", "111", "1001", "11111111"]:
        result, steps = run(INCREMENT, word, show=False)
        assert int(result, 2) == int(word, 2) + 1
        print(f"  {word:>9} + 1 = {result:>9}   ({steps} steps)")
