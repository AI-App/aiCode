---
description: review written rules and implemented code against higher-level principles/rules and architectures/designs
alwaysApply: false
---

# Rules and Code Review Process

## Review Approach: High-Level to Low-Level

### Principle: Progressive Refinement
- Start from the **most meta rules** (how to write rules, general coding principles)
- Progressively move to **increasingly specific rules** (domain-specific rules, implementation-specific rules)
- At each level, review **before** moving to the next level
- This ensures higher-level principles are established and stable before applying them to specific cases

### Review Scope at Each Level

For each rule file or implementation being reviewed, check:

#### 1. Internal Consistency
- **Within the rule/implementation itself**: Are there contradictions, redundancies, or gaps?
- Are concepts defined consistently throughout?
- Are examples aligned with stated principles?
- Is terminology used consistently (e.g., "section number" vs "dotted-numeric section-numbering string")?

#### 2. Consistency with Higher Levels
- **Against all higher-level rules already reviewed**: Does this rule/implementation align with meta rules and general principles?
- Are there violations of established principles (e.g., CLARITY OVER BREVITY, separation of concerns)?
- Are there gaps where higher-level principles should apply but aren't mentioned?
- **For rule files**: Verify alignment with `AI-rule-writing-for-code-guidance.md` (e.g., light usage of canonical/popular dependencies like PyPDF or pandas is acceptable when they materially clarify intent)

#### 3. Mutual Consistency (for Rule-Implementation Pairs)
- **Between rule files and their corresponding implementations**: Does the implementation follow the rule?
- Does the rule accurately describe what the implementation does?
- Are there discrepancies in terminology, approach, or requirements?

## Review Process Steps

### Step 1: Review Meta Rules
- Review the most abstract rules first (e.g., "AI Rule Writing Guidelines" - see `AI-rule-writing-for-code-guidance.md`, "General Code Organization")
- Check for internal consistency and clarity
- Ensure principles are well-defined and non-contradictory

### Step 2: Review General Rules
- Review domain-agnostic general rules (e.g., "General Code Organization Guidelines")
- Check alignment with meta rules (including `AI-rule-writing-for-code-guidance.md`)
- Check for internal consistency
- Identify any gaps or conflicts with meta rules

### Step 3: Review Specific Rules
- Review domain-specific or implementation-specific rules
- Check alignment with meta rules (including `AI-rule-writing-for-code-guidance.md`) and general rules
- Check for internal consistency
- Identify redundancies that can be consolidated
- Ensure terminology is consistent and unambiguous
- **Note**: Light usage of canonical/popular dependencies (like PyPDF, pandas) in rule examples is acceptable per `AI-rule-writing-for-code-guidance.md` when they materially clarify intent

### Step 4: Review Implementations
- Review code implementations against their corresponding rules
- Check alignment with all applicable higher-level rules
- Verify that implementations follow stated principles
- Check for consistency in naming, structure, and organization

### Step 5: Refactor and Align
- Fix identified issues in order (meta → general → specific → implementations)
- Apply principles consistently (e.g., extract constants, use explicit naming, separate concerns)
- Update both rules and implementations to maintain consistency

## Key Principles to Apply During Review

### For Rule Files
When reviewing rule files, verify alignment with `AI-rule-writing-for-code-guidance.md`:
- Rules should stay above code-level implementation details, but light usage of canonical/popular dependencies (e.g., PyPDF, pandas) is acceptable when they materially clarify intent
- Rules should specify what must be true rather than how to implement
- Illustrative examples should be minimal and non-normative
- Rules should use placeholders unless a widely-used dependency materially clarifies intent

### For Code Implementations
When reviewing code, verify that implementations follow these key principles:

- **CLARITY OVER BREVITY**: Prioritize clear, explicit code over terse or clever implementations
- **Public API First**: Organize code with public interfaces first, followed by implementation details
- **Extract Constants**: Use named constants instead of magic numbers or strings
- **Internal Utilities Use Leading Underscore**: Mark non-public methods and variables with a leading underscore

Additionally, verify adherence to methodology-specific principles:

- **Separation of Concerns**: Each rule file should focus on a single, well-defined concern. Avoid duplicating guidance that belongs in other rule files; instead, cross-reference them.
- **Lightweight Instantiation**: Keep constructors simple and fast. Defer expensive operations until they're actually needed.
- **Lazy Loading**: Load resources and compute expensive values only when they're first accessed, not during initialization.

## Common Issues to Identify

### Redundancy and Repetition
- Look for repeated content that can be consolidated
- Check for unfinished editing/change-tracking artifacts
- Identify overlapping sections that should be merged

### Terminology Inconsistency
- Check for inconsistent use of terms (e.g., "section number" vs "dotted-numeric section-numbering string")
- Ensure terminology aligns with the domain and is unambiguous

### Rule-Implementation Mismatch
- Verify that implementations follow their rule files
- Check that rule files accurately describe implementations
- Identify gaps where rules don't cover implementation details

### Principle Violations

#### For Rule Files
- Check for violations of `AI-rule-writing-for-code-guidance.md` (e.g., overly prescriptive implementation details, missing flexibility for canonical dependencies)
- Verify that rules stay above code-level details while allowing illustrative examples with popular dependencies when they clarify intent

#### For Code Implementations
- Check for violations of principles defined in `code-guidance-general.mdc` (e.g., hardcoded defaults instead of class constants, ambiguous naming instead of explicit distinctions, missing leading underscores on internal utilities)
- Check for violations of methodology-specific principles (e.g., upfront directory creation instead of lazy initialization)
- Verify that all mandatory principles are applied consistently

### Missing Coverage
- Identify gaps where higher-level principles should apply but aren't mentioned
- Check for edge cases or special handling that should be documented

### Code Quality Checks
- **Unused Code**: Check for unused imports, unused private methods, unused query files, and unused constants that should be removed
- **Database Efficiency**: Check for loops of database operations that indicate potentially inefficient database handling (N+1 query problems) that should be optimized or at least raised for mutual discussion

## Review Output

When reviewing, identify:
1. **Conflicts**: Contradictory statements or principles
2. **Gaps**: Missing coverage of principles or requirements
3. **Redundancies**: Repeated content that should be consolidated
4. **Inconsistencies**: Terminology, naming, or structural inconsistencies
5. **Proposed Fixes**: Concrete changes to resolve identified issues

## Example Review Flow

```
1. Review meta-rule: AI-rule-writing-for-code-guidance.md
   → Check internal consistency
   → Refine if needed

2. Review general rule: code-guidance-general.mdc
   → Check internal consistency
   → Check alignment with meta-rule (AI-rule-writing-for-code-guidance.md)
   → Refine both if needed

3. Review specific rule: ASHRAE-Guideline36-document.mdc
   → Check internal consistency
   → Check alignment with meta and general rules
   → Verify light usage of canonical dependencies (PyPDF) is acceptable per meta-rule
   → Remove redundancies
   → Fix terminology

4. Review implementation: ashrae_guideline36_document_resource.py
   → Check alignment with specific rule
   → Check alignment with general rules
   → Refactor to match principles
   → Update both rule and implementation for consistency
```
