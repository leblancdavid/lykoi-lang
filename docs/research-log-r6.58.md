# R6.58 research observations

[Report and evidence](../benchmark/results/phase6/R6_58-REPORT.md) retain exactly
one baseline and one cache-release process. Baseline3/4, cache4/4 backward calls;
no static padding. Fully inactive reservation grows while cleanup live/split bytes
stay fixed. Empty_cache reclaims exactly the fully inactive segment bytes and
preserves gradient bytes. Shared-prefix losses/gradients match bitwise.

Actual cache parameter equality passed before a subsequent guard-induced scheduler
state_dict comparison failure. CPU-only reproduction explains the added step key;
no outcome-driven GPU rerun or historical repair. Publication helper's initial
nested-kwargs lookup error was corrected before any CPU optimizer construction.
Outside-allocator device pressure remains unattributed; WDDM per-process bytes N/A.
One window supports a prospective cache-release adjustment, not20-step qualification.
All training updates and saves remain zero. Stopped pending explicit authorization.
