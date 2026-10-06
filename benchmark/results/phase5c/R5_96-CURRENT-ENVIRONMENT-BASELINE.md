# Lykoi current-environment research snapshot

- Started (UTC): 2026-10-06T18:00:59.347703+00:00
- Git commit: 5543a3a1bb7a43fb0adb21c0c461b6141ef9fb22
- Core serialization/semantics: 0.3 (`docs/axiom-v0.3.md`)
- Python backend: 0.3.0
- Generic semantic prototype: current repository sources at the recorded commit/tree
- Representation: BenchmarkDocumentContractV1 / BehavioralContractV1
- AI model (declared): openai/gpt-6.1-sol
- Provider (declared): OpenAI
- Python: 3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]
- Interpreter (provenance only): C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe
- Platform (provenance only): Windows-11-10.0.26300-SP0
- B03 held-out declaration: B03 has not previously been inspected; it remains unread/unexposed.
- Declaration basis: explicit operator attestation; this command never opens B03 and cannot prove prior nonexposure.
- This records a baseline, not benchmark success or machine/model eligibility.

## Working tree before checks

```text
 M AGENTS.md
 M README.md
 M benchmark/README.md
 M docs/agent-workflow.md
 M docs/decisions.md
 M docs/project-overview.md
 M docs/research-log.md
?? docs/research-workflow-r5.96.md
?? src/lykoi_research/__init__.py
?? src/lykoi_research/snapshot.py
```

## Current relevant checks

### `python -m air_compiler.cli validate air/task_manager.json`

Exit code: 0

```text
Lykoi validate: ok
```

### `python -m air_compiler.cli safety air/task_manager.json`

Exit code: 0

```text
{
  "capability_violations": 0,
  "declared_transitions": 1,
  "evidence_counts": {
    "RUNTIME_ENFORCED": 5,
    "SCENARIO_VERIFIED": 0,
    "STRUCTURALLY_GUARANTEED": 1,
    "UNVERIFIED": 0
  },
  "findings": [
    {
      "evidence": "RUNTIME_ENFORCED",
      "id": "inv_unique_ids"
    },
    {
      "evidence": "RUNTIME_ENFORCED",
      "id": "inv_valid_tasks"
    },
    {
      "evidence": "RUNTIME_ENFORCED",
      "id": "inv_title"
    },
    {
      "evidence": "RUNTIME_ENFORCED",
      "id": "inv_status"
    },
    {
      "evidence": "RUNTIME_ENFORCED",
      "id": "inv_priority"
    },
    {
      "evidence": "STRUCTURALLY_GUARANTEED",
      "id": "inv_overdue_excludes_completed"
    }
  ],
  "invalid_transitions": 0,
  "invariants": 6,
  "mutations": [
    {
      "behavior": "fn_create",
      "mutates": [
        "field_created_at",
        "field_description",
        "field_due_date",
        "field_id",
        "field_priority",
        "field_status",
        "field_title"
      ],
      "relevant_invariants": [
        "inv_unique_ids",
        "inv_valid_tasks",
        "inv_title",
        "inv_status",
        "inv_priority",
        "inv_overdue_excludes_completed"
      ]
    },
    {
      "behavior": "fn_complete",
      "mutates": [
        "field_status"
      ],
      "relevant_invariants": [
        "inv_status",
        "inv_overdue_excludes_completed"
      ]
    },
    {
      "behavior": "fn_delete",
      "mutates": [
        "field_created_at",
        "field_description",
        "field_due_date",
        "field_id",
        "field_priority",
        "field_status",
        "field_title"
      ],
      "relevant_invariants": [
        "inv_unique_ids",
        "inv_valid_tasks",
        "inv_title",
        "inv_status",
        "inv_priority",
        "inv_overdue_excludes_completed"
      ]
    }
  ],
  "protected_resources": 1,
  "state_machines": 1
}
```

### `python -m unittest discover -s tests -p test_compiler.py -v`

Exit code: 0

