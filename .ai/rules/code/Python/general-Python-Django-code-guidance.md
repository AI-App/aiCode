# General Python Django Code Guidance

This document provides general principles for adapting Django and Django Admin to work with non-standard backends or systems that don't follow Django's default assumptions. These principles apply to any Django integration with alternative ORMs, graph databases, external APIs, or other non-Django-ORM data sources.

## Overview

Django Admin is designed to work with Django's ORM, which assumes:
- Models have a `pk` (primary key) field
- Models are backed by database tables
- Query operations use Django's `Q` objects
- Models follow Django's field and relationship patterns

When integrating Django with non-standard backends (graph databases, external APIs, alternative ORMs, etc.), these assumptions often don't hold. This document provides patterns for adapting Django Admin to work with such systems.

## Core Adaptation Principles

### Principle: Consolidate Integration Complexity

**MANDATORY**: Create base classes that handle all Django adaptation complexity, rather than duplicating code across multiple admin classes.

**Pattern**:
- Create a base `ModelAdmin` class with all necessary overrides
- Create a custom `ChangeList` class with all necessary overrides
- Apply monkey-patches at module level (once, when base classes are imported)
- Subclasses only need to override `get_queryset` to return the appropriate queryset/collection

**Rationale**:
- DRY: All adaptation logic in one place
- Maintainability: Changes to adaptation happen in one place
- Readability: Admin classes are simple and focused
- Extensibility: Easy to add new admin classes

**Benefits**:
- Simpler admin classes (only need to set `list_display`, `search_fields`, `ordering`, and override `get_queryset`)
- Consistent behavior across all admin classes
- Easier to maintain and update adaptation logic
- Clear separation between adaptation complexity and domain-specific admin configuration

### Principle: Identify and Handle All Backend Differences

**MANDATORY**: Systematically identify all differences between Django's expectations and your backend, then handle them in base classes.

**Common Differences to Address**:

1. **Primary Key Differences**
   - Django expects `pk` field → Backend may use different identifier
   - **Solution**: Add `pk` property to model classes, override `ChangeList._get_deterministic_ordering` to filter out `pk`

2. **Query Object Differences**
   - Django uses `django.db.models.Q` → Backend may use different query objects
   - **Solution**: Override `get_queryset` and `get_search_results` in base `ModelAdmin` to use backend's query objects

3. **Database Table Assumptions**
   - Django expects database tables → Backend may not use tables
   - **Solution**: Set `managed = False` in Meta, override permission methods to return `True`

4. **Queryset Interface Differences**
   - Django expects queryset-like objects with `.filter()`, `.count()`, `._clone()` → Backend may return lists or different interfaces
   - **Solution**: Wrap backend collections with queryset-like wrapper in `ChangeList.get_results`

5. **Field Interface Differences**
   - Django Admin expects fields with `empty_values` attribute → Backend fields may not have this
   - **Solution**: Monkey-patch backend field classes to add missing attributes

6. **Model Metadata Differences**
   - Django expects `model._meta.pk` to exist → Backend models may not have this
   - Django Admin expects consistent `model._meta` object → Backend may recreate `_meta` on each access
   - Django Admin uses `model._meta.model_name` for URL generation → Backend may use base class name instead of actual class name
   - **Solution**: 
     - Cache `_meta` classproperty after first creation to ensure Django Admin gets consistent object
     - Explicitly set `opts.model_name` and `opts.object_name` after `contribute_to_class` to ensure correct model name
     - Skip processing for base classes that start with `_` to avoid URL conflicts

7. **Serialization Differences**
   - Django Admin calls `serializable_value(field_name)` → Backend may not handle `None` field names
   - **Solution**: Monkey-patch backend model classes to handle edge cases

8. **Metaclass Conflicts**
   - Base class may need to inherit from both backend base class and `ABC` → Python requires combined metaclass
   - **Solution**: Create combined metaclass that inherits from both backend's metaclass and `ABCMeta`

9. **Form Validation Method Differences**
   - Django Admin calls `full_clean(validate_unique, validate_constraints)` → Backend may not accept these parameters
   - Django Admin calls `validate_constraints()` → Backend may not have this method
   - **Solution**: Override `full_clean()` to accept and ignore Django ORM parameters, add no-op `validate_constraints()` method

