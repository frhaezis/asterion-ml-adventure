"""Executable teaching and boundary regressions for the forty V2 exercises.

These checks establish that examples run and illustrate the specified behavior;
they do not claim to measure whether a human learner understands an explanation.
Run from the project root: python3 tests/test_mobile_python_teaching.py
"""
import contextlib
import copy
import io
import json
from pathlib import Path
import runpy
import unittest


ROOT = Path(__file__).resolve().parents[1]
AUTHORING = runpy.run_path(str(ROOT / "tools/mobile_python_teaching_content.py"))
DATA = json.loads((ROOT / "web/python/exercises.json").read_text())
EXERCISES = {entry["id"]: entry for entry in DATA["exercises"]}


def reference(exercise, name):
    namespace = {}
    exec(EXERCISES[exercise]["solution"], namespace)
    return namespace[name]


class TeachingTests(unittest.TestCase):
    def test_all_displayed_demonstrations_execute_exactly_as_explained(self):
        demos = []
        for identity, exercise in EXERCISES.items():
            example = exercise["teaching"]["workedExample"]
            with self.subTest(exercise=identity):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exec(compile(example["code"], f"<teaching {identity}>", "exec"), {})
                self.assertEqual(output.getvalue(), example["expectedStdout"])
                self.assertNotEqual(example["code"].strip(), exercise["solution"].strip())
                self.assertGreaterEqual(len(example["steps"]), 3)
                demos.append(example["code"])
        self.assertEqual(len(demos), 40)
        self.assertEqual(len(set(demos)), 40)

    def test_syntax_primers_are_runnable_in_a_fresh_namespace(self):
        # Learners can copy even the small prerequisite snippets into Python.
        for name, primer in AUTHORING["PRIMERS"].items():
            with self.subTest(primer=name), contextlib.redirect_stdout(io.StringIO()):
                exec(compile(primer["example"], f"<primer {name}>", "exec"), {})

    def test_export_is_current_and_preserves_the_complete_course(self):
        self.assertEqual(list(EXERCISES), [f"p{i:02}" for i in range(1, 41)])
        self.assertEqual(DATA["teachingVersion"], 2)
        for identity, exercise in EXERCISES.items():
            with self.subTest(exercise=identity):
                self.assertEqual(exercise["learningVersion"], 2)
                self.assertEqual(exercise["teaching"], AUTHORING["make_teaching"](
                    exercise, AUTHORING["LESSONS"][identity]))
                self.assertEqual(len(exercise["teaching"]["steps"]), 4)
                self.assertTrue(exercise["teaching"]["prerequisites"])
                self.assertGreaterEqual(len(exercise["teaching"]["pitfalls"]), 2)

    def test_packet_rule_distinguishes_numeric_keys_and_preserves_payload(self):
        decode = reference("p01", "decode_packets")
        values = ["12|old", "02|start|", "12|end", "-3|bad", "x|bad", ""]
        before = list(values)
        self.assertEqual(decode(values), "start|end")
        self.assertEqual(values, before)

    def test_policy_validation_and_authorization_are_different(self):
        validate = reference("p28", "validate_call")
        authorize = reference("p02", "permit_action")
        self.assertFalse(validate({"required": ["n"], "types": {"n": "int"}}, {"n": True}))
        self.assertTrue(validate({"required": ["action"], "types": {"action": "str"}}, {"action": "erase"}))
        self.assertEqual(authorize(dict(action="erase", cost=0, battery=10, risk=0, consent=True)), "deny")
        self.assertEqual(authorize(dict(action="scan", cost=1, battery=10, risk=.5, consent=1)), "ask")

    def test_json_lines_count_physical_lines_and_reject_booleans(self):
        parse = reference("p09", "read_log")
        self.assertEqual(parse('\n{"ts": 2, "value": 0}\n\n{"ts": 3, "value": false}\nbroken'),
                         ([{"ts": 2, "value": 0}], [4, 5]))

    def test_rrf_keeps_physical_rank_after_ignoring_a_duplicate(self):
        fuse = reference("p27", "reciprocal_rank_fusion")
        # a receives 1/3, not 1/2: its original position remains three.
        self.assertEqual(fuse([["z", "z", "a"], ["a"]], k=0), ["a", "z"])
        self.assertEqual(fuse([["z", "z", "a"], ["q", "b"]], k=0), ["q", "z", "b", "a"])

    def test_ledger_cancel_reopens_key_and_commit_is_idempotent(self):
        ledger = reference("p31", "EnergyLedger")(7)
        self.assertTrue(ledger.reserve("task", 5))
        self.assertTrue(ledger.cancel("task"))
        self.assertTrue(ledger.reserve("task", 3))
        self.assertTrue(ledger.commit("task"))
        self.assertTrue(ledger.commit("task"))
        self.assertEqual(ledger.available(), 4)
        self.assertFalse(ledger.cancel("task"))
        self.assertFalse(ledger.reserve("task", 3))

    def test_recursive_copy_protects_untouched_nested_containers(self):
        redact = reference("p30", "redact_events")
        original = {"public": [{"values": [1, 2]}], "token": {"a": "private"}}
        before = copy.deepcopy(original)
        changed = redact(original, {"token"})
        changed["public"][0]["values"].append(3)
        self.assertEqual(original, before)
        self.assertEqual(changed["token"], "[REDACTED]")

    def test_topological_choice_is_smallest_currently_ready_not_initial_batch(self):
        order = reference("p38", "dependency_order")
        # After a, newly ready b must precede initially ready z.
        self.assertEqual(order({"b": ["a", "a"], "z": []}), ["a", "b", "z"])
        with self.assertRaises(ValueError):
            order({"a": ["b"], "b": ["a"]})

    def test_knapsack_does_not_reuse_an_item_or_require_exact_capacity(self):
        optimize = reference("p40", "rescue_value")
        self.assertEqual(optimize(6, [(3, 5)]), 5)
        self.assertEqual(optimize(7, [(3, 5), (3, 5)]), 10)


if __name__ == "__main__":
    unittest.main()
