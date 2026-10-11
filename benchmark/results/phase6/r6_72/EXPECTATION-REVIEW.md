# Pre-inference expectation review

Distinct reviewer session: `ses_ed434f440ffeGoANY3nkuPhYXS`, general agent explicitly
assigned under the owner's reviewer instruction. Research only; no edits or model
calls. Requirements and listed targets were visible together. No attested context
isolation, blinded derivation or independent sourcing. Qualification is therefore
**coordinator-reviewed**, with a distinct same-platform consistency review.

Reviewer derived these choices from prose, checked order/type/direct closure and
manually verified all28 fixture values including prior prefixes:

|Case|Operation|Ordered operands|Type|Sorted distinct direct deps|
|---|---|---|---|---|
|S01|add|const(-9), const(14)|Int64|none|
|S02|add|const(8), ref(credit)|Int64|credit|
|S03|add|ref(adjusted), ref(adjusted)|Int64|adjusted|
|S04|add|const(8), ref(credit)|Int64|credit|
|S05|le|ref(ceiling), ref(observed)|Bool|ceiling, observed|
|S06|le|const(-6), ref(reading)|Bool|reading|
|S07|le|ref(echo), ref(adjusted)|Bool|adjusted, echo|
|S08|le|ref(ceiling), ref(observed)|Bool|ceiling, observed|
|S09|eq|ref(active), const(false)|Bool|active|
|S10|eq|const(0), ref(code)|Bool|code|
|S11|eq|ref(snapshot), ref(snapshot)|Bool|snapshot|
|S12|eq|ref(left), ref(right)|Bool|left, right|

No material ambiguity, invalid types, missing literals, out-of-scope identities,
or unrepresentable gold choices were found. Reviewer recommends freeze unchanged.
Coordinator's separate deterministic qualification must pass before inference.

Limitations identified: add/eq order is structurally specified but behaviorally
commutative; repeated identical operands have no distinguishable reversal. S07's
echo aliases raw; S11's snapshot aliases origin. Behavioral fixtures cannot alone
establish exact identity. S01/S11 are constant; S07 is false whenever its prefix
succeeds. S07's reversed comparison is nevertheless distinguishable. Fixtures are
finite and omit overflow, malformed arguments and S12 true/true. Prefix raw-3 can
overflow outside the declared fixtures. Result type is supplied in each scope.
Two paraphrase/reordered-scope pairs are correlated observations, not independent
tasks. Full acceptance must retain exact operation/ordered binding/dependency
dimensions, not merely successful execution.
