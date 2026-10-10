# R6.52 — Setup decisions

1. Use native Windows fallback because WSL2 has no installed distro; avoid new
   Windows feature/admin changes. Private Python3.12.11 leaves system3.14 packages
   untouched. Exact core pins plus a full47-package lock/installed-file hashes retain
   the actual resolved environment.
2. Use only the authorized Qwen1.5B revision with safetensors/local-only loads and
   explicit asset hashes. NF4/double quant/BF16 q/v rank8 succeeds without method
   substitution. Keep large assets in the pre-approved external temporary store.
3. Use explicit prompt-prefix/EOS masks rather than assuming native template supports
   assistant_only_loss. All10 exact targets fit2048. Retain the six-row R6.51 smoke
   subset despite longer rows fitting; setup is not dataset/protocol expansion.
4. Save untrained adapter before backward; verify unchanged tensors afterward and
   reload in a fresh model process. Gradients are qualification evidence, not updates.
5. Recommend unchanged20-step mechanics smoke only after explicit authorization.
   Preserve memory limits and recheck asset persistence/headroom; optimizer-step
   memory and independent/generalization evidence are not inferred from setup.

[Evidence](../benchmark/results/phase6/R6_52-REPORT.md).
