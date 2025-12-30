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

### Principle: Helper Methods After Public API Methods
- **MANDATORY**: Helper methods that support specific public API methods should be placed immediately after those public methods, not in a separate Utilities section
- **Pattern**: When a helper method is only used by one or a few closely related public methods, place it directly after those methods
- **Rationale**: Better readability - the helper is directly related to and used by the public methods, keeping related code together
- **Benefits**:
  - **Readability**: Helper logic is immediately visible after the public method that uses it
  - **Maintainability**: Related code stays together, easier to understand and modify
  - **Discoverability**: When reading a public method, the helper is right below it
- **When to apply**: Use this pattern for helpers that are tightly coupled to specific public methods (e.g., `_pre_process_aspects_of_point_roles` used only by `add_aspects_to_point_roles` and `set_aspects_of_point_roles`)
- **When NOT to apply**: General-purpose utilities used across multiple unrelated methods should still go in the Utilities section
- **Example**:
  ```python
  # CORRECT - Helper immediately after public methods that use it
  def add_aspects_to_point_roles(
      self,
      point_role_uri_to_aspect_uri_to_properties_dict_dict: dict[PointRoleUri, AspectUriToPropertiesDict]
  ) -> list[PointRoleAspect]:
      rows = self._pre_process_aspects_of_point_roles(...)  # Uses helper
      # ... implementation ...
      return self._post_process_aspects_of_point_roles(results, "add")  # Uses helper

  def set_aspects_of_point_roles(
      self,
      point_role_uri_to_aspect_uri_to_properties_dict_dict: dict[PointRoleUri, AspectUriToPropertiesDict]
  ) -> list[PointRoleAspect]:
      rows = self._pre_process_aspects_of_point_roles(...)  # Uses helper
      # ... implementation ...
      return self._post_process_aspects_of_point_roles(results, "set")  # Uses helper

  # Helper methods placed immediately after the public methods that use them
  def _pre_process_aspects_of_point_roles(
      self,
      point_role_uri_to_aspect_uri_to_properties_dict_dict: dict[PointRoleUri, AspectUriToPropertiesDict]
  ) -> list[dict[str, Any]]:
      """Helper to prepare rows for bulk PointRole-to-Aspect mapping operations."""
      # ... implementation ...

  def _post_process_aspects_of_point_roles(
      self,
      results: list[list[Any]],
      operation_name: str
  ) -> list[PointRoleAspect]:
      """Helper to process query results from PointRole-to-Aspect mapping operations."""
      # ... implementation ...
  ```
- **Anti-pattern** (DO NOT USE):
  ```python
  # WRONG - Helper separated from public methods that use it
  def add_aspects_to_point_roles(...):
      rows = self._pre_process_aspects_of_point_roles(...)
      # ... implementation ...

  def set_aspects_of_point_roles(...):
      rows = self._pre_process_aspects_of_point_roles(...)
      # ... implementation ...

  # ... many other methods ...

  # ========================================================================
  # Utilities (helpers and properties)
  # ========================================================================

  def _pre_process_aspects_of_point_roles(...):  # Too far from where it's used
      ...

  def _post_process_aspects_of_point_roles(...):  # Too far from where it's used
      ...
  ```

### Principle: Lightweight Instantiation and Lazy Indexing
- **MANDATORY**: Do not perform expensive operations (indexing, file I/O, network calls) in constructors/initializers
- **Terminology Clarification**:
  - **Initialization/Instantiation**: Creating the object instance - should be lightweight
  - **Indexing**: Computing potentially large and complex intermediate structures to aid accurate and fast subsequent retrieval - should happen lazily
- **Separation of Concerns**: Separate indexing time (when intermediate structures are computed) from retrieval/usage time (when they are used)
- Perform expensive operations lazily (on first access) via properties or in retrieval methods
- This ensures fast instantiation and avoids side effects during import
- **Pattern**: For cases involving indexing resources and then using them, use an explicit intermediate helper method like `_get_or_create_<index-or-something-else-specific>()` that handles lazy indexing logic and returns the needed content. This is more disciplined than directly calling `index()` in retrieval methods.
- **Example**: A resource's `index()` method (which computes intermediate structures) should be called lazily via an intermediate helper method (e.g., `_get_or_create_section_index()`), not directly in retrieval methods or in constructors

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
  # WRONG: Premature optimization - database override not used anywhere
  def run_query(self, cypher_query: str, parameters: Optional[Dict] = None,
                database: Optional[str] = None) -> Result:  # YAGNI violation
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

