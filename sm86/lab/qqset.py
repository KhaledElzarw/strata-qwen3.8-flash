"""A larger text set for the perplexity guard (tools/quant_quality.py run --ids FILE): N segments of 1,000 tokens
cut from this repository's own tracked files (code, lab notes, docs, configs, diffs).

    python qqset.py --tokenizer ../../packs/iq3_xxs/tokenizer --out runs/qq/set2.ids.json [--segments 60]

The shipped set (data/quant_quality/v1) has 5 x 1,000 tokens: its paired interval is about +-0.013 in mean
log-probability, wider than the difference between two neighbouring quant tiers.  60 segments bring it to about
+-0.004.  The files are picked with a fixed seed, so the set is reproducible from a checkout.
"""
import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
REPO = LAB.parents[1]
sys.path.insert(0, str(REPO / "tools"))
import strata_tokenizer as ST  # noqa: E402

GROUPS = [  # (name, extensions, path prefixes, share of the segments)
    ("cuda", (".cu", ".cuh"), ("src/",), 0.20),
    ("cpp", (".cpp", ".hpp", ".h"), ("src/", "include/"), 0.20),
    ("python", (".py",), ("tools/", "serve/", "strata_control/", "sm86/lab/"), 0.25),
    ("docs", (".md",), ("docs/", "sm86/"), 0.20),
    ("config", (".json", ".toml", ".yml", ".sh", ".ps1", ".cmake"), ("",), 0.15),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--segments", type=int, default=60)
    ap.add_argument("--seg-tokens", type=int, default=1000)
    a = ap.parse_args()
    tp = Path(a.tokenizer)
    vocab = json.loads((tp / "vocab.json").read_text(encoding="utf-8"))
    toks = [None] * len(vocab)
    for t, i in vocab.items():
        toks[i] = t
    tok = ST.Tokenizer(toks, (tp / "merges.txt").read_text(encoding="utf-8").split("\n"), json.loads((tp / "token_type.json").read_text()))
    files = subprocess.run(["git", "-C", str(REPO), "ls-files"], capture_output=True, text=True, encoding="utf-8").stdout.split("\n")
    files = [f for f in files if "third_party/" not in f and "/runs/" not in f and "/tasks" not in f and not f.startswith("README.")]
    rng = random.Random(20261117)
    segs = []
    for name, exts, prefixes, share in GROUPS:
        want = round(a.segments * share)
        pool = [f for f in files if f.endswith(exts) and f.startswith(prefixes)]
        rng.shuffle(pool)
        got = 0
        for f in pool:
            if got >= want:
                break
            try:
                text = (REPO / f).read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if len(text) < 12000 or sum(1 for c in text[:20000] if ord(c) > 127) > 200:
                continue
            start = rng.randrange(0, max(1, len(text) - 11000))
            start = text.find("\n", start) + 1                     # begin on a line
            ids = tok.encode(text[start:start + 12000])
            if len(ids) < a.seg_tokens:
                continue
            segs.append({"name": f"{name}{got:02d}", "file": f, "ids": ids[:a.seg_tokens]})
            got += 1
        print(f"{name}: {got} segments")
    Path(a.out).write_text(json.dumps({"version": "sm86-set2", "seg_tokens": a.seg_tokens, "vocab_size": len(toks), "segments": segs}))
    print(f"wrote {a.out}: {len(segs)} segments, {sum(len(s['ids']) for s in segs)} tokens")


if __name__ == "__main__":
    main()
