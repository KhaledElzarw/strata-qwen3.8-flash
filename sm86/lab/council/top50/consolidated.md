# Qwen engine: council top-10s, validated and deduplicated (2026-11-16)

Members: Codex gpt-6.1-sol xhigh (10), Gemini 3.8 Flash high via Antigravity (9, reply cut off), ChatGPT web GPT-6 max
effort (10; read PR #25 head 8d41c6f08, 55 files), the chair (Claude Opus 5.5, 10, written first), Gemini web 3.1 Pro High (10; read 0 files, Argon
errored first). Hermes (Claude Opus) unavailable: gateway service_disabled. Code checked by a Sonnet read-only pass and the chair.

Baseline: a window takes 18.9 ms and keeps 3.25 tokens = 172 tok/s replay, 151.8 live (live = 0.883 x replay).
Live tok/s for a time saving d: 151.8 x 18.9 / (18.9 - d).

## Caps from the measurements
- The GPU waits on the CPU pool 17.1 us a layer = 0.82 ms a window (Nsight q3_layers). Every CPU-side and
  cache-size item together saves at most this, after which the GPU's own expert work (~88 us a layer) sets the pace.
- HC kernels: 60 us a layer = 2.9 ms a window. Router GEMV 11.5 us, block_topk 6.7, gdn_step_norm 7.3, gdn_ab 5.6.
- Prompt lookup (suffix drafter, on by default) already takes 5-6% of windows at 4.3-4.7 tokens each.
- Effective window cap is already 8 rows (m_spec 8), not --spec 4; DFlash2 always drafts 7.
- Route tail skip rank 7 is on in serve (minimum rank over the window, VRAM-resident experts exempt). Any change to
  window widths or the resident set changes which experts are skipped: not bit-identical, same quality class.

## Valid items, ranked by central gain
| # | Item (sources) | Saves | Live tok/s | Exactness | Effort |
|---|---|---|---|---|---|
| 1 | HC read kernels for short sm_86 windows: DOWN87/UP75 pipelining, occupancy (Codex 1, ChatGPT 4, chair 5) | 0.4-0.9 ms, central 0.6 | 155-159 (157) | exact | 5-12 d |
| 2 | CPU expert step: pool scheduling toward the 55-59 GB/s pinned ceiling, STRATA_IQ512_FUSED_MAX (exists, never run on Zen 5), pre-gating #19 (ChatGPT 2, Codex 3, chair 3, 7) | 0.3-0.8 cap, central 0.5 | 154-159 (156) | exact; fused gate/up rounding | 0.5 d test + 4-9 d |
| 3 | GPU undervolt, owner-applied (Codex 5, Gemini 3, ChatGPT 7, chair 9) | 0.3-0.6, central 0.45 | 154-157 (155) | exact if stable | 0.5 d (owner) |
| 4 | DFlash2 window calibration: STRATA_DF2_GATE=1 with STRATA_DF2_ROW_MS measured on the 3090 (default 3.0 ms from a Mac), conf sweep (Codex 2, ChatGPT 3, Gemini 8, chair 1) | +0-0.2 tokens, central +0.1 | 152-161 (156) | verify-exact; tail-skip set changes | 1-2 d |
| 5 | Dense BF16 projections and the router GEMV toward its floor (4.7-9.2 vs 2.8 us), issue #23 (ChatGPT 6, 10, Codex 9 part) | 0.15-0.4, central 0.25 | 153-155 (154) | exact | 4-10 d |
| 6 | More VRAM expert slots: find the 0.9 GB stall, trim decode-time VRAM, issue #4 (chair 2) | inside item 2's cap | - | not bit-identical (fewer skips) | 2-5 d |
| 7 | DFlash2 Q4 GEMM table for sm_86: df2_q4_auto returns variant 17 everywhere (tuned on sm_120), STRATA_DF2_GEMM4 sweep (Codex 7, Gemini 5 part) | 0.1-0.3, central 0.2 | 153-154 | drafter-only | 1 d |
| 8 | GDN: gdn_ab and the step kernel's 4 barriers a step; conv+L2 and step+norm are already fused (Codex 8, ChatGPT 9, Gemini 4, chair 6) | 0.05-0.25, central 0.12 | 152-154 | rounding unless order kept | 4-10 d |
| 9 | QSA selection bounded by active length (decode graph uses the capacity rule) (Codex 10) | 0.05-0.15, central 0.1 | 152-153 | exact | 3-6 d |
| 10 | Skip the DFlash2 draft on long suffix matches on CUDA (STRATA_DF2_LOOKUP_SKIP is Metal-only), --lookup-chain (ChatGPT 5, Gemini 9) | ~0.1 | ~152.6 | verify-exact; tail-skip set changes | 1-2 d |
| 11 | Retrain/distill the DFlash2 drafter on agent transcripts (ChatGPT 1) | +0.3 tokens claimed, unmeasured | ~164 alone | verify-exact | 12-25 d, high risk |
| 12 | Cost-aware cache placement (Codex 4, chair 8): allocation is already global by profile rank plus adaptive swaps; a learned profile gave no hit-rate gain | 0-0.2, inside item 2's cap | - | not bit-identical | 3-5 d |

