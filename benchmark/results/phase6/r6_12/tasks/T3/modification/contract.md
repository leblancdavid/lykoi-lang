# T3 staged change — Bounded greedy coalescing

1. Preserve the base contract; extend action with `coalesce`. Validation is
   unchanged. For this action, normalize every original payload first, retaining
   zero-length records. Then scan records left→right with an output list.
2. If the next record has the same tag as the last output record and concatenating
   their payloads would have length≤8, append its payload to that output record.
   Otherwise append a new output record. The possibly enlarged last record is
   used for the next decision. Do not normalize concatenated payloads again,
   reconsider earlier output records or remove empty records.
3. Recompute count/checksums and return the base success shape. Other actions and
   all original fixtures are unchanged; all base bounds/environment rules apply.
