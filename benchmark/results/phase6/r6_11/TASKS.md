# Shared formal requirements — R6.11

## Common contract

Inputs are bytes of length 0..64, delivered as hexadecimal by an unscored JSON
transport. Above 64 bytes reject INPUT_LIMIT at byte 64 before any task behavior.
Successful observation is {status: success, value: V}. Failure observation is
{status: reject, code: C, offset: N}; no partial value is published. Offsets are
zero-based bytes; EOF offset is input length. Inputs are immutable. No persistence,
files, clock, randomness, locale or network are required. Output records have exactly
the named fields; list order and multiplicity matter, object key order does not.
Unexpected process exceptions, plan rejection or non-JSON output fail acceptance.
The input type is guaranteed by transport; malformed transport is outside scoring.

## T1 — Two-channel aggregation

Read exactly two unsigned 8-bit bytes x then y. Missing byte rejects TRUNCATED
at EOF; any byte after the second rejects TRAILING at byte 2. Return the record
{left: x, right: y, total: x+y}, with mathematical integer total (0..510), no
wrapping. Zero and 255 are valid; order determines left/right. Common input bound
precedes reading. This task measures structured transformation and checked addition.

## T2 — Sample validation

The first byte must be ASCII A. Empty input rejects TRUNCATED at 0; any other
first byte rejects SYNTAX at 0. Following bytes are zero to eight unsigned 8-bit
sample values, in input order. Read and check each sample immediately: values
greater than 10 reject RANGE at that sample's byte, before later samples. Before
reading a ninth sample reject OCCURRENCE_LIMIT at byte 9, even if it exceeds 10.
Return the ordered integer list, preserving duplicates. Empty sample list is valid.

## T3 — Ordered ticket processing

Input is zero to eight two-byte records: unsigned 8-bit id, then unsigned 8-bit
priority. Empty list is valid. Missing priority rejects TRUNCATED at EOF. Before
reading a ninth record reject OCCURRENCE_LIMIT at byte 16. Complete structural
reading precedes uniqueness validation, so an incomplete later record wins over
an earlier duplicate. Duplicate id rejects DUPLICATE at the second id's byte;
the first duplicate in occurrence order wins. Uniqueness includes excluded records.
After validation, retain records whose priority is at most 5, preserving occurrence
order, and return [{id: integer, priority: integer}, ...]. No sorting or deduplication.

## T4 — Configuration interpretation

Whole-input ASCII preflight precedes syntax; first byte above 127 rejects ENCODING
at its byte. Choose a prefix from the complete spellings on: or off:; a nonempty
input matching neither complete prefix rejects SYNTAX at 0 (including partial
spellings); empty input rejects TRUNCATED at 0. Consume the selected prefix,
one ASCII digit 0..9, then LF, then require EOF. Missing digit/LF rejects TRUNCATED
at EOF. Non-digit rejects DIGIT at its byte. Wrong LF rejects SYNTAX at its byte.
Extra bytes reject TRAILING at the first extra byte. Only after structural reading
validate digit <=5; otherwise RANGE at the digit byte. Return {enabled: Boolean,
limit: integer}; on means true, off means false. No whitespace normalization.

## M2 — Separately frozen T2 modification

Retain every T2 observation for A inputs. Also accept prefix B with the identical
sample/order/limit/error rules, except permitted values are 0..20 inclusive.
All other prefixes still reject SYNTAX at 0. No existing acceptance is superseded.

## M4 — Separately frozen T4 modification

Retain every T4 on:/off: observation and unrelated error behavior. Add complete
prefix auto: (the sole newly admitted spelling), with the identical digit,
LF, EOF, ASCII and range rules. auto means enabled true. Partial auto prefixes
still reject SYNTAX at 0. No existing acceptance is superseded.
