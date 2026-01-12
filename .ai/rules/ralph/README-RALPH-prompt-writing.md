---
description: writing README-RALPH.md prompt files
alwaysApply: false
---

# Writing README-RALPH.md Prompt Files

This guide provides best practices for writing `README-RALPH.md` prompt files that drive Ralph autonomous development loops. These files serve as the persistent prompt that gets fed to the AI agent in each iteration.

## Core Principles

### 1. Iteration > Perfection
Don't aim for perfect on first try. Let the loop refine the work.

### 2. Failures Are Data
"Deterministically bad" means failures are predictable and informative. Use them to tune prompts.

### 3. Operator Skill Matters
Success depends on writing good prompts, not just having a good model.

### 4. Persistence Wins
Keep trying until success. The loop handles retry logic automatically.

## Essential Structure

A well-structured `README-RALPH.md` should include:

```markdown
# [Task Name]

## Overview
[Brief description of what needs to be built/fixed/improved]

## Requirements
[Functional and non-functional requirements]

## Success Criteria
[Clear, verifiable completion criteria]

## Context
[Technical constraints, frameworks, existing patterns]

## Instructions
[Step-by-step guidance for the agent]

## Completion Signal
[How to signal completion]
```

## Best Practices

### 1. Clear Completion Criteria

**❌ Bad:**
```markdown
Build a todo API and make it good.
```

**✅ Good:**
```markdown
Build a REST API for todos.

When complete:
- All CRUD endpoints working (GET, POST, PUT, DELETE)
- Input validation in place (validate all inputs)
- Tests passing (coverage > 80%)
- README with API docs (endpoints, request/response examples)
- Output: <promise>COMPLETE</promise>
```

**Key Points:**
- Each criterion must be **objectively verifiable**
- Use checkboxes `[ ]` for trackable criteria (where supported)
- Specify measurable thresholds (e.g., "coverage > 80%")
- Include the completion signal format

### 2. Incremental Goals

**❌ Bad:**
```markdown
Create a complete e-commerce platform.
```

**✅ Good:**
```markdown
Phase 1: User authentication (JWT, tests)
- User registration endpoint
- User login endpoint
- JWT token generation and validation
- Tests for all endpoints

Phase 2: Product catalog (list/search, tests)
- Product listing endpoint
- Product search endpoint
- Product detail endpoint
- Tests for all endpoints

Phase 3: Shopping cart (add/remove, tests)
- Add item to cart
- Remove item from cart
- Get cart contents
- Tests for all endpoints

Output <promise>COMPLETE</promise> when all phases done.
```

**Key Points:**
- Break large tasks into phases
- Each phase should be completable in one context window
- Define clear boundaries between phases
- Specify testing requirements per phase

### 3. Self-Correction Mechanisms

**❌ Bad:**
```markdown
Write code for feature X.
```

**✅ Good:**
```markdown
Implement feature X following TDD:
1. Write failing tests first
2. Implement feature to make tests pass
3. Run tests
4. If any fail, debug and fix
5. Refactor if needed (tests must still pass)
6. Repeat until all green
7. Output: <promise>COMPLETE</promise>
```

**Key Points:**
- Include explicit feedback loops (test → fix → test)
- Specify what to do when tests fail
- Define refactoring criteria
- Include iteration instructions

### 4. Escape Hatches

Always include safety mechanisms to prevent infinite loops:

```markdown
## Escape Hatches

If stuck after 15 iterations:
- Document what's blocking progress
- List what was attempted
- Suggest alternative approaches
- Output: <promise>BLOCKED</promise>
```

**Key Points:**
- Set iteration limits (use `--max-iterations` flag where supported)
- Define "stuck" conditions
- Specify what to do when stuck
- Include alternative completion signals (BLOCKED, GUTTER, etc.)

### 5. Context and Constraints

Provide clear technical context:

```markdown
## Project Setup

- **Project Root Directory**: [path]
- **Python Executable**: [command, e.g., `uv run python`]
- **Files & Folders Ralph Can Modify**: [explicit list]

## Context

- Use Express.js for the API
- Store users in memory (no database needed for MVP)
- Follow REST conventions
- Use TypeScript
- Existing codebase patterns: [describe patterns]

## Constraints

- Must work with existing authentication system
- Cannot modify database schema
- Must maintain backward compatibility
- Performance: < 200ms response time
```

**Key Points:**
- **Always include Project Setup section** with project root, Python executable, and allowed files/folders
- Specify technology stack
- Document existing patterns to follow
- List hard constraints
- Include performance requirements

### 6. Testing Guidelines

Be explicit about testing expectations:

```markdown
## Testing Requirements

- Write tests for NEW functionality only
- Do NOT refactor existing tests unless broken
- Focus on CORE functionality first, comprehensive testing later
- Test coverage target: > 80% for new code
- Run tests after each implementation
- If tests fail, fix them as part of current work
```

**Key Points:**
- Balance testing with implementation
- Avoid test-only loops (where supported)
- Specify coverage targets
- Define test failure handling

### 7. Status Reporting (For Supported Implementations)

Some Ralph implementations (e.g., FrankBria.Ralph-Claude-Code) require structured status reporting:

```markdown
## Status Reporting

At the end of each iteration, output:

```
---RALPH_STATUS---
STATUS: IN_PROGRESS | COMPLETE | BLOCKED
TASKS_COMPLETED_THIS_LOOP: <number>
FILES_MODIFIED: <number>
TESTS_STATUS: PASSING | FAILING | NOT_RUN
WORK_TYPE: IMPLEMENTATION | TESTING | DOCUMENTATION | REFACTORING
EXIT_SIGNAL: false | true
RECOMMENDATION: <one line summary>
---END_RALPH_STATUS---
```

Set EXIT_SIGNAL to true when:
- All items in task list are complete
- All tests are passing
- No errors or warnings
- All requirements implemented
```

