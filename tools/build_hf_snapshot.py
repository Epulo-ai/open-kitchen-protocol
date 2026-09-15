"""Build the explicitly approved public Hugging Face snapshot (standard library)."""
import argparse
import hashlib
import json
from pathlib import Path
import re

FILES = {
    'LICENSE': 'LICENSE',
    'ONTOLOGY.md': 'ONTOLOGY.md',
    'schema/kitchen-event.schema.json': 'kitchen-event.schema.json',
    'docs/CONFORMANCE.md': 'docs/CONFORMANCE.md',
    'docs/TIER_ACTOR_CHECK.md': 'docs/TIER_ACTOR_CHECK.md',
    'docs/MIGRATION-v0.1-to-v0.2.md': 'docs/MIGRATION-v0.1-to-v0.2.md',
    'docs/LEROBOT_MAPPING.md': 'docs/LEROBOT_MAPPING.md',
    'CHANGELOG.md': 'CHANGELOG.md',
    'examples/banqueting.example.json': 'banqueting.example.json',
    'examples/breakfast-rush.example.json': 'breakfast-rush.example.json',
    'examples/inflight.example.json': 'inflight.example.json',
}


def build(root, output, revision):
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('A full GitHub commit SHA is required')
    # A new directory prevents accidentally including stale or private files.
    if output.exists():
        raise ValueError('Output directory must not already exist')
    payloads = {}
    entries = []
    for source, destination in FILES.items():
        path = root / source
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):
            raise ValueError('Symlink sources are not allowed')
        payloads[destination] = path.read_bytes()
        entries.append({'path': destination, 'github_path': source,
                        'sha256': hashlib.sha256(payloads[destination]).hexdigest()})
    card = (root / 'publishing/huggingface-card.md').read_text(encoding='utf-8')
    if '{{GITHUB_SHA}}' not in card:
        raise ValueError('Dataset card must include the revision placeholder')
    payloads['README.md'] = card.replace('{{GITHUB_SHA}}', revision).encode('utf-8')
    entries.append({'path': 'README.md', 'github_path': 'publishing/huggingface-card.md',
                    'generated': True, 'sha256': hashlib.sha256(payloads['README.md']).hexdigest()})
    manifest = {'github_repository': 'Epulo-ai/open-kitchen-protocol',
                'github_commit': revision, 'protocol_status': 'v0.2 frozen release',
                'dataset_repository': 'Epulo-ai/open-kitchen-protocol',
                'records_are_synthetic': True, 'files': entries}
    payloads['alignment.json'] = (json.dumps(manifest, indent=2) + '\n').encode('utf-8')
    output.mkdir(parents=True)
    for name, data in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(Path(__file__).resolve().parents[1], args.output, args.revision)
    print('Built 13 public files at GitHub revision ' + args.revision)