```text
test_dangling_reference (test_compiler.CompilerTests.test_dangling_reference) ... ok
test_impact_paths_and_clock_validation (test_compiler.CompilerTests.test_impact_paths_and_clock_validation) ... ok
test_impossible_contract (test_compiler.CompilerTests.test_impossible_contract) ... ok
test_incompatible_type_and_mutation (test_compiler.CompilerTests.test_incompatible_type_and_mutation) ... ok
test_index_and_diff (test_compiler.CompilerTests.test_index_and_diff) ... ok
test_invalid_filter_migration_and_contract_identity (test_compiler.CompilerTests.test_invalid_filter_migration_and_contract_identity) ... ok
test_least_authority_for_behaviors_and_migrations (test_compiler.CompilerTests.test_least_authority_for_behaviors_and_migrations) ... ok
test_lifecycle_rejects_unmodeled_and_inconsistent_changes (test_compiler.CompilerTests.test_lifecycle_rejects_unmodeled_and_inconsistent_changes) ... ok
test_manifest_and_schema (test_compiler.CompilerTests.test_manifest_and_schema) ... ok
test_manifest_provenance_is_artifact_wide (test_compiler.CompilerTests.test_manifest_provenance_is_artifact_wide) ... ok
test_missing_and_duplicate_ids (test_compiler.CompilerTests.test_missing_and_duplicate_ids) ... ok
test_optional_enum_and_effects_are_validated (test_compiler.CompilerTests.test_optional_enum_and_effects_are_validated) ... ok
test_parser_rejects_duplicate_keys (test_compiler.CompilerTests.test_parser_rejects_duplicate_keys) ... ok
test_plan_fails_without_mutating_model (test_compiler.CompilerTests.test_plan_fails_without_mutating_model) ... ok
test_plan_rejects_duplicate_and_stale_baseline (test_compiler.CompilerTests.test_plan_rejects_duplicate_and_stale_baseline) ... ok
test_plan_rejects_unauthorized_change_before_generation (test_compiler.CompilerTests.test_plan_rejects_unauthorized_change_before_generation) ... ok
test_predicates_safety_and_impact (test_compiler.CompilerTests.test_predicates_safety_and_impact) ... ok
test_renaming_preserves_identity (test_compiler.CompilerTests.test_renaming_preserves_identity) ... ok
test_safety_cli (test_compiler.CompilerTests.test_safety_cli) ... ok
test_transition_references_and_guard (test_compiler.CompilerTests.test_transition_references_and_guard) ... ok
test_undeclared_effect_and_dependency (test_compiler.CompilerTests.test_undeclared_effect_and_dependency) ... ok
test_valid_and_deterministic (test_compiler.CompilerTests.test_valid_and_deterministic) ... ok

----------------------------------------------------------------------
Ran 22 tests in 0.056s

OK
```

### `python -m unittest discover -s tests -p test_application.py -v`

Exit code: 0

```text
test_explicit_legacy_migration (test_application.ApplicationTests.test_explicit_legacy_migration) ... ok
test_failures_leave_state_intact (test_application.ApplicationTests.test_failures_leave_state_intact) ... ok
test_high_priority_filter_and_default (test_application.ApplicationTests.test_high_priority_filter_and_default) ... ok
test_invariants_on_load (test_application.ApplicationTests.test_invariants_on_load) ... ok
test_lifecycle_and_persistence (test_application.ApplicationTests.test_lifecycle_and_persistence) ... ok
test_overdue_and_optional_due_date (test_application.ApplicationTests.test_overdue_and_optional_due_date) ... ok
test_semantic_scenario_with_fixed_clock (test_application.ApplicationTests.test_semantic_scenario_with_fixed_clock) ... ok
test_semantic_transition_scenario (test_application.ApplicationTests.test_semantic_transition_scenario) ... ok
test_version_two_migration (test_application.ApplicationTests.test_version_two_migration) ... ok

----------------------------------------------------------------------
Ran 9 tests in 2.641s

OK
```

### `python -m unittest discover -s tests -p test_authority_controller.py -v`

Exit code: 0

