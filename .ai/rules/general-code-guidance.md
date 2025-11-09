---
alwaysApply: true
---

# General Code Organization Guidelines

## Method Ordering and Logical Flow

### Principle: Public API First (Discoverability)
- Public API methods and properties should appear early in the class, immediately after initialization.
- This allows readers to quickly understand what the class does and how to use it.
- Supporting implementation details (utilities, helpers) appear below the public API.
- Within each section, methods still follow "Dependencies Before Dependents" ordering.

### Principle: Group by Purpose, Not Alphabetically
- Organize code into logical sections with clear separators:
  1. **Initialization** - `__init__` and setup
  2. **Public API (methods and properties)** - User-facing surfaces, public methods, and any public properties. This includes artifact-creation methods that are first-class method calls used by maintainers/users.
  3. **Utilities (helpers and properties)** - Low-level, reusable helpers (format conversions, transformations, etc.) and internal/lazy properties
  4. **Domain Helpers** - Domain-specific business logic helpers (in dependency order)
- Properties follow the same grouping principle as methods: public properties belong with Public API; internal/utility properties belong with utilities.
- Use section headers/banners where helpful to delineate groups; customize headings to the class/module. Example (illustrative only):
  ```
  # ============================================================================
  # Initialization
  # ============================================================================

  # ============================================================================
  # Public API (methods and properties)
  # ============================================================================

  # ============================================================================
  # Utilities (helpers and properties)
  # ============================================================================

  # ============================================================================
  # Domain Helpers
  # ============================================================================
  ```
- Within each section, methods follow "Dependencies Before Dependents": dependencies (methods used by others) appear before dependents (methods that use them).

### Principle: Public API Visibility
- Public API methods (user-facing methods) should be discoverable and appear early in the class.
- Supporting implementation details (utilities, helpers, artifact creation) appear below, organized by dependency relationships within their sections.
- This ordering prioritizes discoverability while maintaining logical dependency flow within implementation sections.

### Principle: Acceptable Nesting
- Nested functions are acceptable when they:
  - Are only used within a single method
  - Share local state with the parent method
  - Would require passing many parameters if extracted
- Prefer extraction to instance/static methods when a helper is reused across multiple methods.

### Principle: Lightweight Instantiation and Lazy Indexing
- **MANDATORY**: Do not perform expensive operations (indexing, file I/O, network calls) in `__init__`
- **Terminology Clarification**:
  - **Initialization/Instantiation**: Creating the object instance (`__init__`) - should be lightweight
  - **Indexing**: Computing potentially large and complex intermediate structures to aid accurate and fast subsequent retrieval - should happen lazily
- **Separation of Concerns**: Separate indexing time (when intermediate structures are computed) from retrieval/usage time (when they are used)
- Perform expensive operations lazily (on first access) via properties or in retrieval methods
- This ensures fast instantiation and avoids side effects during import
- **Pattern**: For cases involving indexing resources and then using them, use an explicit intermediate helper method like `_get_or_create_<index-or-something-else-specific>()` that handles lazy indexing logic and returns the needed content. This is more disciplined than directly calling `index()` in retrieval methods.
- **Example**: A resource's `index()` method (which computes intermediate structures) should be called lazily via an intermediate helper method (e.g., `_get_or_create_section_index()`), not directly in retrieval methods or in `__init__`

## Class Constants and Initialization Defaults

### Principle: Extract Initialization Defaults as Class Constants
- **MANDATORY**: Default values used in `__init__` method parameters should be defined as class constants (not hardcoded in the method signature).
- This improves clarity, maintainability, and makes defaults discoverable and reusable.
- Class constants for initialization defaults should:
  - Be defined at the class level (before `__init__`)
  - Follow explicit naming conventions (e.g., `DEFAULT_RESOURCE_TYPE_STR: str`, `DEFAULT_PDF_FILE_NAME_STR: str`)
  - Include type annotations for clarity
  - Be referenced in `__init__` method signatures and implementations
