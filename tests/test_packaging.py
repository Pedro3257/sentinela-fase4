import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def run_cli(self, args, cwd):
        env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONIOENCODING="utf-8")
        return subprocess.run([sys.executable, "-m", "sentinela", *args], cwd=cwd,
                              env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)

    def test_default_configuration_available_outside_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.run_cli(["demo", "--out", "demo"], folder)
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads((Path(folder)/"demo/summary.json").read_text(encoding="utf-8"))
            self.assertEqual((summary["stored_events"], summary["alerts"]), (20, 13))

    def test_explicit_missing_configuration_does_not_silently_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.run_cli(["--config", "inexistente.json", "demo"], folder)
            self.assertEqual(result.returncode, 1)
            self.assertIn("inexistente.json", result.stderr)

    def test_local_and_bundled_default_are_equal(self):
        local = json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
        bundled = json.loads((ROOT/"sentinela/default_config.json").read_text(encoding="utf-8"))
        self.assertEqual(local, bundled)
