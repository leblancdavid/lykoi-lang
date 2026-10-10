# R6.52 — Setup observations

See [report and evidence](../benchmark/results/phase6/R6_52-REPORT.md).
Existing WSL2 has no distro; authorized native Windows fallback succeeds with private
Python3.12.11/PyTorch2.7.1+cu128/BitsAndBytes0.47.0. Exact pinned tokenizer lengths
are702–1458, lower than R6.51's conservative estimates; no target truncation/context
increase is necessary. All10 mask/causal-shift/padding/overflow controls pass.

Real NF4 backward on E04/855 and synthetic2048 passes with finite adapter gradients,
no base gradients and no updates.2048 peak reserved7.29GiB/free1.77GiB provides
bounded but modest headroom against proposed limits. Saved-before-backward adapter
reloads in a fresh process with112 identical tensors and bitwise-equal short logits.
No training or trained-model benefit observed. Historical data/semantics and kernel26
preserved. Future actual accumulation/optimizer/RSS measurements require separate
training authorization; independent evaluation and semantic-tool captures remain open.
