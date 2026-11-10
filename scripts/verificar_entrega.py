"""Verifica estrutura, documentação e execução do pacote instalado fora do código."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def verify():
    required = ["pyproject.toml", "config.json", ".gitignore", ".env.example", "sentinela/core.py",
                "sentinela/media.py", "sentinela/default_config.json", "schemas/event.schema.json",
                ".github/workflows/ci.yml", "docs/Relatorio_Tecnico_Sentinela_Fase4.pdf",
                "docs/Relatorio_Tecnico_Sentinela_Fase4.md", "docs/Apresentacao_Sentinela_Fase4.pptx",
                "docs/Roteiro_10_Minutos_Sentinela_Fase4.pdf", "evidencias/alerts.json",
                "evidencias/metrics.json", "evidencias/fixtures/events.jsonl"]
    for name in required:
        if not (ROOT/name).is_file():
            raise ValueError(f"Arquivo obrigatório ausente: {name}")
    for target in re.findall(r"\]\(([^)]+)\)", (ROOT/"README.md").read_text(encoding="utf-8")):
        if not target.startswith(("http:", "https:", "#")) and not (ROOT/target.split("#")[0]).exists():
            raise ValueError(f"Link local quebrado no README: {target}")
    for name in ["config.json", "sentinela/default_config.json", "schemas/event.schema.json"]:
        json.loads((ROOT/name).read_text(encoding="utf-8"))
    # A CLI deve importar da instalação, não ser encontrada apenas pelo cwd.
    with tempfile.TemporaryDirectory() as folder:
        command = [sys.executable, "-m", "sentinela", "demo", "--out", "demo"]
        result = subprocess.run(command, cwd=folder, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=30)
        if result.returncode:
            raise ValueError("Execução fora do código falhou. Instale com python -m pip install .\n" + result.stderr)
        summary = json.loads((Path(folder)/"demo/summary.json").read_text(encoding="utf-8"))
        if (summary["stored_events"], summary["alerts"], summary["rejected"]) != (20, 13, 0):
            raise ValueError(f"Resultado de demonstração inesperado: {summary}")
    return {"status": "passed", "python": sys.version.split()[0], "required_files": len(required),
            "readme_links": "valid", "installed_cli_outside_repository": "passed",
            "synthetic_demo": {"events": 20, "alerts": 13, "rejected": 0},
            "limits": ["CI remota ainda não executada", "Azure e YOLO reais pendentes"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = verify()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text+"\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
