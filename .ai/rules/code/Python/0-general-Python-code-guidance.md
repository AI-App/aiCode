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
# ❌ Constants before __all__
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
      type: Optional[AssetType] = None  # ✅ No quotes needed
  ```
- **Example of bad practice** (DO NOT USE):
  ```python
  from dataclasses import dataclass
  from typing import Optional

  @dataclass
  class Asset:
      name: str
      type: Optional["AssetType"] = None  # ❌ Quotes required without __future__ import
  ```

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
# ❌ Mixed ordering - hard to read and maintain
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
