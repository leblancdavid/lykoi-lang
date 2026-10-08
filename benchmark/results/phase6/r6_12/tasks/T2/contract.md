# T2 — Deadline-constrained optimal schedule

1. Interface: one JSON stdin request→one JSON stdout observation, no other stdout.
   Request is exactly `{jobs:[...]}` with 0–7 jobs, each exactly
   `{id,duration,weight,deadline,deps}`. IDs and dependency IDs are single ASCII
   uppercase letters. duration is an integer 1–9, weight 0–9, deadline 0–63;
   deps is a list of 0–7 distinct IDs. Types are strict; booleans are not integers.
2. Validate all shapes/types/ranges and distinct deps first (`shape`), then
   distinct job IDs (`duplicate_id`), then existence of all dependency IDs
   (`unknown_dep`), then absence of directed cycles including self-loops
   (`cycle`). Errors are exactly `{"error":CODE}`. Earlier phases win regardless
   of input order. No schedule with all deadlines satisfied yields `infeasible`.
3. A schedule is a permutation of all jobs on one processor starting at time 0,
   without idle time or preemption. Every dependency must finish before its job
   starts. Completion is the cumulative sum of durations. Each job must complete
   at or before its deadline (inclusive). Cost is sum(weight×completion).
4. Among feasible schedules choose minimum cost, then lexicographically smallest
   sequence of IDs in ASCII order. Input job/dependency order has no priority.
   Return exactly `{"order":[ID,...],"completion":[C,...],"cost":K}`;
   completions correspond to order. Empty jobs succeed with empty lists and 0.
5. Pure deterministic computation; no network, files, clocks or randomness.
   Valid JSON, unique object keys and at most 16 KiB UTF-8 are transport
   preconditions. No floats satisfy integer fields. Bounds allow at most 7!
   permutations, completion≤63, cost≤3969; no unbounded search is requested.
