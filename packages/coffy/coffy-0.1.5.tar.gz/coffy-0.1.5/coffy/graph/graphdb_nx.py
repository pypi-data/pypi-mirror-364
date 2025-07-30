# coffy/graph/graphdb_nx.py
# author: nsarathy

import networkx as nx
import json
import os

class GraphDB:

    def __init__(self, directed=False, path=None):
        self.g = nx.DiGraph() if directed else nx.Graph()
        self.directed = directed
        self.in_memory = path == ":memory:"

        if path:
            if not path.endswith(".json"):
                raise ValueError("Path must be to a .json file")
            self.path = path
        else:
            self.in_memory = True
        if not self.in_memory and os.path.exists(self.path):
            self.load(self.path)
        elif not self.in_memory:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.save(self.path)


    # Node operations
    def add_node(self, node_id, labels=None, **attrs):
        if labels is not None:
            attrs["_labels"] = labels if isinstance(labels, list) else [labels]
        self.g.add_node(node_id, **attrs)
        self._persist()

    def add_nodes(self, nodes):
        for node in nodes:
            node_id = node["id"]
            labels = node.get("labels") or node.get("_labels")  # Accept either form
            attrs = {k: v for k, v in node.items() if k not in ["id", "labels", "_labels"]}
            self.add_node(node_id, labels=labels, **attrs)

    def get_node(self, node_id):
        return self.g.nodes[node_id]

    def _get_neighbors(self, node_id, direction):
        if self.directed:
            if direction == "out":
                return self.g.successors(node_id)
            elif direction == "in":
                return self.g.predecessors(node_id)
            elif direction == "any":
                return set(self.g.successors(node_id)).union(self.g.predecessors(node_id))
            else:
                raise ValueError("Direction must be 'in', 'out', or 'any'")
        else:
            return self.g.neighbors(node_id)

    def remove_node(self, node_id):
        self.g.remove_node(node_id)
        self._persist()

    # Relationship (edge) operations
    def add_relationship(self, source, target, rel_type=None, **attrs):
        if rel_type:
            attrs["_type"] = rel_type
        self.g.add_edge(source, target, **attrs)
        self._persist()

    def add_relationships(self, relationships):
        for rel in relationships:
            source = rel["source"]
            target = rel["target"]
            rel_type = rel.get("type") or rel.get("_type")
            attrs = {k: v for k, v in rel.items() if k not in ["source", "target", "type", "_type"]}
            self.add_relationship(source, target, rel_type=rel_type, **attrs)

    def get_relationship(self, source, target):
        return self.g.get_edge_data(source, target)

    def remove_relationship(self, source, target):
        self.g.remove_edge(source, target)
        self._persist()

    # Basic queries
    def neighbors(self, node_id):
        return list(self.g.neighbors(node_id))

    def degree(self, node_id):
        return self.g.degree[node_id]

    def has_node(self, node_id):
        return self.g.has_node(node_id)

    def has_relationship(self, u, v):
        return self.g.has_edge(u, v)
    
    def update_node(self, node_id, **attrs):
        if not self.has_node(node_id):
            raise KeyError(f"Node '{node_id}' does not exist.")
        self.g.nodes[node_id].update(attrs)
        self._persist()

    def update_relationship(self, source, target, **attrs):
        if not self.has_relationship(source, target):
            raise KeyError(f"Relationship '{source}->{target}' does not exist.")
        self.g.edges[source, target].update(attrs)
        self._persist()

    def set_node(self, node_id, labels=None, **attrs):
        if self.has_node(node_id):
            self.update_node(node_id, **attrs)
        else:
            self.add_node(node_id, labels=labels, **attrs)
        self._persist()

    # Advanced node search
    def project_node(self, node_id, fields=None):
        if not self.has_node(node_id):
            return None
        node = self.get_node(node_id).copy()
        node["id"] = node_id
        if fields is None:
            return node
        return {k: node[k] for k in fields if k in node}

    def project_relationship(self, source, target, fields=None):
        if not self.has_relationship(source, target):
            return None
        rel = self.get_relationship(source, target).copy()
        rel.update({"source": source, "target": target, "type": rel.get("_type")})
        if fields is None:
            return rel
        return {k: rel[k] for k in fields if k in rel}

    def find_nodes(self, label=None, fields=None, **conditions):
        return [
            self.project_node(n, fields) for n, a in self.g.nodes(data=True)
            if (label is None or label in a.get("_labels", [])) and self._match_conditions(a, conditions)
        ]

    def find_by_label(self, label, fields=None):
        return [
            self.project_node(n, fields) for n, a in self.g.nodes(data=True)
            if label in a.get("_labels", [])
        ]

    def find_relationships(self, rel_type=None, fields=None, **conditions):
        return [
            self.project_relationship(u, v, fields) for u, v, a in self.g.edges(data=True)
            if (rel_type is None or a.get("_type") == rel_type) and self._match_conditions(a, conditions)
        ]

    def find_by_relationship_type(self, rel_type, fields=None):
        return [
            self.project_relationship(u, v, fields) for u, v, a in self.g.edges(data=True)
            if a.get("_type") == rel_type
        ]

    def _match_conditions(self, attrs, conditions):
        if not conditions:
            return True
        logic = conditions.get("_logic", "and")
        conditions = {k: v for k, v in conditions.items() if k != "_logic"}
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
    
    def match_node_path(self, start, pattern, return_nodes=True, node_fields=None, direction="out"):
        start_nodes = self.find_nodes(**start)
        node_paths = []

        for s in start_nodes:
            self._match_node_path(
                current_id=s["id"],
                pattern=pattern,
                node_path=[s["id"]],
                node_paths=node_paths,
                direction=direction
            )

        unique_paths = list({tuple(p) for p in node_paths})

        if return_nodes:
            return [
                [self.project_node(n, node_fields) for n in path]
                for path in unique_paths
            ]
        return unique_paths


    def _match_node_path(self, current_id, pattern, node_path, node_paths, direction):
        if not pattern:
            node_paths.append(node_path)
            return

        step = pattern[0]
        rel_type = step.get("rel_type")
        next_node_cond = step.get("node", {})

        for neighbor in self._get_neighbors(current_id, direction):
            rel = self.get_relationship(current_id, neighbor)
            if rel_type and rel.get("_type") != rel_type:
                continue
            node_attrs = self.get_node(neighbor)
            if not self._match_conditions(node_attrs, next_node_cond):
                continue
            if neighbor in node_path:  # avoid cycles
                continue
            self._match_node_path(neighbor, pattern[1:], node_path + [neighbor], node_paths, direction)
    
    def match_full_path(self, start, pattern, node_fields=None, rel_fields=None, direction="out"):
        start_nodes = self.find_nodes(**start)
        matched_paths = []

        for s in start_nodes:
            self._match_full_path(
                current_id=s["id"],
                pattern=pattern,
                relationship_path=[],
                node_path=[s["id"]],
                matched_paths=matched_paths,
                direction=direction
            )

        return [
            {
                "nodes": [self.project_node(n, node_fields) for n in nodes],
                "relationships": [self.project_relationship(u, v, rel_fields) for u, v in path]
            }
            for path, nodes in matched_paths
        ]

    def _match_full_path(self, current_id, pattern, relationship_path, node_path, matched_paths, direction):
        if not pattern:
            matched_paths.append((relationship_path, node_path))
            return

        step = pattern[0]
        rel_type = step.get("rel_type")
        next_node_cond = step.get("node", {})

        for neighbor in self._get_neighbors(current_id, direction):
            if neighbor in node_path:
                continue
            rel = self.get_relationship(current_id, neighbor)
            if rel_type and rel.get("_type") != rel_type:
                continue
            if not self._match_conditions(self.get_node(neighbor), next_node_cond):
                continue

            self._match_full_path(
                neighbor,
                pattern[1:],
                relationship_path + [(current_id, neighbor)],
                node_path + [neighbor],
                matched_paths,
                direction
            )
            
    def match_path_structured(self, start, pattern, node_fields=None, rel_fields=None, direction="out"):
        start_nodes = self.find_nodes(**start)
        structured_paths = []

        for s in start_nodes:
            self._match_structured_path(
                current_id=s["id"],
                pattern=pattern,
                path=[{"node": self.project_node(s["id"], node_fields)}],
                structured_paths=structured_paths,
                direction=direction
            )

        return structured_paths
    
    def _match_structured_path(self, current_id, pattern, path, structured_paths, direction):
        if not pattern:
            structured_paths.append({"path": path})
            return

        step = pattern[0]
        rel_type = step.get("rel_type")
        next_node_cond = step.get("node", {})

        for neighbor in self._get_neighbors(current_id, direction):
            if any(e.get("node", {}).get("id") == neighbor for e in path):
                continue  # Avoid cycles

            rel = self.get_relationship(current_id, neighbor)
            if rel_type and rel.get("_type") != rel_type:
                continue
            if not self._match_conditions(self.get_node(neighbor), next_node_cond):
                continue

            extended_path = path + [
                {"relationship": self.project_relationship(current_id, neighbor)},
                {"node": self.project_node(neighbor)}
            ]

            self._match_structured_path(
                neighbor,
                pattern[1:],
                extended_path,
                structured_paths,
                direction
            )

    # Export
    def nodes(self):
        return [{"id": n, "labels": a.get("_labels", []), **{k: v for k, v in a.items() if k != "_labels"}} for n, a in self.g.nodes(data=True)]

    def relationships(self):
        return [
            {
                "source": u,
                "target": v,
                "type": a.get("_type"),
                **{k: v for k, v in a.items() if k != "_type"}
            }
            for u, v, a in self.g.edges(data=True)
        ]

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
        if os.path.getsize(path) == 0:
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.g.clear()
        for node in data.get("nodes", []):
            self.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
        for rel in data.get("relationships", []):
            self.add_relationship(
                rel["source"], rel["target"],
                rel_type=rel.get("type") or rel.get("_type"),
                **{k: v for k, v in rel.items() if k not in ["source", "target", "type", "_type"]}
            )
    
    def save_query_result(self, result, path=None):
        if path is None:
            raise ValueError("No path specified to save the query result.")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
            
    def _persist(self):
        if not self.in_memory:
            self.save(self.path)