### Principle: Remove Redundant Helper Methods and Properties
- **MANDATORY**: Do not create helper methods or properties that simply wrap direct attribute access or method calls.
- **Pattern**: Use direct access instead of unnecessary indirection
- **Rationale**: Reduces code complexity, improves readability, follows KISS principle
- **When to remove**:
  - Helper methods that only return `self._attribute`
  - Properties that duplicate existing attributes
  - Getter methods that don't add any logic beyond access
- **Example of good practice**:
  ```python
  # CORRECT: Direct access - simple and clear
  def run_query(self, query: str) -> Result:
      return self._graph_db.run_query(query, parameters={})
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  # WRONG: Redundant helper method - adds no value
  def _get_graph_db(self) -> GraphDb:
      return self._graph_db  # Just returns the attribute

  def run_query(self, query: str) -> Result:
      return self._get_graph_db().run_query(query, parameters={})  # Unnecessary indirection
  ```
- **Benefits**: Simpler code, fewer methods to maintain, clearer intent
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
  # WRONG: Redundant parameters - manager is already available internally
  def populate_schema_in_neo4j(self, manager: Neo4jConnectionManager) -> dict:
      # ... implementation ...

  # WRONG: Redundant parameter - building name only used for display
  def populate_schema_in_neo4j(self, building_name: Optional[str] = None) -> dict:
      if building_name:
          print(f"Building: {building_name}")  # Only for display
      # ... implementation ...

  # WRONG: Redundant - both parameters do the same thing (identify asset type)
  def upsert_asset(self, uuid: str, name: str,
                   asset_type_uri: Optional[str] = None,
                   asset_type_name: Optional[str] = None,
                   asset_type_id: Optional[str] = None) -> dict:  # Too many ways to specify same thing
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
          self._config_data = config_dict  # WRONG: hoarded raw config
          self._neo4j_manager: Optional[Neo4jConnectionManager] = None

      def get_neo4j_connection_manager(self) -> Neo4jConnectionManager:
          if self._neo4j_manager is None:
              # WRONG: repeatedly dig into raw config stored on self
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
  # WRONG: Redundant parameter - mode can be inferred
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
          print("Connection manager obtained")
      except Exception as e:
          print(f"ERROR: {e}")
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
              raise ValueError("Asset UUID is required")  # WRONG: Validation at wrong level
          return self.ontology.physical_ontology.upsert_asset(uuid, name)
      except Exception as e:  # WRONG: Error handling repeated
          print(f"Error: {e}")
          raise

  # Domain class: Also has error handling (duplication)
  def upsert_asset(self, uuid: str, name: str) -> dict:
      if not uuid:
          raise ValueError("Asset UUID is required")  # WRONG: Duplicated validation
      try:
          # ... implementation ...
      except Exception as e:  # WRONG: Error handling repeated
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
      manager = building._get_neo4j_connection_manager()  # WRONG: Exposing internals
      result = building.ontology.physical_ontology.populate_schema_in_neo4j()
      print("SUCCESS")
  except Exception as e:  # WRONG: Error handling at user level
      print(f"ERROR: {e}")
      traceback.print_exc()
  ```

## Benefits
- **Discoverability**: Public API is immediately visible at the top of the class, allowing readers to quickly understand what the class does
- **Readability**: Clear separation between public interface and implementation details; within each section, dependencies appear before dependents
- **Maintainability**: Clear separation between public API, helpers, and domain logic; error handling and logging in one place reduces duplication
- **Debugging**: When diving into implementation, dependency ordering within sections makes execution flow easier to trace
- **Clean User Code**: Higher-level classes are thin orchestration layers, resulting in extremely clean and readable user-level code
- **DRY Compliance**: Error handling, logging, and user-facing output implemented once at the right abstraction level, eliminating repetition

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

### Principle: When to Use Add vs Set for Incremental Data Processing
- **MANDATORY**: When processing incremental or incomplete data sources (e.g., CSV files that may not contain all relationships), use `add_*` methods instead of `set_*` methods
- **Use `add_*` when**:
  - Data source is incremental (not exhaustive)
  - Multiple data sources may contribute to the same relationships
  - Existing relationships should be preserved
  - Data may be processed in multiple passes
- **Use `set_*` when**:
  - Data source is complete and authoritative
  - You want to replace all existing relationships with the new data
  - Data represents the complete, final state
- **Rationale**: `add_*` methods preserve existing relationships, while `set_*` methods replace all relationships (replace-all pattern)
- **Example**: When processing CSV files that may be incremental updates, use `add_point_roles_to_asset_type()` instead of `set_point_roles_of_asset_type()` to avoid removing relationships not present in the current CSV
- **Benefits**: Prevents data loss from incremental updates, allows safe processing of partial data sources

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

## Database Access Patterns

### Principle: Direct Database Access (MANDATORY)
- **MANDATORY**: Use direct property access for database operations - NO session management, NO local variable assignment
- **Pattern**: `self._graph_db.run_query(QUERY, parameters=...)` directly - do NOT assign to local variables
- **NEVER** use `with manager.session()` blocks in domain methods
- **NEVER** specify `default_access_mode` - let auto-inference handle it
- **NEVER** assign `manager = self._graph_db` - this is tedious and unnecessary
- **NEVER** create `_get_graph_db()` helper methods - use `self._graph_db` directly (KISS/YAGNI)
- **Rationale**: Cleaner code, auto-inferred READ vs WRITE mode, consistent with KISS/YAGNI principles
- **Benefits**: Less code, easier to test and maintain, no unnecessary indirection

**WRONG**:
```python
# WRONG: Helper method - unnecessary indirection
def _get_graph_db(self) -> "GraphDb":
    if not self._graph_db:
        raise ValueError("Graph database not set")
    return self._graph_db

