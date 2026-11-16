"""Run one force_check step behind guards (written by fc_step0.sh).

  python guard.py --expect 9504 --log OUT.engine.log --label NAME -- python force_check.py gen|score ...

Before the engine: no strata.exe running, nothing listening on 19100, no runs/THERMAL_STOP, then replay.py's GPU gate
(no other program >= 5% of the SMs for 30 s, at most 30 min; still busy after that = abort).
While it runs: when the engine log prints its expert-cache slot count and the "token graph hit path: N resident experts"
line, N must equal --expect, else the step's process tree is killed (exit 3).  A finished run without those lines is exit 4.
"""
import argparse
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

LAB = Path(sys.argv[sys.argv.index("--lab") + 1]) if "--lab" in sys.argv else Path(r"C:\src\Strata\sm86\lab")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect", type=int, required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--lab")
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd

    tl = subprocess.run(["tasklist", "/FI", "IMAGENAME eq strata.exe"], capture_output=True, text=True).stdout
    if "strata.exe" in tl:
        print(f"GUARD {a.label}: a strata.exe is already running (the A/B?): not starting a second engine", flush=True)
        return 5
    with socket.socket() as s:
        s.settimeout(1)
        if s.connect_ex(("127.0.0.1", 19100)) == 0:
            print(f"GUARD {a.label}: something listens on 19100: not starting", flush=True)
            return 5
    if (LAB / "runs" / "THERMAL_STOP").exists():
        print(f"GUARD {a.label}: runs/THERMAL_STOP present: aborting", flush=True)
        return 5
    sys.path.insert(0, str(LAB))
    import replay  # noqa: E402
    waited = replay.wait_gpu_free(5, 1800.0, a.label)
    busy = sorted({n for n, sm in replay.gpu_others() if sm >= 5})
    if busy:
        print(f"GUARD {a.label}: GPU still busy after {waited:.0f} s ({', '.join(busy)}): aborting", flush=True)
        return 5
    print(f"GUARD {a.label}: GPU idle after {waited:.0f} s, starting", flush=True)

    p = subprocess.Popen(cmd)
    seen = {"slots": None, "graph": None}
    pat = {"slots": re.compile(r"expert cache (\d+) slots"), "graph": re.compile(r"token graph hit path: (\d+) resident experts")}
    bad = None
    while p.poll() is None and bad is None:
        time.sleep(2)
        try:
            text = Path(a.log).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for k, rx in pat.items():
            m = rx.search(text)
            if m:
                seen[k] = int(m.group(1))
                if seen[k] != a.expect:
                    bad = f"{k} = {seen[k]}, expected {a.expect}"
    if bad:
        subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
        p.wait()
        print(f"GUARD {a.label}: ABORT, engine {bad} (is VRAM free? is another program on the GPU?). "
              f"Step killed; log {a.log}", flush=True)
        return 3
    rc = p.wait()
    try:
        text = Path(a.log).read_text(encoding="utf-8", errors="replace")
        for k, rx in pat.items():
            m = rx.search(text)
            seen[k] = int(m.group(1)) if m else None
    except OSError:
        pass
    if rc == 0 and (seen["slots"] != a.expect or seen["graph"] != a.expect):
        print(f"GUARD {a.label}: slot lines missing or wrong after the run: {seen} (expected {a.expect})", flush=True)
        return 4
    print(f"GUARD {a.label}: exit {rc}, slots {seen['slots']}, resident {seen['graph']}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
