---
description: Python coding
alwaysApply: false
---

# Python-Specific Code Organization Guidelines

**Note**: This document contains **Python-specific** patterns and guidelines. For **general** coding principles (KISS, YAGNI, method ordering, error handling, client code simplicity, database access patterns, query organization, etc.), see `aiCode/.ai/rules/code/0-general-code-guidance.md`. This document references the general guidance where applicable and adds Python-specific details.

## Module Organization and `__init__.py` Files

### Principle: Module-Level Code Organization (MANDATORY)
- **MANDATORY**: All Python modules must follow this exact ordering:
  1. **Module docstring** (if any)
  2. **Imports** (standard library → third-party → internal)
  3. **`__all__`** (if used - explicit public API declaration)
  4. **Module-level constants** (if any)
  5. **Class/function definitions**
- **Rationale**: `__all__` should appear immediately after imports to clearly declare the public API before any implementation code or constants
- **Benefits**: Clear public API declaration, consistent module structure, easier to understand module exports

**Example of good practice**:
```python
"""
Module docstring describing the module's purpose.
"""

# 1. Imports
from dataclasses import dataclass, field
from typing import Any, Optional

# 2. __all__ (immediately after imports)
__all__ = [
    'DEFAULT_SCHEMA_NAMESPACE_LABEL',
    'SchemaNamespace',
    'AssetType',
]

# 3. Module-level constants (after __all__)
DEFAULT_SCHEMA_NAMESPACE_LABEL: str = "c-som-default"

# 4. Class/function definitions
@dataclass
class SchemaNamespace:
    # ...
```

**Example of bad practice** (DO NOT USE):
```python
# WRONG: Constants before __all__
DEFAULT_SCHEMA_NAMESPACE_LABEL: str = "c-som-default"

__all__ = [
    'DEFAULT_SCHEMA_NAMESPACE_LABEL',
    # ...
]
```

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

# 1. Imports
from .connection_manager import ConnectionManager, create_connection
from .queries import execute_query, QueryBuilder
from .utils import parse_config, validate_input

# 2. __all__ (immediately after imports)
__all__ = [
    'DEFAULT_TIMEOUT',
    'ConnectionManager',
    'create_connection',
    'execute_query',
    'QueryBuilder',
    'parse_config',
    'validate_input',
]

# 3. Module-level constants (after __all__)
DEFAULT_TIMEOUT: int = 30

# 4. Class/function definitions (if any - typically in dedicated modules)
```

### Example of Bad Practice (DO NOT USE)
```python
# my_package/__init__.py - AVOID THIS
"""My Package"""

# WRONG: Using absolute imports for sibling modules
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

# WRONG: AVOID - Unnecessarily long absolute imports for sibling modules
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

# WRONG: Class definition in __init__.py (should be in dedicated module)
class ConnectionManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._connection = None

    def connect(self) -> None:
        # 100+ lines of implementation
        pass

    # ... more methods ...

# WRONG: Function definitions in __init__.py (should be in dedicated module)
def execute_query(query: str, params: Optional[Dict] = None):
    # 50+ lines of implementation
    pass

# WRONG: Heavy initialization logic
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

## Script Entry Points

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

## Type Hints and Annotations

### Principle: Use `from __future__ import annotations` for Forward References
- **MANDATORY**: When using forward references (type hints that reference types defined later or in other modules), use `from __future__ import annotations` at the top of the file to avoid quoting type names
- **Pattern**: Place `from __future__ import annotations` as the first import (before any other imports)
- **Rationale**: Makes type hints cleaner and more readable by avoiding quoted strings for forward references
- **Benefits**: Cleaner code, no need to quote type names, better IDE support
- **Example of good practice**:
  ```python
  from __future__ import annotations

  from dataclasses import dataclass
  from typing import Optional, TYPE_CHECKING

  if TYPE_CHECKING:
      from .schema import AssetType, PointRole

  @dataclass
  class Asset:
      name: str
      type: Optional[AssetType] = None  # CORRECT: No quotes needed
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  from dataclasses import dataclass
  from typing import Optional

  @dataclass
  class Asset:
      name: str
      type: Optional["AssetType"] = None  # WRONG: Quotes required without __future__ import
  ```

