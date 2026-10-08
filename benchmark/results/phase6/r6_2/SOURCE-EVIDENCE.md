# P6-A04 — R6.2 Q1/Q2 source-evidence analysis

**Finding: Q1 and Q2 remain material clarification questions.** The preserved
issue supports the local-wheel/path-space installation objective, but does not
sufficiently determine acceptance of every character of the reproduction.
No revised FRC or fixed acceptance plan is justified on this evidence alone.

## Evidence boundary

Only the R5.116A-preserved title/body of `pypa/pip#13139` supplies behavioral
evidence. Capture identity and original API/provenance are verified offline.
The full saved body was rendered after verification, including the reported
traceback; its caller shim is failure context, not a solution. No external link,
standard, comment, fixing PR, implementation commit or newer issue was inspected.
No P6-A05 source or artifact was accessed. This is the retrieved revision, not
a reconstructed creation-time body. Labels/resolution metadata have no behavioral
authority here. Same-agent/same-model review; no independent cognition claim.

## Source fragments and their roles

| Location | Exact fragment | What it establishes |
| --- | --- | --- |
| Title | `` `pip` fails to parse `install_requires` containing local wheel with spaces in path `` | Reported parsing defect centered on path spaces |
| Description | `` `pip` fails to install a package when its `setup.py`'s `install_requires` contains a local wheel file path that includes spaces. `` | Containing-package installation is the workflow |
| Expected behavior | `` `pip` should correctly parse the `install_requires` and install the local wheel, even if its path contains spaces. `` | Positive parsing and wheel-installation objective; parsing alone is insufficient |
| Reproduction | `mkdir "my folder"` | Deliberate filesystem directory space |
| Reproduction | `pipefunc-0.46.0-py3-none-any.whl @ file://$(pwd)/my folder/pipefunc-0.46.0-py3-none-any.whl` | Exact demonstrated input template, including both disputed spellings |
| Output | `Expected end or semicolon (after URL and whitespace)` | Observed rejection; does not decide what syntax must be supported |
| Output | `'install_requires' must be a string or iterable of strings containing valid project/version requirement specifiers` | Diagnostic validity language; not an authoritative ruling that either token is incorrect |

The reproduction uses a shell-expanded heredoc. `$(pwd)` is replaced by the
working directory before Python executes; it is not a literal placeholder that
the requirement parser must accept. Neither that expansion nor the quoted Python
string encodes the space in `my folder`. The saved diagnostic confirms the raw
space remains in the submitted requirement. None of this proves support is required.

## Q1 — literal raw-space file URL

**Evidence in favor:** The reporter deliberately creates `my folder`, supplies
a raw-space `file://` URL, and asks for correct parsing and installation despite
path spaces. Read together, these strongly motivate the exact-input research
branch; this is more than a stray space in a traceback.

**Limit:** The expected-behavior sentence specifies a path containing spaces,
not separately an unencoded URL containing spaces. A URL spelling that represents
the same space-containing filesystem path could also satisfy that sentence.
The issue never distinguishes these meanings or says the declaration must work
unchanged without URL encoding. The reproduction appears under **How to Reproduce**
and the result under **Output**, not as an expressly accepted syntax rule.

**Classification:** Raw-space syntax is presented as a failing example connected
to a desired installation outcome. The source does not expressly present it as an
error to correct, nor does it specify an encoded alternative. Intended URL spelling
remains unresolved. Do not infer raw acceptance just from failure, and do not infer
an encoding requirement from standards memory. Absence of a cited standard is not
itself the blocker: the blocker is underdetermined desired input behavior.

**Answer needed:** Must that raw-space URL parse/install unchanged, or is a
specified encoded representation intended? A corrected branch requires an exact
attributed clarification, not silent substitution.

## Q2 — wheel-filename token before @

