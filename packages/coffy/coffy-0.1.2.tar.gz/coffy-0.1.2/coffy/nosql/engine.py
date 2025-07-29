# coffy/nosql/engine.py
# author: nsarathy

import json
import os
import re

class QueryBuilder:
    def __init__(self, documents, all_collections=None):
        self.documents = documents
        self.filters = []
        self.current_field = None
        self.all_collections = all_collections or {}
        self._lookup_done = False
        self._lookup_results = None

    def where(self, field):
        self.current_field = field
        return self

    # Comparison
    def eq(self, value): return self._add_filter(lambda d: d.get(self.current_field) == value)
    def ne(self, value): return self._add_filter(lambda d: d.get(self.current_field) != value)
    def gt(self, value):
        return self._add_filter(
            lambda d: isinstance(d.get(self.current_field), (int, float)) and d.get(self.current_field) > value
        )

    def gte(self, value):
        return self._add_filter(
            lambda d: isinstance(d.get(self.current_field), (int, float)) and d.get(self.current_field) >= value
        )

    def lt(self, value):
        return self._add_filter(
            lambda d: isinstance(d.get(self.current_field), (int, float)) and d.get(self.current_field) < value
        )

    def lte(self, value):
        return self._add_filter(
            lambda d: isinstance(d.get(self.current_field), (int, float)) and d.get(self.current_field) <= value
        )

    def in_(self, values):
        return self._add_filter(
            lambda d: d.get(self.current_field) in values
        )

    def nin(self, values):
        return self._add_filter(
            lambda d: d.get(self.current_field) not in values
        )

    def matches(self, regex): return self._add_filter(lambda d: re.search(regex, str(d.get(self.current_field))))
    
    def exists(self): return self._add_filter(lambda d: self.current_field in d)

    # Logic grouping
    def _and(self, *fns):
        for fn in fns:
            sub = QueryBuilder(self.documents, self.all_collections)
            fn(sub)
            self.filters.append(lambda d, fs=sub.filters: all(f(d) for f in fs))
        return self

    def _not(self, *fns):
        for fn in fns:
            sub = QueryBuilder(self.documents, self.all_collections)
            fn(sub)
            self.filters.append(lambda d, fs=sub.filters: not all(f(d) for f in fs))
        return self

    def _or(self, *fns):
        chains = []
        for fn in fns:
            sub = QueryBuilder(self.documents, self.all_collections)
            fn(sub)
            chains.append(sub.filters)
        self.filters.append(lambda d: any(all(f(d) for f in chain) for chain in chains))
        return self

    # Add filter
    def _add_filter(self, fn):
        negate = getattr(self, "_negate", False)
        self._negate = False
        self.filters.append(lambda d: not fn(d) if negate else fn(d))
        return self

    # Core execution
    def run(self):
        results = [doc for doc in self.documents if all(f(doc) for f in self.filters)]
        if self._lookup_done:
            results = self._lookup_results
        return DocList(results)

    def update(self, changes):
        count = 0
        for doc in self.documents:
            if all(f(doc) for f in self.filters):
                doc.update(changes)
                count += 1
        return {"updated": count}

    def delete(self):
        before = len(self.documents)
        self.documents[:] = [doc for doc in self.documents if not all(f(doc) for f in self.filters)]
        return {"deleted": before - len(self.documents)}

    def replace(self, new_doc):
        replaced = 0
        for i, doc in enumerate(self.documents):
            if all(f(doc) for f in self.filters):
                self.documents[i] = new_doc
                replaced += 1
        return {"replaced": replaced}

    def count(self): return len(self.run())
    def first(self): return next(iter(self.run()), None)

    # Aggregates
    def sum(self, field):
        return sum(doc.get(field, 0) for doc in self.run() if isinstance(doc.get(field), (int, float)))

    def avg(self, field):
        values = [doc.get(field) for doc in self.run() if isinstance(doc.get(field), (int, float))]
        return sum(values) / len(values) if values else 0

    def min(self, field):
        values = [doc.get(field) for doc in self.run() if isinstance(doc.get(field), (int, float))]
        return min(values) if values else None

    def max(self, field):
        values = [doc.get(field) for doc in self.run() if isinstance(doc.get(field), (int, float))]
        return max(values) if values else None

    # Lookup
    def lookup(self, foreign_collection_name, local_key, foreign_key, as_field):
        foreign_docs = self.all_collections.get(foreign_collection_name, [])
        fk_map = {doc[foreign_key]: doc for doc in foreign_docs}
        enriched = []
        for doc in self.run():
            joined = fk_map.get(doc.get(local_key))
            if joined:
                doc = dict(doc)  # copy
                doc[as_field] = joined
                enriched.append(doc)
        self._lookup_done = True
        self._lookup_results = enriched
        return self

    # Merge
    def merge(self, fn):
        docs = self._lookup_results if self._lookup_done else self.run()
        merged = []
        for doc in docs:
            new_doc = dict(doc)
            new_doc.update(fn(doc))
            merged.append(new_doc)
        self._lookup_done = True
        self._lookup_results = merged
        return self



