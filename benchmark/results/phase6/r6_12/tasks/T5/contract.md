# T5 — Weighted ranked-choice rounds

1. One JSON stdin request→one JSON stdout observation, no other stdout. Request
   is exactly `{candidates,ballots}`. candidates is a list of 1–6 single ASCII
   uppercase letters. ballots is a list of 0–12 objects, each exactly
   `{ranks,weight}`; ranks is a list of 0–6 distinct single ASCII uppercase
   letters, weight is an integer 1–9 (not a boolean). Extra/missing keys fail.
2. Validate all shapes/types/ranges, including distinct ranks per ballot, first
   (`shape`); then distinct candidates (`duplicate_candidate`); then all ranks
   belonging to candidates (`unknown_candidate`). Errors are exactly
   `{"error":CODE}`; this phase order overrides input order.
3. Initially all candidates are active. In each round assign each ballot's
   entire weight to its first active ranked candidate, or count its weight as
   exhausted if none remains. Totals include every active candidate, even zero
   votes, sorted by ID ascending ASCII. Nonexhausted weight is the sum of totals.
4. If nonexhausted weight is zero, terminate with winner null. Otherwise a total
   strictly greater than half the nonexhausted weight wins. If none wins,
   eliminate the candidate with lowest total; ties eliminate the largest ASCII
   ID. Recompute assignments from original ballots in the next round. Exactly
   half is not a majority; exhausted weight is excluded from its denominator.
5. Success is exactly `{"winner":ID_OR_NULL,"rounds":[ROUND,...]}`. ROUND is
   exactly `{"totals":[{"id":ID,"votes":V},...],"exhausted":E,"eliminated":ID_OR_NULL}`.
   Append each round including the terminal one; terminal eliminated is null.
   Nonterminal eliminated names that round's removed candidate. No rounds are
   omitted, merged or reordered; at most six rounds, total ballot weight≤108.
6. Pure deterministic decoded-data computation, no persistence/network/clock or
   randomness. Valid JSON with unique object keys and ≤16 KiB UTF-8 per request
   are transport preconditions; integer observations use JSON integers.
