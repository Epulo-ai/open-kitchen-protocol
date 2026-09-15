---
license: apache-2.0
pretty_name: Open Kitchen Protocol (OKP)
thumbnail: "https://raw.githubusercontent.com/Epulo-ai/open-kitchen-protocol/main/publishing/okp-card.png"
language:
- en
tags:
- robotics
- food
- synthetic
- ontology
- physical-ai
- foodservice
---

# Open Kitchen Protocol: kitchen work, described together

A frozen public release for recording kitchen operations across people,
robots and software agents. Start with one workflow, inspect its Events,
and show us the meaning your implementation needs.

**OKP v0.2 frozen | 3 synthetic scenarios | 13 Events | Apache-2.0**

OKP can be used without an Epulo account, a CKB subscription or a proprietary
service. [Epulo](https://epulo.ai/) stewards the project.

## What GitHub and Hugging Face provide

[GitHub](https://github.com/Epulo-ai/open-kitchen-protocol) is the protocol's
source of truth: specifications, validator, tests and contribution process.
This Hugging Face dataset provides synthetic fixtures and the corresponding
protocol snapshot for inspection and evaluation.

This snapshot was built from GitHub commit
[`{{GITHUB_SHA}}`](https://github.com/Epulo-ai/open-kitchen-protocol/tree/{{GITHUB_SHA}}).
Every protocol file in it is a byte copy of the immutable
[`v0.2`](https://github.com/Epulo-ai/open-kitchen-protocol/tree/v0.2) tag. A later
commit on `main` may change packaging or presentation; the frozen protocol moves
only with a new version.
[alignment.json](alignment.json) records source paths and SHA-256 checksums.

## Explore one kitchen scenario

| File in this dataset | Scenario | Events |
| --- | --- | ---: |
| [breakfast-rush.example.json](breakfast-rush.example.json) | Synthetic morning production with human, robot and agent Events | 4 |
| [banqueting.example.json](banqueting.example.json) | Synthetic preparation, service and handoffs across sites | 5 |
| [inflight.example.json](inflight.example.json) | Synthetic catering production and service context | 4 |

Each JSON document contains an `events` array and contextual information.
Events describe actions, timestamps, actor categories, references, outcomes,
measurements and stated observation sources. Values and outcomes in these
files are illustrative, not measurements from deployed kitchens.

Other files:

- [ONTOLOGY.md](ONTOLOGY.md): conceptual entities, actions and v0.2 tier policy.
- [kitchen-event.schema.json](kitchen-event.schema.json): the Event schema.
- [docs/CONFORMANCE.md](docs/CONFORMANCE.md): current strict validation profile.
- [docs/TIER_ACTOR_CHECK.md](docs/TIER_ACTOR_CHECK.md): the normative human-only actor-reference rule.
- [docs/MIGRATION-v0.1-to-v0.2.md](docs/MIGRATION-v0.1-to-v0.2.md): breaking-change migration.
- [docs/LEROBOT_MAPPING.md](docs/LEROBOT_MAPPING.md): LeRobot v3 annotation mapping.
- [CHANGELOG.md](CHANGELOG.md): compatibility classification for every v0.2 change.
- [LICENSE](LICENSE): Apache-2.0 license text.

The schema and example files sit at the root of this Hugging Face repository.
In GitHub they sit in `schema/` and `examples/` respectively. Validator commands
in the documentation are run from the GitHub checkout.

## Reproduce validation

Git and Python 3.8 or newer are sufficient. No paid service is required.

```sh
git clone https://github.com/Epulo-ai/open-kitchen-protocol.git
cd open-kitchen-protocol
git checkout --detach {{GITHUB_SHA}}
python3 -m unittest discover -s tests -v
python3 tools/validate_okp.py --strict examples/*.json
```

Publication requires the regression tests and synthetic examples to pass the current
strict profile. It checks Event structure and selected consistency rules.
It does not resolve all contextual references or prove an entire workflow.

The v0.2 schema forbids `actor_ref` on human T2/T3 Events while retaining robot and agent references. The normal strict command enforces the rule; the v0.1 experimental flag is retired.

## Intended use and limits

Use these examples to explore the vocabulary, build parsers, test mappings,
or report concrete implementation gaps. They are too small and too synthetic
to establish kitchen coverage, a representative benchmark, performance,
commercial savings or production reliability.

The files contain no camera streams, sensor sequences or motor trajectories.
The field mapping is specified in `docs/LEROBOT_MAPPING.md`. A tested runnable converter is deferred because no paired rights-cleared fixture is available,
and these files are not presented as a ready-to-train LeRobot dataset.

An Event records an operational observation. CKB is a separately developed
culinary knowledge layer; its private contents are not distributed here.
Cloud planning, local sensing and skills, robot controllers and independent
safety systems have separate responsibilities. These fixtures do not execute
or certify a robot.

Pseudonymous actor tokens and tier labels do not establish anonymity, consent,
publication rights or legal compliance. The Event validator requires a session
reference for human Events but does not verify the referenced agreement or
retention information. Contextual fields can still link records.

Real customer-kitchen data is not included. Publishing OKP does not grant
Epulo or anyone else access to a contributor's operational data.

## Contribute one workflow

**Operators:** describe five steps and one exception, quality check or handoff
in plain language. No coding is required.

**Builders:** create a synthetic Event or report one concrete meaning v0.2
cannot preserve. Include the exact revision, command, result and first point
of confusion. An independently returned file is evidence of evaluation;
sustained use is stronger evidence of adoption.

Use the [GitHub issue tracker](https://github.com/Epulo-ai/open-kitchen-protocol/issues)
or submit a pull request. Only contribute synthetic or explicitly rights-cleared
material suitable for public distribution. Keep private customer, employee,
recipe and equipment material out of public submissions.

The public protocol and example fixtures are offered under Apache-2.0.
The standardization goal remains open for community implementation and review.
