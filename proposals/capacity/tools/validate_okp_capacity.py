#!/usr/bin/env python3
"""
OKP Capacity validator -- checks JSON files against the capacity extension proposal.

    python3 proposals/capacity/tools/validate_okp_capacity.py examples/*.json
    python3 proposals/capacity/tools/validate_okp_capacity.py --strict one.json
    cat document.json | python3 proposals/capacity/tools/validate_okp_capacity.py -

Accepts three shapes:

    1. a single capability, capacity_offer, commitment or commitment_outcome object
    2. an array of those objects
    3. a bundle: {"documents": [...]} with optional description and note

Exit code is 0 when every file passes and 1 when any error is found.
--strict also fails on warnings.

This validates a PROPOSAL. Nothing here is a ratified standard, a conformance
profile or a claim that an implementation is compliant with anything. OKP is
being built as an open standard; the capacity extension is a draft inside it.

The JSON Schema engine is not reimplemented: it is imported from the
protocol's own tools/validate_okp.py, so a keyword behaves identically in both
validators or neither. The vocabularies are read from the four schema files
rather than repeated here, so extending a schema extends this tool.

What this file adds on top of the schemas are the rules JSON Schema cannot
express: time ordering, identifier uniqueness, the arithmetic between promised
and delivered units, agreement between an offer and a commitment taken against
it in the same file, and the honesty rules that make a forward record worth
reading rather than merely well formed.

No check compares anything to the current clock. A fixture that passes today
and fails next Tuesday teaches nobody anything.

Zero dependencies beyond the protocol's own validator: standard library only,
Python 3.8 or newer.
"""

import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# tools/validate_okp.py lives at the repository root in a checkout; the two
# other candidates cover a copy kept beside this file and a run from the root.
_VALIDATOR_DIRS = (
    os.path.normpath(os.path.join(SCRIPT_DIR, os.pardir, os.pardir, os.pardir, "tools")),
    SCRIPT_DIR,
    os.path.join(os.getcwd(), "tools"),
)
for _candidate in _VALIDATOR_DIRS:
    if os.path.isfile(os.path.join(_candidate, "validate_okp.py")):
        sys.path.insert(0, _candidate)
        break

try:
    import validate_okp as okp
except ImportError:  # pragma: no cover - exercised by hand, not by the suite
    sys.stderr.write(
        "cannot import validate_okp.py. This validator reuses the protocol's own\n"
        "schema engine rather than shipping a second one. Looked in:\n"
        + "".join("  {}\n".format(d) for d in _VALIDATOR_DIRS)
        + "Run it from a checkout of the protocol repository.\n"
    )
    raise SystemExit(2)

Finding = okp.Finding
parse_time = okp.parse_time
load_json = okp.load_json
read_json = okp.read_json

SCHEMA_DIR_CANDIDATES = (
    os.path.join(SCRIPT_DIR, os.pardir, "schema"),
    os.path.join(SCRIPT_DIR, "schema"),
    os.path.join(os.getcwd(), "schema"),
)

SCHEMA_FILES = {
    "capability": "capability.schema.json",
    "capacity_offer": "capacity-offer.schema.json",
    "commitment": "commitment.schema.json",
    "commitment_outcome": "commitment-outcome.schema.json",
}

# The id field each object type is unique on. Two objects of the same type
# sharing an id in one file is a copy-paste, not a document.
ID_FIELD = {
    "capability": None,
    "capacity_offer": "offer_id",
    "commitment": "commitment_id",
    "commitment_outcome": "outcome_id",
}

# Capacity is expressed in producible units. Anything that reaches for the
# roster is either personal data or a competitor's homework, and neither
# belongs in an answer to "can you make forty of these by seven".
STAFFING_WORDS = ("staff", "roster", "headcount", "employee", "shift_plan", "crew")


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def find_schema_dir():
    for candidate in SCHEMA_DIR_CANDIDATES:
        if os.path.isfile(os.path.join(candidate, SCHEMA_FILES["capability"])):
            return os.path.normpath(candidate)
    return None


def load_schemas(directory):
    schemas = {}
    for kind, filename in SCHEMA_FILES.items():
        with open(os.path.join(directory, filename), "r", encoding="utf-8") as handle:
            schemas[kind] = load_json(handle)
    return schemas


# --------------------------------------------------------------------------
# Rules JSON Schema cannot express
# --------------------------------------------------------------------------


