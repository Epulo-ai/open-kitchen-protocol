# Experimental tier actor-reference check

The v0.1 ontology describes T2 Events with the actor reference removed and T3
as aggregates. The current Event schema does not enforce that boundary. The
published synthetic examples retain `actor_ref` on T2/T3 Events and pass the
current strict validation profile. A strict pass alone must not be read as
proof that those tier policies are satisfied.

## Run the additional check

From the repository root, using only Python 3.8 or newer:

```sh
python3 tools/validate_okp.py --strict --check-tier-actors PATH.json
```

This opt-in check rejects the presence of `actor_ref` on T2 or T3 Events,
regardless of whether `actor_kind` is `human`, `robot` or `agent`. T1 actor
references remain subject to the existing Event rules. The additional finding
is an error even without `--strict`. The summary identifies the enabled check
with `(tier-actor check)`.

The tool only inspects its input. It does not remove fields, change a tier,
rewrite a file or authorize an export. The check works with a single Event,
an Event array or an object containing an `events` array, from files or stdin.

## Expected results on the existing synthetic examples

```sh
python3 tools/validate_okp.py --strict examples/*.json
# Exit 0: the existing strict profile still passes.

python3 tools/validate_okp.py --strict --check-tier-actors examples/*.json
# Exit 1: 13 actor-reference errors across 3 files at this revision.
```

These fixtures are synthetic illustrations of the Event format. Their current
tier/reference mismatch is deliberately exposed by the opt-in check. Keep
both commands and the exact Git commit when reporting an evaluation.

## What remains unresolved

This is one experimental field rule, not a complete T2/T3 privacy or exchange
profile. In particular:

- `actor_kind` is a category, not the actor-reference field, and is retained.
- Human Events still require `session_ref`. The validator does not resolve the
  RecordingSession or verify its consent, retention or agreement information.
- Site, station, session, object and other context references can still link
  records. Absence of `actor_ref` does not establish anonymity or reuse rights.
- T3 aggregation, grouping, time precision and suppression are not checked.
  An individual T3-labelled Event without `actor_ref` can pass this check while
  failing the ontology's intended aggregate model.
- The Event schema remains unchanged. A third-party JSON Schema validator
  alone will not perform this extra rule.

## Compatibility and technical feedback

Default validation and `--strict` retain their existing acceptance behaviour.
Only an explicit `--check-tier-actors` invocation adds the restriction. No
published example payload, schema, release tag or Hugging Face dataset changes.

Before making any tier restriction part of a stable profile, we need explicit
decisions on human versus equipment references, session linkage, the T3 record
model and migration of existing exports. Contribute a synthetic counterexample
through the repository's issue or pull-request process if this rule removes
meaning your implementation needs. Include the exact tested commit, command,
output and missing workflow meaning. Do not submit private production records.

Neither Epulo nor CKB access is required to run or implement this check.
