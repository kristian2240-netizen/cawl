---
name: knowledge-graph-search
description: "Search and query the knowledge graph. Find entities, relations, and connections. Apply when researching or looking up information."
user-invocable: true
---

# Knowledge Graph Search

The knowledge graph is at `memory/knowledge-graph.json`. It stores entities (things) and relations (connections between things).

## How to Search

### Search by ID
```python
# Exact match
entity = next((e for e in data["entities"] if e["id"] == "tech-priest-alpha"), None)
```

### Search by Type
```python
# All agents
agents = [e for e in data["entities"] if e["type"] == "agent"]

# All providers
providers = [e for e in data["entities"] if e["type"] == "provider"]

# All models
models = [e for e in data["entities"] if e["type"] == "model"]

# All projects
projects = [e for e in data["entities"] if e["type"] == "project"]
```

### Search by Name (fuzzy)
```python
# Partial match
results = [e for e in data["entities"] if "groq" in e["name"].lower()]

# Multiple terms
results = [e for e in data["entities"] if any(term in e["name"].lower() for term in ["priest", "alpha"])]
```

### Search by Properties
```python
# By property value
fast = [e for e in data["entities"] if e["properties"].get("speed") and "fast" in str(e["properties"]["speed"]).lower()]

# By status
broken = [e for e in data["entities"] if "broken" in str(e["properties"].get("status", "")).lower()]

# By role
reasoning = [e for e in data["entities"] if "reasoning" in str(e["properties"].get("role", "")).lower()]
```

### Search Relations
```python
# Find what an entity is connected to
outgoing = [r for r in data["relations"] if r["source"] == "tech-priest-alpha"]
incoming = [r for r in data["relations"] if r["target"] == "tech-priest-alpha"]

# Find all relations of a type
delegations = [r for r in data["relations"] if r["type"] == "delegates_to"]
bindings = [r for r in data["relations"] if r["type"] == "bound_to"]

# Find connection path between two entities
def find_path(source, target, relations, visited=None):
    if visited is None:
        visited = set()
    if source == target:
        return [source]
    visited.add(source)
    for r in relations:
        if r["source"] == source and r["target"] not in visited:
            path = find_path(r["target"], target, relations, visited)
            if path:
                return [source] + path
    return None
```

### Full-Text Search
```python
# Search all fields
def search_all(query, entities):
    query = query.lower()
    results = []
    for e in entities:
        score = 0
        if query in e["name"].lower():
            score += 10
        if query in e["id"].lower():
            score += 8
        if query in str(e["properties"]).lower():
            score += 5
        if score > 0:
            results.append((score, e))
    return sorted(results, key=lambda x: -x[0])
```

## Common Queries

### "What's the fastest provider?"
```python
fast = [e for e in entities if e["type"] == "provider"]
fast.sort(key=lambda e: e["properties"].get("latency_ms", 9999))
return fast[0]
```

### "What models does provider X have?"
```python
# Find relations from provider
provider_id = "groq-provider"
models = [r["source"] for r in relations if r["target"] == provider_id and r["type"] == "bound_to"]
```

### "What does entity X do?"
```python
entity = next((e for e in entities if e["id"] == entity_id), None)
if entity:
    return f"{entity['name']}: {entity['properties'].get('role', 'No role defined')}"
```

### "Show me all broken things"
```python
broken = [e for e in entities if "broken" in str(e["properties"].get("status", "")).lower()]
return broken
```

### "What's connected to entity X?"
```python
outgoing = [r for r in relations if r["source"] == entity_id]
incoming = [r for r in relations if r["target"] == entity_id]
return outgoing + incoming
```

## Updating the Graph

When adding new entities:
1. Generate a unique ID (lowercase-kebab-case)
2. Add entity with `created` and `lastAccessed` dates
3. Add relations to connect it
4. Update `metadata.entityCount` and `metadata.relationCount`
5. Update `metadata.lastConsolidated` to today

## Graph Maintenance

- **Consolidate weekly:** Merge duplicate entities, update stale data
- **Prune monthly:** Remove entities that are no longer relevant
- **Backup:** Keep a copy before major changes
