# 0007: Phase B order: the decode HC down, then the prefill expert path (sm86 lab)

Date: 2026-11-17. Status: decided by the chair (Claude Code); reversible (every change is an opt-in switch until a
paired A/B adopts it).

## Problem
Two kernel problems, ranked by decode and prompt time together (the owner: no compromise on quality or prefill speed):
- #6, the hyper-connection (HC) read in decode: ~60 us a layer, 2.9 ms of a ~19 ms window (Nsight, live q3 config),
  against a ~15 us DRAM floor per read. GR_RES and HC_PERSIST lost inside the engine before (0004).
- #11, the fixed cost of a short prompt: 466 ms of a median warm agent turn, of which the batched read's expert path
  is 304 ms, flat from 122 to ~2,000 new tokens because nearly every expert is routed to.

## Evidence gathered before deciding
- Cold prefill on the live config (Nsight, 2026-11-16): 4K: expert MMQ 28.8%, cuBLAS/cutlass GEMM 23.4%, HC 9.6%,
  GDN 7.5%, expert copy into group buffers 6.2%; 32K: GEMM 31.6%, MMQ 21.4%, HC 11.9% (of which write/norm + mix
  1.1 s), GDN 9.2%, attention 8.1%. Coldbench A/A spread <= 1%.
- Decode and prefill share no HC kernel: decode runs fused_gr_read_multi (norm, gr_down87, gr_up75/up_wide); prefill
  runs gr_norm_rs, cuBLAS bf16 GEMMs and gr_mix_r (code appendix, prefill.cpp:4150-4209). One design cannot serve both.
- The prompt "dequant" phase is a byte copy of each routed expert into MMQ group buffers (copy16_group_kernel), also
  for experts resident in VRAM. STRATA_MMQ_DIRECT=1 (pointer-table MMQ, build option STRATA_MMQ_TAB) reads resident
  experts in place: bit-identical on the pinned forced decode once the slot count is matched (--expert-cache 7101
  keeps 9,504 slots; the in-place read adds a 256 B guard per slot).

## Council (design mode, one round; Hermes unavailable: gateway "service_disabled")
- Codex gpt-6.1-sol xhigh (read the checkout and the appendix):
  - #6 decode: give each down CTA four complete output rows (80 CTAs + 1 for the injection) so the partials no longer
    pass through global memory and a last-arrival counter; an 8-column 256-thread up between up_wide and up75.
    Exact if each lane keeps its dot8u sequence and the final warp reduction. 8-20 us a layer (0.38-0.96 ms a window,
    +2-5%), 4-6 days.
  - Prefill HC: a 4-stream write/norm CTA per token and an sm_86 up+mix route: 3-6 ms at 120 new tokens, 100-250 ms
    at a cold 32K (the GEMM part rounding-level), 4-7 days.
  - #11: a count-bucketed, weight-stationary small-row expert path with gate/up + SwiGLU + q8_1 fused: 0-70 ms a
    short turn beyond DIRECT, rounding-level, 10-15 days. First measure per-layer CPU completion, DMA bytes and GPU
    completion: if the host path decides each layer's end, stop.
- Gemini 3.8 Flash (Antigravity; Argon out until 2026-11-21): answered as a defect review instead of proposals; the
  three defects checked against the code were wrong (the HC_PERSIST return, the g_d82_cnt reset, the unused m.inj).
- The chair did not write a proposal before reading the members this round.

## Decision
1. #11 first: measure STRATA_MMQ_DIRECT=1 on the paired real-turn A/B (prompt time first, decode guard). It is exact
   and already built; nothing else on #11 starts before its result and the per-layer CPU/DMA/GPU completion trace
   Codex asked for.
2. #6 next: build Codex's row-owning down kernel behind a new switch, with a bitwise parity bench against gr_down87
   at T = 1..8 and an in-engine Nsight check. Stop rule (handoff): 0.4 ms a window saved in Nsight by day 5, or stop.
3. Prefill HC (write/norm + mix) after #6: it pays on long cold prompts (~1-2% at 32K) and little on agent turns.
4. The small-row expert path (#11, 10-15 days, rounding-level) only if the completion trace shows GPU products on
   the critical path after DIRECT.
