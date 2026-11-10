import argparse
from collections import Counter
from datetime import timedelta
import json
from pathlib import Path
import sys
import time

from .core import Engine, Store, timestamp
from .demo import generate
from .media import analyze_audio, analyze_video

DEFAULT_CONFIG = Path(__file__).with_name("default_config.json")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def process_file(source, output, config, interval=0, follow=False):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    store = Store(output/"monitor.db")
    engine = Engine(config)
    # Reconstrói baseline e fusão após reinício, preservando ordem de ingestão.
    for event in store.events():
        engine.process(event)
    errors, count = [], 0
    try:
        with open(source, encoding="utf-8") as stream:
            line_number = 0
            while True:
                position = stream.tell()
                line = stream.readline()
                if not line or not line.endswith("\n"):
                    if follow:
                        stream.seek(position)
                        time.sleep(0.25)
                        continue
                    if not line:
                        break
                line_number += 1
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    alerts = engine.process(event)
                    store.save(event, alerts)
                    count += 1
                    for alert in alerts:
                        print(json.dumps(alert, ensure_ascii=False), flush=True)
                except (ValueError, KeyError, TypeError, OverflowError) as exc:
                    errors.append({"line": line_number, "error": str(exc)})
                    print(f"Evento rejeitado na linha {line_number}: {exc}", file=sys.stderr)
                if interval:
                    time.sleep(interval)
    except KeyboardInterrupt:
        pass
    alerts = store.alerts()
    write(output/"alerts.json", alerts)
    write(output/"errors.json", errors)
    summary = {"events_read_this_run": count, "stored_events": len(store.events()), "alerts": len(alerts),
               "by_code": dict(Counter(a["code"] for a in alerts)), "rejected": len(errors)}
    write(output/"summary.json", summary)
    rows = ["# Relatório automático", "", "Protótipo acadêmico. Alertas exigem revisão humana.", "",
            f"Eventos armazenados: {summary['stored_events']}. Alertas: {len(alerts)}. Rejeitados nesta execução: {len(errors)}.", "",
            "| Instante | Paciente | Código | Gravidade | Estado |", "|---|---|---|---|---|"]
    rows += [f"| {a['timestamp']} | {a['patient_id']} | {a['code']} | {a['severity']} | {a['status']} |" for a in alerts]
    (output/"report.md").write_text("\n".join(rows)+"\n", encoding="utf-8")
    store.db.close()
    return 1 if errors else 0


def evaluate(source, config):
    engine = Engine(config)
    tp = fp = fn = 0
    cases = []
    for line in Path(source).read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        predicted = {a["code"] for a in engine.process(event)}
        expected = set(event["expected_codes"])
        tp += len(predicted & expected)
        fp += len(predicted - expected)
        fn += len(expected - predicted)
        cases.append({"event_id": event["id"], "expected": sorted(expected), "predicted": sorted(predicted)})
    precision = tp/(tp+fp) if tp+fp else 0
    recall = tp/(tp+fn) if tp+fn else 0
    return {"scope": "Teste de regressão com fixtures sintéticas; não mede desempenho clínico ou dos modelos Azure/YOLO",
            "true_positive_codes": tp, "false_positive_codes": fp, "false_negative_codes": fn,
            "precision": precision, "recall": recall, "f1": 2*precision*recall/(precision+recall) if precision+recall else 0, "cases": cases}


def main():
    parser = argparse.ArgumentParser(description="Sentinela multimodal — protótipo acadêmico")
    parser.add_argument("--config", help="JSON de configuração; usa config.json local ou padrão do pacote")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Gera dados sintéticos e processa o fluxo")
    demo.add_argument("--out", default="resultados/demo")
    run = sub.add_parser("run", help="Consome eventos JSONL")
    run.add_argument("source")
    run.add_argument("--out", default="resultados/monitor")
    run.add_argument("--interval", type=float, default=0)
    run.add_argument("--follow", action="store_true", help="Acompanha novas linhas; Ctrl+C encerra")
    audio = sub.add_parser("audio")
    audio.add_argument("source")
    audio.add_argument("--transcript", help="Arquivo .txt com transcrição fornecida no modo local")
    audio.add_argument("--azure", action="store_true")
    audio.add_argument("--patient", required=True)
    audio.add_argument("--timestamp", required=True)
    audio.add_argument("--id", required=True)
    audio.add_argument("--out", default="resultados/audio.jsonl")
    video = sub.add_parser("video")
    video.add_argument("source")
    video.add_argument("--patient", required=True)
    video.add_argument("--timestamp", required=True, help="Instante inicial do vídeo com fuso")
    video.add_argument("--id", required=True)
    video.add_argument("--weights", default="yolov8n-pose.pt")
    video.add_argument("--out", default="resultados/video.jsonl")
    ack = sub.add_parser("ack")
    ack.add_argument("alert_id")
    ack.add_argument("--db", required=True)
    listing = sub.add_parser("alerts")
    listing.add_argument("--db", required=True)
    ev = sub.add_parser("evaluate")
    ev.add_argument("source")
    ev.add_argument("--out", default="resultados/metrics.json")
    args = parser.parse_args()
    try:
        config_path = args.config or (Path("config.json") if Path("config.json").is_file() else DEFAULT_CONFIG)
        config = load(config_path)
        if args.command == "demo":
            source = generate(Path(args.out)/"fixtures")
            code = process_file(source, args.out, config)
            write(Path(args.out)/"metrics.json", evaluate(source, config))
            return code
        if args.command == "run":
            if args.interval < 0:
                raise ValueError("--interval deve ser não negativo")
            return process_file(args.source, args.out, config, args.interval, args.follow)
        if args.command == "audio":
            timestamp(args.timestamp)
            transcript = Path(args.transcript).read_text(encoding="utf-8") if args.transcript else None
            data = analyze_audio(args.source, transcript, args.azure)
            events = [dict(id=args.id, patient_id=args.patient, timestamp=args.timestamp, modality="audio", data=data)]
        elif args.command == "video":
            start = timestamp(args.timestamp)
            report = analyze_video(args.source, config, args.weights)
            write(str(args.out)+".report.json", report)
            events = [dict(id=f"{args.id}-{i}", patient_id=args.patient,
                           timestamp=(start+timedelta(seconds=f["offset_seconds"])).isoformat(), modality="video", data=f)
                      for i, f in enumerate(report["findings"])]
        elif args.command in ("ack", "alerts"):
            if not Path(args.db).is_file():
                raise ValueError("Banco não encontrado")
            store = Store(args.db)
            if args.command == "ack":
                store.acknowledge(args.alert_id)
            print(json.dumps(store.alerts(), ensure_ascii=False, indent=2))
            store.db.close()
            return 0
        elif args.command == "evaluate":
            write(args.out, evaluate(args.source, config))
            return 0
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text("".join(json.dumps(e, ensure_ascii=False)+"\n" for e in events), encoding="utf-8")
        return 0
    except (ValueError, KeyError, RuntimeError, OSError, ImportError, TimeoutError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
