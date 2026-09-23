# Open Kitchen Protocol (OKP) — v0.2

**A shared language for describing what actually happens in professional kitchens, built for the physical AI era.**

Stewarded by [epulo.ai](https://epulo.ai). v0.2 is frozen as of 7 September
2026 and published under Apache-2.0. Implementations and concrete gap reports
are welcome.

## Scope

OKP v0.2 is a vendor-neutral ontology and Event format for kitchen operations.
It standardizes the container, not ownership of operational corpora. Nutrition,
procurement, scheduling and the separately versioned culinary knowledge base
are outside this release.

## Files

- `schema/kitchen-event.schema.json` — frozen Event schema
- `ONTOLOGY.md` — entities, action taxonomy, tiers and resolved deferrals
- `examples/` — three synthetic episode envelopes (13 Events)
- `docs/CONFORMANCE.md` — `okp-event-strict-v0.2`
- `docs/MIGRATION-v0.1-to-v0.2.md` — both breaking changes with before/after
- `docs/LEROBOT_MAPPING.md` — LeRobot v3 annotation mapping and converter deferral
- `CHANGELOG.md` — release-by-release compatibility record

**Proposals.** `proposals/capacity/` drafts a forward counterpart to the Event
record: what a kitchen can produce next, and a commitment someone honours. It is a
proposal, not part of v0.2 and not ratified. Comments welcome.

## Validate independently

```sh
git clone https://github.com/Epulo-ai/open-kitchen-protocol.git
cd open-kitchen-protocol
git checkout --detach v0.2
python3 -m unittest discover -s tests -v
python3 tools/validate_okp.py --strict examples/*.json
```

Expected validator summary:

```text
3 files checked, 0 errors, 0 warnings (strict)
```

The validator is Python 3.8+ standard library only. It accepts one Event, an
Event array or an episode envelope. A pass proves the frozen structural and
repository-level checks at the exact commit; it does not establish truth,
consent, anonymity, publication rights, food safety, robot performance or
LeRobot conversion.

## Compatibility policy

The `v0.2` tag is immutable. Consumers SHOULD pin the tag and exact commit, not
`main`. Later releases may add optional fields or vocabulary with a changelog
entry. Any change that invalidates a v0.2 Event requires a new numbered release
and migration note. v0.2 is stable to build against; it is not a claim of v1.0
completeness or industry certification.
