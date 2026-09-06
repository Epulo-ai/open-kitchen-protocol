# OKP v0.1 draft validation profile

This document names the behavior currently exercised by the repository's
validator and continuous-integration checks. It is a provisional profile for a
working draft, not an industry certification or a claim of full JSON Schema
2020-12 implementation.

## Profile identifier

`okp-event-strict-v0.1-draft`

An implementation claiming this provisional profile MUST identify the exact
OKP Git commit it tested. Until a numbered release is tagged, `main` is a moving
development target and MUST NOT be used as the only version identifier in an
interoperability result.

## Required check

From the repository root, run:

```sh
python3 tools/validate_okp.py --strict PATH.json
```

`PATH.json` may contain a single Event, an array of Events or an object with an
`events` array. A passing result has exit status zero and reports zero errors
and zero warnings.

## What the current validator checks

The validator implements the structural rules used by the current Event schema
and these repository-level checks:

- required fields, allowed values, basic types, formats, ranges and conditional
  requirements used by `schema/kitchen-event.schema.json`;
- `t_end` is not before `t_start`;
- `measures.duration_s` agrees with the timestamps within the documented
  tolerance;
- `event_id` values are unique within the input file;
- `actor_ref` values do not resemble direct personal identifiers, with an
  additional warning for long numeric sequences that may be personnel numbers;
- manual and vision observations at full confidence produce a warning;
- a completed Event without `t_end` produces a warning;
- strict mode treats every warning as a failure.

The repository's CI also runs its regression tests and validates every
published example in strict mode.

## What a pass does not prove

A pass does not establish:

- full conformance with every JSON Schema 2020-12 keyword;
- semantic completeness of an episode or the existence of referenced objects;
- provenance, truth, consent, privacy-law compliance or rights to publish data;
- culinary correctness, food safety or regulatory compliance;
- equipment interoperability, robot capability, deterministic timing or safe
  control behavior;
- LeRobot dataset compatibility or successful conversion.

Those properties require separate profiles, evidence and tests. OKP validation
MUST NOT be used as a substitute for responsible process, equipment or safety
controls.

## Reporting an independent result

A useful report SHOULD include:

1. exact OKP Git commit;
2. implementation and environment;
3. synthetic or rights-cleared input;
4. exact command and output;
5. elapsed human setup time and first failure, if any;
6. any workflow meaning the current Event model could not preserve.

Passing one file is evidence of evaluation, not sustained adoption. Report a
concrete gap even when no valid Event can represent the chosen workflow.

## Compatibility status

This document describes current behavior without changing the Event schema or
valid example payloads. It does not promote the draft to v1.0 and does not add a
release tag.
