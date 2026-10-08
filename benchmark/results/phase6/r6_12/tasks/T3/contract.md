# T3 — Checked binary record normalization

1. One JSON stdin request→one JSON stdout observation; no other stdout. Request
   has exactly `{hex,action}`. hex is an even-length string of ASCII hex digits
   (either case), 0–180 characters. action is `normalize` or `prune`. Any
   shape/type/range violation returns exactly `{"error":"shape"}`.
2. Decode hex into bytes. Header is version byte 1 followed by count byte 0–8.
   Validation order: fewer than two bytes→`short_header`; wrong version→`version`;
   count>8→`count`. Parse exactly count records in order. Each record is tag,
   length, length payload bytes, checksum byte. At each record: missing tag or
   length→`truncated`; tag outside 0–2→`tag`; length>8→`length`; missing payload
   or checksum→`truncated`; checksum unequal to bitwise XOR of tag, length and
   all payload bytes→`checksum`. The first failing record wins. Only after all
   records pass, unused bytes→`trailing`. All errors use `{"error":CODE}`.
3. Validate the entire original binary message before any transformation. Tag 0
   preserves payload; tag 1 reverses payload; tag 2 sorts payload bytes ascending
   unsigned, preserving duplicates. Keep record order. `prune` additionally
   removes records with zero-length payload, after normalization.
4. Re-encode version 1, updated count, records and recomputed XOR checksums.
   Success is exactly `{"hex":H,"records":N,"payloadBytes":B}`, with lowercase
   hex, N retained records and B their total payload length. No text decoding.
5. Pure deterministic, no files/network/clock/randomness. At most 16 KiB UTF-8
   request, valid JSON with unique object keys are transport preconditions.
   The byte bound is 90, retained records≤8 and payload bytes≤64; input violating
   hex bounds is a shape error even if its binary header would fail earlier.
