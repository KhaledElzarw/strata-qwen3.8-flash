"""Crossed text effect of one setting, as in runs/fc/check3-crossed.json: every text set is scored by BOTH scorers
(S0 = the reference scorer, S1 = the default scorer); the text effect is (default text - reference text) averaged over the
two scorers, bootstrapped over the same requests (4000 resamples, 90% two-sided = the rule's one-sided 95% bounds).
own_path_effect = mean mismatch rate of text scored by the other path minus by its own path (the scorer's bias).

  python crossed.py --ref S0A S0B --cand S0A S0B --ref-x S1A S1B --cand-x S1A S1B [--json out]
(--ref/--cand: reference-text / default-text TSVs scored by S0; --ref-x/--cand-x: the same texts scored by S1, same order)
"""
import argparse
import json
import random
import sys

sys.path.insert(0, r"C:\src\Strata\tools")
import force_check as fc  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    for k in ("ref", "cand", "ref-x", "cand-x"):
        ap.add_argument("--" + k, nargs="+", required=True)
    ap.add_argument("--json")
    a = ap.parse_args()
    arms = {k: [fc.load_arm(t) for t in getattr(a, k.replace("-", "_"))] for k in ("ref", "cand", "ref-x", "cand-x")}
    ids = [i for i in arms["cand"][0] if all(i in x for v in arms.values() for x in v)]
    cnt = {k: [[(len(x[i]), sum(1 for r in x[i] if r[0])) for i in ids] for x in v] for k, v in arms.items()}

    def rate(k, pick):
        rs = [100.0 * sum(c[j][1] for j in pick) / max(1, sum(c[j][0] for j in pick)) for c in cnt[k]]
        return sum(rs) / len(rs)

    def stats(pick):
        r = {k: rate(k, pick) for k in cnt}          # ref/cand under S0, ref-x/cand-x under S1
        text = ((r["cand"] - r["ref"]) + (r["cand-x"] - r["ref-x"])) / 2
        own = ((r["cand"] + r["ref-x"]) / 2) - ((r["ref"] + r["cand-x"]) / 2)   # other path - own path
        return r, text, own

    allj = list(range(len(ids)))
    r, text, own = stats(allj)
    rng, ts, os_ = random.Random(1), [], []
    for _ in range(4000):
        pick = [rng.randrange(len(ids)) for _ in ids]
        _, t, o = stats(pick)
        ts.append(t)
        os_.append(o)
    ts.sort()
    os_.sort()
    lo, hi = ts[200], ts[3799]
    out = {"requests": len(ids),
           "rates_pct": {"S0 scorer / reference text": round(r["ref"], 3), "S0 scorer / default text": round(r["cand"], 3),
                         "S1 scorer / reference text": round(r["ref-x"], 3), "S1 scorer / default text": round(r["cand-x"], 3)},
           "text_effect_pts": round(text, 3), "text_effect_ci90": [round(lo, 3), round(hi, 3)],
           "own_path_effect_pts": round(own, 3), "own_path_effect_ci90": [round(os_[200], 3), round(os_[3799], 3)],
           "rate_rule_text_effect": "REJECT" if lo > 0.5 else ("PASS" if hi <= 0.5 else "INCONCLUSIVE")}
    print(json.dumps(out, indent=1))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
    sys.exit({"PASS": 0, "REJECT": 1, "INCONCLUSIVE": 2}[out["rate_rule_text_effect"]])


if __name__ == "__main__":
    main()