```text
test_append_only_store_and_journal (test_authority_controller.ControllerTests.test_append_only_store_and_journal) ... ok
test_clarification_answer_replacement_invalidates_descendants (test_authority_controller.ControllerTests.test_clarification_answer_replacement_invalidates_descendants) ... ok
test_clarification_mismatch_across_sealed_graph (test_authority_controller.ControllerTests.test_clarification_mismatch_across_sealed_graph) ... ok
test_conflicting_answer_needs_explicit_resolution (test_authority_controller.ControllerTests.test_conflicting_answer_needs_explicit_resolution) ... ok
test_disputed_coverage_and_unsupported_what_only (test_authority_controller.ControllerTests.test_disputed_coverage_and_unsupported_what_only) ... ok
test_durable_reservation_crash_replay_and_completion (test_authority_controller.ControllerTests.test_durable_reservation_crash_replay_and_completion) ... ok
test_external_verification_and_author_self_verification (test_authority_controller.ControllerTests.test_external_verification_and_author_self_verification) ... ok
test_false_ai_assertions_have_no_authority (test_authority_controller.ControllerTests.test_false_ai_assertions_have_no_authority) ... ok
test_grant_reissue_cannot_bypass_single_use_dispatch (test_authority_controller.ControllerTests.test_grant_reissue_cannot_bypass_single_use_dispatch) ... ok
test_input_access_and_no_candidate_self_review (test_authority_controller.ControllerTests.test_input_access_and_no_candidate_self_review) ... ok
test_invalidation_all_authoritative_dependency_classes (test_authority_controller.ControllerTests.test_invalidation_all_authoritative_dependency_classes) ... ok
test_malformed_request_structured_and_audit_event_identity (test_authority_controller.ControllerTests.test_malformed_request_structured_and_audit_event_identity) ... ok
test_persistence_actual_process_restart (test_authority_controller.ControllerTests.test_persistence_actual_process_restart) ... ok
test_policy_adoption_and_precedence (test_authority_controller.ControllerTests.test_policy_adoption_and_precedence) ... ok
test_positive_synthetic_clarification_policy_chain (test_authority_controller.ControllerTests.test_positive_synthetic_clarification_policy_chain) ... ok
test_post_seal_dispute_denies_grant_and_dispatch (test_authority_controller.ControllerTests.test_post_seal_dispute_denies_grant_and_dispatch) ... ok
test_prior_clarifications_remain_normative_in_later_roots (test_authority_controller.ControllerTests.test_prior_clarifications_remain_normative_in_later_roots) ... ok
test_registry_cannot_be_spoofed_on_restart (test_authority_controller.ControllerTests.test_registry_cannot_be_spoofed_on_restart) ... ok
test_rejected_and_revision_required_lifecycle (test_authority_controller.ControllerTests.test_rejected_and_revision_required_lifecycle) ... ok
test_restart_detects_corrupt_artifact_and_journal (test_authority_controller.ControllerTests.test_restart_detects_corrupt_artifact_and_journal) ... ok
test_revision_race_rollback_and_no_partial_authority (test_authority_controller.ControllerTests.test_revision_race_rollback_and_no_partial_authority) ... ok
test_revocation_after_reservation_prevents_completion (test_authority_controller.ControllerTests.test_revocation_after_reservation_prevents_completion) ... ok
test_role_spoof_self_escalation_and_scope (test_authority_controller.ControllerTests.test_role_spoof_self_escalation_and_scope) ... ok
test_same_artifacts_events_reproduce_identity_and_decisions (test_authority_controller.ControllerTests.test_same_artifacts_events_reproduce_identity_and_decisions) ... ok
test_same_display_path_and_immutable_returned_content (test_authority_controller.ControllerTests.test_same_display_path_and_immutable_returned_content) ... ok
test_source_recovery_provenance_is_not_implicit_human_authority (test_authority_controller.ControllerTests.test_source_recovery_provenance_is_not_implicit_human_authority) ... ok
test_unresolved_clarification_and_wrong_answer (test_authority_controller.ControllerTests.test_unresolved_clarification_and_wrong_answer) ... ok
test_unsealed_plan_and_freeze_substitution_deny (test_authority_controller.ControllerTests.test_unsealed_plan_and_freeze_substitution_deny) ... ok
test_unsupported_adequacy_and_missing_evidence_do_not_grant (test_authority_controller.ControllerTests.test_unsupported_adequacy_and_missing_evidence_do_not_grant) ... ok
test_wrong_human_version_and_artifact_substitution (test_authority_controller.ControllerTests.test_wrong_human_version_and_artifact_substitution) ... ok
test_canonical_conformance_vector (test_authority_controller.IdentityTests.test_canonical_conformance_vector) ... ok
test_duplicate_keys_float_nonfinite_large_integer_reject (test_authority_controller.IdentityTests.test_duplicate_keys_float_nonfinite_large_integer_reject) ... ok
test_reformatting_not_content_and_order_is_authoritative (test_authority_controller.IdentityTests.test_reformatting_not_content_and_order_is_authoritative) ... ok
test_type_schema_content_and_dependencies_bound (test_authority_controller.IdentityTests.test_type_schema_content_and_dependencies_bound) ... ok

----------------------------------------------------------------------
Ran 34 tests in 17.029s

OK
```