**Evidence in favor:** The sole declaration uses
`pipefunc-0.46.0-py3-none-any.whl` before `@`; the expected-behavior sentence
refers to parsing `install_requires`. Exact-input fidelity would preserve it.

**Limit:** No sentence requests wheel-filename tokens as supported dependency
names, discusses the left-hand token, or distinguishes it from a project-name
form. The report isolates path spaces as the problem. Repetition of the token in
the error output is the same failed example, not additional authority. The source
does not say the token is correct, incorrect, or that correcting it is acceptable.
The parser's stopping point cannot prove subsequent syntax validity or intent.

**Classification:** Incidental example syntax in a failing reproduction; supported
form versus erroneous/replaceable spelling is unresolved. It is not an explicit
request for a wheel-filename-name feature. Do not label it invalid using remembered
packaging rules, and do not replace it with `pipefunc` to manufacture an oracle.

**Answer needed:** Must this exact token be accepted and select the designated
wheel, or is a specifically clarified project-name token intended?

## Bounded interpretation and acceptance consequences

The following remains a **proposal requiring clarification**, not source-established:

> Given the exact dependency declaration from the preserved issue, including its
> wheel-filename token and raw-space local file URL, installing the containing
> package resolves and installs the designated local wheel.

Both material input decisions must be resolved legitimately before selecting this
branch or a corrected branch. Merely choosing an appealing research assumption or
approving the old candidate cannot supply missing behavioral authority.

| Stage | Source-grounded goal | Exact-input expectation now |
| --- | --- | --- |
| Parsing | Parse the intended local-wheel `install_requires` despite a space-containing path | Conditional on Q1/Q2; no unconditional acceptance of the literal declaration |
| Resolution | Select the designated local wheel | Conditional; no remote or different-artifact substitute |
| Containing package | Complete installation with otherwise satisfied prerequisites | Conditional; `my-local-package` 0.1.0 recipe retained |
| Dependency observation | Independently establish installed designated dependency | Conditional; parser success or rewritten input alone is insufficient |

R6.1 T1/T2 retain their conditional positive expectations; T3/T4 remain interpretation
witnesses with no selected oracle. No success/failure expectation is invented for
encoded URLs or project-name alternatives. No new acceptance candidate is produced.
No revised candidate validity claim is made: the existing revision 1 is revalidated
mechanically and preserved, not semantically approved.

## Fixture authority

| Detail | Delegable faithful setup | Boundary |
| --- | --- | --- |
| Package directory | A temporary absolute working directory and cleanup policy | Keep `my folder` and the source suffix; substitute only the shell working directory; do not add extra syntax stressors |
| Containing package | Materialize `setup.py` and empty `my_module.py` | Retain `my-local-package`, 0.1.0, source declaration, and install workflow; no preprocessor correcting it |
| Wheel | Stage and hash the source-designated `pipefunc-0.46.0-py3-none-any.whl` | Original download URL is the retrieval locator, not a content digest. No arbitrary wheel renamed to that filename or invented replacement distribution |
| Environment | Pin compatible interpreter/backend and satisfied transitive prerequisites; isolated initially absent target/dependency | Record versions and provenance; do not use preinstallation to mask missing installation or a backend that rewrites disputed syntax |
| Observation | Choose reliable installed-distribution/version and artifact-correspondence inspection | Show both containing package and dependency were installed from the designated local wheel; an import or version string alone cannot exclude substitution |

Controlled environmental setup is not a new no-network, rollback, universal platform,
or diagnostic contract. The reported pip 24.3.1/Python 3.13.1/macOS/Ubuntu are context;
fixture choices must not create compatibility guarantees. Wheel bytes, metadata,
digest, backend/interpreter pins, transitive fixture identities and the concrete
observation procedure remain unfixed. No download or executable fixture was made.
Compatible fixture selection cannot settle Q1/Q2: syntactic acceptance is behavior,
not test setup. These unresolved details require a later source-faithful plan identity
before approval; the human need not design parser algorithms or package internals.
