"""tools/quant_quality.py `run` with ONE of its pinned settings changed, to measure that setting's own effect.

    python ppl_run.py --config CFG.json --ids SET.ids.json --out RUN.tsv --kv int8|fp16|q4_0|k8v4

The yardstick pins FP16 K/V (and CPU experts, no tail skip, no prefill CPU share), so it cannot see what the K/V
precision costs.  This runs the same teacher-forced pass with the K/V format given here and everything else pinned
as before; compare two runs with ppl.py.  Use a long-context set (qqset.py --seg-tokens 16000): K/V precision
matters more the further back attention reads.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import quant_quality as QQ  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--kv", required=True, choices=["int8", "fp16", "q4_0", "k8v4"])
    a = ap.parse_args()
    QQ.FIXED[QQ.FIXED.index("--kv") + 1] = a.kv
    ns = argparse.Namespace(config=a.config, ids=a.ids, out=a.out, env=[], gpu_experts=None, wrap=None, min_free_gb=0)
    return QQ.cmd_run(ns)


if __name__ == "__main__":
    sys.exit(main())
