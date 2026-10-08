# T1 — Stock holds

1. Interface: one JSON object on stdin, one JSON object on stdout; no other stdout.
   The request has exactly `stock` and `ops`. JSON types are strict (booleans are
   not integers); every object below rejects extra or missing keys.
2. `stock` is a list of 1–8 `{sku,qty}` objects. `sku` matches `[A-Z]{1,4}`;
   `qty` is an integer 0–100. `ops` is a list of 0–16 operations:
   `{kind:"reserve",id,sku,n}`, `{kind:"release",id}`, or `{kind:"ship",id}`.
   IDs match `[a-z]{1,4}`; reserve `n` is an integer 1–100.
3. Validate the entire request's shapes/types/ranges first, returning
   `{"error":"shape","at":-1}` on any violation. Then reject duplicate stock
   SKUs with `{"error":"duplicate_sku","at":-1}`. No partial state is returned
   on error. Each subsequent error is `{"error":CODE,"at":I}`, where I is the
   zero-based operation index; the first failing operation wins.
4. Initially each SKU has free=qty, held=0, shipped=0. Reserve first rejects an
   ID ever successfully reserved (`duplicate_id`), then an absent SKU
   (`unknown_sku`), then insufficient free units (`insufficient`). Otherwise it
   moves n units free→held and creates an active hold. Release/ship first reject
   a nonactive ID (`unknown_hold`); release moves its units held→free, ship moves
   them held→shipped. Both remove the active hold. Used IDs remain used.
5. Success is exactly `{"stock":[{"sku":S,"free":F,"held":H,"shipped":P},...],
   "holds":[{"id":I,"sku":S,"n":N},...]}`. Stock is sorted by SKU and active
   holds by ID, ascending ASCII order. Operations run in supplied order.
6. Pure deterministic input→output state; no files, clock, randomness or network.
   A request is at most 16 KiB UTF-8, one valid JSON value with unique object keys;
   transport-invalid JSON/oversize requests are outside the contract. Output
   integers are JSON integers. Bounds above bound all work and state.
