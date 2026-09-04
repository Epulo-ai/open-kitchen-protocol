#!/usr/bin/env python3
"""
OKP validator -- checks JSON files against the Open Kitchen Protocol event schema.

    python3 tools/validate_okp.py examples/*.json
    python3 tools/validate_okp.py --strict examples/breakfast-rush.example.json
    cat episode.json | python3 tools/validate_okp.py -

Accepts three shapes:

    1. a single event object
    2. an array of event objects
    3. an episode file: {"events": [...], "site": {...} or "sites": [...]}

Exit code is 0 when every file passes and 1 when any error is found.
--strict also fails on warnings.

Zero dependencies: standard library only, Python 3.8 or newer.

The vocabulary is NOT repeated in this file. Verbs, outcomes, sources and
privacy tiers are read from schema/kitchen-event.schema.json, so extending the
schema is enough to extend the validator. What this file adds on top of the
schema are the rules JSON Schema cannot express: time ordering, id uniqueness,
declared-site consistency, and the privacy and provenance rules that make an
OKP record trustworthy rather than merely well-formed.

Malformed input is reported, never raised: a file that is wrong in an
unexpected way must still produce findings rather than a traceback.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# The validator normally sits in tools/ next to schema/, but it is also useful
# on its own, so a few sane locations are tried before giving up with advice.
SCHEMA_CANDIDATES = (
    os.path.join(SCRIPT_DIR, os.pardir, "schema", "kitchen-event.schema.json"),
    os.path.join(SCRIPT_DIR, "schema", "kitchen-event.schema.json"),
    os.path.join(os.getcwd(), "schema", "kitchen-event.schema.json"),
    os.path.join(SCRIPT_DIR, "kitchen-event.schema.json"),
)

TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "null": type(None),
}

# RFC 3339, which is what JSON Schema means by "date-time": a full date, a full
# time and an explicit offset. A bare date or a timestamp without an offset is
# not a moment in time, and comparing one against an offset timestamp is how
# naive/aware bugs get into other people's pipelines.
RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt ]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})$"
)

# The canonical 8-4-4-4-12 spelling only. uuid.UUID() also swallows braces,
# urn: prefixes and unhyphenated hex, which are not valid JSON Schema uuids.
CANONICAL_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)

PERSONNEL_NUMBER = re.compile(r"\d{4,}")
LOOKS_LIKE_A_NAME = re.compile(r"^[a-z]+[._][a-z]+$")


class Finding:
    def __init__(self, level, path, message):
        self.level = level  # "error" or "warning"
        self.path = path
        self.message = message

    def __str__(self):
        return "  {:<8} {:<28} {}".format(self.level, self.path or "(root)", self.message)


# --------------------------------------------------------------------------
# JSON Schema subset
# --------------------------------------------------------------------------
# Only the keywords the OKP schema actually uses are implemented: type,
# required, properties, additionalProperties, enum, const, pattern, format
# (uuid, date-time), minimum, maximum, items, allOf, if/then/else. An unknown
# keyword is ignored rather than pretended to be enforced.


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_integer(v):
    return isinstance(v, int) and not isinstance(v, bool)


def check_type(value, expected):
    if expected == "number":
        return _is_number(value)
    if expected == "integer":
        return _is_integer(value)
    py = TYPES.get(expected)
    if py is None:
        return True
    if py is not bool and isinstance(value, bool):
        return False
    return isinstance(value, py)


def parse_time(value):
    """Return a timezone-aware datetime, or None if this is not an RFC 3339 instant."""
    if not isinstance(value, str) or not RFC3339.match(value):
        return None
    text = value.replace(" ", "T")
    if text[-1] in "Zz":
        text = text[:-1] + "+00:00"
    # Python 3.8's fromisoformat accepts at most 6 fractional digits.
    text = re.sub(r"\.(\d{1,6})\d*(?=[+-])", r".\1", text)
    try:
        stamp = datetime.fromisoformat(text)
    except ValueError:
        return None
    return stamp if stamp.tzinfo is not None else None


def check_format(value, fmt):
    if fmt == "uuid":
        return bool(CANONICAL_UUID.match(value)) if isinstance(value, str) else False
    if fmt == "date-time":
        return parse_time(value) is not None
    return True


def matches(instance, schema):
    """Silent check, used for the `if` branch of a conditional."""
    probe = []
    validate(instance, schema, "", probe)
    return not probe


def validate(instance, schema, path, out):
    """Append a Finding to `out` for every schema violation."""
    if not isinstance(schema, dict):
        return

    if "type" in schema and not check_type(instance, schema["type"]):
        out.append(Finding("error", path, "expected type {}, got {}".format(
            schema["type"], type(instance).__name__)))
        return

    if "enum" in schema:
        allowed = schema["enum"]
        if not any(instance == option and type(instance) is type(option) for option in allowed):
            shown = ", ".join(repr(v) for v in allowed[:8])
            more = "" if len(allowed) <= 8 else ", ... ({} allowed)".format(len(allowed))
            out.append(Finding("error", path, "value {!r} is not in the vocabulary: {}{}".format(
                instance, shown, more)))

    if "const" in schema and instance != schema["const"]:
        out.append(Finding("error", path, "expected {!r}".format(schema["const"])))

    if isinstance(instance, str):
        pattern = schema.get("pattern")
        if pattern:
            try:
                hit = re.search(pattern, instance)
            except re.error as exc:
                out.append(Finding("error", path, "schema pattern is not valid regex: {}".format(exc)))
                hit = True
            if not hit:
                out.append(Finding("error", path, "{!r} does not match {}".format(instance, pattern)))
        fmt = schema.get("format")
        if fmt and not check_format(instance, fmt):
            out.append(Finding("error", path, "{!r} is not a valid {}".format(instance, fmt)))

    if _is_number(instance):
        if "minimum" in schema and instance < schema["minimum"]:
            out.append(Finding("error", path, "{} is below the minimum {}".format(
                instance, schema["minimum"])))
        if "maximum" in schema and instance > schema["maximum"]:
            out.append(Finding("error", path, "{} is above the maximum {}".format(
                instance, schema["maximum"])))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                out.append(Finding("error", path, "missing required field '{}'".format(key)))
        props = schema.get("properties", {})
        for key, value in instance.items():
            child = "{}.{}".format(path, key) if path else str(key)
            if key in props:
                validate(value, props[key], child, out)
            else:
                extra = schema.get("additionalProperties", True)
                if extra is False:
                    out.append(Finding("error", child, "unknown field '{}' (the schema is closed)".format(key)))
                elif isinstance(extra, dict):
                    validate(value, extra, child, out)

    if isinstance(instance, list):
        items = schema.get("items")
        if isinstance(items, dict):
            for i, item in enumerate(instance):
                validate(item, items, "{}[{}]".format(path, i), out)

    for sub in schema.get("allOf", []):
        if not isinstance(sub, dict):
            continue
        # A member may carry ordinary assertions alongside if/then/else. Both
        # halves apply; skipping the siblings would quietly accept bad data
        # the first time someone extends the conditional.
        siblings = {k: v for k, v in sub.items() if k not in ("if", "then", "else")}
        if siblings:
            validate(instance, siblings, path, out)
        if "if" in sub:
            if matches(instance, sub["if"]):
                if "then" in sub:
                    validate(instance, sub["then"], path, out)
            elif "else" in sub:
                validate(instance, sub["else"], path, out)


# --------------------------------------------------------------------------
# OKP rules that JSON Schema cannot express
# --------------------------------------------------------------------------


def check_event_semantics(event, path, declared_sites, out):
    t_start = parse_time(event.get("t_start"))
    t_end = parse_time(event.get("t_end"))

    if t_start and t_end:
        if t_end < t_start:
            out.append(Finding("error", path, "t_end is before t_start"))
        else:
            measures = event.get("measures")
            measured = measures.get("duration_s") if isinstance(measures, dict) else None
            if _is_number(measured):
                actual = (t_end - t_start).total_seconds()
                tolerance = max(2.0, actual * 0.02)
                if abs(actual - measured) > tolerance:
                    out.append(Finding("warning", path, (
                        "measures.duration_s is {}s but t_end - t_start is {:.0f}s"
                    ).format(measured, actual)))
    elif event.get("outcome") == "completed" and event.get("t_end") is None:
        out.append(Finding("warning", path, "outcome is 'completed' but there is no t_end"))

    actor = event.get("actor_ref")
    if isinstance(actor, str):
        if "@" in actor or LOOKS_LIKE_A_NAME.match(actor):
            out.append(Finding("error", path + ".actor_ref", (
                "actor_ref {!r} looks like a person, not a pseudonymous role token"
            ).format(actor)))
        elif PERSONNEL_NUMBER.search(actor):
            out.append(Finding("warning", path + ".actor_ref", (
                "actor_ref {!r} contains a long number; make sure it is not a personnel number"
            ).format(actor)))

    source = event.get("source")
    confidence = event.get("confidence")
    if source in ("vision", "manual") and _is_number(confidence) and 0.99 <= confidence <= 1:
        out.append(Finding("warning", path + ".confidence", (
            "source is '{}' but confidence is {}; the field exists to carry uncertainty, not to hide it"
        ).format(source, confidence)))

    site_id = event.get("site_id")
    if declared_sites and isinstance(site_id, str) and site_id not in declared_sites:
        out.append(Finding("warning", path + ".site_id", (
            "site_id {!r} is not declared in this file (declared: {})"
        ).format(site_id, ", ".join(sorted(declared_sites)))))


def collect_sites(doc):
    sites = set()
    if not isinstance(doc, dict):
        return sites
    single = doc.get("site")
    if isinstance(single, dict) and isinstance(single.get("site_id"), str):
        sites.add(single["site_id"])
    listed = doc.get("sites")
    if isinstance(listed, list):
        for entry in listed:
            if isinstance(entry, dict) and isinstance(entry.get("site_id"), str):
                sites.add(entry["site_id"])
    return sites


def extract_events(doc):
    """Return (events, kind) or raise ValueError for a shape OKP does not define."""
    if isinstance(doc, list):
        return doc, "event array"
    if isinstance(doc, dict):
        if isinstance(doc.get("events"), list):
            return doc["events"], "episode"
        if "event_id" in doc or "verb" in doc:
            return [doc], "single event"
    raise ValueError(
        "not an OKP document: expected an event object, an array of events, "
        "or an object with an 'events' array"
    )


def validate_document(doc, schema):
    findings = []
    events, kind = extract_events(doc)
    declared = collect_sites(doc)

    seen = {}
    for i, event in enumerate(events):
        path = "events[{}]".format(i) if kind != "single event" else "event"
        if not isinstance(event, dict):
            findings.append(Finding("error", path, "event is not an object, got {}".format(
                type(event).__name__)))
            continue

        validate(event, schema, path, findings)
        check_event_semantics(event, path, declared, findings)

        event_id = event.get("event_id")
        if isinstance(event_id, str):  # a non-string id is already an error above
            if event_id in seen:
                findings.append(Finding("error", path + ".event_id", (
                    "duplicate event_id, already used by {}"
                ).format(seen[event_id])))
            else:
                seen[event_id] = path

    return findings, kind, len(events)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def find_schema():
    for candidate in SCHEMA_CANDIDATES:
        if os.path.isfile(candidate):
            return os.path.normpath(candidate)
    return None


def read_json(path):
    if path == "-":
        return json.load(sys.stdin), "<stdin>"
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle), path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate JSON files against the Open Kitchen Protocol event schema.")
    parser.add_argument("files", nargs="+", help="JSON files to check, or - for stdin")
    parser.add_argument("--schema", default=None,
                        help="path to kitchen-event.schema.json (found automatically in a checkout)")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--quiet", action="store_true", help="print only failures and the summary")
    args = parser.parse_args(argv)

    schema_path = args.schema or find_schema()
    if not schema_path:
        print("cannot find kitchen-event.schema.json. Looked in:", file=sys.stderr)
        for candidate in SCHEMA_CANDIDATES:
            print("  " + os.path.normpath(candidate), file=sys.stderr)
        print("pass --schema /path/to/kitchen-event.schema.json", file=sys.stderr)
        return 2
    try:
        with open(schema_path, "r", encoding="utf-8") as handle:
            schema = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print("cannot read the schema at {}: {}".format(schema_path, exc), file=sys.stderr)
        return 2

    total_errors = 0
    total_warnings = 0
    failed_files = 0

    for name in args.files:
        try:
            doc, label = read_json(name)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            print("FAIL  {}\n  error    (file)                      {}".format(name, exc))
            total_errors += 1
            failed_files += 1
            continue

        try:
            findings, kind, count = validate_document(doc, schema)
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
            print("{}  {}  [{}, {} event{}]".format(
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
