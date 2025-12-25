# N+1 Query Problem: Pre-Fetching Solution Pattern

## Problem: The N+1 Query Anti-Pattern

**What it is:** Making 1 query to get a list of records, then N individual queries (one per record) to fetch related data.

**Why it's slow:**
- Database round-trips are expensive (network latency, query parsing, connection overhead)
- Large numbers of individual queries can take minutes or hours
- Each query has overhead even if it returns quickly

**Example:**
```python
# ❌ BAD: N+1 pattern
records = query("SELECT * FROM mappings")  # 1 query

for record in records:  # N records
    related_obj1 = get_or_update_object(record.obj1_id)  # Query 1
    related_obj2 = get_or_update_object(record.obj2_id)  # Query 2
    # Total: 1 + (N × 2) = 2N + 1 queries!
```

**Performance impact:**
- **Before optimization:** Can take minutes or hours for large datasets
- **After optimization:** Typically seconds
- **Speedup:** Often 10-100x faster or more

## Solution: Pre-Fetching / Batch Fetching Pattern

**The pattern:**
1. **Identify what you need:** Collect all unique IDs/URIs you'll need
2. **Bulk fetch once:** Make 1-2 queries to fetch ALL related data upfront
3. **Build lookup caches:** Create dictionaries/hash maps for O(1) lookups
4. **Use caches:** Replace individual queries with dictionary lookups

**Example:**
```python
# ✅ GOOD: Pre-fetching pattern
records = query("SELECT * FROM mappings")  # 1 query

# Collect unique IDs needed
unique_obj1_ids = {record.obj1_id for record in records}
unique_obj2_ids = {record.obj2_id for record in records}

# Bulk fetch ALL related data (2 queries total)
all_obj1s = get_all_objects_by_ids(list(unique_obj1_ids))  # 1 bulk query
all_obj2s = get_all_objects_by_ids(list(unique_obj2_ids))  # 1 bulk query

# Build in-memory lookup caches
obj1_cache = {obj.id: obj for obj in all_obj1s}
obj2_cache = {obj.id: obj for obj in all_obj2s}

# Now use O(1) dictionary lookups (no more queries!)
for record in records:
    obj1 = obj1_cache.get(record.obj1_id)  # O(1) lookup
    obj2 = obj2_cache.get(record.obj2_id)  # O(1) lookup
    # Total: 1 + 2 = 3 queries (down from 2N + 1!)
```

## When to Apply This Pattern

### Red Flags (Signs You Have N+1 Problem)

1. **Looping with database calls:**
   ```python
   for item in items:
       related = get_or_update_related(item.id)  # ❌ Query in loop
   ```

2. **Processing query results with individual lookups:**
   ```python
   results = query("SELECT ...")
   for result in results:
       obj = get_or_update_object(result.uri)  # ❌ Query per result
   ```

3. **Reconstructing objects from query results:**
   ```python
   mappings = []
   for record in query_results:
       obj1 = get_or_update_object(record.obj1_uri)  # ❌ Individual query
       obj2 = get_or_update_object(record.obj2_uri)  # ❌ Individual query
       mappings.append(Mapping(obj1, obj2))
   ```

### When It's Safe to Skip

- **Small datasets:** If you're processing < 10 items, the overhead may not matter
- **One-time operations:** If this code path runs rarely, optimization may not be worth it
- **Already optimized:** If the `get_or_update_*` method already uses caching internally

## Implementation Steps

### Step 1: Identify the Pattern

Look for:
- Loops that call `get_or_update_*` methods
- Methods that process query results and fetch related objects
- Code that reconstructs dataclass instances from query results

### Step 2: Collect Unique Identifiers

```python
# Collect all unique IDs/URIs you'll need
unique_ids = set()
for record in query_results:
    unique_ids.add(record.related_id)
```

### Step 3: Bulk Fetch Once

```python
# Use bulk GET methods if available
all_objects = get_all_objects()  # 1 query for all

# Or fetch by list of IDs if supported
all_objects = get_objects_by_ids(list(unique_ids))  # 1 query with WHERE IN
```

