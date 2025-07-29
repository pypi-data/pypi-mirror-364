import networkx as nx
import json
import os

class GraphDB:
    def __init__(self, directed=False, path=None):
        self.g = nx.DiGraph() if directed else nx.Graph()
        self.directed = directed
        self.path = path
        if path and os.path.exists(path):
            self.load(path)

    # Node operations
    def add_node(self, node_id, **attrs):
        self.g.add_node(node_id, **attrs)

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})

    def get_node(self, node_id):
        return self.g.nodes[node_id]

    def remove_node(self, node_id):
        self.g.remove_node(node_id)

    # Relationship (edge) operations
    def add_relationship(self, source, target, **attrs):
        self.g.add_edge(source, target, **attrs)

    def add_relationships(self, relationships):
        for rel in relationships:
            self.add_relationship(rel["source"], rel["target"],
                                  **{k: v for k, v in rel.items() if k not in ["source", "target"]})

    def get_relationship(self, source, target):
        return self.g.get_edge_data(source, target)

    def remove_relationship(self, source, target):
        self.g.remove_edge(source, target)

    # Basic queries
    def neighbors(self, node_id):
        return list(self.g.neighbors(node_id))

    def degree(self, node_id):
        return self.g.degree[node_id]

    def has_node(self, node_id):
        return self.g.has_node(node_id)

    def has_relationship(self, u, v):
        return self.g.has_edge(u, v)

    # Advanced node search
    def find_nodes(self, **conditions):
        return [
            {"id": n, **a} for n, a in self.g.nodes(data=True)
            if self._match_conditions(a, conditions)
        ]

    def find_relationships(self, **conditions):
        return [
            {"source": u, "target": v, **a} for u, v, a in self.g.edges(data=True)
            if self._match_conditions(a, conditions)
        ]

    def _match_conditions(self, attrs, conditions):
        if not conditions:
            return True
        logic = conditions.pop("_logic", "and")
        results = []

        for key, expected in conditions.items():
            actual = attrs.get(key)
            if isinstance(expected, dict):
                for op, val in expected.items():
                    if op == "gt": results.append(actual > val)
                    elif op == "lt": results.append(actual < val)
                    elif op == "gte": results.append(actual >= val)
                    elif op == "lte": results.append(actual <= val)
                    elif op == "ne": results.append(actual != val)
                    elif op == "eq": results.append(actual == val)
                    else: results.append(False)
            else:
                results.append(actual == expected)

        if logic == "or":
            return any(results)
        elif logic == "not":
            return not all(results)
        return all(results)

    # Export
    def nodes(self):
        return [{"id": n, **a} for n, a in self.g.nodes(data=True)]

    def relationships(self):
        return [{"source": u, "target": v, **a} for u, v, a in self.g.edges(data=True)]

    def to_dict(self):
        return {
            "nodes": self.nodes(),
            "relationships": self.relationships()
        }

    def save(self, path=None):
        path = path or self.path
        if not path:
            raise ValueError("No path specified to save the graph.")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)

    def load(self, path=None):
        path = path or self.path
        if not path:
            raise ValueError("No path specified to load the graph.")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.g.clear()
        for node in data.get("nodes", []):
            self.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
        for rel in data.get("relationships", []):
            self.add_relationship(rel["source"], rel["target"],
                                  **{k: v for k, v in rel.items() if k not in ["source", "target"]})
