# R6.27 compatibility decisions

- **Publication annotation:** add only root object type to an object-only oneOf.
  It is acceptance-set equivalent by branch typing; retain authoritative original
  validation. Reject unsupported conversions instead of flattening or weakening.
- **Neutral metadata:** preserve identities/order and full semantic descriptions,
  but honestly prefix echo-only endpoints. Metadata never enters argument objects.
  Record original-description refusals rather than interpreting them as schema gaps.
- **Windows prompt delivery:** use direct installed executable and UTF-8 stdin;
  attest requested versus exported user text. Retain failed argv attempts.
- **Evidence boundary:** controlled runtime delta establishes compatibility cause;
  public-tag source and separate SDK reproduction do not recover the original
  bundled exception or attest every provider's schema handling.
- **Stop:** [report](../benchmark/results/phase6/R6_27-REPORT.md) qualifies neutral
  exposure only. Actual semantic construction and a second provider require new
  authorization; historical R6.26 and scored tasks stay preserved/unexposed.
