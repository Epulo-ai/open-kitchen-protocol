# Rights-cleared kitchen pilot workflow

This workflow turns a small, staged kitchen sequence into OKP Events without
making access to a third-party dataset a prerequisite. It is intended for an
operator and an implementer preparing a demonstration, not as evidence of
food-safety compliance, worker consent or autonomous robot capability.

## 1. Set the evidence boundary

Choose one preparation sequence and one operational question, such as whether
a delayed handoff can be detected early enough for a person to respond. Define
the expected Events, acceptable misses and false alerts, and how a human will
score each recommendation before recording anything.

Keep the pilot deliberately narrow. A useful first evaluation reports:

- expected Events that were detected, missed or detected at the wrong time;
- false Events and false alerts;
- the delay between an observable occurrence and its OKP Event;
- recommendations accepted, rejected or edited by the human reviewer; and
- failure cases, including observations that cannot be represented faithfully.

Schema validation is only a format and consistency check. It does not establish
that an observation is true or that a recommendation is safe.

## 2. Clear every input before use

Maintain a rights register outside this public repository. For each recording,
annotation, codebase, model weight and other input, record its owner, source,
applicable version, permitted uses, attribution requirements and evidence of
permission. Record participant consent and retention terms where relevant.

Do not assume that a software repository's license covers separately hosted
videos, annotations, model weights or dependencies. If two sources describe
different terms for the same material, quarantine it from commercial training,
customer demonstrations and public examples until the rights holder resolves
the conflict in writing. Describing product development as an internal
experiment does not itself settle whether a noncommercial restriction applies.

Only synthetic or explicitly rights-cleared records intended for public release
belong in this repository or its Hugging Face snapshot. Keep consent records,
raw footage, identifiable worker data, customer records, private CKB material
and credentials outside both repositories.

## 3. Capture and translate the sequence

1. Record a staged sequence under the agreed permissions.
2. Annotate observable actions, timestamps, handoffs and exceptions.
3. Translate the annotations into OKP Events at the least identifying privacy
   tier that preserves the pilot's operational meaning.
4. Add clearly labelled synthetic order and equipment context if needed. Never
   present synthetic context as a measured fact.
5. Validate the resulting Event file and inspect the timeline manually.
6. Run the delay detector or recommender with a human reviewer in control.
7. Report the predefined metrics and limitations, including negative results.

The public repository contains no raw-media ingestion or inference pipeline.
Those implementation components should consume OKP rather than becoming a
requirement for using the protocol.

## 4. Give a coding agent a bounded task

Codex, Claude Code or another coding agent can work from the same GitHub branch.
Give it repository access, this repository's `AGENTS.md`, and a reviewable task
rather than access to private source material. A useful task brief is:

```text
Add one synthetic, rights-cleared OKP episode for <workflow> that demonstrates
<operational question>. Do not add raw recordings, personal data, credentials,
customer data or third-party dataset content. Preserve existing valid examples.
Update the Hugging Face card and explicit snapshot allowlist if the example is
intended for publication. Add or update tests, run every command in AGENTS.md,
state compatibility impact, and open a pull request for human review. Do not
claim that a local commit, a pull request or validation published a release.
```

For observations derived from private recordings, provide the agent only the
minimum de-identified annotations it needs, in an approved environment. A human
must review the Event semantics, rights status and recommendation behavior.

## 5. Publish through the reviewed path

GitHub is the source of truth. The person or coding agent making a change must
push its branch to the `Epulo-ai/open-kitchen-protocol` GitHub repository and
open a pull request into `main`. A repository maintainer—such as a co-founder
with write access—then reviews the files, rights status and check results. Once
required checks and approvals pass, the maintainer selects **Merge pull
request** in GitHub. Nobody needs to copy these files manually into `main`.

For example, a contributor working on a branch named `pilot-demo` runs:

```sh
git remote -v
git push -u origin pilot-demo
```

If `origin` is missing, the contributor must first clone the GitHub repository
or add the correct authenticated GitHub remote. A local Codex or Claude Code
workspace without a remote cannot push by itself. Do not share a maintainer's
password or access token with another person or paste credentials into a prompt;
each contributor should authenticate with their own authorized GitHub account.

After the pull request is merged, another checkout receives it with:

```sh
git switch main
git pull --ff-only origin main
```

That `git pull` updates a local checkout of OKP. The GitHub repository itself
does not pull from a coding agent: the agent pushes a branch, and GitHub merges
the reviewed pull request. Do not edit the managed Hugging Face files as an
independent source of truth.

After a reviewed commit reaches `main`, the sync workflow validates it, builds
the explicit public allowlist, uploads that snapshot and verifies the published
bytes. A pull request does not publish to Hugging Face. A successful local run
does not publish to either service. Confirm the GitHub Actions result and the
immutable commit recorded in the Hugging Face `alignment.json` before describing
the snapshot as published.

If the Hugging Face job does not run, a maintainer should first check the
**Sync Hugging Face** workflow in the GitHub Actions tab. The trusted publisher
must already be configured for this repository and `main`; merging code does
not create that external authorization automatically.

Changing the protocol vocabulary or schema is a separate decision from adding
a pilot episode. If an observation cannot be represented, document the gap and
propose the smallest schema or ontology change with a regression test and an
explicit compatibility note.
