"""Section 3.3: vary context (quantization fixed) and quantization (context fixed) for one model."""
from pathlib import Path

from vram_estimate import estimate_and_verdict, max_context_k

MODEL, PARAMS_B = "Qwen3-8B", 8.2
TOTAL_GB, USABLE_GB = 16.0, 10.0
FIXED_QUANT, FIXED_CTX = "Q4_K_M", 8

lines = [f"Model: {MODEL} ({PARAMS_B}B).  Installed {TOTAL_GB:g} GB, usable {USABLE_GB:g} GB.", "",
         "| Setting changed | Value used | Weights (GB) | KV cache (GB) | Total (GB) | Fits in 10 GB usable? | Fits in 16 GB? |",
         "|---|---|---|---|---|---|---|"]
for ctx in (4, 8, 32, 128):
    w, kv, t, v10 = estimate_and_verdict(PARAMS_B, FIXED_QUANT, ctx, USABLE_GB)
    v16 = estimate_and_verdict(PARAMS_B, FIXED_QUANT, ctx, TOTAL_GB)[3]
    lines.append(f"| Context length ({FIXED_QUANT}) | {ctx}K | {w:.2f} | {kv:.2f} | {t:.2f} | {v10} | {v16} |")
for q in ("Q3_K_M", "Q4_K_M", "Q5_K_M", "Q8_0"):
    w, kv, t, v10 = estimate_and_verdict(PARAMS_B, q, FIXED_CTX, USABLE_GB)
    v16 = estimate_and_verdict(PARAMS_B, q, FIXED_CTX, TOTAL_GB)[3]
    lines.append(f"| Quantization ({FIXED_CTX}K context) | {q} | {w:.2f} | {kv:.2f} | {t:.2f} | {v10} | {v16} |")

lines += ["", "Largest context before the estimate exceeds memory:"]
for q in ("Q3_K_M", "Q4_K_M", "Q5_K_M", "Q8_0"):
    lines.append(f"  {q:<7} usable 10 GB: {max_context_k(PARAMS_B, USABLE_GB, q):5.1f}K tight limit, "
                 f"{max_context_k(PARAMS_B, USABLE_GB * 0.7, q):5.1f}K comfortable | "
                 f"16 GB: {max_context_k(PARAMS_B, TOTAL_GB, q):5.1f}K tight limit")

text = "\n".join(lines)
out = Path(__file__).parent / "results"
out.mkdir(exist_ok=True)
(out / "context_quant_study.md").write_text(text + "\n")
print(text)
