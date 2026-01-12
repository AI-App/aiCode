---
alwaysApply: false
---

# Meta-Rule: Coupling Process-Specifying Rules with Process-Implementing Artifacts

## Purpose

Certain workflows require both:
1. **Process-specifying rules** – documents that define conventions, structure, and requirements.
2. **Process-implementing artifacts** – living documents or files (memos, email logs, etc.) that apply those rules in daily work.

To guarantee consistent execution and alignment, these paired documents must enforce a tight coupling: anyone touching the process-implementing artifact must first read (or re-read) the governing process rule.

## Meta Requirements

For every such paired workflow:
1. **Process-Specifying Rule Responsibilities**
   - Clearly describe the workflow, formatting conventions, and maintenance expectations.
   - Explicitly state that the rule belongs to this meta pattern.
   - Require any corresponding artifacts to cite this rule and mandate reading it before further work.

2. **Process-Implementing Artifact Responsibilities**
   - Cite the governing process rule near the top of the document with **FORCEFUL, IMPOSSIBLE-TO-MISS LANGUAGE** (e.g., "⚠️ DO THIS IMMEDIATELY: READ THE PROCESS DOCUMENT NOW ⚠️").
   - Include a **MANDATORY READING REQUIREMENT** that uses strong, directive language (e.g., "STOP. DO NOT PROCEED...", "IMMEDIATE ACTION REQUIRED", "NO EXCEPTIONS") instructing contributors to read the process rule immediately before making ANY changes, edits, summaries, or other actions.
   - Require explicit confirmation that contributors have read the rule and understand the requirements before proceeding with any work.
   - Make it clear that this is not optional, not a suggestion, and that there are zero exceptions to this requirement.

## Examples

| Process-Specifying Rule | Process-Implementing Artifact(s) | Notes |
| --- | --- | --- |
| `project/.ai/rules/!-META-PROCESS/work-memos-for-seamless-relay.md` | `project/.ai/work-memos/MEMO-#0-main.md`, `project/subproject/.ai/MEMO.md`, etc. | Work memos must cite the rule, display the mandatory automation string ("READ … NOW before proceeding."), and require re-reading before any action. |
| `project/.ai/rules/!-ADMIN/emails.md` | `project/subproject/!-Comms-and-Discussions/2025.11-date project emails.md`, etc. | Email chains must cite the rule, display the mandatory automation string, and require re-reading before any action. |
| `aiCode/.ai/rules/ralph/README-RALPH-prompt-writing.md` | `project/_RALPH/*/README-RALPH.md` | README-RALPH.md files must cite the rule, display the mandatory reading requirement, and require explicit confirmation before proceeding. |

## ⚠️ CRITICAL ENFORCEMENT REQUIREMENT ⚠️

**FOR AI ASSISTANTS AND ALL CONTRIBUTORS:**

When you encounter a process-implementing artifact (e.g., a work memo) that references a process-specifying rule, you MUST:

1. **IMMEDIATELY STOP** all work on that artifact
2. **IMMEDIATELY READ** the referenced process rule using a concrete tool call (e.g., `read_file()`)
3. **EXPLICITLY CONFIRM** that you have read the rule and understand the requirements
4. **ONLY THEN** proceed with any work on the artifact

**THIS IS NOT OPTIONAL. THIS IS NOT A SUGGESTION. THERE ARE ZERO EXCEPTIONS.**

Failure to follow this requirement breaks the coupling between process rules and artifacts, creates misalignment, and violates the fundamental principle of this meta-rule.

## Rationale

- Prevents misalignment between methodology and implementation.
- Ensures process updates propagate instantly to all working documents.
- Enables automation hooks: process-implementing artifacts must surface an easily searchable mandatory string (e.g., `MANDATORY: READ <rule> NOW before proceeding.`) so AI assistants or tooling can block work until the governing rule has been re-read.
- Reduces onboarding overhead by forcing contributors (especially AI assistants) to review the governing rule before taking any action on artifacts.
- Creates a repeatable pattern for future workflows that rely on governed living documents.

## When to Apply

- Whenever a rule defines how another document should be maintained (e.g., memos, email logs, run-books, ticket summaries).
- When creating new process-driven artifacts to ensure they are tightly coupled to their governing rules from day one.