# WRONG: Low-level session management
manager = self._get_graph_db()
with manager.session(default_access_mode="WRITE") as session:
    result = session.run(QUERY, parameters)
    # ...

# WRONG: Unnecessary local variable assignment
manager = self._graph_db
manager.run_query(QUERY, parameters={'rows': chunk})
```

**CORRECT**:
```python
# CORRECT: Direct use of self._graph_db
result = self._graph_db.run_query(QUERY, parameters={'param': value})
existing = result[0] if result else None

# CORRECT: Direct use in bulk operations
self._graph_db.run_query(BULK_UPSERT_QUERY, parameters={'rows': chunk})
```

### Principle: Database Indexes Are Critical for Performance (MANDATORY)
- **MANDATORY**: Database indexes are **critical for query performance**, especially for large datasets
- **Performance impact**: Missing indexes cause **significant slowdowns** and can lead to timeouts on bulk operations
- **Real-world evidence**: Databases without proper indexes experience degraded performance (queries that should take seconds can take minutes or hours)
- **When indexes are needed**: Indexes are required for:
  - Properties used in lookup operations (WHERE clauses, JOIN conditions)
  - Properties used in filter operations (IN clauses, range queries)
  - Primary keys and unique identifiers
  - Foreign keys and relationship traversal
- **Index maintenance**: Indexes must be created/updated when:
  - Schema changes (new properties added to entities)
  - New databases are set up
  - Entity definitions are modified
  - Performance issues indicate missing indexes
- **Best practices**:
  - Index all properties used in queries (lookups, filters, joins)
  - Use unique indexes for primary keys
  - Use regular indexes for frequently-queried properties that may have duplicates
  - Don't index rarely-queried properties (saves storage and write performance)
  - Document indexing decisions in code comments
- **Performance benefits**:
  - Fast lookup operations (O(log n) instead of O(n))
  - Efficient bulk operations on large datasets
  - Better query planning by database engine
  - Prevents timeouts on complex queries
- **Note**: Specific indexing mechanisms vary by database system (e.g., NeoModel for Neo4j, CREATE INDEX for SQL databases). See project-specific rules for implementation details.

---

## Query Organization and File Naming

### Principle: Separate Query Files (MANDATORY)
- **MANDATORY**: Store database queries in separate files (e.g., `.cypher`, `.sql`) rather than inline in code
- **Pattern**: One query per file, organized in a dedicated queries directory
- **Rationale**: Better IDE support, easier testing, clear organization, reusable queries
- **Benefits**: Better maintainability, easier to review query logic, supports query versioning

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

### Principle: Well-Commented Complex Queries
- **MANDATORY**: Complex database queries MUST include comprehensive comments explaining:
  - **Purpose**: What the query does (replace-all pattern, incremental update, etc.)
  - **Input format**: What parameters are expected and their structure
  - **CALL subqueries** (for graph databases): Why CALL is used (to avoid row multiplication), what it does
  - **Relationship properties**: Which properties are stored on relationships vs nodes
  - **OPTIONAL MATCH**: Why optional matching is used and what it means
  - **MERGE semantics**: When MERGE creates vs updates, why idempotency matters
  - **Complex patterns**: Step-by-step explanations for multi-step queries
- **Rationale**: Database queries can be complex; comments help maintainers understand intent and avoid bugs
- **Benefits**: Easier maintenance, faster onboarding, fewer bugs from misunderstanding query logic

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

### Principle: Use Progress Tracking Libraries
- **MANDATORY**: Use appropriate progress tracking libraries for visual progress bars in long-running operations
- **NEVER** use callback functions for progress tracking
- **Rationale**: Cleaner API, automatic progress display, no manual callback management
- **Benefits**: Better user experience, less code, consistent progress display
- **Client script usage**: Client scripts should also use progress tracking when they have their own loops (e.g., iterating over grouped data before calling library methods), even though library methods use progress tracking internally

### Principle: Default Chunk Sizes
- **MANDATORY**: Use module-level constants for chunk sizes instead of method parameters
- **Pattern**: `DEFAULT_BULK_CHUNK_SIZE` constant, used directly in methods
- **Rationale**: KISS/YAGNI - one default size works for all cases, reduces API complexity
- **Benefits**: Simpler API, consistent behavior, less configuration overhead

---

## Data Structure Patterns

### Principle: Data Structure Creation Timing
- **MANDATORY**: Create data structure instances (objects, records, etc.) RIGHT BEFORE return statements, AFTER all database/IO operations are complete
- **Rationale**: Separates "business logic" from "result preparation"
- **Benefits**: Clear separation of concerns, easier to see what's being persisted vs returned

**WRONG**:
```python
def create_item(self, data: dict) -> Item:
    item = Item(**data)  # WRONG: Too early
    self._save_to_db(data)
    return item