### `python -m unittest discover -s tests -p test_requirements_workspace.py -v`

Exit code: 0

```text
test_ai_status_strings_and_role_escalation_are_inert (test_requirements_workspace.WorkspaceTests.test_ai_status_strings_and_role_escalation_are_inert) ... ok
test_blind_request_has_no_candidate_or_controller (test_requirements_workspace.WorkspaceTests.test_blind_request_has_no_candidate_or_controller) ... ok
test_clarification_replacement_invalidates_old_seal (test_requirements_workspace.WorkspaceTests.test_clarification_replacement_invalidates_old_seal) ... ok
test_correlated_agreement_can_be_wrong (test_requirements_workspace.WorkspaceTests.test_correlated_agreement_can_be_wrong) ... ok
test_exact_version_approval_cannot_approve_next_frc (test_requirements_workspace.WorkspaceTests.test_exact_version_approval_cannot_approve_next_frc) ... ok
test_feature_requirement_overrides_waivable_policy (test_requirements_workspace.WorkspaceTests.test_feature_requirement_overrides_waivable_policy) ... ok
test_finite_review_budget_survives_restart (test_requirements_workspace.WorkspaceTests.test_finite_review_budget_survives_restart) ... ok
test_ingestion_exact_version_and_immutable_source (test_requirements_workspace.WorkspaceTests.test_ingestion_exact_version_and_immutable_source) ... ok
test_invented_domain_or_freedom_is_divergent (test_requirements_workspace.WorkspaceTests.test_invented_domain_or_freedom_is_divergent) ... ok
test_invention_with_plausible_source_quote_denied (test_requirements_workspace.WorkspaceTests.test_invention_with_plausible_source_quote_denied) ... ok
test_inventory_span_and_text_accountability_checks (test_requirements_workspace.WorkspaceTests.test_inventory_span_and_text_accountability_checks) ... ok
test_material_divergence_returns_product_question_to_human (test_requirements_workspace.WorkspaceTests.test_material_divergence_returns_product_question_to_human) ... ok
test_nonbehavioral_inventory_cannot_authorize_an_frc_obligation (test_requirements_workspace.WorkspaceTests.test_nonbehavioral_inventory_cannot_authorize_an_frc_obligation) ... ok
test_omission_detected_cannot_seal_then_corrected (test_requirements_workspace.WorkspaceTests.test_omission_detected_cannot_seal_then_corrected) ... ok
test_policy_exact_provenance_and_supersession (test_requirements_workspace.WorkspaceTests.test_policy_exact_provenance_and_supersession) ... ok
test_producer_exact_unicode_roundtrip (test_requirements_workspace.WorkspaceTests.test_producer_exact_unicode_roundtrip) ... ok
test_public_end_to_end_controller_seal (test_requirements_workspace.WorkspaceTests.test_public_end_to_end_controller_seal) ... ok
test_question_priorities_and_required_human_answer (test_requirements_workspace.WorkspaceTests.test_question_priorities_and_required_human_answer) ... ok
test_sealed_workspace_actual_process_restart (test_requirements_workspace.WorkspaceTests.test_sealed_workspace_actual_process_restart) ... ok
test_shared_session_is_rejected (test_requirements_workspace.WorkspaceTests.test_shared_session_is_rejected) ... ok
test_stable_logical_id_and_new_artifact_after_clarification (test_requirements_workspace.WorkspaceTests.test_stable_logical_id_and_new_artifact_after_clarification) ... ok
test_unadopted_or_inapplicable_policy_rejects (test_requirements_workspace.WorkspaceTests.test_unadopted_or_inapplicable_policy_rejects) ... ok
test_uncommitted_inventory_cannot_expose_candidate (test_requirements_workspace.WorkspaceTests.test_uncommitted_inventory_cannot_expose_candidate) ... ok
test_unresolved_mapping_and_umbrella_are_insufficient (test_requirements_workspace.WorkspaceTests.test_unresolved_mapping_and_umbrella_are_insufficient) ... ok
test_unresolved_nonwaivable_policy_conflict_blocks (test_requirements_workspace.WorkspaceTests.test_unresolved_nonwaivable_policy_conflict_blocks) ... ok
test_unsupported_scope_halts (test_requirements_workspace.WorkspaceTests.test_unsupported_scope_halts) ... ok

----------------------------------------------------------------------
Ran 26 tests in 16.470s

OK
```

