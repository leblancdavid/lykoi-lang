# Lykoi — Master Project Context

**Updated:** October 9, 2026

## Project vision

Lykoi is an experimental AI-native symbolic software construction system.

Its purpose is to investigate whether AI can transform human software requirements into structured symbolic representations that can be deterministically validated, compiled and executed without an AI model.

Lykoi is not necessarily intended to replace Python or other programming languages.

Its architecture should be determined by experimental evidence.

## Primary goals

1. Improve correctness of AI-generated software.
2. Improve reliability and modification safety.
3. Reduce total AI development effort and cost.
4. Increase software development speed.
5. Support generalization to unfamiliar requirements.
6. Preserve deterministic, AI-independent execution.

Human readability of the symbolic representation and compiled output is not required.

AI authoring may use local or cloud models. Lykoi's core execution must remain provider-independent.

## Proposed architecture

Human requirements → AI interpretation → Symbolic construction → Semantic validation → Deterministic lowering → Executable software.

The current proposed representation is a typed semantic DAG with ordered sequence regions and immutable symbolic references.

AI may eventually discover and reuse higher-level abstractions composed from stable semantic primitives.

## Existing technical foundation

- Production semantic kernel: 26 constructs.
- Formal requirement contracts and validation research.
- State transitions, invariants, effects and impact analysis.
- R6.10 experimental semantic VM.
- R6.14 exhaustive finite-relation composition.
- R6.18 typed symbolic composition wrapper.
- R6.23 deterministic construction adapter.
- R6.25 provider-neutral tool-call transport.

These capabilities have different levels of experimental qualification and must not be represented as one production-ready system.

## Key research findings

**R6.15:** Conventional Python outperformed the experimental VM in a limited exploratory authoring comparison.

**R6.16:** Structured intent generated fully accepted applications. Adding Lykoi did not demonstrate additional scored correctness or modification-safety benefits.

**R6.18:** Typed symbolic composition and deterministic expansion succeeded in bounded exhaustive testing.

**R6.19–R6.23:** Local Qwen3 8B struggled with symbolic authoring. Several prompt, decoding and interface issues were investigated.

**R6.24:** Model tool-call transport was rejected before task exposure.

**R6.25:** Transport compatibility was repaired, but Qwen3 8B did not complete an executable symbolic program.

**R6.26:** A capable-model attempt using GPT-6.1 Sol was blocked by OpenCode tool exposure before construction began.

These results do not disprove the value of symbolic software construction.

## Current status

Latest completed round: **R6.26 — PROVIDER_COMPATIBILITY_GAP**.

R6.27 has been proposed to investigate tool exposure and schema compatibility. It has not been reported as completed.

The next strategic milestone is demonstrating that a capable AI can construct and execute a symbolic program using the existing tools.

After that, compare:

- Direct conventional programming.
- Structured intent with deterministic generation.
- Lykoi symbolic construction and semantic validation.

## Research principles

- Do not assume Lykoi must be retained as a separate programming language.
- Prefer general-purpose capabilities over benchmark-specific patches.
- Distinguish production Lykoi from experimental components.
- Compare functional behavior, not generated source-code similarity.
- Preserve historical benchmark identities and results.
- Do not claim independent qualification where isolation is unverified.
- Record capability gaps honestly.
- Do not confuse passing finite tests with universal correctness.
- Keep AI-independent execution as a hard architectural requirement.
- Use capable AI models without requiring local-only inference.
- Avoid excessive infrastructure research when direct experiments can answer the question.

## Development workflow

OpenCode is the primary development agent environment.

ChatGPT assists with architecture, research interpretation, experimental design, critical evaluation and OpenCode prompts.

OpenCode publishes implementation reports, classifications, evidence and verification results.

Each research round should end at an explicit authorization boundary.

## Long-term hypothesis

AI may be able to organize software more effectively through reusable symbolic representations than through conventional source-code generation.

Lykoi should test this hypothesis rather than assume it is true.

A successful outcome may be a symbolic programming language, semantic intermediate representation, verification system or AI software-construction toolkit.