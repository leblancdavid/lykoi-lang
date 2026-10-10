# R6.43 historical preservation verification

[BASELINE.json](BASELINE.json) carries5,031 exact SHA256 identities. It extends the
R6.42 inherited chain, verifies R6.32/R6.40/R6.41/R6.42 publication manifests and
receipt bindings, and preserves both R6.42 local raw JSON originals by their published
archive identities. Baseline verified before successor execution, after execution,
and at publication; [VERIFICATION.json](VERIFICATION.json) records the final check.

| Protected group | Verification basis |
| --- | --- |
| R6.3–R6.42 history | Inherited protected index plus R6.42 publication and raw originals; no first result rewritten. |
| R6.40 |701 published file identities, manifest/receipt binding; historical acceptance49 identities remain frozen. |
| R6.41 |14 published identities and manifest/receipt binding. |
| R6.42 | Publication manifest/receipt, original FREEZE/EXPECTATIONS, failed results, raw originals and gzip archives unchanged. |
| Production |129 entries in inherited implementation index, compiler/lowerer/runtime/model/schema/generated artifacts unchanged. |
| R6.10 VM |21 inherited implementation entries; interpreter SHA256 bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3. |
| R6.18 wrapper |27 inherited entries; composition SHA256 e5e57901d4df32bcb2eed3b5bbd7ce6f19ee3145bbf71303d96e15b4e3d67fab. |
| R6.23 adapter / R6.25 contracts |14/9 inherited implementation entries respectively. |
| R6.32 immutable registry |11 inherited implementation entries,1,262 publication identities; no registry write in R6.43. |
| Existing maps/forms | COMPACT/EXACT/FLAT/EXPECTED-MAP/CORRESPONDENCE are old files bound directly in new FREEZE. Actual expansion compared but not persisted over old data. |
| Kernel | R5.114 final_count26 and its exact accounting hash preserved; no new independent recount. |

Group counts refer to the unchanged R6.42 implementation index, not disjoint totals
to add to5,031. The baseline manifest is the complete machine-readable identity
index. Reading an inherited index is not accessing P6-A05 content. No P6-A05 source
was opened; no P6-A04 acceptance was executed.

R6.42 remains R6_42_PROVENANCE_PARTIAL with its original frozen failures. R6.43 is a
new specification-derived successor check of the unchanged saved representations,
not a retrospective repair, waiver or rescore of R6.42 or R6.40.

All repository writes are additive round-local files or additive versioned R6.43
documentation. No tracked source is changed. Large new raw qualification evidence
is published losslessly as gzip, with the exact original hash/size in RAW-ARCHIVE.
Publication checks JSON, new-file whitespace, relative links, credential patterns,
protected/frozen/publication hashes, recovery bytes and git diff --check.