### Principle: Use Lowercase Built-in Generics for Type Hints
- **MANDATORY**: Use lowercase built-in generic types (`list`, `dict`, `set`, `tuple`) instead of uppercase `typing` module types (`List`, `Dict`, `Set`, `Tuple`)
- **Pattern**: Use `list[str]`, `dict[str, int]`, `set[str]`, `tuple[str, int]` instead of `List[str]`, `Dict[str, int]`, `Set[str]`, `Tuple[str, int]`
- **Rationale**: Python 3.9+ supports lowercase generics directly; they're cleaner and don't require imports from `typing`
- **Benefits**: Cleaner code, fewer imports, better readability, aligns with modern Python style
- **Example of good practice**:
  ```python
  from typing import Any, Optional  # Only import what's needed from typing

  def process_items(items: list[str]) -> dict[str, int]:
      counts: dict[str, int] = {}
      seen: set[str] = set()
      pairs: list[tuple[str, str]] = []
      # ...
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  from typing import List, Dict, Set, Tuple, Any  # WRONG: Unnecessary uppercase imports

  def process_items(items: List[str]) -> Dict[str, int]:  # WRONG: Use lowercase
      counts: Dict[str, int] = {}  # WRONG: Use lowercase
      seen: Set[str] = set()  # WRONG: Use lowercase
      pairs: List[Tuple[str, str]] = []  # WRONG: Use lowercase
  ```
- **Note**: This applies to Python 3.9+. For older Python versions, uppercase `typing` module types may be required.

### Principle: Type Aliases for Complex Types
- **MANDATORY**: For complex nested types, declare named type aliases near the top of the module
- **Pattern**: `UriToPropertiesDict: type = dict[str, dict[str, Any]]`
- **Rationale**: Self-documenting, DRY, easier to maintain
- **Benefits**: Clarity, consistency, single source of truth for type definitions

## Dataclass Patterns

### Principle: Dataclass Creation Timing
- **MANDATORY**: Create dataclass instances RIGHT BEFORE return statements, AFTER all database/IO operations are complete
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

## Import Organization

### Principle: Standard Import Ordering (MANDATORY)
- **MANDATORY**: Imports must follow a consistent ordering pattern for readability and maintainability.
- **Standard Order**:
  1. **Future imports** (if needed): `from __future__ import annotations`
  2. **Standard library imports**: `import argparse`, `import json`, `from pathlib import Path`
  3. **Third-party imports**: `import pandas as pd`, `from tqdm import tqdm`
  4. **Internal/local imports**: `from autonomous_building import ...`
  5. **Within each group**: **MANDATORY** - Alphabetical ordering (unless explicitly instructed/overridden otherwise)

**Example of good practice**:
```python
#!/usr/bin/env python3
"""Example script with proper import ordering"""

# 1. Future imports (if needed)
from __future__ import annotations

# 2. Standard library imports (alphabetical)
import argparse
import json
from pathlib import Path

# 3. Third-party imports (alphabetical)
import pandas as pd

# 4. Internal/local imports
from autonomous_building import AutonomousBuilding
from autonomous_building.util.paths import BUILDINGS_DIR_PATH
```

**Example of bad practice** (DO NOT USE):
```python
# WRONG: Mixed ordering - hard to read and maintain
from autonomous_building import AutonomousBuilding
import json
import pandas as pd
from pathlib import Path
import argparse
```

### Benefits of Standard Import Ordering
- **Readability**: Easy to scan and find imports
- **Consistency**: All files follow the same pattern
- **Tool compatibility**: Works well with auto-formatters (black, isort)
- **Maintainability**: Clear separation between stdlib, third-party, and internal code

### Import Grouping Rules
- **Group by source**: Standard library, third-party, internal
- **Separate groups**: Use blank lines between groups (one blank line is sufficient)
- **Within groups**: **MANDATORY** - Alphabetical ordering (unless explicitly instructed/overridden otherwise)
- **Relative vs absolute**: Use absolute imports for cross-package imports, relative imports for same-package modules. **Within internal imports group**: Absolute imports come first, then relative imports (both alphabetically ordered within their respective subgroups)
- **Organize large import lists**: For large import lists (e.g., many query constants), use comments to group related imports for readability
  - **Pattern**: `# Group name` comment before related imports
  - **When to use**: When importing 10+ items from a single module, especially when they can be logically grouped
  - **Benefits**: Makes large import lists scannable and maintainable
  - **Example**:
    ```python
    from ._graph_db_queries import (
        # SchemaNamespace queries
        UPSERT_SCHEMA_NAMESPACE,
        GET_SCHEMA_NAMESPACE,
        # AssetType queries
        UPSERT_ASSET_TYPE,
        GET_ASSET_TYPE,
    )
    ```

