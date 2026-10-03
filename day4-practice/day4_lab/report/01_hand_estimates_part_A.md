# Part A – Estimate Three Models by Hand (8K context)

Formulas: weights = B x bytes/param | KV = B x 8 x 0.02 | total = (weights + KV) x 1.10

| Model | Precision | Weights (GB) | KV (GB) | Total (GB) | Working |
|---|---|---|---|---|---|
| 1.5B small | Q4_K_M | 0.86 | 0.24 | 1.20 | 1.5x0.57=0.855; 1.5x8x0.02=0.24; (0.855+0.24)x1.1=1.20 |
| 8B mid | Q4_K_M | 4.56 | 1.28 | 6.42 | 8x0.57=4.56; 8x8x0.02=1.28; 5.84x1.1=6.42 |
| 8B mid | FP16 | 16.00 | 1.28 | 19.01 | 8x2=16; 1.28; 17.28x1.1=19.01 |
| 30B large | Q4_K_M | 17.10 | 4.80 | 24.09 | 30x0.57=17.1; 30x8x0.02=4.8; 21.9x1.1=24.09 |
| 70B server | Q4_K_M | 39.90 | 11.20 | 56.21 | 70x0.57=39.9; 70x8x0.02=11.2; 51.1x1.1=56.21 |

## Questions

1. **Which fit on my machine?**  My machine has: ______ GB RAM / VRAM  (fill in).
   Rule used by the program: "comfortable" = total <= 70% of memory, "tight" = total <= 100%.
   - 8 GB machine: 1.5B fits comfortably; 8B Q4_K_M (6.42 GB) fits but is tight; 8B FP16, 30B and 70B do not fit.
   - 16 GB machine: 1.5B and 8B Q4 fit comfortably; 30B and 70B do not fit.
   - 24 GB GPU: 8B Q4 fits comfortably; 30B Q4 (24.09 GB) just misses at 8K context; 70B does not fit.

2. **Saving from Q4_K_M instead of FP16 for the 8B model:**
   weights 16.00 - 4.56 = 11.44 GB; total 19.01 - 6.42 = **12.59 GB** (about 66% less).
   The KV cache is the same in both because it depends on context length, not on weight precision.

3. **Friend with a 6 GB graphics card, Q4_K_M, 8K context:**
   total per billion parameters = (0.57 + 8x0.02) x 1.10 = 0.803 GB.
   6 / 0.803 = **about 7.5B parameters** at the absolute limit. So an 8B model (6.42 GB) does NOT fit;
   a 7B model (about 5.6 GB) technically fits but is tight; for comfortable headroom (70% = 4.2 GB) the limit is about 5.2B,
   so a 4B model is the safe choice.