**Rationale**: All of these differences are fundamental to Django-backend integration and should be handled once in base classes, not repeated in every admin class.

### Principle: Model Configuration Requirements

**MANDATORY**: All backend model classes must be configured for Django Admin compatibility.

**Common Requirements**:

1. **Add `pk` property**: Return backend's unique identifier to satisfy Django Admin's expectation of `obj.pk`. If the backend doesn't allow querying by internal identifiers, use a preferred unique field (e.g., `uri`, `name`) instead.
   ```python
   # Pattern 1: Simple pk property (if backend allows querying by internal identifier)
   @property
   def pk(self):
       """Return unique identifier as pk to adapt backend to Django conventions."""
       return self.backend_unique_id

   # Pattern 2: Abstract pk property with field name specification (recommended)
   # In base class:
   class BackendNode(BackendBase, ABC, metaclass=CombinedMeta):
       _pk_field_name: str = None  # Each subclass must set this

       @property
       @abstractmethod
       def pk(self):
           """Return unique identifier as pk to adapt backend to Django conventions."""
           raise NotImplementedError("Subclasses must implement pk property")

   # In subclass:
   class Asset(BackendNode):
       _pk_field_name = 'name'  # Field name used for primary key queries

       @property
       def pk(self):
           """Return name as pk to adapt backend to Django conventions."""
           return self.name
   ```

2. **Set `managed = False` in Meta**: Prevents Django from expecting database tables
   ```python
   class Meta:
       managed = False  # Prevent Django from managing this model in the RDBMS
   ```

3. **Set default ordering in Meta**: Use actual field names instead of `'pk'`
   ```python
   class Meta:
       ordering: tuple[str, ...] = ('name',)  # Use actual field, not 'pk'
   ```

4. **Provide Django-compatible field interface**: Ensure fields have attributes Django Admin expects (e.g., `empty_values`)

5. **Override form validation methods if needed**: If backend doesn't support Django ORM validation parameters, override `full_clean()` and add `validate_constraints()` method
   ```python
   def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
       """Override to accept Django ORM parameters that backend doesn't support."""
       # Accept parameters but ignore Django ORM-specific ones
       return super().full_clean(exclude=exclude)

   def validate_constraints(self, exclude=None):
       """Override to satisfy Django Admin's expectations."""
       # Backend doesn't have Django ORM constraints, so this is a no-op
       pass
   ```

6. **Provide default `__str__` method**: Base class can provide default string representation using `pk` property
   ```python
   def __str__(self) -> str:
       """Default string representation using pk property."""
       return str(self.pk)
   ```

**Example**:
```python
class Asset(BackendNode):
    _pk_field_name = 'name'  # Field name used for primary key queries

    name: str
    # ... other fields ...

    @property
    def pk(self):
        """Return name as pk to adapt backend to Django conventions."""
        return self.name

    @classproperty
    def _meta(self):
        """Return Django Options object, cached after first creation."""
        # Cache _meta to avoid recreating Options object each time
        # This is important for Django Admin to properly read verbose_name and verbose_name_plural
        if hasattr(self, '_cached_meta'):
            return self._cached_meta

        opts = Options(self.Meta, app_label=self.Meta.app_label)
        actual_class_name = self.__name__

        # Skip processing for base classes that start with underscore
        # This prevents Django Admin from trying to register abstract-like base classes
        # and avoids URL conflicts where all subclasses resolve to the base class name.
        if actual_class_name.startswith('_'):
            import warnings
            warnings.warn(
                f"Model class name '{actual_class_name}' starts with underscore. "
                f"This may cause Django Admin URL conflicts if used as a base class."
            )

        opts.contribute_to_class(self, actual_class_name)

        # Explicitly set model_name and object_name AFTER contribute_to_class
        # Django Admin uses model._meta.model_name for URL generation
        # We set these explicitly to ensure they're correct, even if contribute_to_class has issues
        opts.model_name = actual_class_name.lower()
        opts.object_name = actual_class_name
        # Note: label_lower is a read-only property computed by Django from app_label and model_name

        # ... rest of _meta setup ...

        setattr(self, '_cached_meta', opts)
        return opts

    class Meta:
        app_label: str = 'your_app'
        verbose_name: str = 'Asset'
        verbose_name_plural: str = 'Assets'
        ordering: tuple[str, ...] = ('name',)
        managed = False  # Prevent Django from managing this model
```