def _window(obj, key="window"):
    value = obj.get(key)
    if not isinstance(value, dict):
        return None, None
    return parse_time(value.get("from")), parse_time(value.get("to"))


def _check_ext_for_staffing(obj, path, out):
    ext = obj.get("ext")
    if not isinstance(ext, dict):
        return
    for key in ext:
        lowered = key.lower()
        if any(word in lowered for word in STAFFING_WORDS):
            out.append(Finding("warning", "{}.ext.{}".format(path, key), (
                "capacity is stated in producible units; staffing detail does not "
                "belong in a capacity answer"
            )))


def check_capability(doc, path, out):
    issued = parse_time(doc.get("issued_at"))
    valid_until = parse_time(doc.get("valid_until"))
    if issued and valid_until and valid_until < issued:
        out.append(Finding("error", path + ".valid_until", "valid_until is before issued_at"))

    if not doc.get("fulfilment_modes"):
        out.append(Finding("error", path + ".fulfilment_modes", (
            "no fulfilment mode: a site that cannot hand anything over cannot commit to anything"
        )))

    items = doc.get("items")
    if not items:
        out.append(Finding("error", path + ".items", "no items: an empty capability states nothing"))
        return
    if not isinstance(items, list):
        return

    seen_items = {}
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        item_path = "{}.items[{}]".format(path, i)
        item_id = item.get("item_id")
        if isinstance(item_id, str):
            if item_id in seen_items:
                out.append(Finding("error", item_path + ".item_id", (
                    "duplicate item_id, already used by {}"
                ).format(seen_items[item_id])))
            else:
                seen_items[item_id] = item_path

        variants = item.get("variants")
        if not variants:
            out.append(Finding("error", item_path + ".variants", (
                "no variants: use variant_id 'standard' where the site makes it one way"
            )))
            continue
        if not isinstance(variants, list):
            continue

        seen_variants = {}
        for j, variant in enumerate(variants):
            if not isinstance(variant, dict):
                continue
            variant_path = "{}.variants[{}]".format(item_path, j)
            variant_id = variant.get("variant_id")
            if isinstance(variant_id, str):
                if variant_id in seen_variants:
                    out.append(Finding("error", variant_path + ".variant_id", (
                        "duplicate variant_id within this item"
                    )))
                else:
                    seen_variants[variant_id] = variant_path
            check_allergen_profile(variant.get("allergen_profile"), variant_path, out)


def check_allergen_profile(profile, path, out):
    if not isinstance(profile, dict):
        return
    declared = profile.get("declared")
    if not isinstance(declared, dict):
        return
    states = [v for v in declared.values() if isinstance(v, str)]
    if states and all(state == "absent" for state in states):
        if not profile.get("assessment_ref"):
            out.append(Finding("warning", path + ".allergen_profile", (
                "every allergen is declared absent but no assessment_ref is given; a "
                "free-from claim with nothing behind it is the one a guest is harmed by"
            )))


def check_offer(doc, path, out):
    issued = parse_time(doc.get("issued_at"))
    expires = parse_time(doc.get("expires_at"))
    start, end = _window(doc)

    if start and end and end <= start:
        out.append(Finding("error", path + ".window", "window.to is not after window.from"))
    if issued and expires and expires < issued:
        out.append(Finding("error", path + ".expires_at", "expires_at is before issued_at"))
    if expires and end and expires > end:
        out.append(Finding("warning", path + ".expires_at", (
            "the offer outlives the window it describes; nothing can be held against it after the window closes"
        )))

    if doc.get("basis") == "declared" and _is_number(doc.get("confidence")) and doc["confidence"] >= 0.99:
        out.append(Finding("warning", path + ".confidence", (
            "basis is 'declared' but confidence is {}; an asserted number is not a measured one"
        ).format(doc["confidence"])))

    constraints = doc.get("constraints")
    if isinstance(constraints, dict):
        available = doc.get("available_units")
        minimum = constraints.get("min_units")
        maximum = constraints.get("max_units")
        if isinstance(minimum, int) and isinstance(maximum, int) and minimum > maximum:
            out.append(Finding("error", path + ".constraints", "min_units is above max_units"))
        if isinstance(minimum, int) and isinstance(available, int) and minimum > available:
            out.append(Finding("error", path + ".constraints.min_units", (
                "min_units {} is above the {} units on offer, so nothing can be ordered"
            ).format(minimum, available)))
        order_by = parse_time(constraints.get("order_by"))
        if order_by and start and order_by > start:
            out.append(Finding("warning", path + ".constraints.order_by", (
                "order_by falls after the window opens; production usually has to start earlier"
            )))

    _check_ext_for_staffing(doc, path, out)


