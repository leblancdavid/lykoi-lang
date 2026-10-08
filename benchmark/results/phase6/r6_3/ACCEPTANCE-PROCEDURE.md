# Fixed executable acceptance procedure — R6.3

**Prepared only. Do not execute in R6.3.** Later exact artifact approval and
separate execution authorization are required. This is a finite fixture procedure,
not an extension of the native evaluator or a claim that its package-install
integration exists. All expected checks are fixed independently of authored software.

## Fixture preparation (later authorized execution only)

Use Ubuntu 24.04 x86_64, standard CPython 3.13.1 (not free-threaded), a clean
`/tmp/lykoi-r6-3-p6-a04` and a fresh venv outside that directory without system
site packages. Assert `sys.version_info[:3] == (3, 13, 1)` and the platform before
proceeding. No host environment or directory reuse is eligible.

Retrieve each URL in `FIXTURE-MANIFEST.json` to its specified filename and verify
SHA-256 before use; a mismatch/unavailable artifact halts fixture preparation.
Stage only the designated wheel under `my folder`; stage the six other pinned
wheels in a separate wheelhouse. Never put pipefunc in the wheelhouse or index.
Copy the manifest's exact UTF-8 `setup_py_utf8` to `setup.py`, and create empty
`my_module.py`. Verify both byte hashes. This reproduces source shell expansion
at the chosen absolute working directory, preserving the raw space and left token.
No pyproject.toml, input rewrite, renamed directory or wheel substitution.

In the fresh venv bootstrap the pinned pip/setuptools/wheel and the three unrelated
transitive prerequisites from the hash-verified wheelhouse. Standard bootstrap:

```bash
python -m pip install --no-index --find-links "$WHEELHOUSE" pip==24.3.1 setuptools==75.6.0 wheel==0.45.1 cloudpickle==3.1.0 networkx==3.4.2 numpy==2.2.1
```

Inspect installed tool/prerequisite versions. These six distributions are the
complete permitted preload set. pipefunc and my-local-package must be absent.
No extras requested; wheel metadata lists only cloudpickle/networkx/numpy as
unconditional pipefunc prerequisites. Optional extras are excluded.

Disable user site/config contamination: unset PYTHONPATH, set PYTHONNOUSERSITE=1,
PIP_CONFIG_FILE=/dev/null, PIP_NO_INDEX=1, PIP_FIND_LINKS to the separate wheelhouse,
PIP_NO_CACHE_DIR=1 and PIP_DISABLE_PIP_VERSION_CHECK=1. Restrict install-time
network as a fixture control. Prerequisites are staged before the subject command;
this does not preinstall the designated dependency or bypass dependency resolution.
Use the declared setuptools/wheel backend in the controlled venv. No permission
to repair baseline parsing or silently change fixture versions follows.

## Exact-input invocation and observations

`MANIFEST` and `OBSERVER` below refer to the approved retained R6.3 files copied
outside the containing-package directory. `$REPORT` is a fresh absolute JSON path.
Run the fixed observer with the **target venv Python** (not host Python):

```bash
python "$OBSERVER" "$MANIFEST" "$REPORT" before
```

It must establish input/wheel identities and both targets absent (**A04-N0**).
Before the command this same absent state cannot satisfy either installed-state
predicate. This is a negative observer control, not an invented missing-file or
alternate-input requirement.

Activate the later authorized subject's pip-compatible installation entry point
in this controlled environment. The subject is the evaluated implementation;
stock pip 24.3.1 is the baseline/tool identity, not claimed success evidence.
Record subject identity, environment, full output and outcome separately.
From `/tmp/lykoi-r6-3-p6-a04`, keep the source command unchanged:

```bash
export PIP_REPORT="$REPORT"
pip install --verbose .
```

Require successful command outcome before post-observation (success convention,
not a new byte-exact exit/error contract). No direct wheel-install command,
`--no-deps`, separate pipefunc preinstallation, percent-encoded input or normalized
name variant can satisfy the positive case. Internal output URL canonicalization
is allowed; rewriting setup.py or the caller's declaration is not.

```bash
python "$OBSERVER" "$MANIFEST" "$REPORT" after
```

The fixed observer checks separately:

1. **Parsing:** input unchanged; containing-package dependency metadata generated
   and represented in the report without syntax rejection. Metadata must retain a
   dependency on the designated local wheel. No parser-only alternative probe.
2. **Resolution:** pipefunc 0.46.0 selected from the exact local path and wheel digest
   in the report. Metadata/distribution spelling is distinct from the unusual input token.
3. **Containing installation:** successful subject command plus independently read
   my-local-package 0.1.0 metadata and empty installed my_module.py.
4. **Dependency installation:** pipefunc was absent and is now installed at 0.46.0;
   direct_url provenance matches local path/digest; all non-dist-info wheel payload
   files match their pinned hashes. Installer-owned metadata/RECORD and bytecode
   may be added; wheel payload may not be substituted.

All four predicates must pass in one run. Installer report supplies resolution
evidence; independent target-environment inspection supplies installed-state evidence.
Neither producer assertions nor a report alone certify installation. Report/direct_url
availability is an observation fixture choice, not a universal pip API guarantee.
If a later subject cannot expose these observations, record the exact integration
limitation, do not infer success or change the approved oracle.

## Outcome and limits

The procedure is fixed and runnable once an authorized subject and environment
exist. It has **not** been executed, and no backend/installation success is claimed.
The existing local native plan adapter has no package-install payload bound here;
that execution-integration limitation is distinct from resolved behavioral authority.
Preparation does not authorize adding an adapter or bypassing native gates.

No success/rejection expectations for encoded URL, normalized token, malformed
wheel, missing wheel, rollback, unrelated package behavior or other platforms.
No claim of pip maintainer intent, production approval, generalization, kernel
coverage or native evaluator readiness. Stop after preparation and publication.
