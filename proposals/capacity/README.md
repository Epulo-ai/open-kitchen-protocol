# OKP Capacity Extension — proposal 0.1-draft

> **Status: proposal.** This is a draft extension, not a ratified standard and not
> part of OKP v0.2. Nothing in this directory is stable to build against, there is
> no conformance profile for it, and no adopters-register entry may cite it. The
> Open Kitchen Protocol is being built as an open standard; this is a piece of that
> work in the open, at the stage where it is still cheap to argue with.

Comments, counter-examples and "this breaks on my system" reports are the point of
publishing it this early. Open an issue.

## What is missing

OKP v0.2 records the past. An Event says what was started, held, changed, plated or
failed, who or what did it, and how confident the record is. That is the right half of
the problem for training, audit and evidence.

The half nobody has specified is the forward one: **what a kitchen can produce next,
and a commitment to it that someone honours.**

An ordering agent does not browse. It asks what can be produced, where, by when, and
at what price, and it needs an answer it can act on. Every channel that agents already
reach into a kitchen through exposes a *menu*. A menu says what a site sells. It does
not say whether the site can make forty of them by seven, what happens if it cannot,
or who is answerable when it does not.

That gap is why this extension exists, and it is also why it has to be open. An
ordering agent will only transact against an interface it can discover and read
without a separate commercial relationship per operator.

## Where this sits

| Concern | Owned by | Not this |
| --- | --- | --- |
| Who pays, with what authorisation | AP2, ACP | ✗ |
| How an agent calls a tool | MCP | ✗ |
| What happened in the kitchen | OKP v0.2 Events | ✗ |
| What the kitchen can do next, and the promise | **this proposal** | — |

This extension defines objects and the rules between them. It borrows OKP's
conventions — `site_id` namespace, reverse-domain `ext` keys, explicit provenance,
a validator that reports rather than raises — so that a forward record and the Events
that close it name the same site in the same language.

## The four objects

### Capability — what this site can produce at all

`schema/capability.schema.json`

A site declares the items it makes, the variants it makes them in, the unit each is
counted in, a typical lead time, and — for every one of the fourteen allergens in
Annex II of Regulation (EU) 1169/2011 — an explicit state.

`present`, `absent`, `may_contain` and `unknown` are all representable. A missing key
is not "absent", and the schema does not allow the question to go unanswered. A
consumer that reads a missing allergen as absent is wrong; a producer that omits one
to look clean cannot, because the document will not validate.

A capability document carries `valid_until`. A capability claim nobody re-checks is a
claim nobody should have believed.

It is not a menu. There are no descriptions, no images, no categories, no prices, no
upsells and no item discovery. `item_id` is the operator's own identifier for
something the caller can already name — the catalogue is somewhere else and stays
there.

### Capacity — what it can produce in a window, given current state

`schema/capacity-offer.schema.json`

An offer is one answer to one question: this many units of this variant, in this
window, for this fulfilment mode, expiring at this instant.

Three fields make the answer usable rather than decorative:

- `basis` — `measured`, `modelled` or `declared`. Read from the running system,
  produced by a model of it, or asserted by a human.
- `confidence` — 0 to 1. It exists to carry uncertainty, not to hide it.
- `expires_at` — required. An offer with no expiry is a promise with no owner.

`available_units: 0` is a legitimate, useful answer. An honest no is worth more to an
agent than a menu entry that might be a yes.

Capacity is stated in producible units, never in people. No roster, no headcount, no
shift plan: that is personal data on one side and commercial detail on the other, and
an ordering agent needs neither to decide.

### Commitment — a hold with an expiry, and what happens when it breaks

`schema/commitment.schema.json`

A commitment is a hold taken against an offer. It carries `held_at` and `expires_at`
in every state, because capacity held open indefinitely is capacity nobody owns.

It also carries `on_failure`, stated when the promise is made rather than discovered
afterwards: the `remedy` (`substitute_offered`, `rebooked`, `released_without_charge`
or `none_stated`) and `notice_min_s`, the notice the site undertakes to give once it
knows it will miss.

`none_stated` is deliberately representable. A site is allowed to promise nothing, and
a consumer is then entitled to refuse the hold. What a site may not do is leave the
question unanswered.

`requester_ref` is an opaque correlation token. It must not encode a name, account,
email address, phone number or payment reference, and the validator refuses one that
looks like a person. This extension carries no identity.

### Accountability — who is answerable, and the way back

`schema/commitment-outcome.schema.json`

Every capability document and every commitment names an `accountable_party`: the food
business operator answerable for what the site produces, a legal entity rather than an
employee, with a `contact_ref` where a broken promise is reported.

An outcome closes the loop. It states what was promised and what was delivered, a
category reason (never a person — `staffing_shortfall` says a shift was short, not who
was missing), the remedy actually applied, and `event_refs`: the OKP Event ids that
evidence what happened.