- **Examples of good practice**:
  ```python
  class MyResource:
      DEFAULT_RESOURCE_TYPE_STR: str = 'my-resource-type'
      DEFAULT_RESOURCE_ID_STR: str = 'my-resource-id'
      DEFAULT_CONFIG_FILE_NAME_STR: str = 'config.yml'

      def __init__(self,
                   resource_type: str = DEFAULT_RESOURCE_TYPE_STR,
                   resource_id: str = DEFAULT_RESOURCE_ID_STR,
                   **kwargs):
          # Use constants in implementation
          config_path = Path(__file__).parent / self.DEFAULT_CONFIG_FILE_NAME_STR
  ```
- **Examples of bad practice** (DO NOT USE):
  ```python
  class MyResource:
      def __init__(self,
                   resource_type: str = 'my-resource-type',  # ❌ Hardcoded default
                   resource_id: str = 'my-resource-id',      # ❌ Hardcoded default
                   **kwargs):
          default_pdf = Path(__file__).parent / "file.pdf"  # ❌ Hardcoded in method
  ```
- Benefits:
  - **Clarity**: Defaults are visible at class level, not buried in method signatures
  - **Maintainability**: Single source of truth for default values
  - **Reusability**: Constants can be referenced elsewhere in the class
  - **Discoverability**: Easy to find and understand all class defaults

## Naming Conventions

### Principle: Internal Utilities Use Leading Underscore
- Utility/helper methods and properties that are not part of the public API should use a leading underscore (e.g., `_helper_method`, `_internal_property`).
- This clearly distinguishes internal implementation details from public-facing surfaces.
- Public API methods should not have leading underscores.

### Principle: Explicit Critical Distinctions in Variable Names and Types (CLARITY OVER BREVITY)
- **MANDATORY**: When a distinction is **critical for correctness** (like 0-based vs 1-based indexing, signed vs unsigned, string vs integer representations, metadata vs footer labels, etc.), make it **explicit and unambiguous** in both the variable/constant name and type annotations.
- **Apply to ALL names**: variables, function parameters, return values, constants, class attributes, and properties.
- **CLARITY OVER BREVITY**: Prefer explicit, unambiguous names over short, ambiguous ones. Every reader should immediately understand the type and meaning without consulting documentation or inferring from context.
- **Examples of good explicit naming**:
  - `index_1_based: int` rather than `index: int` (when 1-based indexing is crucial)
  - `start_index_1_based: int`, `end_index_1_based: int` rather than `start_index: int`, `end_index: int`
  - `array_index_0_based: int` vs `position_1_based: int` when both are needed
  - `identifier_string: str` (e.g., `"5.1"`) rather than `identifier: str` when the format matters
  - `display_label_string: str` vs `internal_id_string: str` vs `numeric_id_int: int` to distinguish different representations of the same logical entity
  - `SECTION_5_START_PAGE_1_BASED_INT: int = 48` rather than `SECTION_5_START_PAGE = 48` (makes it clear it's a 1-based integer, not a string or 0-based)
  - `footer_label_string: str` vs `metadata_label_string: str` vs `integer_page_1_based: int` when multiple page number types exist
- **Examples of bad ambiguous naming** (DO NOT USE):
  - `page: int` (unclear: 0-based or 1-based? integer or string representation?)
  - `start_page: int` (unclear: which page number system?)
  - `section_number: str` (unclear: what format? dotted-numeric? plain number? identifier?)
  - `SECTION_START_PAGE = 48` (unclear: integer or string? which page number system?)
- This makes the code self-documenting and reduces bugs from index confusion, type confusion, and format mismatches.
- Apply this principle especially when converting between different indexing systems, number formats, or representation types (e.g., converting 1-based positions to 0-based array indices, or between string identifiers and integer IDs).
- **When in doubt, be MORE explicit, not less.**

## Benefits
- **Discoverability**: Public API is immediately visible at the top of the class, allowing readers to quickly understand what the class does
- **Readability**: Clear separation between public interface and implementation details; within each section, dependencies appear before dependents
- **Maintainability**: Clear separation between public API, helpers, and domain logic
- **Debugging**: When diving into implementation, dependency ordering within sections makes execution flow easier to trace
