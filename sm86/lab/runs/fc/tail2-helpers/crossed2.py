"""Crossed text effect of one setting over SEVERAL request groups pooled (extends step0-helpers/crossed.py).

Same arithmetic and rule as crossed.py (= runs/fc/check3-crossed.json): every text set is scored by BOTH scorers (S0 = the
reference scorer, S1 = the default scorer); text effect = (default text - reference text) averaged over the two scorers;
bootstrap over requests (4000 resamples, seed 1, 90% two-sided = the rule's one-sided 95% bounds); PASS if the upper bound
<= 0.5 points, REJECT if the lower bound > 0.5, else INCONCLUSIVE.  own_path_effect = the scorer's bias, as in crossed.py.

  python crossed2.py --ref R1 R2 --cand C1 C2 --ref-x X1 X2 --cand-x Y1 Y2 [--json out] [--by-group out]

Each TSV argument is one arm.  To pool groups, join the same arm's TSVs of the groups with '+':
  --ref "step0-score-offT-offTA.tsv+tail2-score-offT-offTA.tsv" "step0-...-offTB.tsv+tail2-...-offTB.tsv" ...
Request ids must differ between groups (they do: corpus2 ids are kind-length, tail2 ids are turn-*); a clash is an error.
Arm k of every group is merged into pooled arm k (the arms of one side are exchangeable repeats of the same text recipe).
--by-group FILE also writes the effect and CI of each group alone (same bootstrap), so the pooled number can be read next to them.
Exit code: 0 PASS, 1 REJECT, 2 INCONCLUSIVE (of the pooled result).
"""
import argparse
import json
import random
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\src\Strata\tools")
import force_check as fc  # noqa: E402


def load_group_arm(spec):
    """'a.tsv+b.tsv' -> ({request id: rows} merged, [ids of each part])"""
    merged, parts = {}, []
    for t in spec.split("+"):
        arm = fc.load_arm(t)
        clash = set(arm) & set(merged)
        if clash:
            raise SystemExit("request ids appear in two groups: %s" % sorted(clash)[:5])
        merged.update(arm)
        parts.append(list(arm))
    return merged, parts


def analyse(arms, ids, boots=4000):
    """arms: {'ref','cand','ref-x','cand-x'} -> list of arm dicts; ids: the requests used"""
    cnt = {k: [[(len(x[i]), sum(1 for r in x[i] if r[0])) for i in ids] for x in v] for k, v in arms.items()}

    def rate(k, pick):
        rs = [100.0 * sum(c[j][1] for j in pick) / max(1, sum(c[j][0] for j in pick)) for c in cnt[k]]
        return sum(rs) / len(rs)

    def stats(pick):
        r = {k: rate(k, pick) for k in cnt}
        text = ((r["cand"] - r["ref"]) + (r["cand-x"] - r["ref-x"])) / 2
        own = ((r["cand"] + r["ref-x"]) / 2) - ((r["ref"] + r["cand-x"]) / 2)   # other path - own path
        return r, text, own

    r, text, own = stats(list(range(len(ids))))
    rng, ts, os_ = random.Random(1), [], []
    for _ in range(boots):
        pick = [rng.randrange(len(ids)) for _ in ids]
        _, t, o = stats(pick)
        ts.append(t)
        os_.append(o)
    ts.sort()
    os_.sort()
    lo, hi = ts[int(0.05 * boots)], ts[int(0.95 * boots) - 1]      # = [200], [3799] at 4000
    tokens = {k: [sum(c[0] for c in a) for a in v] for k, v in cnt.items()}
    return {"requests": len(ids), "tokens_per_arm": {k: v for k, v in tokens.items()},
            "rates_pct": {"S0 scorer / reference text": round(r["ref"], 3), "S0 scorer / default text": round(r["cand"], 3),
                          "S1 scorer / reference text": round(r["ref-x"], 3), "S1 scorer / default text": round(r["cand-x"], 3)},
            "text_effect_pts": round(text, 3), "text_effect_ci90": [round(lo, 3), round(hi, 3)],
            "ci90_width": round(hi - lo, 3),
            "own_path_effect_pts": round(own, 3), "own_path_effect_ci90": [round(os_[int(0.05 * boots)], 3), round(os_[int(0.95 * boots) - 1], 3)],
            "rate_rule_text_effect": "REJECT" if lo > 0.5 else ("PASS" if hi <= 0.5 else "INCONCLUSIVE")}


def main():
    ap = argparse.ArgumentParser()
    for k in ("ref", "cand", "ref-x", "cand-x"):
        ap.add_argument("--" + k, nargs="+", required=True)
    ap.add_argument("--json")
    ap.add_argument("--by-group")
    a = ap.parse_args()
    arms, groups = {}, {}
    for k in ("ref", "cand", "ref-x", "cand-x"):
        loaded = [load_group_arm(s) for s in getattr(a, k.replace("-", "_"))]
        arms[k] = [m for m, _ in loaded]
        groups[k] = [p for _, p in loaded]
    ngroups = len(groups["cand"][0])
    if any(len(p) != ngroups for v in groups.values() for p in v):
        raise SystemExit("every arm must name the same number of '+' groups")
    ids = [i for i in arms["cand"][0] if all(i in x for v in arms.values() for x in v)]
    if len(ids) != len(arms["cand"][0]):
        print("warning: %d requests are not in every arm and are left out" % (len(arms["cand"][0]) - len(ids)), file=sys.stderr)
    pooled = analyse(arms, ids)
    pooled["groups"] = ngroups
    print(json.dumps(pooled, indent=1))
    if a.json:
        json.dump(pooled, open(a.json, "w"), indent=1)
    if a.by_group:
        out = {}
        for g in range(ngroups):
            gi = [i for i in groups["cand"][0][g] if i in set(ids)]
            out["group%d" % (g + 1)] = analyse(arms, gi)
        print("--- by group (same bootstrap, each group alone)")
        for k, v in out.items():
            print(k, "requests", v["requests"], "effect", v["text_effect_pts"], "ci90", v["text_effect_ci90"], "width", v["ci90_width"], v["rate_rule_text_effect"])
        json.dump(out, open(a.by_group, "w"), indent=1)
    sys.exit({"PASS": 0, "REJECT": 1, "INCONCLUSIVE": 2}[pooled["rate_rule_text_effect"]])


if __name__ == "__main__":
    main()
