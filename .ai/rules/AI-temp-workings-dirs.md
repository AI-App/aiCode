---
alwaysApply: true
---

# AI Temporary Workings Directories

## Practice

When AI assistants create temporary workings files (e.g., review documents, analysis reports, temporary scripts), place them in the appropriate `.ai/tmp/` directory within the relevant project or subdirectory.

## Directory Structure

- **Project root**: `.ai/tmp/` for project-wide temporary workings
- **Subdirectories**: `<subdir>/.ai/tmp/` for subdirectory-specific temporary workings
- Create the directory if it doesn't exist

## Examples

- Review documents: `.ai/tmp/REVIEW.md`
- Analysis reports: `.ai/tmp/ANALYSIS.md`
- Temporary scripts: `.ai/tmp/temp-script.py`
- Subdirectory-specific: `test/20250924-cases/.ai/tmp/analysis.md`

## Rationale

- Keeps temporary files organized and separate from permanent code/rules
- Makes it clear which files are temporary workings vs. permanent artifacts
- Easy to clean up when no longer needed
- Maintains clean project structure
