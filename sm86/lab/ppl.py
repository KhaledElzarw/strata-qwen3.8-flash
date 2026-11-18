"""Reference-free quality numbers from tools/quant_quality.py runs: perplexity and next-token accuracy on the fixed
text set, and the paired difference between two runs.

    python ppl.py BASE.tsv [CAND.tsv ...]

Each RUN.tsv row is one text position: pos, target id, logp(target), argmax id, logp(argmax), argmax==target, ...
(the engine's STRATA_LOGPOS format; RUN.tsv.seg.json holds the segments' line ranges).  Perplexity = exp(-mean
logp(target)): how surprised the model is by real text, lower is better.  Accuracy = the share of positions where
the model's most likely token is the text's token.  Against the first file, every other file gets the paired
difference in mean log-probability per position with a 95% interval from a block bootstrap (blocks of 100
consecutive positions, since neighbouring positions are correlated; positive = the candidate predicts the text
better), overall and per segment.
"""
import json
import math
import random
import sys
from pathlib import Path


def load(path):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        f = line.split("\t")
        if len(f) >= 6:
            rows.append((int(f[1]), float(f[2]), int(f[5])))
    segs = json.loads(Path(str(path) + ".seg.json").read_text(encoding="utf-8"))["segments"]
    return rows, segs


def summary(rows):
    lp = [r[1] for r in rows]
    return math.exp(-sum(lp) / len(lp)), sum(r[2] for r in rows) / len(rows)


BLOCK = 100   # positions per bootstrap block: neighbouring positions of a text are correlated, single ones are not independent


def paired(a, b, rng):
    """Mean paired difference and a 95% interval from a block bootstrap (blocks of BLOCK consecutive positions)."""
    d = [y[1] - x[1] for x, y in zip(a, b)]
    n = len(d)
    mean = sum(d) / n
    blocks = [d[i:i + BLOCK] for i in range(0, n, BLOCK)]
    boots = []
    for _ in range(2000):
        s = c = 0
        for _ in blocks:
            blk = rng.choice(blocks)
            s += sum(blk)
            c += len(blk)
        boots.append(s / c)
    boots.sort()
    return mean, boots[49], boots[1949]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base, segs = load(sys.argv[1])
    ppl, acc = summary(base)
    print(f"{sys.argv[1]}: {len(base)} positions, perplexity {ppl:.4f}, next-token accuracy {acc:.2%}")
    for s in segs:
        p, a = summary(base[s["first_line"]:s["end_line"]])
        print(f"    {s['name']:13s} perplexity {p:8.4f}  accuracy {a:.2%}")
    rng = random.Random(7)
    for path in sys.argv[2:]:
        cand, _ = load(path)
        if len(cand) != len(base) or any(x[0] != y[0] for x, y in zip(base, cand)):
            print(f"{path}: different positions or targets than the base: not comparable")
            continue
        ppl2, acc2 = summary(cand)
        m, lo, hi = paired(base, cand, rng)
        same = sum(1 for x, y in zip(base, cand) if x[1] == y[1])
        print(f"{path}: perplexity {ppl2:.4f} ({100 * (ppl2 / ppl - 1):+.2f}%), accuracy {acc2:.2%} ({100 * (acc2 - acc):+.2f} points); "
              f"mean log-prob {m:+.5f} [{lo:+.5f}, {hi:+.5f}]; {same} of {len(base)} positions identical")
        for s in segs:
            x, y = base[s["first_line"]:s["end_line"]], cand[s["first_line"]:s["end_line"]]
            m, lo, hi = paired(x, y, rng)
            print(f"    {s['name']:13s} {m:+.5f} [{lo:+.5f}, {hi:+.5f}]  accuracy {100 * (summary(y)[1] - summary(x)[1]):+.2f} points")


if __name__ == "__main__":
    main()
