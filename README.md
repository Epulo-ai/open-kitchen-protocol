# Open Kitchen Protocol (OKP) — v0.1 DRAFT

**A shared language for describing what actually happens in professional kitchens, built for the physical AI era.**

Stewarded by [epulo.ai](https://epulo.ai). v0.1, published on [GitHub](https://github.com/Epulo-ai/open-kitchen-protocol) and [Hugging Face](https://huggingface.co/datasets/Epulo-ai/open-kitchen-protocol). Feedback and implementations welcome.
---

## Why this exists

Physical AI is arriving in foodservice. Robots can move; what they lack is context: what a kitchen *is*, what a task *means*, how ingredients, stations, humans, machines and time relate. Every robotics vendor, every operator and every research lab currently describes kitchen work in its own incompatible vocabulary. That fragmentation slows everyone down.

OKP is a vendor-neutral ontology and event format for kitchen operations:

- **Describe** any professional kitchen (motorway, airport, hospital, ghost kitchen, QSR) in one schema.
- **Record** operational events — human and machine — as structured, timestamped, privacy-preserving data.
- **Exchange** that data between operators, robot vendors, orchestration layers and researchers without translation loss.
- **Benchmark** robots and AI systems against standardized kitchen tasks.

The analogy: GTFS did this for public transport. FHIR did it for healthcare. Kitchens deserve the same.

## What is open, and what is not

- **The protocol is open.** This schema, the action taxonomy, the documentation and example data are free for anyone to use, implement and extend. Contributions welcome.
- **Operational corpora are not part of this repository.** Real production data recorded in OKP format belongs to the operators and processors who create it, under their own licenses and data agreements. OKP standardizes the *container*, not the contents.

## Privacy by design

OKP uses pseudonymous actor references and describes tiers for handling kitchen data. Human Events require a recording-session reference. The current validator does not resolve that session or establish consent, anonymity or legal compliance. An optional [tier actor-reference check](docs/TIER_ACTOR_CHECK.md) detects actor references on T2/T3 Events; complete tier and exchange rules remain in development. See `ONTOLOGY.md`, section 6, for the intended policy and its current implementation limits.

## Repository layout

- `ONTOLOGY.md` — the conceptual model: entities, action taxonomy, event model, LeRobot mapping
- `schema/kitchen-event.schema.json` — JSON Schema for the core event record
- `examples/breakfast-rush.example.json` — a synthetic morning shift at a German motorway site, robot and human events side by side
- `examples/banqueting.example.json` — a synthetic banqueting service across multiple sites, long-duration prep tasks
- `examples/inflight.example.json` — a synthetic inflight catering run, high-count tray-line production
- `docs/CONFORMANCE.md` — the provisional strict validation profile and its limits

## Independent quickstart

You need Git and Python 3.8 or newer. The validator uses only Python's standard
library. No Epulo account, CKB subscription, API key or hosted service is
required.

```sh
git clone https://github.com/Epulo-ai/open-kitchen-protocol.git
cd open-kitchen-protocol
python3 tools/validate_okp.py --strict examples/*.json
```

For the current v0.1 draft, the expected summary is:

```text
3 files checked, 0 errors, 0 warnings (strict)
```

Create `my-event.json`:

```json
{
  "event_id": "7d3e1a52-9f6b-4a1e-8c2d-1b5f0e7a3c94",
  "site_id": "demo-kitchen-01",
  "verb": "check_temp",
  "t_start": "2026-09-06T10:00:00Z",
  "t_end": "2026-09-06T10:00:01Z",
  "outcome": "completed",
  "source": "sensor",
  "confidence": 0.98,
  "privacy_tier": "T3"
}
```

Then validate it:

```sh
python3 tools/validate_okp.py --strict my-event.json
```

This proves that the file passes the current OKP validator. It does not verify
real-world provenance, food safety, robot performance or regulatory
compliance. Record the revision you tested with `git rev-parse HEAD`; v0.1 is a
working draft and breaking changes are expected. See
[`docs/CONFORMANCE.md`](docs/CONFORMANCE.md) for the provisional validation
profile and its limits.

## Validating your data

The repository ships a validator with no dependencies at all: Python 3.8 or
newer, standard library only. It reads the vocabulary from
`schema/kitchen-event.schema.json`, so it cannot drift away from the spec.
Adding a verb to the schema is enough; the validator picks it up.

```
python3 tools/validate_okp.py examples/*.json
python3 tools/validate_okp.py --strict my-episode.json
cat episode.json | python3 tools/validate_okp.py -
```

It accepts a single event object, an array of events, or an episode file with
an `events` array, and it checks three things a JSON Schema cannot express:

- **Time.** `t_end` cannot precede `t_start`, and `measures.duration_s` has to
  agree with the timestamps.
- **Identity.** `event_id` must be unique within a file, and an `actor_ref`
  that looks like a person rather than a pseudonymous role token is an error,
  not a style note.
- **Provenance.** A `vision` or `manual` observation recorded at full
  confidence is flagged. The `confidence` field exists to carry uncertainty,
  not to hide it.

Errors fail the run. Warnings are advisory unless you pass `--strict`, which is
what CI runs on every pull request.

## Contributing

v0.1 is a conversation starter. We are looking for:

- **Operators** who can sanity-check the action taxonomy against real production
- **Robotics engineers** who want to review the conceptual LeRobot annotation mapping; a runnable converter is planned, not yet included
- **Researchers** in food process engineering, HRI and operations research
- **Culinary methodologists** — the taxonomy deliberately leaves room for structured culinary knowledge systems to plug in at the technique level

Open an issue, or propose changes via pull request. Substantial contributors are credited in the spec.

## License

Protocol and documentation: Apache 2.0. See `LICENSE`.

## Status

v0.1 draft, September 2026. Breaking changes expected until v1.0.
