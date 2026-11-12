#!/usr/bin/env python3
"""Runs every algorithm in code/ in all three languages and checks they print the same thing.

code/<topic>/<name>.py, code/<topic>/<Name>.java (the same name in CamelCase) and code/<topic>/<name>.cpp each end
with a small demo that prints its results. The three outputs must match line for line. Needs python3, javac/java
(17+) and g++ (C++17). Usage: python3 tools/test_code.py [name-filter]
"""
import pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent / "code"
flt = sys.argv[1] if len(sys.argv) > 1 else ""


def camel(stem):
    return "".join(p.capitalize() for p in stem.split("_"))


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, **kw)
    if r.returncode != 0:
        raise RuntimeError(" ".join(map(str, cmd)) + "\n" + r.stdout + r.stderr)
    return r.stdout


bad = 0
count = 0
for py in sorted(ROOT.rglob("*.py")):
    if flt not in py.stem:
        continue
    if "guides" in py.relative_to(ROOT).parts:      # code shown in a guide (one language, tested on its own)
        continue
    count += 1
    java = py.with_name(camel(py.stem) + ".java")
    cpp = py.with_suffix(".cpp")
    try:
        out = {"python": run([sys.executable, str(py)])}
        with tempfile.TemporaryDirectory() as tmp:
            if not java.exists() or not cpp.exists():
                raise RuntimeError("missing " + (java.name if not java.exists() else cpp.name))
            run(["javac", "-d", tmp, str(java)])
            out["java"] = run(["java", "-cp", tmp, java.stem])
            exe = pathlib.Path(tmp) / "a.out"
            run(["g++", "-std=c++17", "-O2", "-Wall", "-Wextra", "-Werror", "-o", str(exe), str(cpp)])
            out["c++"] = run([str(exe)])
        if not (out["python"] == out["java"] == out["c++"]):
            bad += 1
            print(f"DIFFERENT {py.relative_to(ROOT)}")
            for k, v in out.items():
                print(f"--- {k}\n{v}")
        else:
            print(f"ok  {py.relative_to(ROOT)}  ({len(out['python'].splitlines())} lines)")
    except Exception as e:  # noqa: BLE001
        bad += 1
        print(f"FAIL {py.relative_to(ROOT)}\n{e}")
print(f"{count - bad} of {count} programs agree in Python, Java and C++")
sys.exit(1 if bad else 0)