### Step 4: Build Lookup Cache

```python
# Create dictionary for O(1) lookups
object_cache = {obj.id: obj for obj in all_objects}
```

### Step 5: Replace Individual Queries

```python
# Replace this:
obj = get_or_update_object(id)  # ❌ Individual query

# With this:
obj = object_cache.get(id)  # ✅ O(1) lookup
if not obj:
    # Handle missing object (skip, log, or raise)
    continue
```

## Real Example: Processing Mappings

### Before (N+1 Pattern)

```python
result_mappings = []
for parent_id, records in parent_id_to_records.items():
    # ❌ Individual query for each parent (N queries)
    parent = self.get_or_update_parent(parent_id)

    for record in records:
        # ❌ Individual query for each child (M queries)
        child = self.get_or_update_child(record.child_id)

        # Create mapping...
        result_mappings.append(Mapping(parent, child))
```

**Total queries:** N + M individual queries
**Time:** Minutes or hours for large datasets

### After (Pre-Fetching Pattern)

```python
# Step 1: Collect unique IDs needed
unique_parent_ids = set(parent_id_to_records.keys())
unique_child_ids = set()
for records in parent_id_to_records.values():
    for record in records:
        child_id = record.get('child_id')
        if child_id:
            unique_child_ids.add(child_id)

# Step 2: Bulk fetch ALL parents and children (2 queries total)
all_parents = self.get_all_parents()  # 1 bulk query
all_children = self.get_all_children()  # 1 bulk query

# Step 3: Build lookup caches
parent_cache: dict[str, Parent] = {p.id: p for p in all_parents}
child_cache: dict[str, Child] = {c.id: c for c in all_children}

# Step 4: Use caches (O(1) lookups, no queries)
result_mappings = []
for parent_id, records in parent_id_to_records.items():
    parent = parent_cache.get(parent_id)  # ✅ O(1) lookup
    if not parent:
        continue

    for record in records:
        child_id = record.get('child_id')
        if not child_id:
            continue
        child = child_cache.get(child_id)  # ✅ O(1) lookup
        if not child:
            continue

        # Create mapping...
        result_mappings.append(Mapping(parent, child))
```

**Total queries:** 2 bulk queries
**Time:** Seconds
**Speedup:** 10-100x faster or more

## Key Principles

1. **Database round-trips are expensive** - Even fast queries have overhead
2. **Bulk queries are better** - Fetch more data in fewer queries
3. **Memory is cheap** - In-memory dictionaries are fast (O(1) lookups)
4. **Pre-fetch once, use many times** - Build cache once, use throughout processing

## Related Patterns

- **SQL JOIN:** Similar concept - fetch related data in one query
- **Django `select_related()` / `prefetch_related()`:** ORM-level pre-fetching
- **GraphQL DataLoader:** Batch loading pattern for GraphQL
- **Neo4j batch operations:** `UNWIND` with lists for bulk operations
- **MongoDB `$lookup`:** Aggregation pipeline for joining collections

## When Reviewing Code

**Ask yourself:**
- Are there loops that call database methods?
- Are we processing query results and fetching related objects?
- Could we bulk fetch all related data upfront?
- Would pre-fetching reduce the number of queries significantly?

**If yes to any:** Apply the pre-fetching pattern!

## Success Metrics

**Before optimization:**
- Queries: N + M individual queries (where N and M can be thousands)
- Time: Minutes or hours
- Scalability: Gets worse as data grows

**After optimization:**
- Queries: 2-3 bulk queries
- Time: Seconds
- Scalability: Constant time regardless of data size

## Remember

**The pattern is universal:**
- Works in SQL, Neo4j, MongoDB, any database
- Applies to ORMs, raw queries, and graph databases
- Same principle: reduce round-trips, use in-memory lookups

**The key insight:**
> "Database round-trips are expensive. It's much faster to make 2-3 bulk queries than thousands of individual queries, even if you fetch more data than you strictly need."
