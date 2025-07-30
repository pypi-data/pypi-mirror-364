# coffy/nosql/nosql_tests.py
# author: nsarathy

import unittest
from engine import CollectionManager

class TestCollectionManager(unittest.TestCase):

    def setUp(self):
        self.col = CollectionManager(name="test_collection")
        self.col.clear()
        self.col.add_many([
            {"name": "Alice", "age": 30, "tags": ["x", "y"]},
            {"name": "Bob", "age": 25, "tags": ["y", "z"]},
            {"name": "Carol", "age": 40, "nested": {"score": 100}},
        ])

    def test_add_and_all_docs(self):
        result = self.col.all_docs()
        self.assertEqual(len(result), 3)

    def test_where_eq(self):
        q = self.col.where("name").eq("Alice")
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["age"], 30)

    def test_where_gt_and_lt(self):
        gt_q = self.col.where("age").gt(26)
        lt_q = self.col.where("age").lt(40)
        self.assertEqual(gt_q.count(), 2)
        self.assertEqual(lt_q.count(), 2)

    def test_exists(self):
        q = self.col.where("nested").exists()
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Carol")

    def test_in_and_nin(self):
        q1 = self.col.where("name").in_(["Alice", "Bob"])
        q2 = self.col.where("name").nin(["Carol"])
        self.assertEqual(q1.count(), 2)
        self.assertEqual(q2.count(), 2)

    def test_matches(self):
        q = self.col.where("name").matches("^A")
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Alice")

    def test_nested_field_access(self):
        q = self.col.where("nested.score").eq(100)
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Carol")

    def test_logic_and_or_not(self):
        q = self.col.match_all(
            lambda q: q.where("age").gte(25),
            lambda q: q.where("age").lt(40)
        )
        self.assertEqual(q.count(), 2)

        q = self.col.match_any(
            lambda q: q.where("name").eq("Alice"),
            lambda q: q.where("name").eq("Bob")
        )
        self.assertEqual(q.count(), 2)

        q = self.col.not_any(
            lambda q: q.where("name").eq("Bob"),
            lambda q: q.where("age").eq(40)
        )
        self.assertEqual(q.count(), 1)
        self.assertEqual(q.first()["name"], "Alice")

    def test_run_with_projection(self):
        q = self.col.where("age").gte(25)
        result = q.run(fields=["name"])
        self.assertEqual(len(result), 3)
        for doc in result:
            self.assertEqual(list(doc.keys()), ["name"])

    def test_update_and_delete_and_replace(self):
        self.col.where("name").eq("Alice").update({"updated": True})
        updated = self.col.where("updated").eq(True).first()
        self.assertEqual(updated["name"], "Alice")

        self.col.where("name").eq("Bob").delete()
        self.assertEqual(self.col.where("name").eq("Bob").count(), 0)

        self.col.where("name").eq("Carol").replace({"name": "New", "age": 99})
        new_doc = self.col.where("name").eq("New").first()
        self.assertEqual(new_doc["age"], 99)

    def test_aggregates(self):
        self.assertEqual(self.col.sum("age"), 95)
        self.assertEqual(self.col.avg("age"), 95 / 3)
        self.assertEqual(self.col.min("age"), 25)
        self.assertEqual(self.col.max("age"), 40)

    def test_merge(self):
        q = self.col.where("name").eq("Alice")
        merged = q.merge(lambda d: {"new": d["age"] + 10}).run()
        self.assertEqual(merged[0]["new"], 40)

unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestCollectionManager))
