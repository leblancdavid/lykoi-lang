# Shared observable interface

Each task accepts immutable bytes, length 0..64. Input above64 rejects INPUT_LIMIT
at offset64 before behavior. No implicit ASCII preflight. Success is exactly
`{status:"success",value:V,output:H}`, H lowercase hex bytes; rejection exactly
`{status:"reject",code:C,offset:N}`. N is zero-based byte position, EOF=input length.
No partial result on error. Strict integer/Boolean fields, record keys and list order
matter; record key order does not. Bytes arrive from guaranteed-valid hex transport;
transport shape is unscored. No files, clock, randomness, network or external state.
Python submission: `solve(data: bytes)` returns this envelope. C submission: JSON
plan consumed by unchanged `interpreter.execute`; coordinator projects value/output
or code/offset only. Adapter implements only the shared64-byte input boundary and
observation projection, never task computation. Default VM limits unchanged.

Acceptance includes normal, boundary and adversarial observations; exact behavior
in these contracts, not source similarity, is scored. Version2 in T1/T2 is RESERVED
and outside the base contract; it has no base acceptance expectation. Other invalid
versions are specified and tested. All specified base observations survive extension.
