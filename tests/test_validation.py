import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sentinela.core import Engine, Store
from sentinela.cli import process_file
from test_core import CONFIG, event


class ValidationTests(unittest.TestCase):
    def test_malformed_modalities(self):
        cases = [None, [], 12, event(mode="text", data={"text": None}),
                 event(mode="audio", data={"transcript": "fala", "acoustic": None}),
                 event(mode="audio", data={"transcript": "fala", "acoustic": {"silence_ratio": 2}}),
                 event(mode="audio", data={"transcript": "fala", "acoustic": {"silence_ratio": float("nan")}}),
                 event(mode="prescription", data={"drug": 123, "unit": "mg", "daily_dose": 2}),
                 event(mode="prescription", data={"drug": "X", "unit": "mg", "daily_dose": True}),
                 event(mode="movement", data={"immobility_seconds": True}),
                 event(mode="video", data={"posture_deviation": "true"})]
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError):
                Engine(CONFIG).process(value)

    def test_bad_line_does_not_stop_next_event(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder)/"events.jsonl"
            source.write_text('null\n'+json.dumps(event())+'\n', encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(process_file(source, Path(folder)/"out", CONFIG), 1)
            store = Store(Path(folder)/"out/monitor.db")
            self.assertEqual(len(store.events()), 1)
            self.assertEqual(len(store.alerts()), 1)
            store.db.close()

    def test_cli_missing_file_exit_code(self):
        result = subprocess.run([sys.executable, "-m", "sentinela", "run", "arquivo-inexistente.jsonl"], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(b"Traceback", result.stderr)
