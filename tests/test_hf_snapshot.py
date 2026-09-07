import hashlib
from pathlib import Path
import tempfile
import unittest
from tools.build_hf_snapshot import build, FILES
ROOT = Path(__file__).resolve().parents[1]
SHA = 'a' * 40
class SnapshotTests(unittest.TestCase):
    def test_exact_allowlist_hashes_and_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'snapshot'
            manifest = build(ROOT, out, SHA)
            self.assertEqual({p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()}, set(FILES.values()) | {'README.md', 'alignment.json'})
            self.assertEqual(manifest['github_commit'], SHA)
            for entry in manifest['files']:
                self.assertEqual(hashlib.sha256((out / entry['path']).read_bytes()).hexdigest(), entry['sha256'])
                if not entry.get('generated'):
                    self.assertEqual((ROOT / entry['github_path']).read_bytes(), (out / entry['path']).read_bytes())
            self.assertIn(SHA, (out / 'README.md').read_text())
            self.assertNotIn('{{GITHUB_SHA}}', (out / 'README.md').read_text())
    def test_refuses_stale_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): build(ROOT, Path(tmp), SHA)
    def test_refuses_non_commit_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): build(ROOT, Path(tmp) / 'snapshot', 'main')
    def test_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / 'a', Path(tmp) / 'b'
            build(ROOT, a, SHA)
            build(ROOT, b, SHA)
            for path in a.rglob('*'):
                if path.is_file(): self.assertEqual(path.read_bytes(), (b / path.relative_to(a)).read_bytes())
