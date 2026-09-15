"""Read back the public HF snapshot at one immutable revision and compare bytes."""
import json
import os
from pathlib import Path
import sys
from urllib.request import urlopen

BASE = 'https://huggingface.co'
REPO = 'Epulo-ai/open-kitchen-protocol'


def verify(folder):
    with urlopen(BASE + '/api/datasets/' + REPO, timeout=30) as response:
        revision = json.load(response)['sha']
    for path in sorted(folder.rglob('*')):
        if path.is_file():
            relative = path.relative_to(folder).as_posix()
            url = BASE + '/datasets/' + REPO + '/resolve/' + revision + '/' + relative
            with urlopen(url, timeout=30) as response:
                if response.read() != path.read_bytes():
                    raise ValueError('Published content mismatch: ' + relative)
    count = sum(1 for path in folder.rglob('*') if path.is_file())
    message = 'Verified {} snapshot files at Hugging Face commit {}'.format(count, revision)
    print(message)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
            summary.write(message + '\n')


if __name__ == '__main__':
    verify(Path(sys.argv[1]))
