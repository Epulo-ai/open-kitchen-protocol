# OKP Ontology — v0.1 DRAFT

This document defines the conceptual model. The machine-readable form lives in `schema/`.

## 1. Design principles

1. **Operator-first.** Concepts map to how kitchens are actually run (stations, shifts, covers, mise en place), not to how software engineers imagine them.
2. **Actor-agnostic.** A task is the same task whether a human, a robot arm or a software agent performs it. Automation readiness becomes measurable instead of ideological.
3. **Privacy by construction.** Humans appear only as pseudonymous role tokens. Identification is impossible at the schema level, not merely discouraged at the policy level.
4. **Composable.** Sites contain stations; recipes decompose into tasks; tasks decompose into actions. Every level can be recorded independently.
5. **Interoperable.** Events map cleanly onto robot-learning episode formats (see section 7).

## 2. Core entities

| Entity | Definition | Key fields |
|---|---|---|
| `Site` | One physical operation | site_id, format (motorway, airport, hospital, qsr, ghost, canteen), country, daypart_profile |
| `Station` | A functional work position within a site | station_id, type (prep, hot, cold, fry, grill, assembly, pass, dish, storage, service), equipment[] |
| `Equipment` | A machine or tool, human-operated or autonomous | equipment_id, class, vendor, autonomy_level (0 manual … 4 autonomous), capabilities[] |
| `Actor` | Any performer of work | actor_id (pseudonymous token), kind (human, robot, agent), role (e.g. line, lead, runner), consent_scope |
| `Ingredient` | A material input | ingredient_id, name, category, unit, allergens[], storage_class, external_refs (GS1/GTIN, LanguaL, FoodOn) |
| `Product` | A sellable output | product_id, name, menu_category, target_time_s, recipe_ref |
| `Recipe` | A directed process graph producing a Product | recipe_id, steps[] (each step = Task template), yield, critical_points[] (HACCP) |
| `Task` | A unit of work with a purpose | task_id, verb (see taxonomy), object, station, nominal_duration_s, skill_level, automation_readiness (0–5) |
| `Order` | A demand event | order_id, products[], channel, placed_at, promised_at |
| `Shift` | A staffing period | shift_id, site, start, end, planned_actors, unfilled_positions |
| `Event` | A timestamped observation | see section 4 |

## 3. Action taxonomy

Tasks use a controlled verb set, grouped in six families. The set is deliberately small in v0.1; extension happens through `variant` qualifiers, not new verbs.

- **PREP** — wash, peel, cut, portion, mix, marinate, weigh
- **THERMAL** — fry, grill, bake, boil, steam, sauté, hold_hot, chill, regenerate
- **ASSEMBLE** — plate, wrap, garnish, pack, combine
- **LOGISTICS** — transport, restock, receive, store, retrieve, dispose
- **HYGIENE** — clean_surface, clean_equipment, wash_dishes, sanitize, handwash_cycle
- **CONTROL** — check_temp, check_stock, taste, inspect, document, handover

Each verb carries: typical duration distribution, required capabilities, hazard class, and an **automation_readiness** score (0 = no known automation, 5 = routinely automated in production). This score is where the dataset becomes a market map: it shows every vendor where the open territory is.

## 4. Event model

The Event is the atomic record. Everything else provides context for it.

```
Event {
  event_id, site_id, station_id,
  actor_ref,            // pseudonymous
  task_ref | verb,      // what was done
  object_refs[],        // ingredients/products/equipment involved
  t_start, t_end,       // ISO 8601
  outcome,              // completed | interrupted | failed | rework
  measures{},           // temp_c, weight_g, count, distance_m, energy_wh …
  quality_flags[],      // e.g. haccp_deviation, spill, near_miss
  source,               // pos | sensor | vision | manual | robot_log | agent
  confidence            // 0–1, honesty about data provenance
}
```

Design choices worth defending:

- **`source` and `confidence` are mandatory.** A POS timestamp, a vision-derived estimate and a manual entry are not equally trustworthy, and the schema refuses to pretend otherwise.
- **`outcome: rework`** exists because rework is where kitchens lose money and where nobody currently measures anything.
- **Aggregation levels.** Events can be recorded raw (robot logs), sessionized (per order), or aggregated (per station per 15 min). The privacy tier determines which levels may leave the site.

## 5. Derived measures (the operator dividend)

From events alone, without any additional instrumentation, OKP data yields: cost per cover, station cycle times, thermal energy per product, waste ratio by cause, unfilled-hour coverage, order-to-pass latency, rework rate, and HACCP compliance evidence as a by-product. This is deliberate: the operator gets a management dividend from day one, which is what makes data collection politically survivable on the floor.

## 6. Privacy tiers (strictest-regime-proof, globally deployable)

| Tier | Content | Leaves the site? |
|---|---|---|
| T0 | Raw sensor/vision streams | Never. Processed and deleted on-site. |
| T1 | Events with pseudonymous actor tokens | Only under operator data agreement |
| T2 | Sessionized events, actor field removed | Shareable under license |
| T3 | Aggregates (station × daypart) | Publishable / open |

Consent, works-council agreement reference and retention period are schema fields on the recording session, not paperwork stored elsewhere. If the fields are empty, conformant tooling refuses to record humans. That rule is the difference between a dataset and a liability.

## 7. Robot-learning mapping (LeRobot compatibility)

An OKP Event maps to an episode annotation: `verb` + `object_refs` become task labels, `t_start/t_end` bound the episode, `measures` and `outcome` become success signals, `Station.equipment` describes embodiment. A conformance note and converter stub will live in `tools/` from v0.2. The goal: any robot vendor can train against OKP-labeled data without ever seeing tier T0/T1 material.

## 8. What v0.1 deliberately excludes

Nutrition claims, dynamic pricing, employee performance scoring (explicitly out of scope and incompatible with section 6), and consumer-facing data. Scope discipline is a feature.

## 9. Open questions for contributors

1. Is the six-family verb taxonomy sufficient for non-European formats (wok lines, sushi lines)?
2. Should `automation_readiness` be centrally maintained or crowd-scored?
3. Which existing food ontologies (FoodOn, LanguaL, GS1) should be normative references vs. optional mappings?
4. Where should structured culinary methodology (technique-level knowledge) attach: at Recipe, at Task, or as its own entity?
