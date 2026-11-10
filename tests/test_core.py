import copy
import json
from pathlib import Path
import tempfile
import unittest

from sentinela.core import Engine, Store, critical_terms
from sentinela.demo import generate
from sentinela.cli import evaluate, process_file
from sentinela.media import acoustic_features

CONFIG = json.loads((Path(__file__).parents[1]/"config.json").read_text())


def event(id="one", patient="p1", mode="vitals", data=None, time="2026-01-01T12:00:00+00:00"):
    return dict(id=id, patient_id=patient, modality=mode, timestamp=time, data=data or {"spo2": 88})


class DetectionTests(unittest.TestCase):
    def setUp(self):
        self.engine = Engine(copy.deepcopy(CONFIG))

    def test_abnormal_vital_and_duplicate(self):
        e = event()
        self.assertEqual(self.engine.process(e)[0]["code"], "vital:spo2:range")
        self.assertEqual(self.engine.process(e), [])

    def test_negation(self):
        self.assertEqual(critical_terms("Nega falta de ar. Sem dor no peito."), [])
        self.assertEqual(critical_terms("Nega dor no peito, mas apresenta falta de ar."), ["falta de ar"])

    def test_patient_isolation(self):
        self.engine.process(event())
        hits = self.engine.process(event("two", "p2", "text", {"text": "falta de ar"}))
        self.assertNotIn("fusion:concurrent_evidence", [a["code"] for a in hits])

    def test_fusion_and_expiry(self):
        self.engine.process(event())
        hits = self.engine.process(event("two", mode="text", data={"text": "falta de ar"}))
        self.assertIn("fusion:concurrent_evidence", [a["code"] for a in hits])
        hits = self.engine.process(event("three", mode="movement", data={"immobility_seconds": 2100}, time="2026-01-01T12:06:00Z"))
        self.assertNotIn("fusion:concurrent_evidence", [a["code"] for a in hits])

    def test_invalid_and_out_of_order(self):
        with self.assertRaises(ValueError):
            self.engine.process(event(data={"spo2": float("nan")}))
        self.engine.process(event())
        with self.assertRaises(ValueError):
            self.engine.process(event("past", time="2025-01-01T12:00:00Z"))
        with self.assertRaises(ValueError):
            self.engine.process(event("naive", time="2026-01-01T12:00:00"))

    def test_dose_change_and_units(self):
        self.engine.process(event(mode="prescription", data={"drug": "X", "daily_dose": 10, "unit": "mg/day"}))
        hits = self.engine.process(event("two", mode="prescription", data={"drug": "X", "daily_dose": 30, "unit": "mg/day"}))
        self.assertEqual(hits[0]["code"], "prescription:dose_change")
        hits = self.engine.process(event("three", mode="prescription", data={"drug": "X", "daily_dose": 0.03, "unit": "g/day"}))
        self.assertEqual(hits[0]["code"], "prescription:unit_change")

    def test_baseline_not_contaminated(self):
        for i in range(8):
            self.engine.process(event(str(i), data={"heart_rate": 75}))
        hits = self.engine.process(event("jump", data={"heart_rate": 100}))
        self.assertEqual(hits[0]["code"], "vital:heart_rate:change")
        self.assertEqual(list(self.engine.history[("p1", "heart_rate")]), [75]*8)

    def test_demo_and_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            source = generate(folder)
            metrics = evaluate(source, CONFIG)
            self.assertEqual(metrics["false_positive_codes"], 0)
            self.assertEqual(metrics["false_negative_codes"], 0)
            features = acoustic_features(Path(folder)/"audio-sintetico.wav")
            self.assertAlmostEqual(features["duration_seconds"], 8)
            self.assertGreater(features["silence_ratio"], 0.7)

    def test_persistence_and_ack(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"monitor.db"
            store = Store(path)
            e = event()
            alerts = self.engine.process(e)
            store.save(e, alerts)
            store.save(e, alerts)
            store.acknowledge(alerts[0]["id"])
            self.assertEqual(len(store.alerts()), 1)
            self.assertEqual(store.alerts()[0]["status"], "acknowledged")
            store.db.close()

    def test_replay_idempotent(self):
        with tempfile.TemporaryDirectory() as folder:
            source = generate(Path(folder)/"fixtures")
            process_file(source, Path(folder)/"out", CONFIG)
            process_file(source, Path(folder)/"out", CONFIG)
            store = Store(Path(folder)/"out/monitor.db")
            self.assertEqual(len(store.events()), 20)
            self.assertEqual(len(store.alerts()), 13)
            store.db.close()


if __name__ == "__main__":
    unittest.main()
