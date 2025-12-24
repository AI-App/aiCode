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

## KISS and YAGNI Principles: Simplicity and Minimalism

### Principle: YAGNI - You Aren't Gonna Need It
- **MANDATORY**: Do not add features, parameters, or complexity until they are actually needed.
- **Start minimal**: Begin with the simplest implementation that solves the current problem.
- **Resist speculation**: Don't add "nice to have" features or parameters "just in case" they might be useful later.
- **Evidence required**: Only add complexity when there is concrete evidence of need (actual usage, explicit requirements).
- **Question every addition**: Before adding any optional parameter or feature, ask:
  - Is this actually being used right now?
  - Is there concrete evidence this will be needed?
  - Can we add it later if/when it's actually needed?
  - What's the cost of maintaining this if it's never used?
- **Example of good practice (YAGNI applied)**:
  ```python
  # Clean API - only what's needed
  def run_query(self, cypher_query: str, parameters: Optional[Dict] = None) -> Result:
      """Execute query with config database."""
      mode = self._infer_query_mode(cypher_query)
      # Uses self.config.database by default
      return self.execute_write(query, params) if mode == "WRITE" else self.execute_read(query, params)

  # If database override is needed later, add it to mid-level methods:
  result = manager.execute_read(query, params, database="system")  # Override when actually needed
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  # ❌ Premature optimization - database override not used anywhere
  def run_query(self, cypher_query: str, parameters: Optional[Dict] = None,
                database: Optional[str] = None) -> Result:  # ❌ YAGNI violation
      """Execute query."""
      mode = self._infer_query_mode(cypher_query)
      db = database or self.config.database  # Added complexity for zero usage
      # ...
  ```
- **When to add features**:
  - When there's actual current usage or immediate concrete requirement
  - When the cost of not having it now is higher than the cost of adding it later
  - When it's a fundamental architectural decision that can't be easily added later