### `python -m unittest discover -s tests -p test_sealed_pipeline.py -v`

Exit code: 0

```text
test_actual_process_restart_audit_by_run (test_sealed_pipeline.PipelineTests.test_actual_process_restart_audit_by_run) ... ok
test_author_adapter_capability_gap (test_sealed_pipeline.PipelineTests.test_author_adapter_capability_gap) ... ok
test_author_cannot_issue_external_authority (test_sealed_pipeline.PipelineTests.test_author_cannot_issue_external_authority) ... ok
test_changed_target_cannot_keep_build_binding (test_sealed_pipeline.PipelineTests.test_changed_target_cannot_keep_build_binding) ... ok
test_compilation_failure_is_distinct (test_sealed_pipeline.PipelineTests.test_compilation_failure_is_distinct) ... ok
test_component_substitution_before_author_rejects (test_sealed_pipeline.PipelineTests.test_component_substitution_before_author_rejects) ... ok
test_component_substitution_before_grant_rejects (test_sealed_pipeline.PipelineTests.test_component_substitution_before_grant_rejects) ... ok
test_default_plan_cannot_verify_component_context (test_sealed_pipeline.PipelineTests.test_default_plan_cannot_verify_component_context) ... ok
test_external_behavior_not_code_identity (test_sealed_pipeline.PipelineTests.test_external_behavior_not_code_identity) ... ok
test_hidden_plan_normal_file_api_denied (test_sealed_pipeline.PipelineTests.test_hidden_plan_normal_file_api_denied) ... ok
test_inadequate_contract_cannot_grant (test_sealed_pipeline.PipelineTests.test_inadequate_contract_cannot_grant) ... ok
test_invalid_fixture_authoring_failure_is_distinct (test_sealed_pipeline.PipelineTests.test_invalid_fixture_authoring_failure_is_distinct) ... ok
test_manifest_substitution_rejects (test_sealed_pipeline.PipelineTests.test_manifest_substitution_rejects) ... ok
test_missing_executed_case_cannot_bind_success (test_sealed_pipeline.PipelineTests.test_missing_executed_case_cannot_bind_success) ... ok
test_missing_plan_obligation_no_seal (test_sealed_pipeline.PipelineTests.test_missing_plan_obligation_no_seal) ... ok
test_native_evidence_cannot_be_text_claim (test_sealed_pipeline.PipelineTests.test_native_evidence_cannot_be_text_claim) ... ok
test_no_grant_no_author (test_sealed_pipeline.PipelineTests.test_no_grant_no_author) ... ok
test_plan_is_sealed_before_author_bundle (test_sealed_pipeline.PipelineTests.test_plan_is_sealed_before_author_bundle) ... ok
test_plan_replacement_does_not_preserve_run (test_sealed_pipeline.PipelineTests.test_plan_replacement_does_not_preserve_run) ... ok
test_public_workspace_exact_seal_halts_at_v1 (test_sealed_pipeline.PipelineTests.test_public_workspace_exact_seal_halts_at_v1) ... ok
test_replay_denies_second_author (test_sealed_pipeline.PipelineTests.test_replay_denies_second_author) ... ok
test_restart_audit_and_fixture_substitution (test_sealed_pipeline.PipelineTests.test_restart_audit_and_fixture_substitution) ... ok
test_runtime_failure_is_not_success (test_sealed_pipeline.PipelineTests.test_runtime_failure_is_not_success) ... ok
test_structural_forged_complete_bool_rejects (test_sealed_pipeline.PipelineTests.test_structural_forged_complete_bool_rejects) ... ok
test_structural_omission_before_bdi (test_sealed_pipeline.PipelineTests.test_structural_omission_before_bdi) ... ok
test_unjustified_plan_exclusion_is_not_coverage (test_sealed_pipeline.PipelineTests.test_unjustified_plan_exclusion_is_not_coverage) ... ok
test_unsupported_bdi_observation_halts (test_sealed_pipeline.PipelineTests.test_unsupported_bdi_observation_halts) ... ok
test_unsupported_structural_relation_halts (test_sealed_pipeline.PipelineTests.test_unsupported_structural_relation_halts) ... ok
test_upstream_invalidation_makes_grant_stale (test_sealed_pipeline.PipelineTests.test_upstream_invalidation_makes_grant_stale) ... ok
test_wrong_but_compilable_target_fails_behavior (test_sealed_pipeline.PipelineTests.test_wrong_but_compilable_target_fails_behavior) ... ok

----------------------------------------------------------------------
Ran 30 tests in 93.178s

OK
```

