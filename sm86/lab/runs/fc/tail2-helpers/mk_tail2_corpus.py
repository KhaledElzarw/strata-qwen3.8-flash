"""Convert the recorded real agent turns (runs/replayset/hermes-v1, the A/B's 57 requests) into a force_check corpus.

force_check's corpus format is one JSON object per line: {"id", "kind", "ids": [prompt token ids], "split": "held"}.
The engine's stdin mode takes `GEN n id,id,...` (force_check.py Engine.gen), so a chat request only has to become the
token ids the server would have fed the engine.  This script does that with the server's own pieces (serve/frontend.py
openai_to_messages, mark_think_literals, ChatTemplate.render; tools/strata_tokenizer.py), CPU only, no engine.

Check built in: the token count of every request is compared with `usage.prompt_tokens` that the A/B replay recorded for
the same file (runs/replay/base1-base-r0.jsonl).  --strict makes any difference an error.

  python -I mk_tail2_corpus.py OUT.jsonl [--src DIR] [--replay JSONL] [--max-prompt 12000] [--strict]
"""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True          # never write __pycache__ under the repo
REPO = Path(r"C:\src\Strata")
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--src", default=str(REPO / "sm86/lab/runs/replayset/hermes-v1"))
    ap.add_argument("--replay", default=str(REPO / "sm86/lab/runs/replay/base1-base-r0.jsonl"))
    ap.add_argument("--tokenizer", default=str(REPO / "packs/iq3_xxs/tokenizer"))
    ap.add_argument("--limit", type=int, default=57, help="the A/B's limit (ab.py/replay.py: sorted(*.json)[:limit])")
    ap.add_argument("--max-prompt", type=int, default=0, help="drop requests with more prompt tokens than this (0: keep all)")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit("%s exists: not overwriting" % out)

    import strata_tokenizer as ST
    from serve.frontend import ChatTemplate, literal_tags, mark_think_literals, openai_to_messages
    from serve.structured import prepare_format

    tp = Path(a.tokenizer)
    vocab = json.loads((tp / "vocab.json").read_text(encoding="utf-8"))
    toks = [None] * len(vocab)
    for t, i in vocab.items():
        toks[i] = t
    merges = (tp / "merges.txt").read_text(encoding="utf-8").split("\n")
    types = json.loads((tp / "token_type.json").read_text())
    try:
        tcfg = json.loads((tp / "tokenizer.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        tcfg = {}
    tok = ST.Tokenizer(toks, merges, types, tcfg.get("pre") or "qwen35", tcfg.get("special_ids") or None)
    tmpl = ChatTemplate(tp / "chat_template.jinja")
    literals = literal_tags(getattr(tok, "control_tokens", ()))

    recorded = {}
    if Path(a.replay).exists():
        for line in open(a.replay, encoding="utf-8"):
            r = json.loads(line)
            if r.get("usage"):
                recorded[r["file"]] = r["usage"]["prompt_tokens"]

    if a.strict and not recorded:
        raise SystemExit("--strict needs the recorded run %s (usage.prompt_tokens per file)" % a.replay)
    files = sorted(Path(a.src).glob("*.json"))[: a.limit or None]
    rows, diffs = [], 0
    for p in files:
        req = json.loads(p.read_text(encoding="utf-8"))
        messages, tools, kw = openai_to_messages(req)
        messages, validator = prepare_format(req.get("response_format"), messages)
        marked, marked_tools, changed = mark_think_literals(messages, tools, literals)
        text = tmpl.render(marked, tools=marked_tools, **kw)
        if changed:
            from serve.frontend import unmark_think_literals
            text, plain = unmark_think_literals(text, literals)
            ids = tok.encode(text, parse_special=True, plain=plain)
        else:
            ids = tok.encode(text, parse_special=True)
        rec = recorded.get(p.name)
        mark = "" if rec is None else ("ok" if rec == len(ids) else "DIFF(recorded %d)" % rec)
        if rec is not None and rec != len(ids):
            diffs += 1
        print("%s: %d tokens %s" % (p.name, len(ids), mark))
        if a.max_prompt and len(ids) > a.max_prompt:
            continue
        rows.append({"id": "turn-" + p.stem, "kind": "agentturn", "ids": ids, "split": "held"})
    if diffs and a.strict:
        raise SystemExit("%d token counts differ from the recorded usage.prompt_tokens" % diffs)
    with open(out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print("wrote %d rows (%d tokens total), %d count differences vs the recorded run" % (len(rows), sum(len(r["ids"]) for r in rows), diffs))


if __name__ == "__main__":
    main()