## Progress Tracking

### Principle: Use tqdm for Progress Tracking
- **MANDATORY**: Use `tqdm` for visual progress bars in long-running operations
- **NEVER** use callback functions for progress tracking
- **Pattern**: `for start in tqdm(range(...), desc="Processing", unit="chunk"):`
- **Rationale**: Cleaner API, automatic progress display, no manual callback management
- **Benefits**: Better user experience, less code, consistent progress display
- **Client script usage**: Client scripts should also use `tqdm` when they have their own loops (e.g., iterating over grouped data before calling library methods), even though library methods use `tqdm` internally
- **Example**: When processing grouped data in a client script before calling library methods, wrap the iteration with `tqdm`:
  ```python
  for asset_type_uri, point_role_labels in tqdm(
      asset_type_to_point_role_labels.items(),
      desc="Adding point roles to asset types",
      unit="asset type"
  ):
      # Map labels to URIs and call library method
      schema.add_point_roles_to_asset_type(asset_type_uri, point_role_uris)
  ```

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
                   resource_type: str = 'my-resource-type',  # WRONG: Hardcoded default
                   resource_id: str = 'my-resource-id',      # WRONG: Hardcoded default
                   **kwargs):
          default_pdf = Path(__file__).parent / "file.pdf"  # WRONG: Hardcoded in method
  ```
- Benefits:
  - **Clarity**: Defaults are visible at class level, not buried in method signatures
  - **Maintainability**: Single source of truth for default values
  - **Reusability**: Constants can be referenced elsewhere in the class
  - **Discoverability**: Easy to find and understand all class defaults

## Code Simplification Patterns

### Principle: Prefer `or` Operator for Simple Fallback Patterns (MANDATORY)
- **MANDATORY**: Use the `or` operator instead of `if ... else` for simple fallback patterns when the falsy value behavior is appropriate.
- **Pattern**: Replace `value if value else default` with `value or default`
- **When to use**: When you want to use a default value when the original value is falsy (None, empty string, empty list, empty dict, 0, False, etc.)
- **When NOT to use**: When you need to distinguish between `None` and other falsy values (e.g., `0` or `False` are valid values that should not be replaced)
- **Rationale**: More concise, Pythonic, and easier to read
- **Benefits**: Cleaner code, reduced verbosity, consistent with Python idioms

**Example of good practice**:
```python
# CORRECT: Use 'or' for simple fallback patterns
filtered_properties = {k: v for k, v in properties.items() if k not in ['uri', 'label']}
properties_param = filtered_properties or None  # Empty dict becomes None

tags = properties.get('tags')
tags_param = tags or []  # None or empty list becomes []

value = properties.get('value')
final_value = value or normalized_uri  # None or empty string becomes normalized_uri
```

**Example of bad practice** (DO NOT USE):
```python
# WRONG: Verbose if-else pattern when 'or' is more appropriate
filtered_properties = {k: v for k, v in properties.items() if k not in ['uri', 'label']}
properties_param = filtered_properties if filtered_properties else None  # WRONG: Too verbose

tags = properties.get('tags')
tags_param = tags if tags else []  # WRONG: Too verbose

value = properties.get('value')
final_value = value if value is not None else normalized_uri  # WRONG: Too verbose (unless you need to preserve empty strings)
```

**When to keep `if ... else`**:
```python
# CORRECT: Keep if-else when you need to distinguish None from other falsy values
count = data.get('count')
# If count could be 0 (which is valid), use explicit None check
final_count = count if count is not None else default_count  # CORRECT: Preserves 0 as valid value

