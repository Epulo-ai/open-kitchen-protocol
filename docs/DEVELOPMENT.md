# Development setup

The public protocol can be developed with Codex, Replit, Claude Code, a normal
editor or another coding agent. All should work from this GitHub repository so
the specification and code have one shared version history.

## Run locally

Python 3.8 or newer is sufficient. No third-party packages or service accounts
are needed for the current validator and tests.

```sh
git clone https://github.com/Epulo-ai/open-kitchen-protocol.git
cd open-kitchen-protocol
python3 -m unittest discover -s tests -v
python3 tools/validate_okp.py --strict examples/*.json
```

The first command verifies regression cases, including malformed input. The
second verifies that the published synthetic examples remain accepted.

## Optional Codex cloud environment

Connect the repository in [Codex](https://chatgpt.com/codex), then create its
environment in [environment settings](https://chatgpt.com/codex/settings/environments).
Use the default image with Python 3.12 to match the current CI. No custom
dependency installation or secrets are required. A setup check can be:

```sh
python3 --version
python3 tools/validate_okp.py --strict examples/*.json
```

That setup check also works on the baseline repository before this development
setup is merged. Once these files are included, `AGENTS.md` supplies the test
commands for coding tasks. Agent internet access can remain off for these
local checks; configure it separately if a later task needs external sources.

The account owner must complete the GitHub authorization flow and choose the
repositories to grant access to. Connecting an environment does not itself
publish a protocol release. See the [official Codex cloud setup guidance](https://learn.chatgpt.com/docs/cloud)
and [environment documentation](https://learn.chatgpt.com/docs/environments/cloud-environment).

## Small changes and releases

Make one bounded change per review. Run the commands in `AGENTS.md` and state
any compatibility impact. Improvements enter the shared project through its
normal review and merge workflow.

Hugging Face examples should identify the GitHub release or commit they match.
Publishing datasets and demos is a separate step from changing the protocol.
Do not upload customer data or imply robot-learning compatibility merely from
an event label or a successful schema check.
