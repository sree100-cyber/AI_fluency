"""Day 4: estimate the memory a model needs, and whether it fits your machine.

Usage:
    python vram_estimate.py                 # uses AVAILABLE_GB below (8 GB)
    python vram_estimate.py --available 16  # override with your own RAM / VRAM
"""
import argparse

# Approximate bytes per parameter for common precisions (GGUF k-quants include
# a little block metadata, so these are effective rates, not the nominal bit depth).
BYTES_PER_PARAM = {
    "FP16": 2.00,
    "Q8_0": 1.00,
    "Q6_K": 0.81,
    "Q5_K_M": 0.68,
    "Q4_K_M": 0.57,
    "Q3_K_M": 0.43,
}

# Rough KV-cache cost for a modern grouped-query-attention model with an FP16
# cache: about 0.02 GB for every 1B parameters per 1K tokens of context used.
# Older multi-head models can be several times higher. Treat this as an estimate.
KV_GB_PER_B_PER_1K = 0.02
OVERHEAD = 1.10  # runtime, activations and fragmentation: about 10%


def estimate(params_b, precision="Q4_K_M", context_k=8):
    """Return (weights_gb, kv_gb, total_gb) for a model of params_b billion parameters."""
    if precision not in BYTES_PER_PARAM:
        raise ValueError(f"Unknown precision {precision}. Choose from {list(BYTES_PER_PARAM)}")
    weights_gb = params_b * BYTES_PER_PARAM[precision]
    kv_gb = params_b * context_k * KV_GB_PER_B_PER_1K
    total_gb = (weights_gb + kv_gb) * OVERHEAD
    return weights_gb, kv_gb, total_gb


def verdict(total_gb, available_gb):
    """Fit verdict: comfortable = within 70% of memory, tight = within 100%."""
    if total_gb <= available_gb * 0.7:
        return "fits comfortably"
    if total_gb <= available_gb:
        return "fits, but tight"
    return "does NOT fit"


def estimate_and_verdict(params_b, precision, context_k, available_gb):
    """Convenience wrapper used by the scenario scripts: (weights, kv, total, verdict)."""
    w, kv, total = estimate(params_b, precision, context_k)
    return w, kv, total, verdict(total, available_gb)


def report(name, params_b, precision, context_k, available_gb):
    weights, kv, total = estimate(params_b, precision, context_k)
    print(f"{name:<22} {precision:<7} {params_b:>5.1f}B ctx {context_k:>3}K "
          f"weights {weights:>6.2f} GB kv {kv:>5.2f} GB total {total:>6.2f} GB "
          f"-> {verdict(total, available_gb)}")


# ---- extra helpers (reverse the formula) -------------------------------------
def max_params_b(available_gb, precision="Q4_K_M", context_k=8):
    """Largest model (billions of params) whose estimated total <= available_gb."""
    per_b = (BYTES_PER_PARAM[precision] + context_k * KV_GB_PER_B_PER_1K) * OVERHEAD
    return available_gb / per_b


def max_context_k(params_b, available_gb, precision="Q4_K_M"):
    """Largest context (in K tokens) at which the model still fits available_gb."""
    budget = available_gb / OVERHEAD - params_b * BYTES_PER_PARAM[precision]
    return max(0.0, budget / (params_b * KV_GB_PER_B_PER_1K))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--available", type=float, default=8.0,
                        help="your RAM or GPU VRAM in GB (default 8.0)")
    AVAILABLE_GB = parser.parse_args().available  # change default above or pass --available

    print(f"Memory available: {AVAILABLE_GB} GB\n")
    report("Qwen small", 1.5, "Q4_K_M", 8, AVAILABLE_GB)
    report("Granite / Qwen mid", 8.0, "Q4_K_M", 8, AVAILABLE_GB)
    report("Mid at FP16", 8.0, "FP16", 8, AVAILABLE_GB)
    report("Large local", 30.0, "Q4_K_M", 8, AVAILABLE_GB)
    report("Server class", 70.0, "Q4_K_M", 8, AVAILABLE_GB)

    print("\nSame 8B model, different context lengths:")
    for context_k in (4, 8, 32, 128):
        report("8B agent", 8.0, "Q4_K_M", context_k, AVAILABLE_GB)

    print("\nSame 8B model, different quantizations:")
    for precision in ("Q3_K_M", "Q4_K_M", "Q5_K_M", "Q8_0", "FP16"):
        report("8B agent", 8.0, precision, 8, AVAILABLE_GB)

    # Experiment 3: your own machine - edit the two lines below for models you consider
    print("\nExperiment 3: models I am considering:")
    report("Model I want", 14.0, "Q4_K_M", 32, AVAILABLE_GB)
    report("Fallback", 8.0, "Q4_K_M", 8, AVAILABLE_GB)

    # Part D candidates (parameter counts from the model cards; see report/03)
    print("\nPart D candidates (Q4_K_M, 8K context):")
    report("Qwen3-8B", 8.2, "Q4_K_M", 8, AVAILABLE_GB)
    report("Mistral-7B v0.3", 7.25, "Q4_K_M", 8, AVAILABLE_GB)
    report("Granite 4.0 Micro", 3.0, "Q4_K_M", 8, AVAILABLE_GB)
    report("gpt-oss-20b (21B)", 21.0, "Q4_K_M", 8, AVAILABLE_GB)

    # Derived answers for the observation sheet
    print("\nDerived answers:")
    print(f"Largest model at Q4_K_M, 8K ctx : {max_params_b(AVAILABLE_GB):.1f}B (tight limit), "
          f"{max_params_b(AVAILABLE_GB * 0.7):.1f}B (comfortable)")
    print(f"Largest ctx for 8B at Q4_K_M    : {max_context_k(8.0, AVAILABLE_GB):.1f}K (tight limit), "
          f"{max_context_k(8.0, AVAILABLE_GB * 0.7):.1f}K (comfortable)")
    print(f"Friend with 6 GB card, Q4_K_M 8K: {max_params_b(6.0):.2f}B max")
