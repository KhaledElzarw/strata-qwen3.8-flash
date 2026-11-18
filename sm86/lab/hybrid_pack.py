"""A pack whose routed experts come from two quant tiers of the same model, layer by layer.

    python hybrid_pack.py --base ../../packs/iq3_xxs --donor ../../packs/iq3_s --donor-shard NAME.gguf \
        --layers 0-5,30 --out ../../packs/hyb_a

Copies the base pack (dense.bin is hard-linked) and rewrites native_experts.txt: the listed layers take the donor
pack's line (types, blob size and GGUF offsets) with the donor's shard named in the last column; the arena offsets
and the total are recomputed.  The engine looks for a named shard beside the --native file, so the donor's shard 1
must be there (a hard link is enough).  Prints the bytes each chosen layer adds.
"""
import argparse
import os
import re
import shutil
from pathlib import Path

N_EXPERT = 512


def read(pack):
    lines = (Path(pack) / "native_experts.txt").read_text(encoding="utf-8").splitlines()
    rows = {}
    for ln in lines[1:]:
        f = ln.split()
        if len(f) >= 8:
            rows[int(f[0])] = f
    return lines[0], rows


def layer_set(spec):
    out = set()
    for part in filter(None, spec.split(",")):
        a, _, b = part.partition("-")
        out.update(range(int(a), int(b or a) + 1))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--donor", required=True)
    ap.add_argument("--donor-shard", required=True, help="file name of the donor's shard 1, as it sits beside the --native file")
    ap.add_argument("--layers", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    head, base = read(a.base)
    _, donor = read(a.donor)
    pick = layer_set(a.layers)
    out = Path(a.out)
    if out.resolve() in (Path(a.base).resolve(), Path(a.donor).resolve()):
        raise SystemExit("--out must not be the base or the donor pack")
    out.mkdir(parents=True, exist_ok=True)
    for p in Path(a.base).iterdir():
        dst = out / p.name
        if p.name == "native_experts.txt":
            continue
        if dst.exists():
            shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
        if p.is_dir():
            shutil.copytree(p, dst)
        elif p.name == "dense.bin":
            os.link(p, dst)
        else:
            shutil.copy2(p, dst)
    rows, off, added = [], 0, 0
    for layer in sorted(base):
        if layer in pick:
            if len(donor[layer]) > 8:
                raise SystemExit(f"layer {layer}: the donor pack names its own shard(s) for this layer; not supported")
            f = list(donor[layer]) + [a.donor_shard]
            added += N_EXPERT * (int(f[4]) - int(base[layer][4]))
        else:
            f = list(base[layer])                     # a base row keeps its own shard column, if it has one
        blob = int(f[4])
        f[3] = str(off)
        rows.append(" ".join(f))
        off += N_EXPERT * blob
    head = re.sub(r"total \d+", f"total {off}", head)
    (out / "native_experts.txt").write_text("\n".join([head, *rows]) + "\n", encoding="utf-8", newline="\n")
    print(f"{out}: layers {sorted(pick)} from the donor, +{added / 1e9:.3f} GB of experts (total {off / 1e9:.2f} GB)")


if __name__ == "__main__":
    main()
