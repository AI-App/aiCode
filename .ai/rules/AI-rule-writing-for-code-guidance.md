---
description: writing AI rules for code guidance
alwaysApply: false
---

# AI Rule Writing Guidelines (for Code Guidance)

## Principle: Stay Above Code-Level Implementation Details (with Minimal Illustrative Examples)
- Default stance: write rules as constraints, requirements, and invariants — not step-by-step code instructions.
- Specify what must be true (inputs/outputs, contracts, boundaries, file placement, packaging) rather than how to implement.
- Prefer domain-level policies (runtime vs. rebuild, performance, determinism, idempotency) over library calls or method names.
- Illustrative examples are allowed to improve clarity — keep them concise and clearly marked as non-normative. They must:
  - be minimal and focused on clarifying the rule (not full implementations),
  - avoid prescribing specific APIs, function names, or control flow,
  - allow common dependencies when they aid clarity (e.g., pandas), but do not imply mandates; prefer placeholders unless a widely-used dependency materially clarifies intent,
  - use placeholders when naming might imply prescription (e.g., `SomeResource`, `some_method`).
- When necessary, separate "Runtime Contract" (what users get) from "Engineering/Rebuild" (internal refresh process) and keep both high level.

## Principle: Living Documents
- Rule files are living documents that evolve over time. Do not use qualifiers like "(Updated)", "(Revised)", "(Concise)", "(New)", etc. in titles or content.
- These qualifiers imply a static state or version, which contradicts the continuous improvement nature of the rules.
- Simply update the content directly; the file modification timestamp provides version context.

## Principle: Document Structure Coherence
- When writing or updating rule files, review and maintain logical header hierarchy (H1, H2, H3, etc.).
- Ensure sections are nested at the appropriate level based on their logical relationship to parent sections.
- Top-level concepts should be H2 under the main H1 title; subsections should be H3, etc.
- **Critical**: After every update, verify that:
  - Headers are at the correct logical level (not nested too deeply or too shallowly)
  - Sections that apply to the entire document are at H2 level, not nested under specific topics
  - The outline/structure remains coherent and logical
- This prevents structural drift where content gets misplaced due to incorrect nesting during edits.
