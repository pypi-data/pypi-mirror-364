# ☕ Coffy

**Coffy** is a lightweight embedded database engine for Python, designed for local-first apps, scripts, and tools. It includes:

- `coffy.nosql`: A simple JSON-backed NoSQL engine with a fluent, chainable query interface  
- `coffy.sql`: A wrapper over SQLite for executing raw SQL with clean tabular results  
- `coffy.graph`: An graph engine built on `networkx` with advanced filtering and logic-based querying

No dependencies (except `networkx`). No boilerplate. Just data.

---

## 🔧 Install

```bash
pip install coffy
```

---

## 📂 Modules

### `coffy.nosql`

- JSON-based collections with fluent `.where().eq().gt()...` query chaining  
- Joins, updates, filters, aggregation, export/import  
- All data saved to human-readable `.json` files  

📄 [NoSQL Documentation →](./NOSQL_DOCS.md)

---

### `coffy.sql`

- SQLite-backed engine with raw SQL query support  
- Outputs as readable tables or exportable lists  
- Uses in-memory DB by default, or json-based if initialized with a path  

📄 [SQL Documentation →](./SQL_DOCS.md)

---

### `coffy.graph`

- Wrapper around `networkx` with simplified node/relationship API  
- Query nodes and relationships using filters like `gt`, `lt`, `eq`, `or`, `not`  
- Uses in-memory DB by default, or json-based if initialized with a path  

📄 [Graph Documentation →](./GRAPH_DOCS.md)

---

## 🧪 Example

```python
from coffy.nosql import db

users = db("users", path="users.json")
users.add({"id": 1, "name": "Neel"})
print(users.where("name").eq("Neel").first())
```

```python
from coffy.sql import init, query

init("app.db")
query("CREATE TABLE test (id INT, name TEXT)")
query("INSERT INTO test VALUES (1, 'Neel')")
print(query("SELECT * FROM test"))
```

```python
from coffy.graph import GraphDB

g = GraphDB(directed=True)
g.add_nodes([{"id": 1, "name": "Neel"}, {"id": 2, "name": "Tanaya"}])
g.add_relationships([{"source": 1, "target": 2, "type": "friend"}])
print(g.find_relationships(type="friend"))
```

---

## 📄 License

MIT © 2025 nsarathy