def check_commitment(doc, path, out):
    held = parse_time(doc.get("held_at"))
    expires = parse_time(doc.get("expires_at"))
    confirmed = parse_time(doc.get("confirmed_at"))
    start, end = _window(doc)

    if start and end and end <= start:
        out.append(Finding("error", path + ".window", "window.to is not after window.from"))
    if held and expires and expires <= held:
        out.append(Finding("error", path + ".expires_at", (
            "expires_at is not after held_at, so the hold never existed"
        )))
    if held and confirmed and confirmed < held:
        out.append(Finding("error", path + ".confirmed_at", "confirmed_at is before held_at"))
    if confirmed and expires and confirmed > expires:
        out.append(Finding("error", path + ".confirmed_at", (
            "the hold was confirmed after it had expired; an expired hold is refused and "
            "re-searched, never silently renewed"
        )))

    requester = doc.get("requester_ref")
    if isinstance(requester, str):
        if "@" in requester or okp.LOOKS_LIKE_A_NAME.match(requester):
            out.append(Finding("error", path + ".requester_ref", (
                "requester_ref {!r} looks like a person; this proposal carries no identity"
            ).format(requester)))
        elif okp.PERSONNEL_NUMBER.search(requester):
            out.append(Finding("warning", path + ".requester_ref", (
                "requester_ref {!r} contains a long number; make sure it is not an account or card reference"
            ).format(requester)))

    on_failure = doc.get("on_failure")
    if isinstance(on_failure, dict) and on_failure.get("remedy") == "none_stated":
        out.append(Finding("warning", path + ".on_failure.remedy", (
            "no remedy is offered for a missed promise; this is a valid answer, and a "
            "consumer is entitled to refuse the hold on it"
        )))

    _check_ext_for_staffing(doc, path, out)


def check_outcome(doc, path, out):
    result = doc.get("result")
    promised = doc.get("units_promised")
    delivered = doc.get("units_delivered")
    ready = parse_time(doc.get("actual_ready_at"))
    start, end = _window(doc, "promised_window")

    if start and end and end <= start:
        out.append(Finding("error", path + ".promised_window", "to is not after from"))

    if isinstance(promised, int) and isinstance(delivered, int):
        if delivered > promised:
            out.append(Finding("error", path + ".units_delivered", (
                "{} units delivered against {} promised; an outcome reports the promise, not a second order"
            ).format(delivered, promised)))
        elif result in ("met", "met_late") and delivered != promised:
            out.append(Finding("error", path + ".result", (
                "result is '{}' but {} of {} units were delivered; that is partially_met or not_met"
            ).format(result, delivered, promised)))
        elif result == "not_met" and delivered != 0:
            out.append(Finding("error", path + ".result", (
                "result is 'not_met' but {} units were delivered"
            ).format(delivered)))
        elif result == "partially_met" and not 0 < delivered < promised:
            out.append(Finding("error", path + ".result", (
                "result is 'partially_met' but {} of {} units were delivered"
            ).format(delivered, promised)))

    if result == "met" and ready and end and ready > end:
        out.append(Finding("error", path + ".result", (
            "result is 'met' but the units were ready after the window closed; that is met_late"
        )))
    if result == "met_late" and ready and end and ready <= end:
        out.append(Finding("error", path + ".result", (
            "result is 'met_late' but the units were ready inside the window"
        )))

    if result in ("met_late", "partially_met", "not_met") and not doc.get("event_refs"):
        out.append(Finding("warning", path + ".event_refs", (
            "a missed promise with no OKP Events behind it is an assertion; the return "
            "path is the point of reporting the outcome at all"
        )))

    note = doc.get("reason_note")
    if isinstance(note, str):
        if okp.PERSONNEL_NUMBER.search(note):
            out.append(Finding("warning", path + ".reason_note", (
                "reason_note contains a long number; make sure it is not a personnel number"
            )))
        for word in note.replace(",", " ").split():
            if okp.LOOKS_LIKE_A_NAME.match(word) or "@" in word:
                out.append(Finding("error", path + ".reason_note", (
                    "reason_note contains {!r}, which looks like a person; a reason is a category, not a name"
                ).format(word)))
                break

    _check_ext_for_staffing(doc, path, out)