### `python -m unittest discover -s tests -p test_public_rehearsal.py -v`

Exit code: 0

```text
test_allowlist_and_schema (test_public_rehearsal.AdapterTests.test_allowlist_and_schema) ... ok
test_binding_substitution_rejects (test_public_rehearsal.AdapterTests.test_binding_substitution_rejects) ... ok
test_credential_not_persisted_and_live_protocol (test_public_rehearsal.AdapterTests.test_credential_not_persisted_and_live_protocol) ... ok
test_provenance_and_instruction_identity (test_public_rehearsal.AdapterTests.test_provenance_and_instruction_identity) ... ok
test_unavailable_configuration_is_not_live_success (test_public_rehearsal.AdapterTests.test_unavailable_configuration_is_not_live_success) ... ok
test_ambiguity_blocks_approval (test_public_rehearsal.EndToEndTests.test_ambiguity_blocks_approval) ... ok
test_author_capability_failure (test_public_rehearsal.EndToEndTests.test_author_capability_failure) ... ok
test_author_receipt_substitution_denied (test_public_rehearsal.EndToEndTests.test_author_receipt_substitution_denied) ... ok
test_authorized_title_end_to_end (test_public_rehearsal.EndToEndTests.test_authorized_title_end_to_end) ... ok
test_blind_disagreement_and_ambiguity_block_approval (test_public_rehearsal.EndToEndTests.test_blind_disagreement_and_ambiguity_block_approval) ... ok
test_compilable_wrong_default_fails (test_public_rehearsal.EndToEndTests.test_compilable_wrong_default_fails) ... ok
test_default_success_and_wrong_author_behavior (test_public_rehearsal.EndToEndTests.test_default_success_and_wrong_author_behavior) ... ok
test_exact_wizard_still_halts_before_author (test_public_rehearsal.EndToEndTests.test_exact_wizard_still_halts_before_author) ... ok
test_high_default_authorized_calibration (test_public_rehearsal.EndToEndTests.test_high_default_authorized_calibration) ... ok
test_low_default_authorized_calibration (test_public_rehearsal.EndToEndTests.test_low_default_authorized_calibration) ... ok
test_plan_sealed_before_bundle_and_no_grant_no_author (test_public_rehearsal.EndToEndTests.test_plan_sealed_before_bundle_and_no_grant_no_author) ... ok
test_public_mode_blocks_before_any_requirement_or_author (test_public_rehearsal.EndToEndTests.test_public_mode_blocks_before_any_requirement_or_author) ... ok
test_restart_configuration_substitution_denied (test_public_rehearsal.EndToEndTests.test_restart_configuration_substitution_denied) ... ok
test_unsupported_structure_visibly_fails (test_public_rehearsal.EndToEndTests.test_unsupported_structure_visibly_fails) ... ok
test_all_mapping_boundaries_and_preservation (test_public_rehearsal.MappingTests.test_all_mapping_boundaries_and_preservation) ... ok
test_duplicate_context_and_domains_reject (test_public_rehearsal.MappingTests.test_duplicate_context_and_domains_reject) ... ok
test_extra_obligation_never_dropped (test_public_rehearsal.MappingTests.test_extra_obligation_never_dropped) ... ok
test_inadequacy_preserved (test_public_rehearsal.MappingTests.test_inadequacy_preserved) ... ok
test_near_miss_mutations_reject (test_public_rehearsal.MappingTests.test_near_miss_mutations_reject) ... ok
test_profile_declares_small_scope (test_public_rehearsal.MappingTests.test_profile_declares_small_scope) ... ok
test_activation_does_not_override_model_qualification (test_public_rehearsal.VerificationFreezeTests.test_activation_does_not_override_model_qualification) ... ok
test_ai_verifier_candidate_remains_untrusted (test_public_rehearsal.VerificationFreezeTests.test_ai_verifier_candidate_remains_untrusted) ... ok
test_all_supported_external_calibrations (test_public_rehearsal.VerificationFreezeTests.test_all_supported_external_calibrations) ... ok
test_containment_filesystem_and_network (test_public_rehearsal.VerificationFreezeTests.test_containment_filesystem_and_network) ... ok
test_coverage_assertion_without_observation_rejects (test_public_rehearsal.VerificationFreezeTests.test_coverage_assertion_without_observation_rejects) ... ok
test_freeze_drift_and_requirement_blind_eligibility (test_public_rehearsal.VerificationFreezeTests.test_freeze_drift_and_requirement_blind_eligibility) ... ok
test_runtime_failure_distinct (test_public_rehearsal.VerificationFreezeTests.test_runtime_failure_distinct) ... ok
test_timeout_is_containment_failure (test_public_rehearsal.VerificationFreezeTests.test_timeout_is_containment_failure) ... ok

----------------------------------------------------------------------
Ran 33 tests in 35.906s

OK
```

