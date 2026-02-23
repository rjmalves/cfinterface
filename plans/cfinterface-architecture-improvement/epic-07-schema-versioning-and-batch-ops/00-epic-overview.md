# Epic 07: Schema Versioning and Batch Operations

## Overview

This epic addresses two related consumer-facing features:

1. **Schema versioning**: The current `set_version()` mechanism is fragile -- it mutates class-level attributes, uses string comparison for version ordering, and provides no explicit contract about what changes between versions. This epic introduces a formal versioning system with explicit schema contracts.

2. **Batch operations**: Currently, consumers read files one at a time and call `set_version()` on each file class individually. For sintetizador-newave which reads 100+ files per synthesis run, this is cumbersome. A batch read API enables reading multiple files with a single version context.

## Goals

1. Introduce a `SchemaVersion` descriptor that explicitly documents what changes between versions
2. Replace the mutable class-level `set_version()` pattern with instance-level version binding
3. Provide a batch `read_many()` API on file classes for reading multiple files with shared settings
4. Add version validation to catch mismatched file format versions early

## Tickets

| Ticket     | Title                                                     | Effort |
| ---------- | --------------------------------------------------------- | ------ |
| ticket-024 | Design SchemaVersion descriptor and registry              | 3      |
| ticket-025 | Implement instance-level version binding for file classes | 3      |
| ticket-026 | Add batch read_many() API to file classes                 | 2      |
| ticket-027 | Add version validation and mismatch detection             | 2      |

## Success Criteria

- File classes support instance-level version binding (no class mutation)
- Batch read API handles 100+ files with shared version context
- Version mismatches are detected early with clear error messages
- Backward compatible with existing `set_version()` pattern (deprecated but working)
