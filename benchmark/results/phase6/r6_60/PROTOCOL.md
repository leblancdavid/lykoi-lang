# R6.60 frozen read-only diagnosis

Owner authorization: one bounded nonproduction read-only investigation of the
R6.59 step20 adapter. No updates, training, expansion or semantic changes.

Before dispatch verify R6.59 publication payload, inherited protected/environment
identities, executable/DLL/lock hashes, all external artifacts, exact checkpoint,
tokenizer, adapter and E01–E06 source/mask identities. Identity mismatch stops
evaluation. Source and this protocol are frozen in FREEZE.json before dispatch.

Two fresh processes, base then adapter, each evaluate the six exact records once.
Use inherited NF4/double-quant/BF16/SDPA/cache-off and identical k-bit preparation.
Adapter is loaded nontrainable. Set eval, requires_grad false and no_grad;
no optimizer or scheduler is constructed. Hash parameters/buffers/quantization
state before/after. Check exact saved adapter tensors. Max sequence2048,
no truncation/packing, process180s, reserved8GiB/free1.5GiB/RSS16GiB bounds.

For every label other than -100, use preceding logit, FP32 cross-entropy and
FP64 host summation in nats. Include target plus im_end; exclude prompt and final
newline. Equal-record mean averages six token means; pooled mean weights every
supervised token equally. Retain every target token ID, exact tokenizer offset,
NLL and target probability. Lexical categories overlap; tag a whole tokenizer
token for any intersecting category span, never divide a token probability.
All-token loss is the authoritative comparison, categories descriptive only.

Audit exact rendered training/evaluation prompts against historical prompt hashes;
retain messages, native template, target format, role boundaries, generation prefix,
EOS and decoding. Inspect preserved raw outputs without extraction, repair or
rescoring. Record first illegal raw-format character/token and lexical absence
of expected package keys; no type/semantic verdict on repaired content.

Optional inference probes are not planned: matched training-style prompts were
already used in the historical calls. If audit suffices, publish NOT_RUN.
Six exposed targets measure resubstitution fit, never generalization or hidden
reasoning. Preserve original0/6 scores, production kernel26 and R6.3–R6.59.
No P6-A04 acceptance or P6-A05 access. Publish evidence and stop.
