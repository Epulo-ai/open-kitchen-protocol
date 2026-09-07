"""Public CLI contract for the optional T2/T3 actor-reference check."""

import json
import tempfile
import unittest
from pathlib import Path

from test_validate_okp import EXAMPLES, run_validator


def synthetic_event(tier="T2", kind="human"):
    return {
        "event_id": "8873a41b-6e40-4372-bd06-c865dd0d25dd",
        "site_id": "synthetic-site",
        "verb": "inspect",
        "actor_kind": kind,
        "actor_ref": "prep-role-a",
        "session_ref": "synthetic-session",
        "t_start": "2026-09-07T06:00:00Z",
        "t_end": "2026-09-07T06:00:01Z",
        "outcome": "completed",
        "source": "manual",
        "confidence": 0.9,
        "privacy_tier": tier,
    }


class TierActorCliTests(unittest.TestCase):
    def test_existing_examples_expose_the_documented_tier_mismatch(self):
        result = run_validator(["--strict", "--check-tier-actors"] +
                               [str(path) for path in EXAMPLES])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("3 files checked, 13 errors, 0 warnings", result.stdout)
        self.assertEqual(result.stdout.count("actor_ref must be absent for T2"), 10)
        self.assertEqual(result.stdout.count("actor_ref must be absent for T3"), 3)

    def test_existing_strict_contract_is_unchanged(self):
        for tier in ("T1", "T2", "T3"):
            with self.subTest(tier=tier):
                result = run_validator(["--strict", "-"], json.dumps(synthetic_event(tier)))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertNotIn("tier-actor check", result.stdout)

    def test_opt_in_rejects_t2_t3_actor_refs_for_every_actor_kind(self):
        for tier in ("T2", "T3"):
            for kind in ("human", "robot", "agent"):
                with self.subTest(tier=tier, kind=kind):
                    result = run_validator(["--check-tier-actors", "-"],
                                           json.dumps(synthetic_event(tier, kind)))
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn("event.actor_ref", result.stdout)
                    self.assertIn("actor_ref must be absent for " + tier, result.stdout)
                    self.assertIn("(tier-actor check)", result.stdout)
                    self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_opt_in_accepts_t1_actor_refs(self):
        result = run_validator(["--strict", "--check-tier-actors", "-"],
                               json.dumps(synthetic_event("T1")))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_absent_actor_ref_passes_each_document_shape(self):
        for tier in ("T2", "T3"):
            event = synthetic_event(tier)
            del event["actor_ref"]
            for document in (event, [event], {"events": [event]}):
                with self.subTest(tier=tier, shape=type(document).__name__):
                    result = run_validator(["--strict", "--check-tier-actors", "-"],
                                           json.dumps(document))
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_human_session_requirement_still_applies(self):
        event = synthetic_event()
        del event["actor_ref"]
        del event["session_ref"]
        result = run_validator(["--check-tier-actors", "-"], json.dumps(event))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("session_ref", result.stdout)

    def test_file_input_is_checked_without_mutation(self):
        content = json.dumps({"events": [synthetic_event()]})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.json"
            path.write_text(content, encoding="utf-8")
            result = run_validator(["--strict", "--check-tier-actors", "--quiet", str(path)])
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("events[0].actor_ref", result.stdout)
            self.assertEqual(path.read_text(encoding="utf-8"), content)


if __name__ == "__main__":
    unittest.main()
