# R6.57 — inspection of the unchanged R6.56 worker

Source: `experiments/lora_smoke_r6_56/worker.py`, publication-bound by R6.56.

| Question | Source observation |
| --- | --- |
| Retained loss tensors/history | Lines149–157 retain Python floats from loss.item(); no loss tensor history. |
| Retained graph | Lines150/158 call backward then delete output/loss/x/y; no explicit graph retention. Runtime verification still required. |
| retain_graph | No retain_graph=True; default backward graph release. |
| Gradient references | Persistent adapter `.grad` is intended across four calls. No gradient history or derivative graph requested. |
| Backward order | One forward, finite loss check, loss/4 backward, temporary deletion, synchronization per microbatch. |
| Accumulation | zero_grad before window; no reset within four; finite checks/clipping/update afterwards. |
| Buffers | AdamW state materializes on optimizer update; no update before the historical abort. Normal model buffers persist. |
| Accounting | memory() reads allocated/reserved/peaks/free but asserts before returning; abort writer omits values. Numeric historical peak cannot be recovered from that packet. |
| Synchronization | Loop synchronizes after cleanup;100ms monitor reads without synchronization and aborts using cumulative reserved peak. |
| Allocator cache | No empty_cache between records; variable sequence lengths may change cached reservations. This is a hypothesis until measured. |

No likely retention defect is demonstrated by inspection. No repair is made.
The telemetry loss is demonstrated by the control flow and preserved abort
packet, independent of any causal diagnosis of the memory growth.