```

**CORRECT**:
```python
def create_item(self, data: dict) -> Item:
    self._save_to_db(data)  # Business logic first
    return Item(**data)  # CORRECT: Create right before return
```

### Principle: Type Aliases for Complex Types
- **MANDATORY**: For complex nested types, declare named type aliases near the top of the module
- **Rationale**: Self-documenting, DRY, easier to maintain
- **Benefits**: Clarity, consistency, single source of truth for type definitions

### Principle: Transparent Type-Hinting with Named Types
- **MANDATORY**: Use named type aliases for all types that represent domain concepts, not just complex nested types
- **Pattern**: Define type aliases at the top of the module for domain-specific types (e.g., `AssetTypeUri`, `PointRoleUri`, `AssetName`, `PointName`) and use them consistently throughout method signatures
- **Rationale**: Makes type hints self-documenting and transparent - readers immediately understand what each parameter represents without consulting documentation
- **Benefits**:
  - **Clarity**: `def upsert_asset(name: AssetName, asset_type_uri: AssetTypeUri)` is immediately clear
  - **Transparency**: Type hints reveal domain semantics, not just technical types
  - **Consistency**: Single source of truth for type definitions across the codebase
  - **Refactoring safety**: Changing the underlying type (e.g., from `str` to a custom class) only requires updating the alias definition
- **When to use**: Apply to all domain-specific types, even simple ones like `str` when they represent specific domain concepts (URIs, names, identifiers)
- **Example**:
  ```python
  # At top of module
  AssetTypeUri = str  # URI for AssetType in dotted-namespace format
  PointRoleUri = str  # URI for PointRole in dotted-namespace format
  AssetName = str  # Primary identifier for Asset instances
  PointName = str  # Primary identifier for Point instances

  # In method signatures
  def upsert_asset(
      self,
      name: AssetName,  # Clear: this is an Asset name
      asset_type_uri: AssetTypeUri  # Clear: this is an AssetType URI
  ) -> Asset:
      ...

  def add_point_roles_to_point(
      self,
      point_name: PointName,  # Clear: this is a Point name
      point_role_uris: list[PointRoleUri]  # Clear: list of PointRole URIs
  ) -> list[PointRole]:
      ...
  ```
- **Anti-pattern** (DO NOT USE):
  ```python
  # WRONG: Ambiguous: what does this str represent?
  def upsert_asset(self, name: str, asset_type_uri: str) -> Asset:
      ...

  # WRONG: Unclear: is this a URI? a name? what format?
  def add_point_roles_to_point(self, point_name: str, point_role_uris: list[str]) -> list[PointRole]:
      ...
  ```

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

---

## Client Code Simplicity and Library Delegation

### Principle: Client Code Should Be Minimal and Situation-Specific
- **MANDATORY**: Client-level code (scripts, applications, user-facing code) should be as simple as possible and specific to the situation, with minimal general boilerplate.
- **Complexity belongs in the library**: General complexities, error handling, validation, progress tracking, and database operations should be handled by the library package code as much as possible.
- **Client code focuses on**: Data extraction, transformation, and high-level orchestration - not implementation details.

**Example of good practice**:
```python
"""Populate Asset Types from CSV Files"""

