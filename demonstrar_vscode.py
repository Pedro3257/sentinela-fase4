"""Execute com F5: demonstração local, sintética, sem serviços externos."""
import contextlib
from datetime import datetime
import io
import json
from pathlib import Path
import time

from sentinela.cli import process_file, evaluate
from sentinela.core import Engine, Store
from sentinela.demo import generate
from sentinela.media import analyze_audio


def main():
    root = Path(__file__).resolve().parent
    output = root / "resultados" / ("vscode-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    source = generate(output / "fixtures")
    print("SENTINELA | DEMONSTRAÇÃO NO VS CODE", flush=True)
    print("Dados sintéticos. Azure e YOLO reais não são usados nesta execução.\n", flush=True)
    engine = Engine(config)
    events = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    total = 0
    for event in events:
        hits = engine.process(event)
        if hits:
            print(f"{event['timestamp'][11:19]} UTC | {event['modality'].upper()} | {event['patient_id']}", flush=True)
            print("  Entrada: " + json.dumps(event["data"], ensure_ascii=False), flush=True)
            for hit in hits:
                print(f"  ALERTA [{hit['severity']}] {hit['code']}", flush=True)
            total += len(hits)
            print(flush=True)
            time.sleep(1)
    print(f"1. DETECÇÃO CONCLUÍDA: {len(events)} eventos e {total} alertas.\n", flush=True)

    with contextlib.redirect_stdout(io.StringIO()):
        process_file(source, output, config)
    store = Store(output / "monitor.db")
    first = store.alerts()[0]
    store.acknowledge(first["id"])
    current = store.alerts()[0]
    print(f"2. REVISÃO HUMANA: {current['code']}", flush=True)
    print(f"   {first['status']} -> {current['status']}\n", flush=True)
    store.db.close()
    with contextlib.redirect_stdout(io.StringIO()):
        process_file(source, output, config)

    audio = analyze_audio(output / "fixtures/audio-sintetico.wav", transcript=(output / "fixtures/transcricao.txt").read_text(encoding="utf-8"))
    (output / "audio-processado.json").write_text(json.dumps(audio, ensure_ascii=False, indent=2), encoding="utf-8")
    print("3. EXTRAÇÃO DO WAV: tom e silêncio, transcrição fornecida separadamente.", flush=True)
    print(f"   Duração: {audio['acoustic']['duration_seconds']} s", flush=True)
    print(f"   Razão de silêncio: {audio['acoustic']['silence_ratio']}", flush=True)
    print(f"   Maior pausa: {audio['acoustic']['longest_pause_seconds']} s\n", flush=True)

    metrics = evaluate(source, config)
    (output / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print("4. REGRESSÃO SINTÉTICA:", flush=True)
    print(f"   Falsos positivos: {metrics['false_positive_codes']} | Falsos negativos: {metrics['false_negative_codes']}", flush=True)
    print("   Esses números não medem desempenho clínico.\n", flush=True)
    (root / "ULTIMA_DEMONSTRACAO.md").write_text(
        "# Demonstração executada no VS Code\n\n"
        f"Pasta dos resultados: `{output.relative_to(root).as_posix()}`\n\n"
        "- 20 eventos sintéticos e 13 alertas.\n"
        "- Um alerta confirmado como acknowledged.\n"
        "- WAV sintético processado; transcrição fornecida.\n"
        "- Relatório e banco persistidos.\n"
        "- Azure e YOLO reais não foram usados.\n\n"
        f"[Abrir relatório]({output.relative_to(root).as_posix()}/report.md)\n",
        encoding="utf-8")
    print("DEMONSTRAÇÃO CONCLUÍDA", flush=True)
    print(f"Relatório: {output / 'report.md'}", flush=True)
    print("Abra ULTIMA_DEMONSTRACAO.md para localizar os arquivos.", flush=True)


if __name__ == "__main__":
    main()
