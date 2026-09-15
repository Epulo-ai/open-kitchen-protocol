# OKP v0.2 frozen validation profile

## Profile identifier

`okp-event-strict-v0.2`

Claimants MUST identify the `v0.2` tag and exact Git commit tested.

## Required check

```sh
python3 tools/validate_okp.py --strict PATH.json
```

`PATH.json` may be one Event, an array of Events, or an episode envelope with
an `events` array. The envelope may also carry `okp_version`, `description`,
`note`, one `site` or a `sites` array, and `service_context`; the v0.2 Event
schema validates Events, not those contextual objects. References are strings
and are not resolved by this profile.

A pass has exit status zero, zero errors and zero warnings. The validator checks
the JSON Schema keywords used by v0.2 (`type`, `required`, `properties`,
`additionalProperties`, `enum`, `const`, `pattern`, `format`, ranges, `items`,
`allOf`, `if`/`then`/`else`, and `not`) plus time ordering, duration agreement,
Event-ID uniqueness, direct-identifier heuristics, implausible full confidence
for manual/vision sources, completed Events without an end, and declared-site
consistency. Strict mode promotes warnings to failure.

The human T2/T3 actor-reference restriction is part of the schema and therefore
part of this profile. The former `--check-tier-actors` experimental flag is removed.

JSON Schema 2020-12 treats `format` as annotation unless an implementation
enables format assertion. A generic validator reproduces this profile only when
its UUID and date-time format checker is enabled. The bundled validator always
asserts both formats; its zero-dependency command above is the normative v0.2
release check.

## What a pass does not prove

It does not prove full JSON Schema 2020-12 support, envelope/reference
completeness, provenance, truth, consent, anonymity, sharing rights, food
safety, robot performance, safe control, LeRobot compatibility or successful
conversion. T3 aggregation, suppression and time precision remain deferred
because v0.2 defines an Event, not an aggregate document.
