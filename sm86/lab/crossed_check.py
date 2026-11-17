"""The crossed token-forcing check: does a change to the decode path change the TEXT, apart from each engine's small
preference for text it produced itself?

    python crossed_check.py --base-scorer B_on_baseA.tsv B_on_baseB.tsv B_on_candA.tsv B_on_candB.tsv \
                            --cand-scorer C_on_baseA.tsv C_on_baseB.tsv C_on_candA.tsv C_on_candB.tsv [--json OUT]

Each file is a tools/force_check.py `score` of one generated set (two sets of the base engine's text, two of the
candidate's) by one scorer (the base engine, then the candidate engine).  A scorer verifies with its own draft
windows, so it favours its own text by a fraction of a point; averaging the text effect over both scorers cancels
that.  Text effect = mean over scorers of (mismatch rate on the candidate's text - on the base's text), in points,
bootstrapped over the requests (4000 resamples, 90% two-sided).  Same thresholds as force_check's rate rule:
PASS when the upper bound is at most 0.5 points, REJECT when the lower bound is above 0.5, else INCONCLUSIVE.
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import force_check as fc  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-scorer", nargs=4, required=True, metavar="TSV")
    ap.add_argument("--cand-scorer", nargs=4, required=True, metavar="TSV")
    ap.add_argument("--json")
    a = ap.parse_args()
    arms = {"base": [fc.load_arm(t) for t in a.base_scorer], "cand": [fc.load_arm(t) for t in a.cand_scorer]}
    every = arms["base"] + arms["cand"]
    ids = [i for i in every[0] if all(i in s for s in every)]

    def counts(arm):
        return [(len(arm[i]), sum(1 for r in arm[i] if r[0])) for i in ids]

    c = {k: [counts(x) for x in v] for k, v in arms.items()}

    def rate(cs, pick):          # the mean of the arms' rates, as pooled_check does
        return sum(100.0 * sum(x[j][1] for j in pick) / max(1, sum(x[j][0] for j in pick)) for x in cs) / len(cs)

    def effects(pick):
        bb, bc = rate(c["base"][:2], pick), rate(c["base"][2:], pick)     # base scorer: base text, candidate text
        cb, cc = rate(c["cand"][:2], pick), rate(c["cand"][2:], pick)     # candidate scorer
        text = ((bc - bb) + (cc - cb)) / 2
        own = ((bb - bc) + (cc - cb)) / 2 * -1                            # how much a scorer favours its own text
        return bb, bc, cb, cc, text, own

    allj = list(range(len(ids)))
    bb, bc, cb, cc, text, own = effects(allj)
    rng, ts, os_ = random.Random(1), [], []
    for _ in range(4000):
        pick = [rng.randrange(len(ids)) for _ in ids]
        e = effects(pick)
        ts.append(e[4])
        os_.append(e[5])
    ts.sort()
    os_.sort()
    lo, hi = ts[200], ts[3799]
    verdict = "PASS" if hi <= 0.5 else "REJECT" if lo > 0.5 else "INCONCLUSIVE"
    out = {"requests": len(ids),
           "rates_pct": {"base scorer / base text": round(bb, 3), "base scorer / candidate text": round(bc, 3),
                         "candidate scorer / base text": round(cb, 3), "candidate scorer / candidate text": round(cc, 3)},
           "text_effect_pts": round(text, 3), "text_effect_ci90": [round(lo, 3), round(hi, 3)],
           "own_path_effect_pts": round(own, 3), "own_path_effect_ci90": [round(os_[200], 3), round(os_[3799], 3)],
           "rate_rule_text_effect": verdict}
    print(json.dumps(out, indent=1))
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return {"PASS": 0, "REJECT": 1, "INCONCLUSIVE": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
