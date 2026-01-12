# Ralph: Autonomous AI Development Loops - Index

This directory contains multiple implementations of the **Ralph Wiggum technique** - a methodology for autonomous AI development through iterative, self-referential loops. The technique is named after Ralph Wiggum from The Simpsons, embodying the philosophy of persistent iteration despite setbacks.

> **Note**: These submodules are constantly changing. This index provides links to both the online repositories and local cloned submodules for easy navigation.

## What is Ralph?

Ralph is fundamentally a **bash loop** that repeatedly feeds the same prompt to an AI agent:

```bash
while :; do cat PROMPT.md | agent ; done
```

The key insight is that **context is like memory** - when you load data into an LLM's context window, it cannot be selectively released. The only way to "free" context is to start a new conversation. Ralph deliberately rotates to fresh context before pollution builds up, with state persisting in **files and git**, not in the LLM's memory.

### Core Philosophy

> "That's the beauty of Ralph - the technique is deterministically bad in an undeterministic world."

Ralph will make mistakes. That's expected. Each mistake is an opportunity to add a "sign" (guardrail) that prevents that mistake in the future. Like tuning a guitar, you adjust Ralph until it plays the right notes.

## Implementations

### 1. **ralph-wiggum** (Anthropic/Claude-Code)

**Target**: Claude Code (claude.ai/code)
**Type**: Claude Code plugin with stop hooks

**Links**:
- **Online Repository**: [anthropics/claude-code/plugins/ralph-wiggum](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)
- **Local Submodule**: [`Anthropic/Claude-Code/plugins/ralph-wiggum/`](./Anthropic/Claude-Code/plugins/ralph-wiggum/)
- **Main Repository**: [anthropics/claude-code](https://github.com/anthropics/claude-code)

**Key Features**:
- Uses **stop hooks** to intercept Claude's exit attempts
- Creates self-referential feedback loop inside current session
- No external bash loops needed - loop happens within Claude Code
- Simple command: `/ralph-loop "task" --completion-promise "DONE"`

**Best For**: Quick iterative tasks within Claude Code, tasks requiring immediate feedback and iteration

---

### 2. **Ralph-Wiggum-Cursor** (Agrim Singh)

**Target**: Cursor IDE with cursor-agent CLI
**Type**: Cursor-specific implementation with token tracking

**Links**:
- **Online Repository**: [agrimsingh/ralph-wiggum-cursor](https://github.com/agrimsingh/ralph-wiggum-cursor)
- **Local Submodule**: [`AgrimSingh.Ralph-Wiggum-Cursor/`](./AgrimSingh.Ralph-Wiggum-Cursor/)

**Key Features**:
- **Accurate token tracking** - Parser counts actual bytes from every file read/write
- **Gutter detection** - Detects when agent is stuck (same command failed 3x, file thrashing)
- **Learning from failures** - Agent updates `.ralph/guardrails.md` with lessons
- **State in git** - Commits frequently so next agent picks up from git history
- **Branch/PR workflow** - Optionally work on a branch and open PR when complete
- **Interactive setup** - Beautiful gum-based UI for model selection and options

**Best For**: Cursor IDE users, projects requiring precise context management, long-running autonomous development tasks

---

### 3. **Ralph-Claude-Code** (Frank Bria)

**Target**: Claude Code CLI (`npx @anthropic/claude-code`)
**Type**: Full-featured autonomous development system

**Links**:
- **Online Repository**: [frankbria/ralph-claude-code](https://github.com/frankbria/ralph-claude-code)
- **Local Submodule**: [`FrankBria.Ralph-Claude-Code/`](./FrankBria.Ralph-Claude-Code/)

**Key Features**:
- **Global installation** - Install once, use everywhere (`ralph`, `ralph-setup`, `ralph-monitor`)
- **Rate limiting** - Built-in API call management (100 calls/hour, configurable)
- **Circuit breaker** - Advanced error detection with two-stage filtering
- **5-hour API limit handling** - Detects Claude's usage limit and offers wait/exit options
- **Live monitoring** - Real-time dashboard with tmux integration
- **PRD import** - Convert existing PRDs/specs to Ralph format
- **JSON output format** - Structured communication with Claude Code CLI
- **Session continuity** - Maintains context across loops with `--continue` flag
- **Comprehensive test suite** - 223 tests (100% pass rate)

**Best For**: Production autonomous development, long-running projects, teams needing monitoring and rate limiting

---

### 4. **Ralph** (SnarkTank)

**Target**: Amp (ampcode.com)
**Type**: Amp-specific implementation with PRD workflow

**Links**:
- **Online Repository**: [snarktank/ralph](https://github.com/snarktank/ralph)
- **Local Submodule**: [`SnarkTank.Ralph/`](./SnarkTank.Ralph/)

**Key Features**:
- **PRD-based workflow** - Uses structured PRD JSON format
- **Story-based execution** - Works on one user story per iteration
- **Quality checks** - Runs typecheck, lint, tests before committing
- **Browser verification** - Uses dev-browser skill for frontend stories
- **AGENTS.md updates** - Automatically updates AGENTS.md with learnings
- **Interactive flowchart** - Visual diagram explaining how Ralph works

**Best For**: Amp users, projects with structured PRDs, story-driven development, frontend-heavy projects

---

## Quick Comparison

| Feature | ralph-wiggum | Ralph-Wiggum-Cursor | Ralph-Claude-Code | SnarkTank.Ralph |
|---------|--------------|---------------------|-------------------|-----------------|
| **Target Platform** | Claude Code (web) | Cursor IDE | Claude Code CLI | Amp |
| **Installation** | Plugin | Per-project | Global | Per-project |
| **Token Tracking** | ❌ | ✅ (accurate) | ❌ | ❌ |
| **Rate Limiting** | ❌ | ❌ | ✅ | ❌ |
| **Circuit Breaker** | ❌ | ❌ | ✅ | ❌ |
| **Monitoring** | ❌ | ✅ (activity.log) | ✅ (tmux dashboard) | ❌ |
| **PRD Import** | ❌ | ❌ | ✅ | ✅ (via skills) |
| **Guardrails/Learning** | ❌ | ✅ (guardrails.md) | ❌ | ✅ (progress.txt) |
| **Git Integration** | Basic | ✅ (commits frequently) | Basic | ✅ (feature branches) |
| **Test Suite** | ❌ | ❌ | ✅ (223 tests) | ❌ |
| **Session Continuity** | ✅ (in-session) | ❌ | ✅ (--continue flag) | ❌ |
| **Browser Testing** | ❌ | ❌ | ❌ | ✅ (dev-browser skill) |

## Original Source

All implementations are based on [Geoffrey Huntley's Ralph technique](https://ghuntley.com/ralph/).

## Additional Resources

- [Original Ralph article](https://ghuntley.com/ralph/) - Geoffrey Huntley
- [Context as memory](https://ghuntley.com/allocations/) - The malloc/free metaphor
- [Context engineering](https://ghuntley.com/gutter/) - Gutter detection concepts

## Directory Structure

```
.submodules/Ralph/
├── INDEX.md (this file)
├── Anthropic/Claude-Code/plugins/ralph-wiggum/     # Claude Code plugin
├── AgrimSingh.Ralph-Wiggum-Cursor/                 # Cursor IDE implementation
├── FrankBria.Ralph-Claude-Code/                    # Claude Code CLI (full-featured)
└── SnarkTank.Ralph/                                # Amp implementation
```

Each subdirectory contains its own README with detailed usage instructions.
