# OKP Ontology — frozen v0.2

This document defines the conceptual model. The machine-readable Event is
`schema/kitchen-event.schema.json`, whose top-level `version` is `0.2`.

## Design principles

Operator-first, actor-agnostic, privacy-oriented, composable and interoperable.
Human references are pseudonymous at T1 and absent at T2/T3, but context and
linked records still require appropriate controls.

## Core entities

`Site`, `Station`, `Equipment`, `Actor`, `Ingredient`, `Product`, `Recipe`,
`Task`, `Order`, `Shift`, `ServiceContext`, `RecordingSession` and `Event`.
The repository examples specify the v0.2 episode envelope in practice: an
`events` array plus optional descriptive context (`okp_version`, `description`,
`note`, `site` or `sites`, and `service_context`). Envelope objects are context,
not validated entities in v0.2; a machine-readable envelope schema and
reference-resolution profile are deferred because incomplete resolution rules
would create false assurance.

## Frozen action taxonomy

- **PREP** — wash, peel, cut, portion, mix, marinate, weigh
- **THERMAL** — fry, grill, bake, boil, steam, saute, hold_hot, chill, regenerate
- **ASSEMBLE** — plate, wrap, garnish, pack, combine
- **LOGISTICS** — transport, restock, receive, store, retrieve, dispose
- **HYGIENE** — clean_surface, clean_equipment, wash_dishes, sanitize, handwash_cycle
- **CONTROL** — check_temp, check_stock, taste, inspect, document, handover

`saute` is the wire spelling; prose may render “sauté”. The family mapping is
specified above. Typical-duration distributions, required-capability sets,
hazard classes and automation-readiness scores are deferred: v0.1 claimed each
verb carried them but published no evidence or values, and v0.2 does not invent
scored metadata.

## Event model

Every Event requires `event_id`, `site_id`, `actor_kind`, `verb`, `t_start`,
`outcome`, `source`, `confidence` and `privacy_tier`. `verb` is always required;
`task_ref` is optional context, not an alternative to it. Human Events require
`session_ref`. Human T2/T3 Events forbid `actor_ref`. See the schema for fields
and vocabularies. `ext` is the only vendor-extension point and uses
reverse-domain keys.

## Privacy tiers

| Tier | Content | Exchange policy |
| --- | --- | --- |
| T0 | Raw sensor/vision streams | Never represented by this Event schema; process and delete on site. |
| T1 | Events with pseudonymous human actor tokens | Only under operator data agreement. |
| T2 | Sessionized Events; human `actor_ref` absent | Shareable only under an applicable licence and controls. |
| T3 | Intended for aggregates; human `actor_ref` absent | Publication still requires rights and an aggregate profile. |

The schema enforces only the stated Event-field rules. It does not resolve
RecordingSession consent/agreement/retention data or establish anonymity.
T3 aggregate shape, suppression and precision are deferred beyond v0.2.

## LeRobot v3 mapping

`docs/LEROBOT_MAPPING.md` specifies the field mapping. A runnable converter is
deferred until a paired, rights-cleared OKP + LeRobot fixture exists because
OKP carries no frame-level sensorimotor data.

## Explicitly out of scope for v0.2

Nutrition, procurement, scheduling, dynamic pricing, employee performance
scoring, consumer-facing data, normative external food-ontology bindings, and
structured culinary methodology. The v0.1 questions about non-European
taxonomy coverage, readiness-score governance, FoodOn/LanguaL/GS1 status and
culinary-method placement remain research questions, not hidden planned
features or normative v0.2 requirements.