## When to Use Ralph

**✅ Good for:**
- Well-defined tasks with clear success criteria
- Tasks requiring iteration and refinement (e.g., getting tests to pass)
- Greenfield projects where you can walk away
- Tasks with automatic verification (tests, linters)
- Tasks that benefit from persistent iteration

**❌ Not good for:**
- Tasks requiring human judgment or design decisions
- One-shot operations
- Tasks with unclear success criteria
- Production debugging (use targeted debugging instead)
- Tasks requiring real-time human feedback

## Template Structure

Here's a comprehensive template:

```markdown
# [Task Name]

## Overview

[2-3 sentence description of what needs to be built/fixed/improved]

## Project Setup

**MANDATORY**: Specify these basics for every README-RALPH.md:

- **Project Root Directory**: [Absolute or relative path to project root]
  - All commands must be run from this directory
  - Example: `Dana projects/Honeywell/Forge-Cognition`

- **Python Executable**: [How to run Python scripts]
  - Specify the exact command to use (e.g., `uv run python`, `python`, `python3`)
  - Specify that commands must be run from project root
  - Example: `uv run python` (run from project root directory)

- **Files & Folders Ralph Can Modify**: [Explicit list of what Ralph is allowed to change]
  - List specific files that can be modified
  - List directories where Ralph can create/write files (e.g., exercise directory)
  - Be explicit about what's allowed vs. what's off-limits
  - Example:
    - `_RALPH/` directory (Ralph exercise directory - can write whatever it wants)
    - `_RALPH/[exercise-name]/` (specific exercise directory)
    - `autonomous_facility/ontology/physical/models.py` (specific file to modify)
    - `autonomous_facility/ontology/physical/schema/models.py` (specific file to modify)

## Requirements

### Functional Requirements
1. [Requirement 1 - specific and testable]
2. [Requirement 2 - specific and testable]
3. [Requirement 3 - specific and testable]

### Non-Functional Requirements
- [Performance requirements]
- [Security requirements]
- [Scalability requirements]

## Success Criteria

The task is complete when ALL of the following are true:

1. [ ] [Verifiable criterion 1]
2. [ ] [Verifiable criterion 2]
3. [ ] [Verifiable criterion 3]

## Context

- Technology stack: [list technologies]
- Existing patterns: [describe patterns to follow]
- Related files: [list relevant files/directories]

## Constraints

- [Hard constraint 1]
- [Hard constraint 2]
- [Performance constraint]

## Implementation Approach

[Optional: Step-by-step approach if helpful]

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Testing Requirements

- [Testing approach]
- [Coverage target]
- [Test failure handling]

## Escape Hatches

If stuck after [N] iterations:
- [What to document]
- [Alternative approaches]
- [Completion signal for blocked state]

## Completion Signal

Output: <promise>COMPLETE</promise> when all success criteria are met.

[If using status reporting:]
Include status block at end of each iteration.
```

## Common Patterns

### Pattern 1: Feature Implementation

```markdown
# Implement [Feature Name]

## Overview
Add [feature description] to [system/component].

## Requirements
1. [Specific requirement 1]
2. [Specific requirement 2]

## Success Criteria
1. [ ] Feature works as specified
2. [ ] Tests pass (coverage > 80%)
3. [ ] Documentation updated

## Context
- Follow existing patterns in [directory]
- Use [framework/library] for [purpose]

## Completion Signal
<promise>COMPLETE</promise>
```

### Pattern 2: Bug Fix

```markdown
# Fix [Bug Description]

## Overview
[Describe the bug and its impact]

## Requirements
1. Bug is fixed (verified by [test/verification method])
2. No regressions introduced
3. Tests added to prevent recurrence

## Success Criteria
1. [ ] Bug no longer occurs
2. [ ] All existing tests pass
3. [ ] New tests prevent regression

## Context
- Bug occurs in [component/file]
- Related to [feature/area]

## Completion Signal
<promise>COMPLETE</promise>
```

### Pattern 3: Refactoring

```markdown
# Refactor [Component/Area]

## Overview
[Describe what needs refactoring and why]

## Requirements
1. [Refactoring goal 1]
2. [Refactoring goal 2]
3. Maintain backward compatibility

## Success Criteria
1. [ ] Code quality improved (specify metrics)
2. [ ] All tests pass
3. [ ] No functionality changes

## Context
- Current implementation: [describe]
- Target pattern: [describe]

## Completion Signal
<promise>COMPLETE</promise>
```

## Anti-Patterns to Avoid

### ❌ Vague Requirements
```markdown
# Bad
Make the code better.
```

### ❌ No Completion Criteria
```markdown
# Bad
Implement authentication.
```

### ❌ Too Large Scope
```markdown
# Bad
Build a complete e-commerce platform with payment, inventory, shipping, etc.
```

### ❌ No Escape Hatches
```markdown
# Bad
Keep trying until it works.
```

### ❌ Unclear Context
```markdown
# Bad
Use the existing code.
```

## Iteration and Refinement

Remember that `README-RALPH.md` files can and should be refined based on what you learn:

1. **After each iteration**: Review what worked and what didn't
2. **Update criteria**: Make success criteria more specific if needed
3. **Add guardrails**: Document patterns to avoid based on failures
4. **Refine scope**: Break down tasks that are too large
5. **Improve clarity**: Add examples or clarify ambiguous requirements

## References

- [Original Ralph technique](https://ghuntley.com/ralph/) - Geoffrey Huntley
- [Anthropic ralph-wiggum plugin](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)
- [Context as memory](https://ghuntley.com/allocations/) - The malloc/free metaphor
- [Context engineering](https://ghuntley.com/gutter/) - Gutter detection concepts