# Imports (standard library → third-party → internal)
import argparse
from pathlib import Path
import pandas as pd

from my_library import DataProcessor
from my_library.util.paths import DATA_DIR_PATH

# Constants at top
MAIN_PROJECT_NAME: str = Path(__file__).parents[2].name
CSV_FILE_NAME: str = "data.csv"
CSV_COLUMN_TYPE: str = "type"

# CLI parsing
parser = argparse.ArgumentParser()
parser.add_argument("--dev", action="store_true", help="Use dev database")
args = parser.parse_args()

PROJECT_NAME = f"{MAIN_PROJECT_NAME}-dev" if args.dev else MAIN_PROJECT_NAME
data_dir = DATA_DIR_PATH / MAIN_PROJECT_NAME / "data"

# Load processor and extract data
processor = DataProcessor.load(PROJECT_NAME)
data_df = pd.read_csv(data_dir / CSV_FILE_NAME)

# Extract IDs (simple data transformation)
ids = {id for value in data_df[CSV_COLUMN_TYPE].dropna().unique()
       if (id := parse_type(value)['id'])}

# Delegate to library - all complexity handled there
id_to_properties_dict = {id: {} for id in ids}
processor.upsert_types(id_to_properties_dict)
```

**Example of bad practice** (DO NOT USE):
```python
# WRONG: Client code doing too much - database queries, error handling, progress tracking
processor = DataProcessor.load(PROJECT_NAME)
db = processor.get_database_connection()

# WRONG: Custom database queries instead of using library methods
result = db.query("SELECT * FROM types")
existing = {r['id']: r['name'] for r in result}

# WRONG: Manual error handling and progress tracking
for id in ids:
    try:
        if id in existing:
            # Manual update logic
            db.query("UPDATE types SET name = $name WHERE id = $id", ...)
        else:
            # Manual create logic
            db.query("INSERT INTO types (id, name) VALUES ($id, $name)", ...)
    except Exception as e:
        print(f"Error: {e}")  # WRONG: Error handling in client code
```

### Benefits of Client Code Simplicity
- **Readability**: Client code reads like a recipe - clear steps, easy to understand
- **Maintainability**: Changes to implementation details don't require client code updates
- **Consistency**: All clients use the same library methods, ensuring consistent behavior
- **Testability**: Library methods are tested once, not duplicated in each client
- **Flexibility**: Library can evolve without breaking client code

### What Client Code Should Do
- **Extract data** from sources (CSV, JSON, files, APIs)
- **Transform data** to library-expected formats (simple transformations)
- **Orchestrate** high-level operations (call library methods in sequence)
- **Handle CLI arguments** for script-specific configuration
- **Define constants** specific to the script's data sources
- **Combine mapping and processing in single loops** when iterating over grouped data (e.g., map labels to URIs and call library method in the same loop)
- **Use progress tracking for client-side loops** when iterating over data before calling library methods

### What Client Code Should NOT Do
- **Database queries** - use library methods instead
- **Error handling** - let library methods handle errors (or propagate)
- **Progress tracking** - library methods handle progress tracking internally
- **Validation logic** - library methods validate inputs
- **Session management** - library handles Neo4j sessions
- **Duplicate scripts** - use CLI flags instead (e.g., `--dev`)

### Principle: Avoid Duplicate Scripts - Use CLI Flags Instead
- **MANDATORY**: When scripts differ only by configuration (e.g., dev vs. production building), use CLI flags rather than duplicating scripts.
- **Pattern**: Single script with flags (e.g., `--dev`) that modify behavior
- **Rationale**: DRY principle - one script to maintain, not multiple copies
- **Benefits**: Easier maintenance, consistent behavior, fewer bugs

**Example**:
```python
# CORRECT: Single script with --dev flag
parser.add_argument("--dev", action="store_true", help="Use dev environment")
ENV_NAME = f"{MAIN_ENV_NAME}-dev" if args.dev else MAIN_ENV_NAME
```

**Avoid**:
```python
# WRONG: Duplicate scripts: populate-types.py and populate-types-dev.py
# Maintenance burden, risk of divergence
```

---

## Constants Organization in Scripts

### Principle: Constants at Top of File (MANDATORY)
- **MANDATORY**: All constants (file names, column names, configuration values) should be defined at the top of the file, immediately after imports and CLI argument parsing.
- **Grouping**: Group related constants together with comments describing their purpose
- **Naming**: Use descriptive, uppercase names with type annotations
- **Documentation**: Add comments explaining what data each constant represents

**Example of good practice**:
```python
"""Populate Types from CSV Files"""

