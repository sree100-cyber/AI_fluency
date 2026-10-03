"""Section 3.2(a): memory estimate table for the scenario (16 GB laptop, ~10 GB usable)."""
import csv
from pathlib import Path

from vram_estimate import estimate_and_verdict

TOTAL_GB = 16.0    # installed RAM of the scenario machine
USABLE_GB = 10.0   # what is left for the model after Windows, VS Code and a browser (assumption)

# (label, parameters in billions from the model card, precision, context in K tokens)
CONFIGS = [
    ("Granite 4.0 Micro",      3.0,  "Q4_K_M", 8),
    ("Qwen3-4B",               4.0,  "Q4_K_M", 8),
    ("Mistral-7B-Instruct v0.3", 7.25, "Q4_K_M", 8),
    ("Qwen3-8B",               8.2,  "Q4_K_M", 8),
    ("Qwen3-8B",               8.2,  "Q4_K_M", 32),
    ("Qwen3-14B",              14.8, "Q4_K_M", 8),
    ("gpt-oss-20b",            21.0, "Q4_K_M", 8),
]

rows = []
for name, p, prec, ctx in CONFIGS:
    w, kv, total, v16 = estimate_and_verdict(p, prec, ctx, TOTAL_GB)
    _, _, _, v10 = estimate_and_verdict(p, prec, ctx, USABLE_GB)
    rows.append([name, p, prec, ctx, round(w, 2), round(kv, 2), round(total, 2), v16, v10])

header = ["Model", "Params (B)", "Precision", "Context (K)", "Weights (GB)", "KV cache (GB)",
          "Total (GB)", f"Fits in {TOTAL_GB:g} GB (installed)?", f"Fits in {USABLE_GB:g} GB (usable)?"]
md = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
md += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]

out = Path(__file__).parent / "results"
out.mkdir(exist_ok=True)
(out / "estimate_table.md").write_text("\n".join(md) + "\n")
with open(out / "estimate_table.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(header); w.writerows(rows)
print("\n".join(md))
