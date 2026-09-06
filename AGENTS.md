# Working on Open Kitchen Protocol

## Purpose and scope

OKP describes operational events across people, robots and software agents in
professional kitchens. Implementing it must not require an Epulo account, a
CKB subscription or a proprietary service.

This repository contains the public protocol and synthetic examples. Keep
customer records, business campaign plans, credentials and private CKB content
outside it. Event validation does not establish equipment safety, legal
compliance or robot-control capability.

## Environment and checks

Use Python 3.8 or newer. The validator and its tests use the standard library;
no package installation, API key or running server is required. CI uses Python
3.12.

From the repository root, run:

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate_okp.py --strict examples/*.json
git diff --check
```

Read the relevant source and these instructions before editing. Treat schema,
ontology and validator disagreement as a finding to resolve explicitly.

## Implementation workflow

- Work on a focused branch and preserve unrelated changes.
- Prefer small changes with a clear user or implementer benefit.
- Add a regression test for a behavior fix. Preserve existing valid examples.
- State compatibility impact when accepted or rejected inputs change.
- Separate proposed designs from implemented and tested behavior.
- For larger work, delegate bounded independent tasks when authorized. Give
  each contributor separate file ownership and integrate the results once.
- Use routine coding capacity for bounded fixes and deeper reasoning for
  conflicting architecture or specification requirements when routing is
  available. Record actual routing only when known.

## Handoff

Explain the result in plain language first: what improved and why a kitchen
operator or implementer benefits. Then report changed files, meaningful check
results, compatibility impact and unresolved dependencies. Distinguish a local
change, a submitted pull request and a published release accurately.

Follow the user's authorized scope for external actions. A local commit or
passing test is not evidence that a change has been published.