**Note**: If the backend base class provides a default `__str__` method that returns `str(self.pk)`, subclasses don't need to implement `__str__` unless they need a different string representation.

### Principle: Admin Class Simplicity

**MANDATORY**: Admin classes should be simple and focused, inheriting from base classes that handle adaptation complexity.

**Pattern**:
```python
@register(Asset)
class AssetAdmin(AdaptedModelAdmin):
    list_display = ('name', 'uuid')
    search_fields = ('name', 'uuid')
    ordering = ('name',)

    def get_queryset(self, request):
        """Return Asset collection for Django Admin."""
        return Asset.backend_query.all()
```

**Rationale**:
- Admin classes should focus on domain-specific configuration (`list_display`, `search_fields`, `ordering`)
- Adaptation complexity belongs in base classes
- Easy to add new admin classes following the same pattern

### Principle: Search Functionality Adaptation

**MANDATORY**: Base classes should provide default search functionality adapted to the backend's query system.

**Pattern**:
- Base `ModelAdmin` class should override `get_search_results` to convert search terms to backend's query objects
- Use backend's query objects (not Django's `Q` objects)
- Support Django-like filter operators if backend supports them (`__icontains`, `__exact`, `__startswith`, etc.)
- Combine multiple search fields with OR logic by default

**Rationale**:
- Many backends support Django-like filter operators, making search implementation straightforward
- Default implementation works for most cases
- Subclasses can override for custom search behavior if needed

**Example**:
```python
def get_search_results(self, request, queryset, search_term):
    """Override to handle search using backend's query objects."""
    if search_term and self.search_fields:
        from backend.query import Q as BackendQ
        q_objects = []
        for field in self.search_fields:
            q_objects.append(BackendQ(**{f"{field}__icontains": search_term}))
        # Combine with OR
        if q_objects:
            combined_q = q_objects[0]
            for q_obj in q_objects[1:]:
                combined_q = combined_q | q_obj
            queryset = queryset.filter(combined_q)
    return queryset, False  # False = no distinct needed
```

### Principle: Error Handling and Logging

**MANDATORY**: Base classes should include comprehensive error handling and logging.

**Pattern**:
- Catch and log exceptions in all override methods
- Use structured logging with context (model name, request path, etc.)
- Re-raise exceptions after logging to allow Django's default error handling

**Rationale**:
- Django-backend integration can fail in subtle ways
- Comprehensive logging helps debug issues quickly
- Error handling prevents silent failures

**Example**:
```python
def changelist_view(self, request, extra_context=None):
    """Override to catch and log exceptions before Django Admin's error handling."""
    try:
        return super().changelist_view(request, extra_context)
    except Exception as e:
        logger.error(
            f"Exception in {self.__class__.__name__}.changelist_view: {e}",
            exc_info=True,
            stack_info=True
        )
        raise
```

### Principle: Monkey-Patching Strategy

**MANDATORY**: Apply monkey-patches at module level when base classes are imported, not in individual admin files.

**Pattern**:
- Monkey-patches applied once in base class module
- Check if already patched to prevent duplicate patching
- Document why each patch is necessary

**Rationale**:
- Prevents duplicate patching when multiple admin files are imported
- Centralizes all adaptation hacks in one place
- Makes it clear what patches are applied and why

**Example**:
```python
# In base class module
from backend import BackendField

# Monkey-patch BackendField to add empty_values attribute for Django Admin compatibility
# Django Admin's display_for_field expects field.empty_values, but BackendField doesn't have it
if not hasattr(BackendField, 'empty_values'):
    BackendField.empty_values = [None, '']
```

## Base Class Structure

### Base ModelAdmin Class

