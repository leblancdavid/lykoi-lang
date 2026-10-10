# Preserved publication-check attempt 2

Command: `python experiments/provenance_r6_42/publication.py`. Exit1 during
whitespace checks, after writing the supplemental implementation index but before
writing a publication manifest or receipt.

```text
publication.py line80: check_text(path, path.read_bytes())
publication.py line32: assert text.endswith('\n')
AssertionError: D:\Dev\axiom\benchmark\results\phase6\r6_42\registry\000001.json:
 missing final newline
```

The unchanged R6.32 registry publishes canonical JSON without a trailing newline.
Its new R6.42 generation is valid canonical output, not a formatting defect to
repair. The unfrozen publication checker now verifies exact canonical bytes for
registry snapshots and continues requiring final newlines for ordinary publication
text. The registry file, all semantic implementations, frozen expectations and
first execution evidence remain unchanged. This verification correction causes
no plan execution, acceptance repair or rescoring.