### `python -m unittest discover -s benchmark/evaluation -p test_benchmark_documents_v1.py -v`

Exit code: 0

```text
test_adapter_canonical_round_trip (test_benchmark_documents_v1.DocumentQualification.test_adapter_canonical_round_trip) ... ok
test_adapter_does_not_call_support (test_benchmark_documents_v1.DocumentQualification.test_adapter_does_not_call_support) ... ok
test_ai_independent_extraction (test_benchmark_documents_v1.DocumentQualification.test_ai_independent_extraction) ... ok
test_ambiguous_assembly_rejects (test_benchmark_documents_v1.DocumentQualification.test_ambiguous_assembly_rejects) ... ok
test_conflicting_obligation (test_benchmark_documents_v1.DocumentQualification.test_conflicting_obligation) ... ok
test_deterministic_contract_identity (test_benchmark_documents_v1.DocumentQualification.test_deterministic_contract_identity) ... ok
test_deterministic_ordering (test_benchmark_documents_v1.DocumentQualification.test_deterministic_ordering) ... ok
test_document_identity_is_canonical (test_benchmark_documents_v1.DocumentQualification.test_document_identity_is_canonical) ... ok
test_duplicate_document_id (test_benchmark_documents_v1.DocumentQualification.test_duplicate_document_id) ... ok
test_explicit_empty_set_permitted (test_benchmark_documents_v1.DocumentQualification.test_explicit_empty_set_permitted) ... ok
test_identical_duplicate_obligation_rejected (test_benchmark_documents_v1.DocumentQualification.test_identical_duplicate_obligation_rejected) ... ok
test_incomplete_synthetic_lifecycle (test_benchmark_documents_v1.DocumentQualification.test_incomplete_synthetic_lifecycle) ... ok
test_independent_schema_payload_rejections (test_benchmark_documents_v1.DocumentQualification.test_independent_schema_payload_rejections) ... ok
test_malformed_configuration_is_not_support_gap (test_benchmark_documents_v1.DocumentQualification.test_malformed_configuration_is_not_support_gap) ... ok
test_malformed_obligation (test_benchmark_documents_v1.DocumentQualification.test_malformed_obligation) ... ok
test_malformed_payload (test_benchmark_documents_v1.DocumentQualification.test_malformed_payload) ... ok
test_malformed_synthetic_lifecycle (test_benchmark_documents_v1.DocumentQualification.test_malformed_synthetic_lifecycle) ... ok
test_metadata_stability (test_benchmark_documents_v1.DocumentQualification.test_metadata_stability) ... ok
test_missing_required_role (test_benchmark_documents_v1.DocumentQualification.test_missing_required_role) ... ok
test_multiple_documents (test_benchmark_documents_v1.DocumentQualification.test_multiple_documents) ... ok
test_no_b02_access (test_benchmark_documents_v1.DocumentQualification.test_no_b02_access) ... ok
test_no_b03_access (test_benchmark_documents_v1.DocumentQualification.test_no_b03_access) ... ok
test_no_benchmark_specific_filename_behavior (test_benchmark_documents_v1.DocumentQualification.test_no_benchmark_specific_filename_behavior) ... ok
test_public_non_heldout_seed_bank_adaptation (test_benchmark_documents_v1.DocumentQualification.test_public_non_heldout_seed_bank_adaptation) ... ok
test_references_intentionally_not_supported (test_benchmark_documents_v1.DocumentQualification.test_references_intentionally_not_supported) ... ok
test_schema_validation (test_benchmark_documents_v1.DocumentQualification.test_schema_validation) ... ok
test_simple_one_obligations_document (test_benchmark_documents_v1.DocumentQualification.test_simple_one_obligations_document) ... ok
test_strict_json_rejection (test_benchmark_documents_v1.DocumentQualification.test_strict_json_rejection) ... ok
test_supported_synthetic_static_pipeline (test_benchmark_documents_v1.DocumentQualification.test_supported_synthetic_static_pipeline) ... ok
test_unknown_obligation_is_not_silently_dropped (test_benchmark_documents_v1.DocumentQualification.test_unknown_obligation_is_not_silently_dropped) ... ok
test_unknown_role_rejects (test_benchmark_documents_v1.DocumentQualification.test_unknown_role_rejects) ... ok
test_unsupported_synthetic_static_pipeline (test_benchmark_documents_v1.DocumentQualification.test_unsupported_synthetic_static_pipeline) ... ok
test_unsupported_version (test_benchmark_documents_v1.DocumentQualification.test_unsupported_version) ... ok

----------------------------------------------------------------------
Ran 33 tests in 0.864s

OK
```