_collection_registry = {}

class CollectionManager:
    DEFAULT_DIR = os.path.join(os.getcwd(), "nosql_data")

    def __init__(self, name: str, path: str = None):
        self.name = name
        self.in_memory = False

        if path:
            self.path = path
        else:
            os.makedirs(self.DEFAULT_DIR, exist_ok=True)
            self.path = os.path.join(self.DEFAULT_DIR, f"{name}.json")
            self.in_memory = True if name == ":memory:" else False

        self.documents = []
        self._load()
        _collection_registry[name] = self.documents

    def _load(self):
        if self.in_memory:
            self.documents = []
        else:
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
            except FileNotFoundError:
                self.documents = []

    def _save(self):
        if not self.in_memory:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=4)

    def add(self, document: dict):
        self.documents.append(document)
        self._save()
        return {"inserted": 1}

    def add_many(self, docs: list[dict]):
        self.documents.extend(docs)
        self._save()
        return {"inserted": len(docs)}

    def where(self, field):
        return QueryBuilder(self.documents, all_collections=_collection_registry).where(field)
    
    def match_any(self, *conditions):
        q = QueryBuilder(self.documents, all_collections=_collection_registry)
        return q._or(*conditions)

    def match_all(self, *conditions):
        q = QueryBuilder(self.documents, all_collections=_collection_registry)
        return q._and(*conditions)

    def not_any(self, *conditions):
        q = QueryBuilder(self.documents, all_collections=_collection_registry)
        return q._not(lambda nq: nq._or(*conditions))
    
    def lookup(self, *args, **kwargs):
        return QueryBuilder(self.documents, all_collections=_collection_registry).lookup(*args, **kwargs)

    def merge(self, *args, **kwargs):
        return QueryBuilder(self.documents, all_collections=_collection_registry).merge(*args, **kwargs)

    def sum(self, field):
        return QueryBuilder(self.documents).sum(field)

    def avg(self, field):
        return QueryBuilder(self.documents).avg(field)

    def min(self, field):
        return QueryBuilder(self.documents).min(field)

    def max(self, field):
        return QueryBuilder(self.documents).max(field)

    def count(self):
        return QueryBuilder(self.documents).count()

    def first(self):
        return QueryBuilder(self.documents).first()

    def clear(self):
        count = len(self.documents)
        self.documents = []
        self._save()
        return {"cleared": count}

    def export(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, indent=4)

    def import_(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
        self._save()

    def all(self): return self.documents
    def count(self): return len(self.documents)

    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, indent=4)
    
    def all_docs(self):
        return self.documents

class DocList:
    def __init__(self, docs: list[dict]):
        self._docs = docs

    def __iter__(self):
        return iter(self._docs)

    def __getitem__(self, index):
        return self._docs[index]

    def __len__(self):
        return len(self._docs)

    def __repr__(self):
        if not self._docs:
            return "<empty result>"
        keys = list(self._docs[0].keys())
        header = " | ".join(keys)
        line = "-+-".join("-" * len(k) for k in keys)
        rows = []
        for doc in self._docs:
            row = " | ".join(str(doc.get(k, "")) for k in keys)
            rows.append(row)
        return f"{header}\n{line}\n" + "\n".join(rows)

    def to_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._docs, f, indent=4)

    def as_list(self):
        return self._docs
