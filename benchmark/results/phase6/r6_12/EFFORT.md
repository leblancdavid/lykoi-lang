# Actual development usage and effort

Source: sanitized OpenCode exports of the assigned sessions. These are actual
reported token fields, not source-size estimates. Whole sessions include setup,
documentation, artifact bookkeeping and final responses. Input and cached-read
tokens are separate fields; reported total equals their sum plus output and
reasoning in these exports. All cache-write counts are zero.

| Session | Input | Cached read | Output | Reasoning | Reported total | Responses | Response s | Tool s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| preparation | 114,012 | 429,952 | 13,143 | 3,436 | 560,543 | 10 | 396.371 | 1.486 |
| A/base | 170,739 | 1,553,920 | 8,855 | 221 | 1,733,735 | 23 | 291.777 | 8.436 |
| B/base | 140,073 | 3,135,488 | 10,192 | 1,516 | 3,287,269 | 30 | 432.787 | 9.167 |
| C/base | 99,230 | 2,054,400 | 7,235 | 814 | 2,161,679 | 26 | 317.934 | 8.247 |
| C/modification | 88,402 | 1,577,856 | 6,521 | 184 | 1,672,963 | 24 | 226.096 | 4.258 |
| B/modification | 96,936 | 1,762,816 | 7,164 | 179 | 1,867,095 | 24 | 270.968 | 5.261 |
| A/modification | 133,629 | 1,717,632 | 9,693 | 318 | 1,861,272 | 25 | 330.196 | 7.658 |

Responses count completed assistant messages with reported usage. Internal
provider retries/HTTP calls remain unobservable. Response time is reported
created→completed duration, not pure reasoning time. Tool intervals may overlap.
Sanitized exports redact read/search inputs: empty scope objects in the tool
audit cannot independently attest paths. Author disclosures supply observed
path histories. Billing remains unavailable; harness cost=0 is not a zero bill.

## Task terminal intervals and partial usage allocation

Interval tokens below include only responses completely contained between
START and terminal result. Boundary-straddling responses are excluded and
explicitly indexed in USAGE-SUMMARY.json. These partial columns must not be
treated as complete task token costs or added to reconstruct whole sessions.

| Track/task/stage | Outcome | Wall s | Test s | Contained input | Cached read | Output | Reasoning | Responses |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A/T1/base | ACCEPTED | 35.952 | 0.466 | 2,279 | 136,704 | 1,077 | 0 | 2 |
| A/T1/modification | ACCEPTED | 68.025 | 0.871 | 6,912 | 282,368 | 2,992 | 38 | 4 |
| A/T2/base | ACCEPTED | 28.501 | 0.539 | 2,285 | 142,720 | 917 | 0 | 2 |
| A/T3/base | ACCEPTED | 28.177 | 0.544 | 1,638 | 148,480 | 828 | 0 | 2 |
| A/T3/modification | ACCEPTED | 33.640 | 0.966 | 4,016 | 228,480 | 1,250 | 0 | 3 |
| A/T4/base | ACCEPTED | 31.907 | 0.554 | 2,200 | 152,704 | 998 | 0 | 2 |
| A/T4/modification | ACCEPTED | 40.608 | 0.739 | 44,503 | 201,728 | 1,322 | 0 | 3 |
| A/T5/base | ACCEPTED | 31.985 | 0.484 | 2,719 | 158,336 | 878 | 0 | 2 |
| B/T1/base | CAPABILITY_GAP | 39.963 | 0.000 | 22,058 | 213,120 | 525 | 192 | 3 |
| B/T1/modification | CAPABILITY_GAP | 41.828 | 0.000 | 5,800 | 142,592 | 918 | 17 | 2 |
| B/T2/base | CAPABILITY_GAP | 16.433 | 0.000 | 155 | 105,344 | 123 | 0 | 1 |
| B/T3/base | CAPABILITY_GAP | 32.565 | 0.000 | 7,088 | 221,312 | 201 | 45 | 2 |
| B/T3/modification | CAPABILITY_GAP | 37.698 | 0.000 | 3,994 | 155,392 | 920 | 0 | 2 |
| B/T4/base | CAPABILITY_GAP | 22.341 | 0.000 | 161 | 118,784 | 156 | 0 | 1 |
| B/T4/modification | CAPABILITY_GAP | 41.172 | 0.000 | 5,458 | 250,112 | 920 | 15 | 3 |
| B/T5/base | CAPABILITY_GAP | 23.530 | 0.000 | 171 | 124,928 | 156 | 0 | 1 |
| C/T1/base | CAPABILITY_GAP | 39.623 | 0.000 | 12,674 | 136,704 | 802 | 57 | 2 |
| C/T1/modification | CAPABILITY_GAP | 50.302 | 0.000 | 12,013 | 364,544 | 1,074 | 12 | 6 |
| C/T2/base | CAPABILITY_GAP | 30.452 | 0.000 | 2,353 | 163,200 | 624 | 40 | 2 |
| C/T3/base | CAPABILITY_GAP | 36.679 | 0.000 | 1,606 | 168,832 | 673 | 104 | 2 |
| C/T3/modification | CAPABILITY_GAP | 36.246 | 0.000 | 5,561 | 210,432 | 966 | 0 | 3 |
| C/T4/base | CAPABILITY_GAP | 32.348 | 0.000 | 2,208 | 173,184 | 700 | 23 | 2 |
| C/T4/modification | CAPABILITY_GAP | 38.674 | 0.000 | 5,447 | 228,352 | 1,036 | 25 | 3 |
| C/T5/base | CAPABILITY_GAP | 42.351 | 0.000 | 2,577 | 178,688 | 689 | 120 | 2 |

Gap intervals measure assessment only, not successful development. No matched
all-track successful task exists, so token/time/cost efficiency rankings are
undefined. Original and modification attempts have zero repairs. A has zero
regressions on 48 original cases; B/C regressions are unavailable.

## Post-result review overhead

The additional verifier session is outside scored development. Its reported
usage is retained separately in REVIEW-USAGE.json. Coordinator/setup/publication
conversation usage is not fully allocated; no experiment-wide cost is asserted.
