# Will It Fit, and May I Use It?  (Day 4 Task)

Estimating memory, weighing quantization and comparing licences for a local open-model scenario:
a 16 GB CPU-only laptop running a local PDF-summarising, tool-calling assistant that will be shown publicly on GitHub.

**Start with [analysis.md](analysis.md)** - it contains the whole written analysis and stands on its own.

| Path | Purpose |
|---|---|
| analysis.md | scenario, concepts, tables, observations, recommendation, conclusion |
| vram_estimate.py | estimator: weights, KV cache, total, fit verdict (plus max context / max size helpers) |
| scenario_estimates.py | estimate table for the scenario (3.2a) |
| context_quant_study.py | context and quantization study (3.3) |
| check_reality.py | compares `ollama list` / `ollama ps` with the estimate (3.4) |
| run_all.py | runs everything and saves into results/ |
| results/ | generated tables and text outputs |
| screenshots/ | terminal output, Ollama output, model card and licence pages |

## Run
    python run_all.py                     # everything, no packages needed (Python 3.9+)
    python vram_estimate.py --available 16
    python scenario_estimates.py
    python context_quant_study.py
    python check_reality.py               # needs Ollama and a loaded model (`ollama run <model>` in another terminal)
