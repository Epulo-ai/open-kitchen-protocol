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

OKP is built to survive the world's strictest privacy regimes — GDPR, German works-council law, Illinois BIPA, CCPA — which makes it deployable everywhere. Human actors are never identified: the schema carries pseudonymous role tokens only, consent and workforce-agreement flags are first-class fields, and the reference architecture assumes on-site processing with aggregation before anything leaves the building. Where local law is more permissive, the same schema simply runs with lighter obligations; the data remains interoperable worldwide. See `ONTOLOGY.md`, section 6.

## Repository layout

- `ONTOLOGY.md` — the conceptual model: entities, action taxonomy, event model, LeRobot mapping
- `schema/kitchen-event.schema.json` — JSON Schema for the core event record
- `examples/breakfast-rush.example.json` — a synthetic morning shift at a German motorway site, robot and human events side by side
- `examples/banqueting.example.json` — a synthetic banqueting service across multiple sites, long-duration prep tasks
- `examples/inflight.example.json` — a synthetic inflight catering run, high-count tray-line production
## Contributing

v0.1 is a conversation starter. We are looking for:

- **Operators** who can sanity-check the action taxonomy against real production
- **Robotics engineers** who want a common target format (LeRobot-compatible mapping included)
- **Researchers** in food process engineering, HRI and operations research
- **Culinary methodologists** — the taxonomy deliberately leaves room for structured culinary knowledge systems to plug in at the technique level

Open an issue, or propose changes via pull request. Substantial contributors are credited in the spec.

## License

Protocol and documentation: Apache 2.0. See `LICENSE`.

## Status

v0.1 draft, September 2026. Breaking changes expected until v1.0.
