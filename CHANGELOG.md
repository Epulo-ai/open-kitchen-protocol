# Changelog

## v0.2 — 2026-09-07

This release is frozen. Compatible additions may be made in later v0.x releases;
breaking changes require a new numbered release and migration note.

| Change | Compatibility |
| --- | --- |
| Added top-level schema `version: "0.2"` and optional Event `okp_version: "0.2"`. | Non-breaking |
| Made `actor_kind` required so human-session rules cannot be bypassed by omission. | **Breaking** |
| Human T2/T3 Events now forbid `actor_ref`; robot and agent references remain allowed. | **Breaking** |
| Added optional namespaced `ext` object for vendor extensions. | Non-breaking |
| Specified the accepted single-Event, Event-array and episode-envelope document shapes. | Non-breaking clarification |
| Published the verb-to-family mapping; deferred scored per-verb metadata. | Non-breaking clarification |
| Published a LeRobot v3 annotation mapping; deferred a runnable converter because OKP contains no frame-level sensorimotor data. | Non-breaking clarification |
| Kept the schema `$id` stable. | Non-breaking |
| Resolved every v0.1 planned/open label as specified or explicitly deferred. | Non-breaking documentation |