Not decode: prefill's fixed ~0.49 s a turn (chair 10, issue #11) shortens turns, not tok/s.

## Rejected, with the evidence
- Router + top-k + doorbell in one kernel (Gemini 2, Codex 9, ChatGPT 10's fusion part): measured 0.05-0.09 ms a
  window, no gaps between the kernels (issue #3, decision 0006).
- Q8_0 dense second VRAM copy (Codex 6): only under STRATA_Q8_PACKED or STRATA_Q8_SM60, both off.
- "512 MB staging ring and 256 MB DFlash2 scratch in VRAM" (Gemini 6): the ring is pinned host RAM; no 256 MB scratch.
- HC 64-bit loads (Gemini 7): the cited kernels already load 128-bit uint4.
- High-priority draft stream, full-vocab draft logits (Gemini 5): streams are already highest priority; logits use the
  pruned drafter vocab.
- Confidence early stop and a 5th draft (Gemini 8): --draft-conf already cuts on the running product; the cap is 8.
- Single-CCD pool pinning (Gemini 1): a pinned 15-thread bench reads 55-59 GB/s and one core 57-58, so cross-CCD
  traffic is not why the pool gets 47 GB/s. --pool-cores can test it in 10 minutes; expect neutral or worse.
- LLC staging from the previous window (ChatGPT 8): #18 data, 20% of bytes covered and 4 wasted bytes per useful one.
- Overlapping drafting with verify (chair 4): the draft needs the verify's accepted state; the GPU is ~98% busy.
- Gemini (Antigravity)'s arithmetic in general: hidden 3584 (really 2560), vocab 152,064 (248,320), 24.5 KB a CPU
  expert (~1.7 MB), 41% hit rate (85-91%), and launch-overhead savings under CUDA graphs.

## Stacked
All valid items 1-10 together, exact or quality-neutral, no new hardware:
- time saved: low 1.45, central 2.3, high 3.5 ms; tokens: +0 / +0.1 / +0.2.
- replay: 3.25/17.45 = 186 / 3.35/16.58 = 202 / 3.45/15.40 = 224 tok/s.
- live: 164 / 178 / 198; about 10% overlap (wider windows raise CPU misses, undervolt scales less GPU time after the
  kernel work) puts the central at ~176-178 live, +16-17%.
- With item 11 (a better drafter) on top: central ~194 live. 200 live needs it, and more.
Cheap-first subset (settings tests plus the owner's undervolt, 1-3 days): items 3, 4, 7, 10 and the fused gate/up
switch: ~0.9 ms and +0.1 tokens = 3.35/18.0 = 186 replay, ~164 live (+8%), each still to be A/B'd.

## Gemini web (3.1 Pro High; Argon errored after 9 minutes)
It could not open the repository (0 files) and worked from the packet's own numbers. Its ten map onto the list above:
better draft model -> 11 (its "2 days, low risk" has no basis: no other drafter exists); HC and dense -> 1, 5 (1.5 ms
is the packet's old range); CPU pool 1.37 ms -> 2 (above the 0.82 ms cap); undervolt 0.69 ms -> 3 (it scales the
CPU's time too); router fusion -> rejected (measured); GDN -> 8; drafter -> 7; cache closer to the stall floor -> 6.
New: INT4 KV cache to free VRAM for experts (LOSSY, needs the owner's OK; KV reads already hit VRAM 98-99%, and the
slots it frees sit inside item 2's cap) and prefill CPU share off (not decode; it is the open quality question,
since GPU-only is the reference path). Its stacked 260-286 tok/s ignores the CPU cap and is not credible.
Totals: 49 proposals (Gemini via Antigravity stopped at 9) -> 12 valid items, 2 not decode or lossy, the rest
duplicates or rejected.
