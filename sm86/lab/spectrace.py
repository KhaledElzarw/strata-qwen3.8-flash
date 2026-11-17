"""Per-position draft acceptance from a STRATA_SPEC_TRACE file (serve).

    python spectrace.py TRACE [--vocab draft_vocab.bin] [--json OUT]

The engine writes one line per timed round:
    R p T a sfx ms k match | 7 probs | 7 drafts | k lookup tokens | a+1 committed tokens
(T rows verified = T-1 drafts tested, a drafts accepted, sfx 1 for a prompt-lookup window) and a "# request" line at
the start of each request.  The committed tokens of consecutive rounds are the text the target really wrote, so every
drafted position can be scored, also the ones the confidence cut never sent to the verify: draft i is "right" when
drafts 1..i all equal the target's tokens.  From that this prints, for DFlash2 windows:
  - tested / accepted by position, the chain acceptance (right given the ones before it were right);
  - the same for all 7 drafted positions, tested or not, with the selector's mean probability (calibration);
  - what a cut on the running product of probabilities would keep at each threshold, per round;
  - with --vocab: how many first misses are a target token outside the draft vocabulary.
"""
import argparse
import json
from array import array
from pathlib import Path


def parse(path):
    reqs, cur = [], None
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("#"):
            cur = []
            reqs.append(cur)
            continue
        if not line.startswith("R "):
            continue
        parts = [s.split() for s in line[2:].split("|")]
        if len(parts) != 5 or len(parts[0]) < 5 or len(parts[1]) != 7 or len(parts[2]) != 7:
            continue                                  # a line cut short when the engine was stopped
        head, probs, drafts, look, out = parts
        if cur is None:
            cur = []
            reqs.append(cur)
        cur.append(dict(p=int(head[0]), T=int(head[1]), a=int(head[2]), sfx=int(head[3]), ms=float(head[4]),
                        probs=[float(x) for x in probs], drafts=[int(x) for x in drafts], out=[int(x) for x in out]))
    return [r for r in reqs if r]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("trace")
    ap.add_argument("--vocab", help="draft vocabulary (int32 ids): classify first misses as in or outside it")
    ap.add_argument("--json", help="write the tables here")
    a = ap.parse_args()
    reqs = parse(a.trace)
    vocab = set(array("i", Path(a.vocab).read_bytes())) if a.vocab else None

    rounds = [r for q in reqs for r in q]
    df2 = [r for r in rounds if not r["sfx"]]
    look = [r for r in rounds if r["sfx"]]
    kept = sum(r["a"] + 1 for r in rounds)
    ms = sum(r["ms"] for r in rounds)
    print(f"requests {len(reqs)}, timed rounds {len(rounds)} (lookup {len(look)} = {len(look) / max(1, len(rounds)):.1%}), "
          f"tokens {kept}, {kept / max(1, len(rounds)):.3f} tokens a round, {ms / max(1, len(rounds)):.2f} ms a round, "
          f"{1000 * kept / max(1e-9, ms):.1f} tok/s in timed rounds")
    for name, rs in (("DFlash2", df2), ("lookup", look)):
        if rs:
            print(f"  {name}: {len(rs)} rounds, mean T {sum(r['T'] for r in rs) / len(rs):.2f}, "
                  f"{sum(r['a'] + 1 for r in rs) / len(rs):.3f} tokens a round, {sum(r['ms'] for r in rs) / len(rs):.2f} ms a round, "
                  f"accept {sum(r['a'] for r in rs) / max(1, sum(r['T'] - 1 for r in rs)):.3f}")

    # the target's real text by position, from the committed tokens (position p holds out[0])
    truth = []
    for q in reqs:
        t = {}
        for r in q:
            for i, tok in enumerate(r["out"]):
                t[r["p"] + i] = tok
        truth.append(t)

    tested = [0] * 8; accepted = [0] * 8          # by position 1..7, as verified
    chain_n = [0] * 8; chain_ok = [0] * 8; psum = [0.0] * 8; psum_ok = [0.0] * 8; known = [0] * 8
    miss_out = miss_in = 0
    cuts = [0.0, 0.2, 0.35, 0.5, 0.6, 0.65, 0.7, 0.8, 0.9]
    cut_rows = {c: 0 for c in cuts}; cut_kept = {c: 0 for c in cuts}; cut_n = 0
    for q, t in zip(reqs, truth):
        for r in q:
            if r["sfx"]:
                continue
            for j in range(1, 8):
                if r["T"] - 1 >= j:
                    tested[j] += 1
                    if r["a"] >= j:
                        accepted[j] += 1
            # score every drafted position against the real text
            right = []
            for j in range(1, 8):
                want = t.get(r["p"] + j - 1)
                if want is None:
                    break
                right.append(r["drafts"][j - 1] == want)
            ok = True
            for j, good in enumerate(right, 1):
                known[j] += 1
                if ok:
                    chain_n[j] += 1
                    psum[j] += r["probs"][j - 1]
                    if good:
                        chain_ok[j] += 1
                        psum_ok[j] += r["probs"][j - 1]
                    elif vocab is not None:
                        if t[r["p"] + j - 1] in vocab:
                            miss_in += 1
                        else:
                            miss_out += 1
                ok = ok and good
            if len(right) == 7:
                cut_n += 1
                for c in cuts:
                    prod, n = 1.0, 0
                    for j in range(1, 8):
                        prod *= r["probs"][j - 1]
                        if prod < c:
                            break
                        n += 1
                    good = 0
                    for j in range(n):
                        if not right[j]:
                            break
                        good += 1
                    cut_rows[c] += n + 1
                    cut_kept[c] += good + 1

    print("\nas verified (DFlash2 windows):  position  tested  accepted  rate")
    for j in range(1, 8):
        if tested[j]:
            print(f"  {j}  {tested[j]:6d}  {accepted[j]:6d}  {accepted[j] / tested[j]:.3f}")
    print("\nevery drafted position scored against the real text (right given all earlier drafts right):")
    print("  position  reached  right  chain rate  mean prob  reach share")
    for j in range(1, 8):
        if chain_n[j]:
            print(f"  {j}  {chain_n[j]:6d}  {chain_ok[j]:6d}  {chain_ok[j] / chain_n[j]:.3f}  {psum[j] / chain_n[j]:.3f}  "
                  f"{chain_n[j] / max(1, known[1]):.3f}")
    if vocab is not None and miss_in + miss_out:
        print(f"\nfirst misses: {miss_in + miss_out}; the target's token was outside the draft vocabulary in {miss_out} "
              f"({miss_out / (miss_in + miss_out):.1%})")
    if cut_n:
        print(f"\ncut on the running product, over {cut_n} rounds with 7 scored drafts:  cut  rows a round  tokens a round")
        for c in cuts:
            print(f"  {c:.2f}  {cut_rows[c] / cut_n:.3f}  {cut_kept[c] / cut_n:.3f}")
    if a.json:
        json.dump(dict(rounds=len(rounds), lookup=len(look), tokens=kept, tested=tested, accepted=accepted, chain_n=chain_n,
                       chain_ok=chain_ok, miss_in=miss_in, miss_out=miss_out,
                       cuts={str(c): [cut_rows[c] / max(1, cut_n), cut_kept[c] / max(1, cut_n)] for c in cuts}),
                  open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