# CORRECT: Keep if-else for complex conditions
result = value if condition and other_condition else default  # CORRECT: Complex condition
```

**Common patterns**:
- `value or None` - Use None when value is falsy
- `value or []` - Use empty list when value is falsy (None, empty list, etc.)
- `value or {}` - Use empty dict when value is falsy
- `value or default_string` - Use default string when value is falsy (None, empty string, etc.)
- `value or normalized_uri` - Use normalized URI when value is falsy (common for URI fallbacks)

---

## Output and User Interface Guidelines

### Principle: Avoid Emoji Characters in Output (MANDATORY)

- **MANDATORY**: Do not use emoji characters (checkmarks, X marks, warning symbols, etc.) in print statements, log messages, or any user-facing output.
- **Rationale**: Emoji characters often cause encoding problems on Windows systems, leading to `UnicodeEncodeError` exceptions when the console encoding (typically `cp1252` on Windows) cannot represent these characters.
- **Impact**: Scripts and applications may crash with errors like:
  ```
  UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 0: character maps to <undefined>
  ```
- **Solution**: Use plain text alternatives:
  - "SUCCESS:" or "OK:" or just remove
  - "ERROR:" or "FAILED:"
  - "WARNING:" or "WARN:"
- **When to apply**: All print statements, log messages, error messages, and any text output that may be displayed in a console or terminal.
- **Benefits**: Cross-platform compatibility, reliable execution on Windows, no encoding errors.

**Example of good practice**:
```python
# CORRECT: Plain text - works on all platforms
print("Assets upserted successfully.")
print("WARNING: Some CSV labels not found in database")
print("ERROR: Found 5 assets with conflicting asset_type values")
print("SUCCESS: All CSV labels verified in database")
```

**Example of bad practice** (DO NOT USE):
```python
# WRONG: Emoji characters - causes encoding errors on Windows
print("Assets upserted successfully.")  # Emoji removed for cross-platform compatibility
print("WARNING: Some CSV labels not found in database")  # Emoji removed
print("ERROR: Found 5 assets with conflicting asset_type values")  # Emoji removed
print("SUCCESS: All CSV labels verified in database")  # Emoji removed
```

---

## Lightweight Instantiation

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

---

## Code Review Checklist

### Principle: Regular Code Quality Audits (MANDATORY)

- **MANDATORY**: During code reviews, refactoring sessions, or maintenance work, regularly audit code for quality issues.
- **Review questions to ask**:
  1. **Unused Code**: Does this module/submodule still have unused imports and unused private methods? Those should be deleted.
  2. **Database Efficiency**: Are there loops of database operations that indicate potentially inefficient database handling? Those should be optimized away if confirmed to be of the N+1 variant, or at least raised for mutual discussion.

### Unused Code Removal

- **MANDATORY**: Remove unused code to maintain codebase cleanliness and reduce maintenance burden.
- **What to check for**:
  - Unused imports (not referenced anywhere in the module)
  - Unused private methods (methods starting with `_` that are never called)
  - Unused query files (database query files not loaded or used in code)
  - Unused constants or type aliases
- **Rationale**: Unused code increases cognitive load, can mislead developers, adds maintenance overhead, and clutters the codebase.
- **When to remove**: During code reviews, refactoring sessions, or when explicitly identified.

**Example of good practice**:
```python
# CORRECT: All imports are used
from dataclasses import dataclass
from typing import Any, Optional

# CORRECT: All methods are called somewhere
def _extract_namespace_from_uri(uri: str) -> str:
    # ... used in multiple places
```

**Example of bad practice** (DO NOT USE):
```python
# WRONG: Unused import
from typing import Union  # Never used

# WRONG: Unused private method
def _generate_uri_from_label(label: str) -> str:
    # ... never called anywhere
    pass
```

### Database Efficiency in Loops

- **MANDATORY**: Check for loops of database operations that indicate potentially inefficient database handling.
- **N+1 Query Problem**: Making 1 query to get a list, then N additional queries (one per item) to get related data = N+1 queries total.
- **What to check for**:
  - Loops that iterate over database results and make additional database queries for each item
  - Loops that access relationship properties without pre-loading
  - Patterns that could be optimized with batch queries or pre-fetching
- **Action**: Optimize away if confirmed to be of the N+1 variant, or at least raise for mutual discussion.
- **Solution Pattern**: Pre-fetch all needed data in batch queries, then use in-memory caches for lookups.

**Example of good practice**:
```python
# CORRECT: Pre-fetching pattern - 2 queries total (not N+1)
aspect_uris = [row['uri'] for row in rows]
aspect_nodes = Aspect.nodes.filter(uri__in=aspect_uris)  # 1 batch query
aspect_cache: dict[str, Aspect] = {a.uri: a for a in aspect_nodes}

# Iterate using cache (no additional queries)
for row in rows:
    aspect_node = aspect_cache.get(row['uri'])  # O(1) lookup
    # ... use aspect_node
```

**Example of bad practice** (DO NOT USE):
```python
# WRONG: N+1 problem - 1 + N queries
for row in rows:
    aspect_node = Aspect.nodes.get(uri=row['uri'])  # N queries in loop!
    # ... use aspect_node
```
