"""Gera evidências locais novas sem substituir os registros históricos versionados."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
target = ROOT/"resultados/evidencias-novas"
target.mkdir(parents=True, exist_ok=True)
tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
(target/"testes.txt").write_text(tests.stderr, encoding="utf-8")
print(tests.stderr)
if tests.returncode:
    sys.exit(tests.returncode)
demo = subprocess.run([sys.executable, "-m", "sentinela", "demo", "--out", str(target/"demo")], cwd=ROOT)
if demo.returncode:
    sys.exit(demo.returncode)
print(f"Evidências novas em: {target}")
