# Tier actor-reference rule in OKP v0.2

The v0.1 experimental blanket check is retired. v0.2 makes the decided rule
normative in `schema/kitchen-event.schema.json`:

- human T2/T3 Events MUST omit `actor_ref`;
- robot and agent T2/T3 Events MAY retain `actor_ref`;
- all Events MUST carry `actor_kind`;
- human Events MUST carry `session_ref`.

Run the normal profile; no extra flag is needed:

```sh
python3 tools/validate_okp.py --strict PATH.json
```

This is one field rule, not proof of anonymity, consent or a right to share.
Context references can still link records. RecordingSession resolution and
verification, a machine-readable envelope schema, and T3 aggregation,
suppression and time-precision rules are explicitly deferred beyond v0.2
because they require document-level and policy profiles rather than another
claim about a single Event.
