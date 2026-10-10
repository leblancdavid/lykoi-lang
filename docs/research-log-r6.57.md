# R6.57 research observation

[Report/evidence](../benchmark/results/phase6/R6_57-REPORT.md) records a single
bounded no-update diagnostic. E01–E03 gradients accumulate exactly against CPU
leaf-hook sums, all112 gradients finite/base gradients absent; dead temporaries
and identical1,647,003,136-byte cleanup allocation baseline provide evidence
against live graph retention in those records. Reserved cleanup grows
3,812,622,336→5,643,436,032→7,656,701,952 bytes.

E04 forward is interrupted at8,698,986,496 reserved bytes and778,858,496 device
free bytes. An additional outside-allocator accounting residual increase is
measured but not attributed. Complete window, final parameter identity comparison
and planned post-window cache-release observation are not reached. Classification
R6_57_MEMORY_DIAGNOSIS_PARTIAL; exactly one next recommendation D. No retry,
update, adapter save or semantic change. Historical classifications preserved.