SEMANTICS = {
    "capability": check_capability,
    "capacity_offer": check_offer,
    "commitment": check_commitment,
    "commitment_outcome": check_outcome,
}


# --------------------------------------------------------------------------
# Agreement between objects that travel together
# --------------------------------------------------------------------------


def check_cross_references(documents, paths, out):
    """Only references resolvable inside this one file are checked.

    References are strings; this proposal does not define a resolver, and a
    validator that invented one would report confident nonsense about a site
    it cannot see.
    """
    offers = {}
    commitments = {}
    for doc, path in zip(documents, paths):
        if not isinstance(doc, dict):
            continue
        if doc.get("object") == "capacity_offer" and isinstance(doc.get("offer_id"), str):
            offers[doc["offer_id"]] = (doc, path)
        elif doc.get("object") == "commitment" and isinstance(doc.get("commitment_id"), str):
            commitments[doc["commitment_id"]] = (doc, path)

    for doc, path in zip(documents, paths):
        if not isinstance(doc, dict):
            continue

        if doc.get("object") == "commitment":
            found = offers.get(doc.get("offer_ref"))
            if not found:
                continue
            offer, offer_path = found
            for field in ("site_id", "item_id", "variant_id", "unit", "fulfilment_mode"):
                if doc.get(field) != offer.get(field):
                    out.append(Finding("error", "{}.{}".format(path, field), (
                        "does not match the offer it was taken against ({}): {!r} against {!r}"
                    ).format(offer_path, doc.get(field), offer.get(field))))
            units = doc.get("units")
            available = offer.get("available_units")
            if isinstance(units, int) and isinstance(available, int) and units > available:
                out.append(Finding("error", path + ".units", (
                    "holds {} units against an offer of {}"
                ).format(units, available)))
            # The offer's constraints are part of the offer. A hold that ignores
            # them is not a smaller ask, it is an ask the site never made.
            constraints = offer.get("constraints")
            if isinstance(units, int) and isinstance(constraints, dict):
                minimum = constraints.get("min_units")
                maximum = constraints.get("max_units")
                if isinstance(minimum, int) and units < minimum:
                    out.append(Finding("error", path + ".units", (
                        "holds {} units but the offer's min_units is {}"
                    ).format(units, minimum)))
                if isinstance(maximum, int) and units > maximum:
                    out.append(Finding("error", path + ".units", (
                        "holds {} units but the offer's max_units is {}"
                    ).format(units, maximum)))
            # An expired offer is void: it cannot be held against, and a hold
            # taken after it lapsed is a promise the site never made.
            held = parse_time(doc.get("held_at"))
            offer_expiry = parse_time(offer.get("expires_at"))
            if held and offer_expiry and held > offer_expiry:
                out.append(Finding("error", path + ".held_at", (
                    "the hold was taken after the offer it cites expired"
                )))

            # order_by is the latest instant a commitment against the offer can
            # be confirmed, because production has to start.
            confirmed = parse_time(doc.get("confirmed_at"))
            offer_constraints = offer.get("constraints")
            order_by = parse_time(offer_constraints.get("order_by")) if isinstance(
                offer_constraints, dict) else None
            if confirmed and order_by and confirmed > order_by:
                out.append(Finding("error", path + ".confirmed_at", (
                    "confirmed after the offer's order_by"
                )))

            start, end = _window(doc)
            offer_start, offer_end = _window(offer)
            if start and offer_start and start < offer_start:
                out.append(Finding("error", path + ".window.from", "starts before the offer's window"))
            if end and offer_end and end > offer_end:
                out.append(Finding("error", path + ".window.to", "ends after the offer's window"))

        elif doc.get("object") == "commitment_outcome":
            found = commitments.get(doc.get("commitment_ref"))
            if not found:
                continue
            commitment, commitment_path = found
            if doc.get("site_id") != commitment.get("site_id"):
                out.append(Finding("error", path + ".site_id", (
                    "does not match the commitment it closes ({})"
                ).format(commitment_path)))
            if doc.get("units_promised") != commitment.get("units"):
                out.append(Finding("error", path + ".units_promised", (
                    "is {!r} but the commitment promised {!r}"
                ).format(doc.get("units_promised"), commitment.get("units"))))
            if doc.get("promised_window") != commitment.get("window"):
                out.append(Finding("error", path + ".promised_window", (
                    "does not match the window the commitment promised"
                )))


