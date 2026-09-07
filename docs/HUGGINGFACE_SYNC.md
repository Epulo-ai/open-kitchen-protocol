# GitHub to Hugging Face publication

GitHub is the protocol source of truth. `sync-huggingface.yml` validates pull
requests without publishing. Pushes to `main` and manual runs on `main`
validate first, then publish the explicit public snapshot to the HF dataset
`Epulo-ai/open-kitchen-protocol` and compare bytes at an immutable HF revision.
Check both jobs in GitHub Actions. Failed validation prevents upload. Upload
or read-back failure fails the run; it does not automatically roll back an upload.

The dataset trusted publisher must match this GitHub repository,
`refs/heads/main`, and `.github/workflows/sync-huggingface.yml`. It uses
short-lived OIDC credentials, without a permanent HF token. See
[HF documentation](https://huggingface.co/docs/hub/trusted-publishers).

Routine eligible updates need no extra approval. Review before merging. This
workflow does not impose branch protection. Publishing jobs are serialized;
obsolete revisions are skipped. If main changes during upload, the next
successful run publishes the newer snapshot.

`tools/build_hf_snapshot.py` defines the exact public allowlist. The schema and
three existing synthetic fixtures go to HF's root; two notes retain `docs/`.
The HF card template is `publishing/huggingface-card.md`; its revision placeholder
is rendered each run. Update counts and limitations when fixtures or validation
change. `alignment.json` records the source commit and checksums. These are
development snapshots, not numbered protocol releases.

Only ten files are written. Existing unrelated HF files are not deleted. New
GitHub files are not automatically published: review suitability, then update
the builder, card and tests. Private CKB, customer and commercial data must
remain outside this list. OKP requires neither Epulo nor a CKB subscription.

Pause via GitHub Actions: disable Sync Hugging Face. Retry by running it manually
on main. Revoke by removing the HF trusted publisher. Reconcile desired content
in GitHub before retrying: manual edits to managed HF files are overwritten by
the next successful sync.
