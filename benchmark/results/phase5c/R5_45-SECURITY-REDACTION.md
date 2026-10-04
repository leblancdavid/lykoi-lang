# R5.45 environment snapshot security correction

The unpushed R5.45 snapshot captured the parent process environment verbatim,
including `OPENAI_API_KEY` and `OPENCODE_SERVER_PASSWORD`. Those values are
replaced with `[REDACTED]` in `R5_45-evidence/state.json`. The owner must revoke
or rotate the exposed credentials with their providers.

This is an explicit security exception to historical-byte preservation. The
snapshot's original identity and all dependent receipts remain unchanged;
the redacted snapshot therefore fails its original integrity seal. Do not
reseal it, rerun the investigation, or treat the redacted file as a qualified
execution-state record. Historical findings and the R5.45 state-identity gap
remain recorded; this correction grants no benchmark exposure authority.

The snapshot collector now uses an explicit allowlist for public environment
values. Other environment variable names remain visible, but their values are
redacted by default, including unknown application credentials. This is
publication metadata, not complete effective-environment identity. Runtime
workers still receive their actual environment.

The single unpushed R5.45 commit is to be rewritten with the owner's permission
so reachable push history does not contain the credentials. A later deletion
commit alone would not remove them from that history. Local Git reflogs may
retain the replaced commit until their normal expiry; do not publish it.
