"""Tests for the OKP capacity extension proposal.

Two claims are tested, and the second one matters more: that the shipped
examples pass, and that a document faulty in exactly one way is refused for
exactly that reason. A validator that accepts everything proves nothing, so
every refusal probe below starts from a passing example and breaks one thing.
"""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY = Path(__file__).resolve().parents[1]
PROPOSAL = REPOSITORY / "proposals" / "capacity"
VALIDATOR = PROPOSAL / "tools" / "validate_okp_capacity.py"
EXAMPLES = sorted((PROPOSAL / "examples").glob("*.json"))
ROOM_SERVICE = PROPOSAL / "examples" / "room-service.example.json"
BROKEN_PROMISE = PROPOSAL / "examples" / "broken-promise.example.json"


def run_validator(arguments, input_text=None):
    return subprocess.run(
        [sys.executable, str(VALIDATOR)] + arguments,
        cwd=str(REPOSITORY),
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def load(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def document(bundle, object_type):
    for entry in bundle["documents"]:
        if entry["object"] == object_type:
            return entry
    raise AssertionError("no {} in this example".format(object_type))


class ExampleTests(unittest.TestCase):
    def test_examples_exist(self):
        self.assertTrue(EXAMPLES, "no examples found; the proposal ships three")

    def test_examples_pass_strict(self):
        result = run_validator(["--strict"] + [str(path) for path in EXAMPLES])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("0 errors, 0 warnings (strict)", result.stdout)

    def test_examples_are_synthetic(self):
        for path in EXAMPLES:
            with self.subTest(example=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("invented for illustration", text)
                self.assertIn("not a ratified standard", text)

    def test_examples_declare_the_draft_version(self):
        for path in EXAMPLES:
            for entry in load(path)["documents"]:
                with self.subTest(example=path.name, object=entry["object"]):
                    self.assertEqual(entry["okp_capacity_version"], "0.1-draft")


class RefusalTests(unittest.TestCase):
    """Each probe is wrong in exactly one way, so a pass cannot come from elsewhere."""

    def check(self, bundle, expected, strict=False, expect_failure=True):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "probe.json"
            path.write_text(json.dumps(bundle), encoding="utf-8")
            arguments = (["--strict"] if strict else []) + [str(path)]
            result = run_validator(arguments)
        self.assertNotIn("Traceback", result.stdout + result.stderr)
        if expect_failure:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        else:
            self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected, result.stdout)
        return result

    def room_service(self):
        return copy.deepcopy(load(ROOM_SERVICE))

    def broken_promise(self):
        return copy.deepcopy(load(BROKEN_PROMISE))

    def test_unknown_object_is_refused(self):
        bundle = self.room_service()
        document(bundle, "capacity_offer")["object"] = "menu"
        self.check(bundle, "is not a capacity object")

    def test_unknown_draft_version_is_refused(self):
        bundle = self.room_service()
        document(bundle, "capacity_offer")["okp_capacity_version"] = "0.2-draft"
        self.check(bundle, "expected '0.1-draft'")

    def test_missing_allergen_is_refused(self):
        bundle = self.room_service()
        profile = document(bundle, "capability")["items"][0]["variants"][0]["allergen_profile"]
        del profile["declared"]["sesame"]
        self.check(bundle, "missing required field 'sesame'")

    def test_unknown_allergen_state_is_refused(self):
        bundle = self.room_service()
        profile = document(bundle, "capability")["items"][0]["variants"][0]["allergen_profile"]
        profile["declared"]["sesame"] = "probably not"
        self.check(bundle, "is not in the vocabulary")

    def test_free_from_without_an_assessment_is_a_warning(self):
        bundle = self.room_service()
        variant = document(bundle, "capability")["items"][0]["variants"][0]
        profile = variant["allergen_profile"]
        del profile["assessment_ref"]
        for allergen in profile["declared"]:
            profile["declared"][allergen] = "absent"
        self.check(bundle, "free-from claim with nothing behind it", expect_failure=False)
        self.check(bundle, "free-from claim with nothing behind it", strict=True)

    def test_offer_without_an_expiry_is_refused(self):
        bundle = self.room_service()
        del document(bundle, "capacity_offer")["expires_at"]
        self.check(bundle, "missing required field 'expires_at'")

    def test_declared_basis_with_full_confidence_is_a_warning(self):
        bundle = self.room_service()
        offer = document(bundle, "capacity_offer")
        offer["basis"] = "declared"
        offer["confidence"] = 1
        self.check(bundle, "an asserted number is not a measured one", strict=True)

    def test_hold_that_never_expires_is_refused(self):
        bundle = self.room_service()
        commitment = document(bundle, "commitment")
        commitment["expires_at"] = commitment["held_at"]
        self.check(bundle, "the hold never existed")

    def test_held_state_with_a_confirmation_is_refused(self):
        bundle = self.room_service()
        commitment = document(bundle, "commitment")
        commitment["state"] = "held"
        self.check(bundle, "value matches a forbidden schema")

    def test_commitment_without_a_failure_remedy_is_refused(self):
        bundle = self.room_service()
        del document(bundle, "commitment")["on_failure"]
        self.check(bundle, "missing required field 'on_failure'")

    def test_no_remedy_stated_is_allowed_but_flagged(self):
        bundle = self.room_service()
        on_failure = document(bundle, "commitment")["on_failure"]
        on_failure["remedy"] = "none_stated"
        self.check(bundle, "entitled to refuse the hold", expect_failure=False)

    def test_requester_ref_that_names_a_person_is_refused(self):
        bundle = self.room_service()
        document(bundle, "commitment")["requester_ref"] = "anna.meier"
        self.check(bundle, "this proposal carries no identity")

    def test_commitment_cannot_exceed_the_offer_it_cites(self):
        bundle = self.room_service()
        document(bundle, "commitment")["units"] = 9
        self.check(bundle, "against an offer of 6")

    def test_commitment_cannot_ignore_the_offer_maximum(self):
        bundle = self.room_service()
        document(bundle, "commitment")["units"] = 5
        self.check(bundle, "the offer's max_units is 4")

    def test_commitment_cannot_ignore_the_offer_minimum(self):
        bundle = self.room_service()
        document(bundle, "capacity_offer")["constraints"]["min_units"] = 3
        self.check(bundle, "the offer's min_units is 3")

    def test_holding_against_an_expired_offer_is_refused(self):
        bundle = self.room_service()
        document(bundle, "capacity_offer")["expires_at"] = "2026-09-18T21:35:00Z"
        self.check(bundle, "after the offer it cites expired")

    def test_confirming_after_the_offer_order_by_is_refused(self):
        bundle = self.room_service()
        document(bundle, "capacity_offer")["constraints"]["order_by"] = "2026-09-18T21:36:30Z"
        self.check(bundle, "confirmed after the offer's order_by")

    def test_confirming_an_expired_hold_is_refused(self):
        bundle = self.room_service()
        document(bundle, "commitment")["confirmed_at"] = "2026-09-18T21:45:00Z"
        self.check(bundle, "never silently renewed")

    def test_commitment_cannot_leave_the_offer_window(self):
        bundle = self.room_service()
        document(bundle, "commitment")["window"]["to"] = "2026-09-18T23:30:00Z"
        self.check(bundle, "ends after the offer's window")

    def test_outcome_must_agree_with_the_commitment_it_closes(self):
        bundle = self.broken_promise()
        document(bundle, "commitment_outcome")["units_promised"] = 5
        self.check(bundle, "but the commitment promised 6")

    def test_met_with_missing_units_is_refused(self):
        bundle = self.room_service()
        document(bundle, "commitment_outcome")["units_delivered"] = 1
        self.check(bundle, "that is partially_met or not_met")

    def test_met_after_the_window_is_refused(self):
        bundle = self.room_service()
        document(bundle, "commitment_outcome")["actual_ready_at"] = "2026-09-18T22:40:00Z"
        self.check(bundle, "that is met_late")

    def test_missed_promise_needs_a_reason(self):
        bundle = self.broken_promise()
        del document(bundle, "commitment_outcome")["reason"]
        self.check(bundle, "missing required field 'reason'")

    def test_missed_promise_without_events_is_a_warning(self):
        bundle = self.broken_promise()
        del document(bundle, "commitment_outcome")["event_refs"]
        self.check(bundle, "the return path is the point", expect_failure=False)
        self.check(bundle, "the return path is the point", strict=True)

    def test_reason_note_naming_a_person_is_refused(self):
        bundle = self.broken_promise()
        document(bundle, "commitment_outcome")["reason_note"] = "j.mueller was off the line"
        self.check(bundle, "which looks like a person")

    def test_staffing_detail_in_an_offer_is_flagged(self):
        bundle = self.room_service()
        document(bundle, "capacity_offer")["ext"] = {"example.invalid-roster": {"cooks": 2}}
        self.check(bundle, "staffing detail does not belong", strict=True)

    def test_duplicate_offer_id_is_refused(self):
        bundle = self.room_service()
        offer = copy.deepcopy(document(bundle, "capacity_offer"))
        bundle["documents"].append(offer)
        self.check(bundle, "duplicate offer_id")

    def test_unknown_field_is_refused(self):
        bundle = self.room_service()
        document(bundle, "capacity_offer")["lead_time_s"] = 300
        self.check(bundle, "the schema is closed")


class CliTests(unittest.TestCase):
    def test_a_shape_the_proposal_does_not_define_is_reported(self):
        result = run_validator(["-"], '{"hello": "world"}')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not an OKP capacity document", result.stdout)
        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_invalid_json_constants_are_reported(self):
        result = run_validator(["-"], '{"object": "capacity_offer", "confidence": NaN}')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid JSON constant", result.stdout)
        self.assertNotIn("Traceback", result.stdout + result.stderr)

    def test_a_single_object_is_accepted(self):
        offer = document(load(ROOM_SERVICE), "capacity_offer")
        result = run_validator(["-"], json.dumps(offer))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("single capacity_offer", result.stdout)


if __name__ == "__main__":
    unittest.main()
