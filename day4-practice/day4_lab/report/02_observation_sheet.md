# Observation Sheet (Sections 7.2, 7.3, 7.4, 8, 11)

Machine used: RAM/VRAM = ______ GB      CPU/GPU = ____________      Date: ____________

## Experiment 1 – Context length (8B, Q4_K_M, 8 GB machine)
| Context | KV (GB) | Total (GB) | Verdict |
|---|---|---|---|
| 4K | 0.64 | 5.72 | fits, but tight |
| 8K | 1.28 | 6.42 | fits, but tight |
| 32K | 5.12 | 10.65 | does NOT fit |
| 128K | 20.48 | 27.54 | does NOT fit |

**Record:** The weights stay at 4.56 GB. The **KV cache** grew (0.64 GB to 20.48 GB), linearly with context length.
It stores the attention keys and values of every token processed so far, so it grows with every token in the conversation.
In the Unit 1 agents every tool result, observation and previous thought is appended to the conversation, so context grows
with each loop iteration. A long agent run or one big tool output (a whole web page, a large file) can push a model that
fits at 4K past the memory limit, and slow it down too. Keep tool outputs short and trim history.

## Experiment 2 – Quantization (8B, 8K context, 8 GB machine)
| Precision | Weights (GB) | Total (GB) | Verdict |
|---|---|---|---|
| Q3_K_M | 3.44 | 5.19 | fits comfortably |
| Q4_K_M | 4.56 | 6.42 | fits, but tight |
| Q5_K_M | 5.44 | 7.39 | fits, but tight |
| Q8_0 | 8.00 | 10.21 | does NOT fit |
| FP16 | 16.00 | 19.01 | does NOT fit |

**Record:** On 8 GB I would choose **Q4_K_M** (6.42 GB) if the machine has a GPU with 8 GB VRAM dedicated to the model, or if I keep the
context at 4K. On an 8 GB laptop without a GPU, where the operating system also uses 2 to 3 GB, Q3_K_M or a smaller (4B) model is safer.
What I give up: Q4 loses a little quality against Q8/FP16 (slightly weaker reasoning and tool-call accuracy); Q3 loses noticeably more;
and Q4 leaves little headroom for a long context.

## Experiment 3 – My own machine (AVAILABLE_GB = ____ )
Paste the output of `python vram_estimate.py --available <your GB>` here:

```
(paste)
```
Reference run with 16 GB: "Model I want" 14B Q4_K_M at 32K context = 18.63 GB, does NOT fit; fallback 8B Q4_K_M at 8K = 6.42 GB, fits comfortably.

## Part C – Estimate vs reality (run `python check_reality.py`, or fill by hand)
| Model on my machine | ollama list size | ollama ps size | My total estimate | PROCESSOR |
|---|---|---|---|---|
| ____________ | ____ GB | ____ GB | ____ GB | ____ |
| ____________ | ____ GB | ____ GB | ____ GB | ____ |

Comments: `ollama list` should be within a few hundred MB of the weights estimate. `ollama ps` is usually below the 8K estimate
because Ollama loads a smaller default context. (Reference: mistral:7b is listed at 4.4 GB on the Ollama library page
against my weights estimate of 4.13 GB for 7.25B parameters: a 0.27 GB difference, so the formula is slightly low.)

## 11.1 Hand estimates vs program
| Model | Your hand total | Program total | Difference |
|---|---|---|---|
| 1.5B Q4_K_M | 1.20 | 1.20 | 0.00 |
| 8B Q4_K_M | 6.42 | 6.42 | 0.00 |
| 8B FP16 | 19.01 | 19.01 | 0.00 |
| 30B Q4_K_M | 24.09 | 24.09 | 0.00 |
| 70B Q4_K_M | 56.21 | 56.21 | 0.00 |

(If your own hand sums differ, put your numbers in the second column and write the mistake you found.)

## 11.3 Effect of context and quantization (for an 8 GB machine, from the program's "Derived answers")
| Question | Your answer |
|---|---|
| Largest context an 8B Q4 model can use on my machine | about 17K tokens at the limit (about 3K to stay "comfortable") |
| Quantization I would choose for 8B on my machine, and why | Q4_K_M: best quality that still fits; Q3_K_M if the OS needs the memory |
| Largest model that fits at Q4_K_M with 8K context | about 10B at the limit (about 7B comfortably) |

For a 16 GB machine: about 62K context and about 20B (limit); 35K and 14B (comfortable).
Change these figures if your machine differs: `python vram_estimate.py --available <GB>`.