# --------------------------------------------------------------------------
# Documents
# --------------------------------------------------------------------------


KNOWN_OBJECTS = tuple(sorted(SCHEMA_FILES))


def extract_documents(doc):
    """Return (documents, kind) or raise ValueError for a shape this proposal does not define."""
    if isinstance(doc, list):
        return doc, "document array"
    if isinstance(doc, dict):
        if isinstance(doc.get("documents"), list):
            return doc["documents"], "bundle"
        if doc.get("object") in KNOWN_OBJECTS:
            return [doc], "single {}".format(doc["object"])
    raise ValueError(
        "not an OKP capacity document: expected an object whose 'object' field is one of "
        + ", ".join(KNOWN_OBJECTS)
        + ", an array of them, or an object with a 'documents' array"
    )


def validate_document(doc, schemas):
    findings = []
    documents, kind = extract_documents(doc)
    paths = []
    seen = {}

    for i, entry in enumerate(documents):
        path = kind.split(" ", 1)[1] if kind.startswith("single ") else "documents[{}]".format(i)
        paths.append(path)

        if not isinstance(entry, dict):
            findings.append(Finding("error", path, "document is not an object, got {}".format(
                type(entry).__name__)))
            continue

        object_type = entry.get("object")
        schema = schemas.get(object_type)
        if schema is None:
            findings.append(Finding("error", path + ".object", (
                "{!r} is not a capacity object; expected one of {}"
            ).format(object_type, ", ".join(KNOWN_OBJECTS))))
            continue

        okp.validate(entry, schema, path, findings)
        SEMANTICS[object_type](entry, path, findings)

        id_field = ID_FIELD[object_type]
        identifier = entry.get(id_field) if id_field else None
        if isinstance(identifier, str):
            key = (object_type, identifier)
            if key in seen:
                findings.append(Finding("error", "{}.{}".format(path, id_field), (
                    "duplicate {}, already used by {}"
                ).format(id_field, seen[key])))
            else:
                seen[key] = path

    check_cross_references(documents, paths, findings)
    return findings, kind, len(documents)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate JSON files against the OKP capacity extension proposal.")
    parser.add_argument("files", nargs="+", help="JSON files to check, or - for stdin")
    parser.add_argument("--schema-dir", default=None,
                        help="directory holding the four capacity schemas (found automatically in a checkout)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--quiet", action="store_true", help="print only failures and the summary")
    args = parser.parse_args(argv)

    schema_dir = args.schema_dir or find_schema_dir()
    if not schema_dir:
        print("cannot find the capacity schemas. Looked in:", file=sys.stderr)
        for candidate in SCHEMA_DIR_CANDIDATES:
            print("  " + os.path.normpath(candidate), file=sys.stderr)
        print("pass --schema-dir /path/to/proposals/capacity/schema", file=sys.stderr)
        return 2
    try:
        schemas = load_schemas(schema_dir)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print("cannot read the schemas in {}: {}".format(schema_dir, exc), file=sys.stderr)
        return 2

    total_errors = 0
    total_warnings = 0
    failed_files = 0

    for name in args.files:
        try:
            doc, label = read_json(name)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            print("FAIL  {}\n  error    (file)                      {}".format(name, exc))
            total_errors += 1
            failed_files += 1
            continue

        try:
            findings, kind, count = validate_document(doc, schemas)
        except ValueError as exc:
            print("FAIL  {}\n  error    (root)                      {}".format(label, exc))
            total_errors += 1
            failed_files += 1
            continue

        errors = [f for f in findings if f.level == "error"]
        warnings = [f for f in findings if f.level == "warning"]
        total_errors += len(errors)
        total_warnings += len(warnings)

        bad = bool(errors) or (bool(warnings) and args.strict)
        if bad:
            failed_files += 1

        status = "FAIL" if bad else ("WARN" if warnings else "ok  ")
        if not args.quiet or bad:
            print("{}  {}  [{}, {} document{}]".format(
                status, label, kind, count, "" if count == 1 else "s"))
            for finding in findings:
                print(finding)

    print("\n{} file{} checked, {} error{}, {} warning{}{}".format(
        len(args.files), "" if len(args.files) == 1 else "s",
        total_errors, "" if total_errors == 1 else "s",
        total_warnings, "" if total_warnings == 1 else "s",
        " (strict)" if args.strict else ""))

    return 1 if failed_files else 0


if __name__ == "__main__":
    sys.exit(main())
