"""Detecção explicável e fusão temporal por paciente, sem dependências externas."""
from collections import defaultdict, deque
from datetime import datetime, timezone
import hashlib
import json
import math
import re
import sqlite3
import statistics
import unicodedata


def timestamp(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamp deve conter fuso horário")
    return dt.astimezone(timezone.utc)


def normalized(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower())
                   if unicodedata.category(c) != "Mn")


def critical_terms(text):
    # Negação local simples: não cobre escopo complexo, ironia ou dupla negação.
    findings = []
    for clause in re.split(r"[.!?;\n]|\bmas\b", normalized(text)):
        for term in ("falta de ar", "dor no peito", "desmaio", "dificuldade para respirar"):
            for match in re.finditer(r"\b" + term + r"\b", clause):
                prefix = clause[:match.start()].split()[-4:]
                if not set(prefix).intersection({"nao", "nega", "sem", "negou"}):
                    findings.append(term)
    return sorted(set(findings))


def number(value, field, minimum=0, maximum=float("inf")):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not minimum <= value <= maximum:
        raise ValueError(f"Número inválido: {field}")
    return value


def validate_data(mode, data):
    if mode == "vitals" and not data:
        raise ValueError("Evento de sinais vitais vazio")
    if mode == "prescription":
        for field in ("drug", "unit"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                raise ValueError(f"Texto obrigatório: {field}")
        if number(data.get("daily_dose"), "daily_dose") == 0:
            raise ValueError("Dose diária deve ser positiva")
    if mode in ("text", "audio"):
        field = "text" if mode == "text" else "transcript"
        if not isinstance(data.get(field), str) or not data[field].strip():
            raise ValueError(f"Texto obrigatório: {field}")
    if mode == "audio":
        acoustic = data.get("acoustic", {})
        if not isinstance(acoustic, dict):
            raise ValueError("acoustic deve ser objeto")
        if "silence_ratio" in acoustic:
            number(acoustic["silence_ratio"], "silence_ratio", maximum=1)
    if mode == "movement":
        number(data.get("immobility_seconds"), "immobility_seconds")
    if mode == "video" and not isinstance(data.get("posture_deviation"), bool):
        raise ValueError("posture_deviation deve ser booleano")


class Engine:
    def __init__(self, config):
        self.config = config
        self.history = defaultdict(lambda: deque(maxlen=config["baseline_window"]))
        self.prescriptions = {}
        self.recent = defaultdict(deque)
        self.last_time = {}
        self.seen = set()

    def process(self, event):
        if not isinstance(event, dict):
            raise ValueError("Evento deve ser objeto JSON")
        for key in ("id", "patient_id", "timestamp", "modality", "data"):
            if key not in event:
                raise ValueError(f"Campo obrigatório: {key}")
        if not all(isinstance(event[k], str) and event[k].strip()
                   for k in ("id", "patient_id", "timestamp", "modality")):
            raise ValueError("Identificadores e modalidade devem ser strings não vazias")
        if not isinstance(event["data"], dict):
            raise ValueError("data deve ser objeto")
        if event["id"] in self.seen:
            return []
        pid, mode, data = event["patient_id"], event["modality"], event["data"]
        validate_data(mode, data)
        now = timestamp(event["timestamp"])
        if pid in self.last_time and now < self.last_time[pid]:
            raise ValueError("Eventos devem estar em ordem temporal por paciente")
        hits = []

        def add(code, severity, evidence):
            hits.append({"code": code, "severity": severity, "evidence": evidence})

        if mode == "vitals":
            pending = []
            for metric, value in data.items():
                if metric not in self.config["vitals"]:
                    raise ValueError(f"Sinal vital desconhecido: {metric}")
                if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise ValueError(f"Valor inválido: {metric}")
                limits = self.config["vitals"][metric]
                hist = self.history[(pid, metric)]
                abnormal = value < limits["min"] or value > limits["max"]
                if abnormal:
                    add(f"vital:{metric}:range", "high", {"value": value, "limits": limits})
                if len(hist) >= self.config["baseline_min"]:
                    med = statistics.median(hist)
                    mad = statistics.median(abs(x - med) for x in hist)
                    score = abs(value - med) / max(1.4826 * mad, limits["scale_floor"])
                    if score >= self.config["robust_z"]:
                        abnormal = True
                        add(f"vital:{metric}:change", "medium", {"value": value, "median": med, "robust_z": round(score, 3)})
                pending.append((hist, value, abnormal))
            for hist, value, abnormal in pending:
                if not abnormal:
                    hist.append(value)
        elif mode == "prescription":
            drug, unit = data["drug"], data["unit"]
            dose = float(data["daily_dose"])
            if not math.isfinite(dose) or dose <= 0:
                raise ValueError("Dose diária deve ser positiva e finita")
            key = (pid, drug.casefold())
            previous = self.prescriptions.get(key)
            if previous:
                old_dose, old_unit = previous
                if old_unit != unit:
                    add("prescription:unit_change", "medium", {"drug": drug, "previous_unit": old_unit, "unit": unit})
                else:
                    ratio = dose / old_dose
                    if ratio >= self.config["dose_ratio"] or ratio <= 1 / self.config["dose_ratio"]:
                        add("prescription:dose_change", "high", {"drug": drug, "previous": old_dose, "current": dose, "unit": unit, "ratio": ratio})
            self.prescriptions[key] = (dose, unit)
        elif mode in ("audio", "text"):
            terms = critical_terms(data.get("transcript", data.get("text", "")))
            if terms:
                add("text:critical_terms", "high", {"terms": terms})
            if mode == "audio" and data.get("acoustic", {}).get("silence_ratio", 0) > self.config["silence_ratio"]:
                add("audio:long_pauses", "medium", {"silence_ratio": data["acoustic"]["silence_ratio"], "interpretation": "Pausas prolongadas; confirmar gravação e avaliação humana"})
        elif mode == "movement":
            duration = float(data["immobility_seconds"])
            if not math.isfinite(duration) or duration < 0:
                raise ValueError("Duração de imobilidade inválida")
            if duration >= self.config["immobility_seconds"]:
                add("movement:immobility", "medium", {"seconds": duration})
        elif mode == "video":
            if data.get("posture_deviation") is True:
                add("video:posture_deviation", "medium", data)
        else:
            raise ValueError(f"Modalidade desconhecida: {mode}")

        self.seen.add(event["id"])
        self.last_time[pid] = now
        recent = self.recent[pid]
        while recent and (now - recent[0][0]).total_seconds() > self.config["fusion_window_seconds"]:
            recent.popleft()
        if hits:
            recent.append((now, mode, event["id"]))
        modalities = sorted({item[1] for item in recent})
        if hits and len(modalities) >= 2:
            add("fusion:concurrent_evidence", "high", {"modalities": modalities, "event_ids": [x[2] for x in recent]})
        for hit in hits:
            hit.update(patient_id=pid, timestamp=event["timestamp"], event_id=event["id"], status="pending_review")
            hit["id"] = hashlib.sha256(f'{event["id"]}:{hit["code"]}'.encode()).hexdigest()[:24]
        return hits


class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS alerts (id TEXT PRIMARY KEY, payload TEXT NOT NULL, status TEXT NOT NULL)")

    def save(self, event, alerts):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO events VALUES (?,?)", (event["id"], json.dumps(event, ensure_ascii=False)))
            self.db.executemany("INSERT OR IGNORE INTO alerts VALUES (?,?,?)", [(a["id"], json.dumps(a, ensure_ascii=False), a["status"]) for a in alerts])

    def acknowledge(self, alert_id):
        with self.db:
            cursor = self.db.execute("UPDATE alerts SET status='acknowledged' WHERE id=?", (alert_id,))
            if not cursor.rowcount:
                raise ValueError("Alerta não encontrado")

    def alerts(self):
        return [dict(json.loads(payload), status=status) for payload, status in self.db.execute("SELECT payload,status FROM alerts ORDER BY rowid")]

    def events(self):
        return [json.loads(row[0]) for row in self.db.execute("SELECT payload FROM events ORDER BY rowid")]
