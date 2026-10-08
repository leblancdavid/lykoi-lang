# R6.10 adversarial coverage (prospective execution)

Historical R6.6 NOT_RUN cells and R6.7–R6.9 non-results remain exact. Test names
refer to `test_interpreter.py`; the execution transcript and counts are in evidence.
The specifications and expected cases were read by the implementing agent; these
are same-agent synthetic conformance tests, not independent or held-out evidence.

## Original 27 format/challenge cells

| Challenge | CFG66 executed coverage | DSV66 executed coverage | BXC66 executed coverage |
| --- | --- | --- | --- |
| Empty | cfg_empty | dsv_empty | bxc_empty, bxc_zero |
| Encoding | cfg_bad_encoding_precedence | dsv_bad_encoding | bxc_bad_name, bxc_witness |
| Truncation | cfg_truncated, all_truncations | dsv_truncated, all_truncations | bxc_truncated, all_truncations |
| Alternatives | ambiguous_prefix/prefix_overlap (generic VM refusal) | same generic refusal | same refusal; bxc_version |
| Nesting | cfg_nested | dsv_nested_looking_literal | bxc_nested_opaque |
| Duplicate | cfg_duplicate | dsv_duplicate and competing-rule cases | bxc_duplicate |
| Lengths | cfg_name_bound/text_bound/overflow | dsv_empty_quantity/quantity_limit/bad_close | count, zero_name, length_before_truncation, echo/total |
| Resources | input_limit_before_encoding, low_work_every_boundary, occurrence_limit_declared | same work/occurrence checks | input/output, work, negative_take |
| Conflicting validation | ordered_conflicting_checks | ordered_conflicting_checks + duplicate/quantity/key precedence | ordered_conflicting_checks |

All listed cases **executed and passed**. These are representative cells, not
exhaustive grammars or all combinations of limits. Unicode/ambiguous grammars/
recursive interpretation remain outside scope rather than failed format tests.

## Original candidate attacks

| ID | R6.10 status / evidence |
| --- | --- |
| X01 | Executed and passed: empty_repeat refused |
| X02 | Executed and passed: cycle refused |
| X03 | Executed and passed: prefix_overlap refused |
| X04 | Executed and passed: negative_take, length_before_truncation |
| X05 | Executed and passed: undeclared_dependency, shadowing |
| X06 | Executed and passed: canonical roundtrip, leading zeros |
| X07 | Executed and passed: conflicting ordered checks |
| X08 | Executed and passed: bad encoding precedes earlier syntax |
| X09 | Executed and passed: BXC bound precedes payload truncation |
| X10 | Executed and passed: same-length tamper is accepted under structural integrity |
| X11 | Executed and passed: independent small fixed-depth plan, depth rejection |
| X12 | Executed and passed under experimental accounting: every low-work cutoff; exact frozen accounting blocked by unresolved specification |
| X13 | Executed and passed: unknown_codec refused |
| X14 | Executed and passed: filesystem_callback/script_expression refused |
| X15 | Blocked by unresolved production result/byte binding; persistence not executed |
| X16 | Streaming/chunk composition not executed; not an admitted operation |

Executable tests additionally cover original hand-derived witnesses and DSV
selection/increment, BXC empty selection, exact CFG span, DSV character provenance,
all prefixes of three complete inputs, all UInt16 values and all 128 ASCII values.
No recorded historical outcomes were retroactively replaced.

Development chronology: the first 74-test run had one failed test because freshly
authored test nodes collided with IDs in a copied plan. The validator correctly
refused that plan. Fresh test IDs fixed the fixture; the subsequent 78-test run
passed. Four additional plan/limit tests were then added before final publication.
The terminal evidence records the final suite, not a claim that every development
attempt passed. Exact frozen cost conformance and statically typed lowering remain
blocked/unexecuted, rather than included in passing test counts.