- **Benefits of YAGNI**:
  - Simpler, cleaner APIs that are easier to understand
  - Less code to maintain and test
  - Faster development (focus on what's needed)
  - Easier to change (less coupling, fewer assumptions)
  - Better discoverability (fewer parameters to understand)

### Principle: Do Not Create Redundant Parameters or Interfaces
- **MANDATORY**: Do not add optional parameters, variables, or interface complexity beyond what is actually required for the operation.
- **Question every parameter**: Before adding an optional parameter, ask:
  - Is this parameter actually needed for the operation to succeed?
  - Can this information be obtained from existing attributes or context?
  - Is this just for display/cosmetic purposes that could be handled internally?
  - Will this parameter be used by the caller, or is it just being passed through?
- **Avoid parameter passing for internal concerns**: If information is only needed for internal implementation details (like display formatting, logging context, etc.), it should be handled internally, not passed as parameters.
- **Avoid redundant optional parameters**: Do not create optional parameters that duplicate information already available in the class or can be derived from existing context.
- **Example of good practice**:
  ```python
  # Clean - no redundant parameters
  def populate_schema_in_neo4j(self) -> dict:
      # Manager accessed internally, building name not needed
      manager = self._get_neo4j_manager()
      # ... implementation ...
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  # ❌ Redundant parameters - manager is already available internally
  def populate_schema_in_neo4j(self, manager: Neo4jConnectionManager) -> dict:
      # ... implementation ...

  # ❌ Redundant parameter - building name only used for display
  def populate_schema_in_neo4j(self, building_name: Optional[str] = None) -> dict:
      if building_name:
          print(f"Building: {building_name}")  # Only for display
      # ... implementation ...

  # ❌ Redundant - both parameters do the same thing (identify asset type)
  def upsert_asset(self, uuid: str, name: str,
                   asset_type_uri: Optional[str] = None,
                   asset_type_name: Optional[str] = None,
                   asset_type_id: Optional[str] = None) -> dict:  # ❌ Too many ways to specify same thing
      # ... implementation ...
  ```
- **When optional parameters are acceptable**:
  - When they provide genuinely different functionality (e.g., `asset_type_uri` vs `asset_type_name` - one is direct, one requires normalization)
  - When they are user-facing configuration options (e.g., `chunk_size` for bulk operations, `progress_callback` for progress reporting)
  - When they are required for the operation but have sensible defaults

### Principle: Do Not Hoard Ephemeral State as Attributes
- **MANDATORY**: Do not keep one-shot or ephemeral inputs (like raw config dictionaries or file paths) as long-lived attributes if they are only needed to construct more stable dependencies (e.g., connection managers, schema objects).
- If a value is **passed once and immediately used** to build a durable dependency, prefer:
  - Using it directly inside the factory/loader method, and
  - Storing **only the durable dependency** (e.g., `Neo4jConnectionManager`, `Neo4jDatabaseConfig`, `PhysicalOntologySchema`) on the instance.
- **Example of good practice**:
  ```python
  class AutonomousBuildingOntology:
      def __init__(self, cognitive_ontology, physical_ontology, neo4j_manager):
          self.cognitive_ontology = cognitive_ontology
          self.physical_ontology = physical_ontology
          self._neo4j_manager = neo4j_manager  # stable dependency

      @classmethod
      def load(cls, config_dict: dict) -> "AutonomousBuildingOntology":
          # Use config once to build manager; do not store raw config on self
          neo4j_config_data = config_dict["ontology"]["physical"]["neo4j-db"]
          neo4j_config = Neo4jDatabaseConfig(... from neo4j_config_data ...)
          neo4j_manager = Neo4jConnectionManager(neo4j_config)
          physical_ontology = PhysicalOntology.load(config_dict)
          cognitive_ontology = CognitiveOntology()
          physical_ontology._neo4j_manager = neo4j_manager
          cognitive_ontology._neo4j_manager = neo4j_manager
          return cls(cognitive_ontology=cognitive_ontology,
                     physical_ontology=physical_ontology,
                     neo4j_manager=neo4j_manager)
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  class AutonomousBuildingOntology:
      def __init__(self, cognitive_ontology, physical_ontology, config_dict: dict):
          self.cognitive_ontology = cognitive_ontology
          self.physical_ontology = physical_ontology
          self._config_data = config_dict  # ❌ hoarded raw config
          self._neo4j_manager: Optional[Neo4jConnectionManager] = None

      def get_neo4j_connection_manager(self) -> Neo4jConnectionManager:
          if self._neo4j_manager is None:
              # ❌ repeatedly dig into raw config stored on self
              cfg = self._config_data["ontology"]["physical"]["neo4j-db"]
              neo4j_config = Neo4jDatabaseConfig(... from cfg ...)
              self._neo4j_manager = Neo4jConnectionManager(neo4j_config)
          return self._neo4j_manager
  ```
- Prefer storing **what the object is about** (ontology instances, schemas, managers) rather than transient inputs used only to build those objects.

### Principle: Intelligent API Design - Auto-Inference Over Manual Parameters
- **MANDATORY**: For high-level convenience APIs, prefer automatic inference of parameters from context when the information can be reliably determined.
- **Goal**: Create the cleanest possible API by eliminating obvious or redundant parameters that can be inferred from the input.
- **When to apply**:
  - When a parameter can be reliably inferred from the primary input (e.g., query mode from Cypher keywords)
  - When the inference is deterministic and unambiguous
  - When explicit control is still available through alternative methods
- **Example of good practice**:
  ```python
  # Clean API - mode automatically inferred from query
  def run_query(self, cypher_query: str, parameters: Optional[Dict] = None) -> Result:
      """Execute query with automatically inferred READ/WRITE mode."""
      mode = self._infer_query_mode(cypher_query)  # Infer from keywords
      if mode == "WRITE":
          return self.execute_write(cypher_query, parameters)
      else:
          return self.execute_read(cypher_query, parameters)

  # Usage - extremely clean
  result = manager.run_query("MATCH (n) RETURN count(n)")  # Auto-inferred READ
  result = manager.run_query("CREATE (n:Asset {name: $name})", {"name": "X"})  # Auto-inferred WRITE

  # Explicit control still available when needed
  result = manager.execute_write(query, params)  # Force WRITE
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  # ❌ Redundant parameter - mode can be inferred
  def run_query(self, cypher_query: str, mode: str = "READ", parameters: Optional[Dict] = None):
      if mode == "WRITE":
          return self.execute_write(cypher_query, parameters)
      else:
          return self.execute_read(cypher_query, parameters)

  # Usage - unnecessarily verbose
  result = manager.run_query("MATCH (n) RETURN n", mode="READ")  # Obvious!
  result = manager.run_query("CREATE (n)", mode="WRITE", params={"x": 1})  # Obvious!
  ```
- **Inference Implementation Best Practices**:
  - Implement inference as a static method (e.g., `_infer_query_mode()`) for testability
  - Use robust pattern matching (regex with word boundaries, not simple string matching)
  - Handle edge cases (comments, multi-line queries, complex statements)
  - Provide escape hatch: Keep explicit methods available (e.g., `execute_read()`, `execute_write()`)
- **Layered API Pattern**:
  - **High-level convenience method**: Auto-infers parameters, uses sensible defaults, cleanest API (e.g., `run_query(query, params)`)
    - No configuration parameters - uses defaults from config
    - Maximum simplicity for 99% of use cases
  - **Mid-level explicit methods**: Explicit control and overrides when needed (e.g., `execute_read(query, params, database)`)
    - Configuration parameters available for edge cases
    - Override defaults when necessary (e.g., `database="system"` for admin queries)
  - **Low-level session/transaction**: Maximum control for advanced use cases (e.g., `session(database, access_mode)`)
    - Full control over all parameters
    - For complex transaction patterns
- Benefits:
  - **Cleaner code**: Eliminates obvious/redundant parameters
  - **Better DX**: Developer writes less, code reads better
  - **Safer**: Hard to accidentally use wrong mode when it's inferred correctly
  - **Flexible**: Explicit control still available when needed

## Hierarchical Class Design and Abstraction Levels

### Principle: Higher-Level Classes Should Be Cleaner and More Public
- **MANDATORY**: Higher-level classes (closer to user code) should be cleaner, more public, and contain less boilerplate than lower-level classes.
- User-level code (the highest level) should be extremely clean and readable, focusing on what needs to be done, not how it's done.
- Higher-level classes should act as thin orchestration layers that delegate to lower-level domain classes.
- **Example of good practice**:
  ```python
  # High-level class (AutonomousBuilding) - Clean and simple
  def populate_physical_ontology_schema_in_neo4j(self) -> dict:
      return self.ontology.physical_ontology.populate_schema_in_neo4j()

  # Lower-level class (PhysicalOntology) - Handles implementation details
  def populate_schema_in_neo4j(self) -> dict:
      # All printing, error handling, user-facing output happens here
      # Manager accessed internally via self._get_neo4j_manager()
      print("=" * 70)
      print("Populate Physical Ontology Schema in Neo4j")
      # ... error handling, progress display, result formatting ...
      return result
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  # High-level class - Too much boilerplate
  def populate_physical_ontology_schema_in_neo4j(self) -> dict:
      import traceback
      print("=" * 70)
      print("Populate Physical Ontology Schema in Neo4j")
      try:
          manager = self.ontology.get_neo4j_connection_manager()
          print("✅ Connection manager obtained")
      except Exception as e:
          print(f"❌ Error: {e}")
          traceback.print_exc()
          raise
      # ... more boilerplate ...
  ```

### Principle: DRY for Error Handling and Logging (Right Abstraction Level)
- **MANDATORY**: Error handling, printing, logging, and user-facing output should be implemented at the **right abstraction level** and **not repeated** across multiple levels of the class hierarchy.
- **Single Responsibility**: Each abstraction level should handle its own concerns:
  - **High-level classes**: Thin orchestration, minimal code, delegate to domain classes
  - **Domain classes**: Handle domain-specific logic, error handling, user-facing output, and presentation
  - **Utility classes**: Handle low-level operations without user-facing concerns
- **DRY Principle**: Do not repeat error handling, printing, or logging at multiple levels. Choose the appropriate level and implement it once.
- **Guidelines**:
  - If a method is user-facing (called directly by user code), its error handling and output should be in the **domain class** that implements the operation, not in the high-level wrapper.
  - High-level classes should be so clean that they read like configuration or declarative code.
  - Lower-level classes own the "how" - including how errors are handled and how progress is communicated.
- **Example of good practice**:
  ```python
  # High-level: Just delegates
  def upsert_asset(self, uuid: str, name: str) -> dict:
      return self.ontology.physical_ontology.upsert_asset(uuid, name)

  # Domain class: Handles all error handling, validation, user feedback
  # Manager accessed internally via self._get_neo4j_manager()
  def upsert_asset(self, uuid: str, name: str) -> dict:
      if not uuid:
          raise ValueError("Asset UUID is required")
      # ... implementation with error handling ...
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  # High-level: Repeats error handling
  def upsert_asset(self, uuid: str, name: str) -> dict:
      try:
          if not uuid:
              raise ValueError("Asset UUID is required")  # ❌ Validation at wrong level
          return self.ontology.physical_ontology.upsert_asset(uuid, name)
      except Exception as e:  # ❌ Error handling repeated
          print(f"Error: {e}")
          raise

  # Domain class: Also has error handling (duplication)
  def upsert_asset(self, uuid: str, name: str) -> dict:
      if not uuid:
          raise ValueError("Asset UUID is required")  # ❌ Duplicated validation
      try:
          # ... implementation ...
      except Exception as e:  # ❌ Error handling repeated
          print(f"Error: {e}")
          raise
  ```

### Principle: User-Level Code Should Be Extremely Clean
- The highest level of code (user scripts, main entry points) should read like declarative configuration.
- User code should focus on **what** needs to be done, not **how** it's done.
- All complexity, error handling, and implementation details should be encapsulated in appropriate domain classes.
- **Example of good practice**:
  ```python
  # User-level code - Extremely clean
  building = AutonomousBuilding.load(building_dir)
  result = building.populate_physical_ontology_schema_in_neo4j()
  print(f"Created {result['asset_types']['created']} asset types")
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  # User-level code - Too much boilerplate
  building = AutonomousBuilding.load(building_dir)
  try:
      print("Starting population...")
      manager = building._get_neo4j_connection_manager()  # ❌ Exposing internals
      result = building.ontology.physical_ontology.populate_schema_in_neo4j()
      print("✅ Success")
  except Exception as e:  # ❌ Error handling at user level
      print(f"❌ Error: {e}")
      traceback.print_exc()
  ```

### Principle: Avoid `def main()` and `if __name__ == '__main__':` Boilerplate
- **MANDATORY**: Prefer **straight-line top-level code** over verbose `def main()` + `if __name__ == "__main__":` boilerplate in most cases.
- This applies to scripts, tools, and operational code that are primarily executed directly rather than imported as modules.
- Scripts should read like a short shell pipeline:
  - Imports
  - A small number of helpers (if needed)
  - A single, top-level "do the thing" flow.
- **Example of good practice**:
  ```python
  #!/usr/bin/env python3
  from pathlib import Path
  from autonomous_building import AutonomousBuilding
  from autonomous_building.util import load_env

  def _get_building_dir() -> Path:
      script_path = Path(__file__).resolve()
      return script_path.parent.parent  # buildings/devtest

  def _delete_label(session, label: str) -> dict:
      # ... helper implementation ...
      return {"before_count": before_count, "deleted_count": deleted_count}

  load_env()
  building_dir = _get_building_dir()
  building = AutonomousBuilding.load(building_dir)
  manager = building.ontology.get_neo4j_connection_manager()

  with manager.session(default_access_mode="WRITE") as session:
      for label in ["Asset", "Point"]:
          stats = _delete_label(session, label)
          print(label, stats)
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  #!/usr/bin/env python3
  def main() -> None:
      # 100+ lines of operational script logic
      ...

  if __name__ == "__main__":
      main()
  ```
- **When `def main()` + guard patterns are acceptable**:
  - Modules that are **both** imported and executed (e.g., library modules that can also be run as scripts)
  - Cases where testing/entrypoint reuse explicitly requires it
  - When the script is part of a larger framework that expects this pattern
- For most scripts, tools, and operational code, the `def main()` + `if __name__ == "__main__":` pattern only adds visual noise and indirection without providing value.

## Module Organization and `__init__.py` Files

### Principle: Keep `__init__.py` Files Light
- **MANDATORY**: `__init__.py` files should be kept lightweight and serve primarily as import aggregation points.
- Their main purpose is to expose the public API of a package by importing from lower-level modules.
- Implementation code (classes, functions, constants) should live in dedicated module files, not in `__init__.py`.

### Guidelines for `__init__.py` Files
1. **Primary Purpose**: Re-export public APIs from submodules
2. **Keep It Minimal**: Typically 10-50 lines, mostly imports and `__all__` definitions
3. **No Heavy Implementation**: Move classes, functions, and complex logic to dedicated module files
4. **What Belongs in `__init__.py`**:
   - Module-level constants (if truly module-scoped, not implementation-specific)
   - Imports from submodules
   - `__all__` list for explicit public API declaration
   - Brief module docstring
5. **What Does NOT Belong in `__init__.py`**:
   - Class definitions (put in dedicated module files)
   - Function implementations (put in dedicated module files)
   - Complex initialization logic
   - Heavy imports that slow down module loading

### Principle: Prefer Relative Imports in `__init__.py` Files
- **MANDATORY**: Within a package, `__init__.py` files should use **relative imports** (`.module_name`) to import from sibling modules.
- Relative imports make the code more readable and maintainable by avoiding verbose absolute paths.
- Absolute imports are still appropriate for:
  - Importing from external packages
  - Importing from parent packages or unrelated modules
  - Top-level module imports where relative imports would be unclear

### Guidelines for Import Styles

**Use Relative Imports:**
- In `__init__.py` files when importing from sibling modules in the same package
- In module files when importing from sibling modules in the same package
- Pattern: `from .module_name import ClassName`
- Pattern: `from ..parent_module import SomethingElse` (when importing from parent)

**Use Absolute Imports:**
- When importing from external packages (e.g., `from pathlib import Path`)
- When importing from unrelated modules in the codebase
- When the relative path would be unclear or overly complex
- At the top-level of the package structure (where relative imports don't make sense)

### Example of Good Practice
```python
# my_package/__init__.py
"""
My Package - Brief description of what this package does.
"""

# Module-level constants
DEFAULT_TIMEOUT: int = 30

# Import from submodules using RELATIVE imports (within same package)
from .connection_manager import ConnectionManager, create_connection
from .queries import execute_query, QueryBuilder
from .utils import parse_config, validate_input

__all__ = [
    'DEFAULT_TIMEOUT',
    'ConnectionManager',
    'create_connection',
    'execute_query',
    'QueryBuilder',
    'parse_config',
    'validate_input',
]
```

### Example of Bad Practice (DO NOT USE)
```python
# my_package/__init__.py - AVOID THIS
"""My Package"""

# ❌ WRONG: Using absolute imports for sibling modules
from my_package.connection_manager import ConnectionManager, create_connection
from my_package.queries import execute_query, QueryBuilder
from my_package.utils import parse_config, validate_input

__all__ = [...]
```

### Real-World Example: Agent Package

**Good (Relative Imports):**
```python
# autonomous_building/costar_agent_system/agents/curation/__init__.py
"""Curation agents for data and knowledge management."""

from .physical_ontology_agent import PhysicalOntologyAgent
from .logical_ontology_agent import LogicalOntologyAgent

__all__ = [
    "PhysicalOntologyAgent",
    "LogicalOntologyAgent",
]
```

**Bad (Absolute Imports - Unnecessarily Verbose):**
```python
# autonomous_building/costar_agent_system/agents/curation/__init__.py
"""Curation agents for data and knowledge management."""

# ❌ AVOID: Unnecessarily long absolute imports for sibling modules
from autonomous_building.costar_agent_system.agents.curation.physical_ontology_agent import PhysicalOntologyAgent
from autonomous_building.costar_agent_system.agents.curation.logical_ontology_agent import LogicalOntologyAgent

__all__ = [
    "PhysicalOntologyAgent",
    "LogicalOntologyAgent",
]
```

### Example of Bad Practice (DO NOT USE)
```python
# my_package/__init__.py
"""My Package"""

from typing import Optional, Dict, Any
import os
import sys

# ❌ Class definition in __init__.py (should be in dedicated module)
class ConnectionManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._connection = None

    def connect(self) -> None:
        # 100+ lines of implementation
        pass

    # ... more methods ...

# ❌ Function definitions in __init__.py (should be in dedicated module)
def execute_query(query: str, params: Optional[Dict] = None):
    # 50+ lines of implementation
    pass

# ❌ Heavy initialization logic
_global_config = load_config_from_file()  # Slows down import
_connection_pool = initialize_pool()      # Side effects on import
```

### Benefits of Lightweight `__init__.py`
- **Fast Imports**: Module loads quickly without executing heavy initialization
- **Clear Organization**: Implementation lives in logical, dedicated modules
- **Maintainability**: Easy to find where code is actually defined
- **Testing**: Can test individual modules without importing the entire package
- **Circular Import Prevention**: Reduces risk of circular import issues
- **Discoverability**: `__init__.py` serves as a clean table of contents for the package API

## Benefits
- **Discoverability**: Public API is immediately visible at the top of the class, allowing readers to quickly understand what the class does
- **Readability**: Clear separation between public interface and implementation details; within each section, dependencies appear before dependents
- **Maintainability**: Clear separation between public API, helpers, and domain logic; error handling and logging in one place reduces duplication
- **Debugging**: When diving into implementation, dependency ordering within sections makes execution flow easier to trace
- **Clean User Code**: Higher-level classes are thin orchestration layers, resulting in extremely clean and readable user-level code
- **DRY Compliance**: Error handling, logging, and user-facing output implemented once at the right abstraction level, eliminating repetition
- **Fast Module Loading**: Lightweight `__init__.py` files ensure quick imports and avoid side effects

---

## One-to-Many Relationship Patterns

### Principle: Consistent Mapping Method Ordering
- **MANDATORY**: For one-to-many relationship mappings, methods MUST follow a consistent ordering pattern
- **Standard Order**: `add` → `remove` → `get` → `set` (singular) → `set` (plural) → `from_source_files` → `_parse_from_ttl`
- **Rationale**: Logical progression from incremental operations (add/remove) to complete operations (get/set), followed by bulk and source file operations
- **Benefits**: Predictable API, easy to find the right method, consistent across all mapping types

### Principle: Replace-All Pattern for Set Operations
- **MANDATORY**: `set_*` methods (singular and plural) MUST use a "replace-all" pattern
- **Pattern**: Delete all existing relationships for the source entity before creating new ones
- **Rationale**: Ensures no stale data remains, guarantees data consistency
- **Implementation**: Cypher queries should first `MATCH` and `DELETE` all existing relationships, then `MERGE` new ones
- **Benefits**: Prevents orphaned relationships, ensures exact match between intended and actual state

### Principle: Unified Source File Processing
- **MANDATORY**: When a source file contains multiple related entities, use a unified method that processes all entities in one pass
- **Pattern**: Parse the source file once, extract all related entities, then upsert in correct dependency order
- **Rationale**: More efficient (single pass), ensures correct dependency order, clearer intent
- **Example**: A TTL file containing AspectTypes, Aspects, and their mappings should be processed by a single unified method
- **Benefits**: Single source of truth, reduced parsing overhead, guaranteed consistency

### Principle: Relationship Properties on Relationships
- **MANDATORY**: When relationships have properties (not just nodes), store properties on the relationship itself
- **Pattern**: Cypher queries return both node data and relationship properties; Python methods construct mapping dataclasses that include relationship properties
- **Rationale**: Some relationships have meaningful properties (e.g., `value`, `tags`) that belong to the relationship, not the nodes
- **Benefits**: Accurate data modeling, enables relationship-specific queries and operations

---

## Query Organization and File Naming

### Principle: Numeric Prefixes for Query Files
- **MANDATORY**: Use numeric prefixes (0-, 1-, 2-, etc.) to organize query files by domain/object type
- **Pattern**: Each major object type or domain gets its own numeric prefix range
- **Rationale**: Clear organization, easy to find related queries, consistent ordering
- **Benefits**: Better IDE support, easier navigation, clear grouping of related queries

### Principle: Bulk Queries Return Data, Not Counts
- **MANDATORY**: Bulk upsert queries MUST return the actual upserted data, not just counts
- **Pattern**: `RETURN n.uri AS uri, n.label AS label` instead of `RETURN count(n) AS created`
- **Rationale**: Provides useful information to callers, enables proper dataclass instantiation, supports verification
- **Benefits**: More informative, enables proper return value construction, supports testing and validation

---

## Get-or-Update Pattern

### Principle: Intelligent Operation Detection
- **MANDATORY**: Methods that can perform multiple operations (GET vs UPDATE) should auto-detect the operation type
- **Pattern**: Check if all update parameters (`to_*`) are `None`:
  - If all `None`: Perform GET operation
  - If any not `None`: Perform UPDATE operation
- **Rationale**: Single method signature for related operations, reduces API surface area, clearer intent
- **Benefits**: Simpler API, fewer methods to maintain, intuitive usage

---

## Consistent Derivation Patterns

### Principle: Consistent Namespace Derivation
- **MANDATORY**: When deriving related values from a primary identifier (e.g., namespace from URI), use a consistent pattern throughout the codebase
- **Pattern**: Extract the namespace prefix using the same method everywhere (e.g., `uri.split('.')[0]` after normalization)
- **Rationale**: Reduces errors from inconsistent handling, makes code self-documenting
- **Benefits**: Predictable behavior, easier to understand, fewer bugs from inconsistent derivation

---

## Progress Tracking and Chunking

### Principle: Use tqdm for Progress Tracking
- **MANDATORY**: Use `tqdm` for visual progress bars in long-running operations
- **NEVER** use callback functions for progress tracking
- **Pattern**: `for start in tqdm(range(...), desc="Processing", unit="chunk"):`
- **Rationale**: Cleaner API, automatic progress display, no manual callback management
- **Benefits**: Better user experience, less code, consistent progress display

### Principle: Default Chunk Sizes
- **MANDATORY**: Use module-level constants for chunk sizes instead of method parameters
- **Pattern**: `DEFAULT_BULK_CHUNK_SIZE` constant, used directly in methods
- **Rationale**: KISS/YAGNI - one default size works for all cases, reduces API complexity
- **Benefits**: Simpler API, consistent behavior, less configuration overhead

---

## Dataclass Patterns

### Principle: Dataclass Creation Timing
- **MANDATORY**: Create dataclass instances RIGHT BEFORE return statements, AFTER all database/IO operations are complete
- **Rationale**: Separates "business logic" from "result preparation"
- **Benefits**: Clear separation of concerns, easier to see what's being persisted vs returned

**WRONG**:
```python
def create_item(self, data: dict) -> Item:
    item = Item(**data)  # ❌ Too early
    self._save_to_db(data)
    return item
```

**CORRECT**:
```python
def create_item(self, data: dict) -> Item:
    self._save_to_db(data)  # Business logic first
    return Item(**data)  # ✅ Create right before return
```

### Principle: Type Aliases for Complex Types
- **MANDATORY**: For complex nested types, declare named type aliases near the top of the module
- **Pattern**: `UriToPropertiesDict: type = dict[str, dict[str, Any]]`
- **Rationale**: Self-documenting, DRY, easier to maintain
- **Benefits**: Clarity, consistency, single source of truth for type definitions

---

## Error Handling Patterns

### Principle: Validation and Error Messages
- **MANDATORY**: Validate inputs early, use clear error messages
- **Pattern**: Check inputs at method entry, raise `ValueError` with descriptive messages
- **Rationale**: Fail fast, clear feedback, easier debugging
- **Benefits**: Better error messages, earlier failure detection, clearer intent

### Principle: Database Error Handling
- **MANDATORY**: Let exceptions propagate in most cases, log context for bulk operations
- **Pattern**: For bulk operations, log which chunk/item failed with context
- **Rationale**: Don't hide errors, provide useful debugging information
- **Benefits**: Easier debugging, better error visibility, proper exception handling