That last field is the join between this extension and the protocol it extends. OKP
already models the return path for actuals; a forward record without it is an
assertion. The validator warns on a missed promise with no Events behind it.

Note what is **not** here: no score, no rating, no reliability index. This extension
produces the record that would make reliability comparable for the first time. Turning
that record into a ranking is somebody's product, not part of the protocol.

## Discovery, without an account anywhere

A site publishes its capability document at:

```
GET https://<host>/.well-known/okp-capacity
```

returning one capability document, or an array of them for an operator serving several
sites from one host. No registry, no broker, no central directory, no account with
anyone — including with the protocol's steward. A manufacturer or a kitchen system can
implement the whole of this extension and never talk to Epulo.

## Lifecycle

```
  .well-known/okp-capacity  ->  capability
  search_capacity           ->  capacity_offer[]      (perishable; may be empty)
  quote                     ->  capacity_offer        (priced, tighter expiry)
  hold                      ->  commitment  state=held      + expires_at
  confirm                   ->  commitment  state=confirmed
  cancel                    ->  commitment  state=released
  status                    ->  commitment, then commitment_outcome
                                commitment_outcome -> OKP Events (the actuals)
```

Six operations over four objects. `TOOL-SURFACE.md` specifies them.

## Rules the schemas cannot express

`tools/validate_okp_capacity.py` adds what JSON Schema cannot: time ordering, id
uniqueness, the arithmetic between promised and delivered units, agreement between an
offer and a commitment taken against it, and the honesty checks above. It reuses the
protocol's own schema engine from `tools/validate_okp.py` rather than shipping a
second one, so a keyword behaves identically in both validators or in neither.

```sh
python3 proposals/capacity/tools/validate_okp_capacity.py --strict proposals/capacity/examples/*.json
```

Expected:

```text
3 files checked, 0 errors, 0 warnings (strict)
```

No check compares anything to the current clock: a fixture that passes today and fails
next Tuesday teaches nobody anything.

References between objects are strings. The validator checks agreement only where both
objects sit in the same file, because a resolver it invented would report confident
nonsense about a site it cannot see.

## Non-goals

- **No payment.** No instruments, authorisation, settlement, refunds, tax or pricing
  rules. `price` on an offer is informational. AP2 and ACP own this, and an
  authorisation object is referenced through `ext` under the payment protocol's own
  key.
- **No identity.** No accounts, no customer records, no authentication scheme, no
  guest data. `requester_ref` is an opaque correlation token and nothing else.
- **No menu or catalogue duplication.** No descriptions, images, categories or item
  discovery. This answers questions about items the caller can already name.
- **No scheduling or staffing.** Capacity is units, not people.
- **No rating, certification, badge or paid scheme.** Same position OKP takes on
  conformance: evidence to re-run, never a credential.
- **No marketplace.** No central broker, no directory, no account with the steward.
- **No new transport.** MCP is one binding; the same six operations over HTTPS and
  JSON are another. The objects are identical either way.

## Relationship to OKP v0.2

Additive and separate. This proposal changes no v0.2 file, adds no verb, and does not
touch the Event schema. A v0.2 implementation that ignores this directory stays
conformant. Events are referenced by id from an outcome; nothing flows the other way.

Privacy tiers apply to Events, not to these objects, because these objects carry no
human actor at all — which is a constraint on their design, not an exemption.

## Reference implementation

The intended reference implementation is the agent-ordering tool surface Epulo is
building for its own demo. **It is not published yet.**

This draft is written to be revised against it rather than the other way round. Where
the running code and this document disagree, the code is right and the document
changes. Nothing here is frozen until an implementation has actually served these
objects to a caller that is not its author.

## Open questions

These are open, not hidden plans:

1. **Units.** `portion`, `cover`, `tray`, `pack`, `litre`, `kilogram` covers the cases
   we have seen. It will be wrong somewhere.
2. **Composite orders.** One request satisfied across several items or several sites is
   not modelled. Deliberately: getting one site's promise right first is the harder and
   more useful half.
3. **Signing.** Offers and commitments are unsigned. Anyone can write a JSON file, and
   a signature would need a trust root this proposal has no business defining.
4. **Price.** Whether an amount belongs here at all, or only an opaque reference into
   the payment protocol, is unresolved.
5. **Second allergen scheme.** Only the EU Annex II list is defined. What a site under
   a different regime declares, and how a consumer knows which it is reading, is open.
6. **Renegotiation.** A site that can offer 4 of the 6 units it promised currently
   reports a missed promise and offers a substitute. Whether a counter-offer belongs in
   the protocol is open.

## Licence

Apache-2.0, the same as the rest of the repository. A proposal under an open licence is
still a proposal.
