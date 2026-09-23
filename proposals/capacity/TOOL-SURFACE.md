# Tool surface — OKP Capacity Extension, proposal 0.1-draft

Part of a **proposal**. Not ratified, not stable to build against, no conformance
profile. See `README.md` for the status this whole directory carries.

Six operations over the four objects in `schema/`. There is no separate wire format:
what a tool returns is the object, validated by the same validator that checks the
examples.

Six is a deliberate ceiling. Nobody integrates a seventy-tool server, and every tool
added here is a surface an untrusted caller can reach. Discovery of *what* a site can
make is a plain HTTPS GET rather than a seventh tool.

## Binding

MCP is one binding: six tools, arguments as below, each result the JSON object named.
The same six operations over HTTPS and JSON are another binding — one path per
operation, arguments as the request body, the object as the response body. The
objects are identical either way, and this proposal does not prefer one.

Discovery is always a plain GET:

```
GET https://<host>/.well-known/okp-capacity      -> capability, or an array of them
```

## The six

### 1. `search_capacity`

What can you produce, in this window?

| Argument | Required | Notes |
| --- | --- | --- |
| `item_id` | yes | An item the capability document declares. |
| `variant_id` | no | Omitted means any variant of the item. |
| `window` | yes | `{from, to}`, RFC 3339 with an offset. |
| `units` | yes | Integer ≥ 1. What the caller actually wants. |
| `fulfilment_mode` | no | Narrows to one of the site's declared modes. |
| `site_id` | no | Required only where one endpoint serves several sites. |

Returns an **array of `capacity_offer`**, possibly empty. An empty array is an answer,
not an error: it means no, in this window, for this thing. A server that manufactures
an offer it cannot meet rather than returning an empty array has defeated the purpose
of the extension.

Offers returned here may be unpriced. They expire.

### 2. `quote`

Turn an offer into one that can be held.

| Argument | Required | Notes |
| --- | --- | --- |
| `offer_id` | yes | From `search_capacity`. |
| `units` | yes | Must satisfy the offer's `constraints`. |

Returns a **`capacity_offer`**: a new `offer_id`, a `price`, usually a shorter
`expires_at`, and `available_units` that must cover the units quoted. A quote is an
offer, not a new object type, so the same validator and the same expiry discipline
apply to it.

`price` is informational. No authorisation happens here and none happens anywhere in
this extension.

### 3. `hold`

Take the capacity off the site's board, briefly.

| Argument | Required | Notes |
| --- | --- | --- |
| `offer_id` | yes | The quoted offer. |
| `units` | yes | ≤ the offer's `available_units`, and inside its `constraints`. |
| `window` | no | Narrower than the offer's window; defaults to it. |
| `requester_ref` | no | Opaque correlation token. Never identity. |

Returns a **`commitment`** with `state: "held"`, an `expires_at` the server chose, an
`accountable_party`, and an `on_failure` remedy. The server decides how long the hold
lasts; the caller learns it from the object rather than guessing.

A held commitment must not carry `confirmed_at`. The schema refuses one that does.

### 4. `confirm`

| Argument | Required | Notes |
| --- | --- | --- |
| `commitment_id` | yes | Must still be `held` and unexpired. |

Returns a **`commitment`** with `state: "confirmed"` and `confirmed_at`.

Confirming a hold that has expired is refused, not silently renewed. Renewal is a new
`search_capacity`; the state of the kitchen has moved on and pretending otherwise is
how an agent learns to distrust the source.

Where a payment protocol is in play, its authorisation is referenced through `ext`
under that protocol's own key. This extension does not sequence the two, and does not
define what happens to an authorisation when a commitment fails.

### 5. `status`

| Argument | Required | Notes |
| --- | --- | --- |
| `commitment_id` | yes | |

Returns the current **`commitment`**, and once the window has passed and the site has
closed it, the **`commitment_outcome`** as well.

The outcome is the return path. A site that never emits one is still implementing the
first three quarters of this extension, and a caller can see that it is.

### 6. `cancel`

| Argument | Required | Notes |
| --- | --- | --- |
| `commitment_id` | yes | |
| `reason` | no | Category from the outcome vocabulary. |

Returns a **`commitment`** with `state: "released"`. The site may also emit a
`commitment_outcome` with `result: "cancelled_by_requester"`.

## Refusals

Refusing correctly is half of what a server is judged on. Coercing a broken request
into a plausible answer is worse than failing it.

| Condition | Code |
| --- | --- |
| `okp_capacity_version` the server does not know | `unsupported_version` |
| Offer expired | `offer_expired` |
| Offer or commitment not found | `unknown_offer`, `unknown_commitment` |
| Units above `available_units` or outside `constraints` | `insufficient_capacity` |
| Hold expired before confirmation | `commitment_expired` |
| Operation not valid in the current state | `invalid_state` |
| Declined for any other reason the server will not elaborate | `refused` |

A refusal is not an outcome: it means no promise was made. Only a commitment that
existed gets a `commitment_outcome`.

## What an implementer must not do behind this surface

An ordering agent reaching these tools is untrusted input arriving at a system that
commits on allergens, on money and on somebody else's kitchen. The tools are a narrow
typed interface in front of whatever plans the kitchen; they are not a way to expose
that planner.

- Do not widen the surface into general kitchen control.
- Do not accept free text that reaches a planner, a model or an operational system.
- Do not answer from a cache the kitchen has moved past. A stale yes is worse than a no.
- Do not fill an unknown allergen state with a guess. `unknown` exists.

## Reference implementation

Not published yet. The tool surface Epulo is building for its own agent-ordering demo
is intended to become it, and this document is written to be corrected by that code
rather than to constrain it.
