import copy
import importlib.util
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = importlib.util.spec_from_file_location("validate_okp", os.path.join(ROOT, "tools", "validate_okp.py"))
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class TierActorRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(ROOT, "schema", "kitchen-event.schema.json"), encoding="utf-8") as handle:
            cls.schema = json.load(handle)
        with open(os.path.join(ROOT, "examples", "breakfast-rush.example.json"), encoding="utf-8") as handle:
            cls.example = json.load(handle)

    def findings_for(self, event):
        findings, _, _ = validator.validate_document(event, self.schema)
        return findings

    def test_published_examples_obey_human_only_rule(self):
        for name in ("banqueting", "breakfast-rush", "inflight"):
            with open(os.path.join(ROOT, "examples", name + ".example.json"), encoding="utf-8") as handle:
                doc = json.load(handle)
            for event in doc["events"]:
                if event["actor_kind"] == "human" and event["privacy_tier"] in ("T2", "T3"):
                    self.assertNotIn("actor_ref", event)

    def test_human_t2_actor_ref_is_rejected(self):
        event = copy.deepcopy(next(e for e in self.example["events"] if e["actor_kind"] == "human"))
        event["actor_ref"] = "hot-line-a"
        self.assertTrue(any("forbidden schema" in f.message for f in self.findings_for(event)))

    def test_robot_t2_actor_ref_is_allowed(self):
        event = copy.deepcopy(next(e for e in self.example["events"] if e["actor_kind"] == "robot"))
        self.assertFalse([f for f in self.findings_for(event) if f.level == "error"])

    def test_actor_kind_is_required(self):
        event = copy.deepcopy(self.example["events"][0])
        event.pop("actor_kind")
        self.assertTrue(any("actor_kind" in f.message for f in self.findings_for(event)))

    def test_human_t1_actor_ref_is_allowed(self):
        event = copy.deepcopy(next(e for e in self.example["events"] if e["actor_kind"] == "human"))
        event["privacy_tier"] = "T1"
        event["actor_ref"] = "hot-line-a"
        self.assertFalse([f for f in self.findings_for(event) if f.level == "error"])

    def test_extension_keys_are_namespaced(self):
        event = copy.deepcopy(self.example["events"][0])
        event["ext"] = {"unqualified": 1}
        self.assertTrue(any("<propertyName>" in f.path for f in self.findings_for(event)))


if __name__ == "__main__":
    unittest.main()
