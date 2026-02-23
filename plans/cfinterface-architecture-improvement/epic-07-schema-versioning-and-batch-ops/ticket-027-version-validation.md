# ticket-027 Add Version Validation and Mismatch Detection

> **[OUTLINE]** This ticket requires refinement before execution.
> It will be refined with learnings from earlier epics.

## Objective

Add validation logic that detects when a file's content does not match its declared schema version, providing early and clear error messages instead of silent data corruption. This addresses the pain point where NEWAVE version updates (e.g., v29.4) broke sintetizador without any diagnostic information.

## Anticipated Scope

- **Files likely to be modified**: `cfinterface/versioning/validation.py` (new), `cfinterface/reading/registerreading.py`, `cfinterface/reading/blockreading.py`, `cfinterface/reading/sectionreading.py`
- **Key decisions needed**:
  - What constitutes a "version mismatch" -- unexpected register types, missing expected sections, extra fields?
  - Whether validation is opt-in (explicit call) or automatic (during read)
  - Whether to raise an exception or return a validation result object
- **Open questions**:
  - Can version be auto-detected from file content (header sniffing)?
  - What metadata is available in the file to determine its version?
  - Should validation produce a diff of expected vs. actual schema?

## Dependencies

- **Blocked By**: ticket-024
- **Blocks**: None

## Effort Estimate

**Points**: 2
**Confidence**: Low (will be re-estimated during refinement)
