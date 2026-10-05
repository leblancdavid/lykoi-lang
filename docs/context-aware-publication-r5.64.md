# R5.64 context-aware publication policy

Publication-field classifications belong to reviewed producer schemas, never to
data supplied by a worker or a self-declared payload. `PublicationSchema` stores
an immutable canonical schema definition. Every typed publication supplies an
independently retained schema identity; changing classification, type, nesting,
membership, or optional fields invalidates that pin. A new reviewed producer may
declare a different schema; that is a trust-boundary decision, not a worker API.
The built-in QualificationIdentity schema has a literal content pin.

## Field meaning

| Class | Publication meaning |
| --- | --- |
| PUBLIC_METADATA | Explicitly reviewed ordinary metadata. |
| PROTOCOL_IDENTITY | Public process/policy/version identity. |
| PROTOCOL_AUTHORIZATION | Non-secret metadata describing permitted experiment/process actions, policy versions or authorization IDs. |
| CONTENT_IDENTITY | Public content identity; ordinary digests are not credentials merely because of entropy. |
| SECRET_REFERENCE | Only the existing redacted/presence/keyed-reference representations; never raw material. |
| SECRET_VALUE | Raw values prohibited; existing safe representations only. |
| CREDENTIAL_HEADER | Authentication header material prohibited; existing safe representations only. |
| SYNTHETIC_SECURITY_FIXTURE | Never publishable; R5.59 immutable designated test-input handling remains separate. |

The bounded schema implementation supports exact object membership, optional
fields, strings and Booleans. It validates the complete tree before inspection.
Unknown fields and type mismatches in a classified document reject. Classification
is recursive and independent of a field's spelling: renaming a credential field
does not change its class. Credential objects reject raw contents as a whole.

`QualificationIdentity.authorization` is PROTOCOL_AUTHORIZATION. It is an
experiment authorization/policy identity, not an HTTP authentication value. The
same reusable declaration mechanism supports an independent nested process schema.
HTTP header producers must declare Authorization as CREDENTIAL_HEADER. There is
no experiment-name, rejected-value or historical-path exception.

## Defense in depth and fallback

All keys and string values retain R5.47 credential-shape/assignment inspection,
including public and protocol fields. Typed strings additionally reject HTTP
authentication prefixes (bearer/basic)
with short opaque payloads, without relying on the free-text token-length threshold.
Explicit sensitive structures still reject
raw values. R5.59 still rejects immutable fixture values anywhere in serialized
publication. Typed publication does not rescan JSON's serialization punctuation
as untyped credential assignments: the schema-aware traversal has already checked
every actual key and value. Free text within fields is still scanned as text.
Untyped text/source publication retains its existing conservative policy.

Without a trusted schema, the R5.47 policy is unchanged: an ambiguous field named
authorization requires an existing safe representation (including redaction or
presence), otherwise publication rejects. Other unknown fields remain subject to
value/marked-structure inspection. A missing/wrong schema pin or a payload-only
declaration cannot confer public status. No unknown occurrence is promoted to
public by assertion or renamed to obtain permission.

This is a bounded detector, not an opaque-password/entropy oracle. Recognizable
provider tokens, bearer/basic material, private keys, credential URLs and credential
assignments reject under innocent names. An opaque password without any contextual
or recognizable indicator cannot be identified by this policy; producers must
classify credential-bearing inputs and never submit arbitrary raw dumps. Explicit
public classification is not permission to embed secrets.

Diagnostics retain fixed categories and sanitized identifier-shaped field names;
rejected values, arbitrary schema definitions and worker exception text are not
included. Schema errors are reported as fixed, redacted publication violations.

## Prospective integration

The exact freeze publication chain accepts explicit `schema` and
`schema_identity` parameters on `tier.seal` and R5.59 `safe_bytes`/`persist`.
Envelope hashing, canonical persistence, observation controls, certificate and
authority semantics remain unchanged. Future reviewed qualification producers
must pass the QualificationIdentity schema and its pin both when sealing and
persisting/revalidating a new identity. Historical producers are not retrofitted
or resumed. A classified identity must be reloaded with the same schema pin;
ordinary untyped scans intentionally cannot infer that context from its contents.
