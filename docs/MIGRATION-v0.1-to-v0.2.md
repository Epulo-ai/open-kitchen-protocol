# Migrating OKP v0.1 to v0.2

v0.2 has two breaking changes. The schema `$id` is unchanged; pin the `v0.2`
tag or its commit rather than following `main`.

## 1. Add `actor_kind` to every Event

Before (valid v0.1, invalid v0.2):

```json
{"event_id":"7d3e1a52-9f6b-4a1e-8c2d-1b5f0e7a3c94","site_id":"demo","verb":"check_temp","t_start":"2026-09-06T10:00:00Z","outcome":"completed","source":"sensor","confidence":0.98,"privacy_tier":"T3"}
```

After:

```json
{"event_id":"7d3e1a52-9f6b-4a1e-8c2d-1b5f0e7a3c94","site_id":"demo","actor_kind":"agent","verb":"check_temp","t_start":"2026-09-06T10:00:00Z","outcome":"completed","source":"sensor","confidence":0.98,"privacy_tier":"T3"}
```

Choose `human`, `robot` or `agent` from the real performer. Do not infer it from
`source`. Human Events still require `session_ref`.

## 2. Remove `actor_ref` from human T2/T3 Events

Before:

```json
{"actor_kind":"human","actor_ref":"hot-line-a","privacy_tier":"T2","session_ref":"session-breakfast-001"}
```

After:

```json
{"actor_kind":"human","privacy_tier":"T2","session_ref":"session-breakfast-001"}
```

Do not hash or encrypt the old value into another Event field. Remove it from
the exchanged Event. `session_ref` remains because the validator needs the
capture-session relationship; that reference can still be identifying in
context, so a schema pass does not establish anonymity or publication rights.
Robot and agent `actor_ref` values may remain at T2/T3.

## Optional additions

Producers may add `"okp_version": "0.2"` to Events and may put vendor fields
inside `ext` under reverse-domain keys they control. Unknown root Event fields
remain invalid.

## Verify

```sh
git checkout --detach v0.2
python3 tools/validate_okp.py --strict YOUR_FILE.json
```
