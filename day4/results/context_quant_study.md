Model: Qwen3-8B (8.2B).  Installed 16 GB, usable 10 GB.

| Setting changed | Value used | Weights (GB) | KV cache (GB) | Total (GB) | Fits in 10 GB usable? | Fits in 16 GB? |
|---|---|---|---|---|---|---|
| Context length (Q4_K_M) | 4K | 4.67 | 0.66 | 5.86 | fits comfortably | fits comfortably |
| Context length (Q4_K_M) | 8K | 4.67 | 1.31 | 6.58 | fits comfortably | fits comfortably |
| Context length (Q4_K_M) | 32K | 4.67 | 5.25 | 10.91 | does NOT fit | fits comfortably |
| Context length (Q4_K_M) | 128K | 4.67 | 20.99 | 28.23 | does NOT fit | does NOT fit |
| Quantization (8K context) | Q3_K_M | 3.53 | 1.31 | 5.32 | fits comfortably | fits comfortably |
| Quantization (8K context) | Q4_K_M | 4.67 | 1.31 | 6.58 | fits comfortably | fits comfortably |
| Quantization (8K context) | Q5_K_M | 5.58 | 1.31 | 7.58 | fits, but tight | fits comfortably |
| Quantization (8K context) | Q8_0 | 8.20 | 1.31 | 10.46 | does NOT fit | fits comfortably |

Largest context before the estimate exceeds memory:
  Q3_K_M  usable 10 GB:  33.9K tight limit,  17.3K comfortable | 16 GB:  67.2K tight limit
  Q4_K_M  usable 10 GB:  26.9K tight limit,  10.3K comfortable | 16 GB:  60.2K tight limit
  Q5_K_M  usable 10 GB:  21.4K tight limit,   4.8K comfortable | 16 GB:  54.7K tight limit
  Q8_0    usable 10 GB:   5.4K tight limit,   0.0K comfortable | 16 GB:  38.7K tight limit