import argparse
from pathlib import Path

from my_library import DataProcessor
from my_library.util.paths import DATA_DIR_PATH

# CLI argument parsing
parser = argparse.ArgumentParser()
parser.add_argument("--dev", action="store_true")
args = parser.parse_args()

# Project configuration
MAIN_PROJECT_NAME: str = Path(__file__).parents[2].name
PROJECT_NAME: str = f"{MAIN_PROJECT_NAME}-dev" if args.dev else MAIN_PROJECT_NAME
data_dir = DATA_DIR_PATH / MAIN_PROJECT_NAME / "data"

# CSV file names
PRIMARY_CSV_FILE_NAME: str = "primary_data.csv"
SECONDARY_CSV_FILE_NAME: str = "secondary_data.csv"

# CSV column names
# Primary CSV: Contains type identifiers in dotted-namespace format
PRIMARY_COLUMN_TYPE: str = "type"

# Secondary CSV: Contains human-readable type labels
SECONDARY_COLUMN_TYPE: str = "Type"
```

**Example of bad practice** (DO NOT USE):
```python
# WRONG: Constants scattered throughout code
def parse_csv():
    csv_file = "data.csv"  # WRONG: Hardcoded in function
    column = "type"  # WRONG: Hardcoded in function
    # ...

# WRONG: No type annotations or documentation
CSV_FILE_NAME = "data.csv"  # WRONG: No type annotation
```

### Benefits of Constants at Top
- **Discoverability**: All configuration visible at a glance
- **Maintainability**: Single place to update file names, column names, etc.
- **Documentation**: Comments explain what each constant represents
- **Type safety**: Type annotations make constants self-documenting
- **Reusability**: Constants can be referenced throughout the script

### Constants Organization Pattern
1. **CLI argument parsing** (if applicable)
2. **Configuration constants** (building names, paths, etc.)
3. **Data source constants** (file names, column names, etc.)
4. **Business logic constants** (thresholds, defaults, etc.)
5. **Each group** with descriptive comments explaining the data they represent

---

## Terminal Command Execution

### Principle: Do Not Suppress Output with `2>&1` (MANDATORY)
- **MANDATORY**: When running scripts or commands via terminal, **DO NOT** use `2>&1` to redirect stderr to stdout
- **Rationale**: Users want to see all output (both stdout and stderr) in real-time to monitor progress and debug issues
- **Pattern**: Run commands without output redirection, allowing both stdout and stderr to display naturally

**Example of good practice**:
```bash
# CORRECT: Output visible to user
run-script populate-schema
```

**Example of bad practice** (DO NOT USE):
```bash
# WRONG: Suppresses output visibility
run-script populate-schema 2>&1
```

**Benefits**:
- **Real-time visibility**: Users can see progress and errors as they occur
- **Better debugging**: Error messages are immediately visible
- **Transparency**: All output is visible, not hidden or redirected
- **User control**: Users can see what's happening and make informed decisions

**When output redirection might be acceptable**:
- Only when explicitly requested by the user
- For logging purposes where output is explicitly saved to a file
- Never as a default behavior in automated scripts or tool execution