### `python -m unittest discover -s benchmark/harness -p test_baseline.py -v`

Exit code: 0

```text
test_lifecycle_filters_and_failures (test_baseline.BaselineOracle.test_lifecycle_filters_and_failures) ... ok
test_migration_and_corruption (test_baseline.BaselineOracle.test_migration_and_corruption) ... ok
test_overdue_boundary_fixture (test_baseline.BaselineOracle.test_overdue_boundary_fixture) ... ok

----------------------------------------------------------------------
Ran 3 tests in 4.221s

OK
```

## Working tree after checks (before snapshot publication)

```text
 M AGENTS.md
 M README.md
 M benchmark/README.md
 M docs/agent-workflow.md
 M docs/decisions.md
 M docs/project-overview.md
 M docs/research-log.md
?? docs/research-workflow-r5.96.md
?? src/lykoi_research/__init__.py
?? src/lykoi_research/snapshot.py
```

- Git metadata exit codes (HEAD / before / after): 0 / 0 / 0
- Check summary: ALL SELECTED CHECKS PASSED
- Finished (UTC): 2026-10-06T18:03:51.083695+00:00

Refresh immediately before eventual B03 access. Preserve relevant dirty-tree changes alongside this record.
At first access mark B03 exposed; record the first terminal result before any B03-informed Lykoi development.
