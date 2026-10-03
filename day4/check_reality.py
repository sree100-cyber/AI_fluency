"""Part C automation: compare `ollama list` / `ollama ps` with the estimator.

Writes outputs/estimate_vs_reality.md (paste it into report/02_observation_sheet.md).
Works even if Ollama is missing: it then writes a note instead of failing.
"""
import re
import shutil
import subprocess
from pathlib import Path

from vram_estimate import estimate

OUT = Path(__file__).parent / "results" / "estimate_vs_reality.md"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout


def to_gb(value, unit):
    value = float(value)
    return value if unit.upper() == "GB" else value / 1024 if unit.upper() == "MB" else value


def guess_params_b(name):
    """qwen2.5:1.5b -> 1.5 ; llama3.1:8b -> 8.0 ; returns None if not in the tag."""
    m = re.search(r"(\d+(?:\.\d+)?)b\b", name.lower())
    return float(m.group(1)) if m else None


def parse_table(text):
    """Return rows of (name, size_gb) from `ollama list` or `ollama ps` output."""
    rows = []
    for line in text.strip().splitlines()[1:]:
        name = line.split()[0]
        m = re.search(r"(\d+(?:\.\d+)?)\s*(GB|MB)", line)
        if m:
            rows.append((name, to_gb(m.group(1), m.group(2)), line))
    return rows


def main():
    OUT.parent.mkdir(exist_ok=True)
    if not shutil.which("ollama"):
        OUT.write_text("Ollama not found on PATH. Install it or pair with a neighbour (Part C).\n")
        print(OUT.read_text())
        return

    disk = {n: s for n, s, _ in parse_table(run(["ollama", "list"]))}
    mem = {n: (s, l) for n, s, l in parse_table(run(["ollama", "ps"]))}

    lines = ["| Model | ollama list (GB) | est. weights (GB) | ollama ps (GB) | est. total 4K ctx | est. total 8K ctx | PROCESSOR |",
             "|---|---|---|---|---|---|---|"]
    for name, disk_gb in disk.items():
        p = guess_params_b(name)
        if p is None:
            lines.append(f"| {name} | {disk_gb:.2f} | (no size in tag) | | | | |")
            continue
        w, _, t8 = estimate(p, "Q4_K_M", 8)
        _, _, t4 = estimate(p, "Q4_K_M", 4)
        ps_gb, ps_line = mem.get(name, (None, ""))
        proc = re.search(r"(\d+%\s*(?:GPU|CPU)(?:/\d+%\s*(?:GPU|CPU))?)", ps_line)
        lines.append(f"| {name} | {disk_gb:.2f} | {w:.2f} | "
                     f"{'-' if ps_gb is None else f'{ps_gb:.2f}'} | {t4:.2f} | {t8:.2f} | "
                     f"{proc.group(1) if proc else '(not loaded)'} |")
    if not mem:
        lines.append("\n_No model was loaded. Run `ollama run <model>` in another terminal, then re-run this script._")
    OUT.write_text("\n".join(lines) + "\n")
    print(OUT.read_text())


if __name__ == "__main__":
    main()
