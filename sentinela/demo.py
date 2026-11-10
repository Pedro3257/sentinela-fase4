from array import array
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import random
import wave


def generate(folder):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    rng = random.Random(42)
    start = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    events = []

    def add(offset, modality, data, labels=(), patient="PAC-SINT-001"):
        events.append(dict(id=f"demo-{len(events):04}", patient_id=patient,
                           timestamp=(start+timedelta(seconds=offset)).isoformat(), modality=modality, data=data, expected_codes=list(labels)))

    for i in range(12):
        add(i*10, "vitals", {"heart_rate": 75+rng.randint(-2, 2), "spo2": 97+rng.randint(-1, 1), "systolic_bp": 120+rng.randint(-3, 3)})
    add(115, "prescription", {"drug": "MEDICAMENTO-DEMO", "daily_dose": 10, "unit": "mg/day"})
    add(120, "vitals", {"heart_rate": 145, "spo2": 88, "systolic_bp": 120},
        ["vital:heart_rate:range", "vital:heart_rate:change", "vital:spo2:range", "vital:spo2:change"])
    add(125, "audio", {"transcript": "Estou com falta de ar e dor no peito.", "acoustic": {"silence_ratio": 0.7}, "transcription_source": "synthetic_fixture"},
        ["text:critical_terms", "audio:long_pauses", "fusion:concurrent_evidence"])
    add(130, "video", {"posture_deviation": True, "trunk_angle_degrees": 57, "duration_seconds": 3, "source": "synthetic_pose_fixture"},
        ["video:posture_deviation", "fusion:concurrent_evidence"])
    add(140, "prescription", {"drug": "MEDICAMENTO-DEMO", "daily_dose": 30, "unit": "mg/day"},
        ["prescription:dose_change", "fusion:concurrent_evidence"])
    add(150, "movement", {"immobility_seconds": 2100}, ["movement:immobility", "fusion:concurrent_evidence"])
    add(160, "text", {"text": "Paciente nega falta de ar. Sem dor no peito."})
    add(165, "vitals", {"heart_rate": 76, "spo2": 98, "systolic_bp": 121}, patient="PAC-SINT-002")
    with (folder/"events.jsonl").open("w", encoding="utf-8") as out:
        for event in events:
            out.write(json.dumps(event, ensure_ascii=False)+"\n")
    rate = 16000
    samples = array("h", [int(4000*math.sin(2*math.pi*180*i/rate)) if i < rate*2 else 0 for i in range(rate*8)])
    import sys
    if sys.byteorder != "little":
        samples.byteswap()
    with wave.open(str(folder/"audio-sintetico.wav"), "wb") as out:
        out.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        out.writeframes(samples.tobytes())
    (folder/"transcricao.txt").write_text("Estou com falta de ar e dor no peito.", encoding="utf-8")
    return folder/"events.jsonl"