**Responsibilities**:
- Override `changelist_view` for error handling
- Override `get_changelist` to return custom `ChangeList`
- Override permission methods (`has_add_permission`, etc.) to return `True` (if backend doesn't use Django tables)
- Provide abstract `get_queryset` method (must be overridden by subclasses)
- Provide default `get_search_results` implementation using backend's query objects

**Example Structure**:
```python
class AdaptedModelAdmin(ModelAdmin):
    """Base ModelAdmin class for non-Django-ORM backends."""

    def changelist_view(self, request, extra_context=None):
        """Override to catch and log exceptions."""
        try:
            return super().changelist_view(request, extra_context)
        except Exception as e:
            logger.error(f"Exception in {self.__class__.__name__}: {e}", exc_info=True)
            raise

    def get_changelist(self, request, **kwargs):
        """Override to use custom ChangeList."""
        return AdaptedChangeList

    def has_add_permission(self, request):
        """Override to prevent Django from checking database table existence."""
        return True

    def get_queryset(self, request):
        """Must be overridden by subclasses."""
        raise NotImplementedError(
            f"{self.__class__.__name__}.get_queryset() must be overridden."
        )

    def get_search_results(self, request, queryset, search_term):
        """Override to use backend's query objects."""
        # Implementation using backend's query system
        ...
```

### Custom ChangeList Class

**Responsibilities**:
- Override `__init__` to handle backend model metadata differences (e.g., mock `model._meta.pk` if needed)
- Override `get_queryset` to return clean queryset from ModelAdmin (bypass Django ORM filtering)
- Override `_get_deterministic_ordering` to filter out `pk` from ordering (if backend doesn't have `pk`)
- Override `url_for_result` to handle `None` `pk_attname` (if backend doesn't have Django-style primary keys)
- Override `get_results` to wrap backend collections with queryset-like wrapper (if backend returns lists or different interfaces)

**Example Structure**:
```python
class AdaptedChangeList(ChangeList):
    """Custom ChangeList that handles backend differences."""

    def __init__(self, request, model, ...):
        """Override to handle backend model metadata differences."""
        # Mock model._meta.pk if backend doesn't have Django-style primary key
        if hasattr(model._meta, 'pk') and model._meta.pk is None:
            class MockPk:
                attname = None
            original_pk = model._meta.pk
            model._meta.pk = MockPk()
            try:
                super().__init__(request, model, ...)
                self.pk_attname = None
            finally:
                model._meta.pk = original_pk
        else:
            super().__init__(request, model, ...)

    def get_queryset(self, request):
        """Override to prevent Django Admin from applying Django ORM filters."""
        return self.model_admin.get_queryset(request)

    def _get_deterministic_ordering(self, ordering):
        """Override to filter out 'pk' from ordering."""
        return tuple(o for o in ordering if o not in ('pk', '-pk'))

    def url_for_result(self, result):
        """Override to handle backend nodes that use pk property instead of pk_attname."""
        original_pk_attname = self.pk_attname
        self.pk_attname = 'pk'  # Use property on backend nodes
        try:
            return super().url_for_result(result)
        finally:
            self.pk_attname = original_pk_attname

    def get_results(self, request):
        """Override to wrap backend collections with queryset-like wrapper."""
        # Wrap lists or other collections to provide queryset-like interface
        ...
```

### Queryset-Like Wrapper

**When Needed**: If backend returns lists or collections that don't have queryset-like methods (`.count()`, `._clone()`, etc.)

**Pattern**:
```python
class QuerysetWrapper:
    """Wrapper that provides queryset-like interface for backend collections."""

    def __init__(self, items):
        self.items = items

    def count(self):
        return len(self.items)

    def _clone(self):
        return QuerysetWrapper(self.items[:])

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def __len__(self):
        return len(self.items)
```

## Django Settings Configuration

### Backend Connection Initialization

**MANDATORY**: Initialize backend connection in Django settings before Django Admin tries to access it.

**Pattern**:
```python
# In settings.py
from your_backend import BackendInitializer

# Load and initialize backend connection
BackendInitializer.load()

# Verify backend connection at startup
try:
    from your_app.models import YourModel
    test_items = list(YourModel.backend_query.all()[:1])
    if test_items:
        print("✅ Backend connection verified successfully.")
    else:
        print("✅ Backend connection verified successfully (no items found).")
except Exception as e:
    logger.error(f"⚠️  WARNING: Backend connection check failed: {e}", exc_info=True)
```

**Rationale**:
- Ensures backend connection is available when Django Admin tries to access it
- Catches connection issues early at startup
- Provides clear feedback about connection status

### Logging Configuration

**MANDATORY**: Configure comprehensive logging to see errors in console.

**Pattern**:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {asctime} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'your_app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'your_backend': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

**Rationale**:
- Django-backend integration issues can be subtle
- Comprehensive logging helps debug issues quickly
- Console output is immediately visible during development

## Common Adaptation Patterns

### Pattern: Primary Key Adaptation

**Issue**: Django Admin expects `obj.pk`, but backend uses different identifier.

**Solution**:
1. Add `pk` property to model classes
2. Override `ChangeList._get_deterministic_ordering` to filter out `pk` from ordering
3. Override `ChangeList.url_for_result` to handle `None` `pk_attname`

### Pattern: Query Object Adaptation

**Issue**: Django Admin uses Django `Q` objects, but backend uses different query objects.

**Solution**:
1. Override `ModelAdmin.get_queryset` to return clean backend queryset
2. Override `ModelAdmin.get_search_results` to use backend's query objects
3. Override `ChangeList.get_queryset` to bypass Django ORM filtering

### Pattern: Queryset Interface Adaptation

**Issue**: Django Admin expects queryset-like objects, but backend returns lists or different interfaces.

**CRITICAL WARNING**: **NEVER** return a plain `list` from `get_queryset()` or any method that Django Admin expects to return a QuerySet/NodeSet. Django Admin relies on queryset-like objects for:
- Pagination (calls `.count()`)
- Filtering and ordering (calls `.order_by()`, `.filter()`)
- Slicing (calls `.__getitem__()`)
- Cloning (calls `._clone()`)

Returning a list will cause Django Admin to fail with opaque "Database error" messages when it tries to call queryset methods that don't exist on lists.

**Solution**:
1. **Always return the original queryset/NodeSet** from `get_queryset()`, never a list
2. If you need to materialize the queryset (e.g., to attach prefetched data), do so internally but still return the queryset
3. If backend returns lists, create queryset-like wrapper class
4. Override `ChangeList.get_results` to wrap backend collections with wrapper
5. Provide `.count()`, `._clone()`, and iteration methods in wrapper

### Pattern: Instance-Level Caching for Django Admin Display Methods

**Issue**: Django Admin may create new instances of model objects when rendering the changelist, causing prefetched data attached to original instances to be lost.

**Solution**: Use instance-level caching on the `ModelAdmin` class to store prefetched data, ensuring it persists across Django Admin's internal object re-instantiations.

**Pattern**:
```python
class AssetTypeAdmin(DjangoNeoModelAdmin):
    def get_queryset(self, request):
        """Prefetch related data and cache it on admin instance."""
        asset_types = super().get_queryset(request)
        
        # Collect identifiers for batch query
        asset_type_uris = [at.uri for at in asset_types]
        
        # Execute batch query to prefetch relationships
        results, _ = db.cypher_query(
            GET_ASSET_TYPES_WITH_RELATIONSHIPS,
            {'asset_type_uris': asset_type_uris}
        )
        
        # Build cache on admin instance (not on model instances)
        if not hasattr(self, '_prefetch_cache'):
            self._prefetch_cache = {}
        
        # Store prefetched data in cache keyed by primary identifier
        for row in results:
            uri = row['uri']
            self._prefetch_cache[uri] = {
                'point_role_uris': row.get('point_role_uris', [])
            }
        
        # Also attach to instances if possible (for direct access)
        for at in asset_types:
            if at.uri in self._prefetch_cache:
                at._prefetched_point_role_uris = self._prefetch_cache[at.uri]['point_role_uris']
        
        return asset_types  # Return queryset, not list
    
    def point_roles(self, obj):
        """Display method that uses cached prefetched data."""
        # First check if data is attached directly to instance
        if hasattr(obj, '_prefetched_point_role_uris'):
            uris = obj._prefetched_point_role_uris
        # Fall back to instance-level cache
        elif hasattr(self, '_prefetch_cache') and obj.uri in self._prefetch_cache:
            uris = self._prefetch_cache[obj.uri].get('point_role_uris', [])
        else:
            uris = []
        
        # Filter out None values from OPTIONAL MATCH
        uris = [uri for uri in uris if uri is not None]
        return '   |   '.join(uris) if uris else '-'
```

**Rationale**:
- Django Admin may create new instances when rendering, losing data attached to original instances
- Instance-level cache on `ModelAdmin` persists across all object instantiations
- Display methods can check both instance attributes and cache for maximum compatibility

**Benefits**:
- Prefetched data persists even if Django Admin creates new instances
- Works with both direct instance attachment and cache lookup
- Enables efficient bulk queries to avoid N+1 problems

### Pattern: Django Admin Display Separators (MANDATORY)

**Issue**: Django Admin tables do not display newlines in cell content, so multi-line displays (e.g., bulleted lists) are not rendered correctly.

**Solution**: Use pipe-separated format (`'   |   '`) instead of newlines for list displays in Django Admin tables.

**Pattern**:
```python
def point_roles(self, obj):
    """Display method that returns pipe-separated list."""
    uris = self._get_point_role_uris(obj)
    # Filter out None values from OPTIONAL MATCH
    uris = [uri for uri in uris if uri is not None]
    # Use pipe separator instead of newlines (Django Admin doesn't display newlines)
    return '   |   '.join(uris) if uris else '-'
```

**Rationale**:
- Django Admin tables render cell content as plain text, not HTML
- Newlines (`\n`) are not displayed in table cells
- Pipe separators (`'   |   '`) provide clear visual separation while being readable in table format

**Benefits**:
- Clear visual separation between items
- Readable in Django Admin table format
- Consistent formatting across all list displays
- Works with Django Admin's plain text rendering

**Example of good practice**:
```python
# CORRECT: Pipe-separated format for Django Admin tables
def asset_types(self, obj):
    uris = self._get_asset_type_uris(obj)
    return '   |   '.join(uris) if uris else '-'

def aspects(self, obj):
    uris = self._get_aspect_uris(obj)
    return '   |   '.join(uris) if uris else '-'
```

**Example of bad practice** (DO NOT USE):
```python
# WRONG: Newlines not displayed in Django Admin tables
def asset_types(self, obj):
    uris = self._get_asset_type_uris(obj)
    return '\n'.join(f'- {uri}' for uri in uris) if uris else '-'  # Newlines won't show
```

### Pattern: Field Interface Adaptation

**Issue**: Django Admin expects fields with specific attributes (e.g., `empty_values`), but backend fields don't have them.

**Solution**:
1. Monkey-patch backend field classes to add missing attributes
2. Apply patches at module level when base classes are imported
3. Check if already patched to prevent duplicate patching

### Pattern: Model Metadata Adaptation

**Issue**: Django Admin expects `model._meta.pk` to exist, but backend models don't have this.

**Solution**:
1. Mock `model._meta.pk` in `ChangeList.__init__` if needed
2. Set `pk_attname = None` after initialization
3. Restore original `pk` in `finally` block

### Pattern: Metaclass Conflict Resolution

**Issue**: Base class needs to inherit from both backend base class and `ABC`, but they have different metaclasses.

**Solution**:
1. Get the metaclass of the backend base class using `type(BackendBase)`
2. Create a combined metaclass that inherits from both backend's metaclass and `ABCMeta`
3. Use the combined metaclass in the base class definition

**Example**:
```python
from abc import ABC, ABCMeta, abstractmethod
from backend import BackendBase

# Get the metaclass of BackendBase to combine with ABCMeta
_BackendBaseMeta = type(BackendBase)

class _CombinedMeta(_BackendBaseMeta, ABCMeta):
    """Combined metaclass for AdaptedBackendNode.

    This metaclass combines the metaclass of BackendBase with ABCMeta
    to allow AdaptedBackendNode to inherit from both BackendBase and ABC without metaclass conflicts.
    """
    pass

class AdaptedBackendNode(BackendBase, ABC, metaclass=_CombinedMeta):
    """Base class for backend nodes that work with Django Admin."""
    # ... rest of class ...
```

### Pattern: Form Validation Method Adaptation

**Issue**: Django Admin's `ModelForm` calls `full_clean(validate_unique, validate_constraints)` and `validate_constraints()`, but backend doesn't support these Django ORM-specific parameters/methods.

**Solution**:
1. Override `full_clean()` in base model class to accept Django ORM parameters but ignore them
2. Add no-op `validate_constraints()` method to base model class

**Example**:
```python
def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
    """Override to accept Django ORM parameters that backend doesn't support.

    Django Admin's ModelForm calls full_clean() with validate_unique and validate_constraints
    parameters, but backend's full_clean() doesn't accept these parameters.
    This override accepts them but ignores them, since backend doesn't have Django ORM
    constraints or unique validation in the same way.

    Args:
        exclude: Fields to exclude from validation (passed to parent)
        validate_unique: Ignored (Django ORM-specific)
        validate_constraints: Ignored (Django ORM-specific)
    """
    # Call parent full_clean with only the exclude parameter
    return super().full_clean(exclude=exclude)

def validate_constraints(self, exclude=None):
    """Override to satisfy Django Admin's expectations.

    Django Admin's ModelForm calls validate_constraints() on the model instance,
    but backend doesn't have this method. This override provides a no-op
    implementation since backend doesn't have Django ORM constraints.

    Args:
        exclude: Fields to exclude from constraint validation (ignored)
    """
    # Backend doesn't have Django ORM constraints, so this is a no-op
    pass
```

## Troubleshooting Guide

### Issue: "Database error" Page in Django Admin

**Possible Causes**:
1. **`get_queryset()` returning a `list` instead of QuerySet/NodeSet** (most common)
2. Backend connection not initialized
3. Exception in admin code
4. Missing `managed = False` in Meta classes
5. Permission methods not overridden

**Solutions**:
1. **CRITICAL**: Ensure `get_queryset()` returns a QuerySet/NodeSet, never a `list`. Django Admin requires queryset-like objects for pagination, filtering, and other operations.
2. Ensure backend connection is initialized in Django settings
3. Add error handling and logging to admin methods
4. Set `managed = False` in all backend model Meta classes
5. Override permission methods to return `True`

### Issue: "ValueError: No such property pk"

**Cause**: Django Admin trying to order by `pk`, but backend doesn't have Django-style primary key.

**Solution**:
- Add `pk` property to model classes
- Set ordering in model `Meta` classes and admin classes using actual field names
- Base `ChangeList` class should filter out `pk` from ordering

### Issue: "TypeError: 'Q' object is not subscriptable" or similar query errors

**Cause**: Django Admin passing Django `Q` objects to backend, which expects its own query objects.

**Solution**:
- Base `ModelAdmin` class should override `get_queryset` to return clean backend queryset
- Base `ModelAdmin` class should override `get_search_results` to use backend's query objects
- Base `ChangeList` class should override `get_queryset` to bypass Django ORM filtering

### Issue: "AttributeError: 'list' object has no attribute 'count'" or "Database error" Page

**Cause**: Django Admin expects queryset-like objects (QuerySet/NodeSet), but `get_queryset()` returned a plain `list`.

**CRITICAL**: **NEVER** return a `list` from `get_queryset()`. Django Admin requires queryset-like objects that support:
- `.count()` for pagination
- `.order_by()` for sorting
- `.filter()` for filtering
- `._clone()` for queryset cloning
- Slicing operations

When Django Admin tries to call these methods on a list, it fails with opaque "Database error" messages.

**Solution**:
- **Always return the original queryset/NodeSet** from `get_queryset()`, never a list
- If you need to materialize data (e.g., for prefetching), do so internally but return the queryset
- If backend naturally returns lists, create a queryset-like wrapper class that provides all required methods
- Override `ChangeList.get_results` to wrap backend collections with the wrapper

## Best Practices

### 1. Start with Base Classes

**MANDATORY**: Always create base classes first, then build admin classes on top of them.

**Rationale**: Base classes handle all adaptation complexity, making admin classes simple and maintainable.

### 2. Document All Adaptations

**MANDATORY**: Document why each adaptation is necessary and what backend difference it addresses.

**Rationale**: Makes it clear what adaptations are needed and why, helping future maintainers understand the code.

### 3. Test Incrementally

**MANDATORY**: Test each adaptation as you add it, not all at once.

**Rationale**: Makes it easier to identify which adaptation fixes which issue, and prevents regressions.

### 4. Keep Admin Classes Simple

**MANDATORY**: Admin classes should only contain domain-specific configuration, not adaptation logic.

**Rationale**: Adaptation logic belongs in base classes, making admin classes easy to read and maintain.

## References

- [Django Admin Customization](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
- [Django Model Meta Options](https://docs.djangoproject.com/en/stable/ref/models/options/)
- [Django QuerySet API](https://docs.djangoproject.com/en/stable/ref/models/querysets/)
