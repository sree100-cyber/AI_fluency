Measured on my laptop (Windows, CPU only) on 3 Oct 2026 with `ollama list`, `ollama ps` and `python check_reality.py`
(see screenshots/02 and screenshots/03). Re-running `python check_reality.py` overwrites this file with fresh readings.

| Model | ollama list (GB) | est. weights (GB) | ollama ps (GB) | est. total 4K ctx | est. total 8K ctx | PROCESSOR | context reported |
|---|---|---|---|---|---|---|---|
| qwen2.5:1.5b | 0.96 (986 MB) | 0.85 | 1.2 | 1.07 | 1.20 | 100% CPU | 4096 |
