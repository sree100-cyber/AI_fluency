# Will It Fit, and May I Use It?
### Day 4 Task – Agentic AI: Foundations and Open-Source Practice (Unit 2: Open LLMs and Local Serving)

All model facts in this document were read on **3 October 2026**. Model cards and licences are revised, so every claim about a card is only true for that date.

---

## 0. My scenario

**Machine.** My own Windows laptop with **16 GB of RAM and no usable GPU** for model work. The 16 GB figure is the one I used in all my estimator runs. My own `ollama ps` reading showed the processor as 100% CPU, so everything the model needs must sit in ordinary RAM. Windows, VS Code and a browser take a share of that RAM; I assume about 6 GB, which leaves a **usable budget of about 10 GB** for a model. I report both numbers: 16 GB (installed) and 10 GB (usable). The 10 GB figure is the one I trust for decisions.

**Purpose.** A local assistant that summarises PDF reports and study notes and can call tools (list a folder, read a file, search the text), working like the agents I built in Unit 1. It must work offline.

**Users.** First myself, for studying. Then the public: the code goes to GitHub and I will demonstrate it in a portfolio and in interviews.

**Licensing situation.** Because the project is public and I may later show it to employers or reuse it commercially, I want a model whose licence permits commercial use, modification and redistribution without asking anyone. In practice that means **Apache 2.0 or MIT**. I will not ship the weights in the repository (users pull them with Ollama), but the demonstration must be reproducible by anyone, so the licence of the model still matters. The licence of my code (MIT) is separate from the licence of the model.

---

## 1. Explanation of each concept

### 1.1 Model weights

The weights are the learned numbers of the network. Their size is fixed by two things only: the number of parameters and the number of bytes used to store each one. The rule is *weights (GB) = parameters in billions × bytes per parameter*. They control the **fit** half of the decision, because they are the largest and least negotiable part of the memory bill: a model that is too big on disk can never be loaded, however short the conversation.

In my scenario I started from the parameter count printed on each model card and multiplied by the bytes per parameter of the precision I intended to use. Qwen3-8B has 8.2 billion parameters, so at Q4_K_M (0.57 bytes per parameter) its weights are 8.2 × 0.57 = 4.67 GB, while the same model at FP16 would need 16.4 GB, which could never run on my laptop. Granite 4.0 Micro (3B) gives 1.71 GB and gpt-oss-20b (21B) gives 11.97 GB.

If the weights are ignored or misjudged, the first symptom is a download that cannot run: an hour is spent on a file that exhausts RAM, or Windows starts swapping to disk and the model becomes unusably slow. The limitation I met on my own machine is that the formula is slightly low. Ollama reports `qwen3:8b` at 5.2 GB on its library page against my 4.67 GB estimate (about 11% more), `mistral:7b` at 4.4 GB against 4.13 GB (about 7% more), and my own installed `qwen2.5:1.5b` at 986 MB against 0.85 GB (about 13% more). The most likely reason is that some tensors, such as the embedding and output layers, are kept at higher precision than the nominal quantization, so the real average cost per parameter is a little above 0.57. The estimate is therefore a good guide to fit, but I add a margin of 10 to 15% on the weights when a model is near the limit. For a mixture-of-experts model such as gpt-oss-20b (21B total, 3.6B active per token) the weights are set by the **total** parameters, because any expert may be chosen for any token; the small active count makes it fast, not small.

### 1.2 Quantization

Quantization stores each weight with fewer bits, which lowers the bytes per parameter and therefore the weights. In the lab table FP16 uses 2.00 bytes per parameter, Q8_0 uses 1.00, Q5_K_M 0.68, Q4_K_M 0.57 and Q3_K_M 0.43. It controls fit, and it buys that fit with quality: fewer bits mean rounding error in every weight. In a K-quant name such as Q4_K_M, the *K* marks the block-wise "k-quant" scheme and the *M* stands for the medium variant, a middle size/quality setting.

I used it as a dial on one model. For Qwen3-8B at 8K context the weights fall from 8.20 GB at Q8_0 to 5.58 GB at Q5_K_M, 4.67 GB at Q4_K_M and 3.53 GB at Q3_K_M, and the total moves from 10.46 GB (does not fit in my 10 GB usable budget) to 5.32 GB (fits comfortably). That is how I found that Q4_K_M is the highest-quality choice that still leaves room for a useful context, while Q5_K_M (7.58 GB) is tight at my usable budget and Q8_0 is out of reach.

If quantization is ignored, I either pick a precision that cannot load, or I over-compress and lose quality without noticing. The cost shows up exactly where my scenario is most demanding: tool calling needs the model to produce well-formed arguments, and an aggressive Q3 build is the first place I would expect malformed calls, so I would test tool-call success on my own agent before accepting a lower precision. The limitation is that the table gives bytes, not quality. It tells me what fits, never how much worse the model becomes, and the labels differ slightly between builds (which is part of why my estimates were a little low).

### 1.3 KV cache and context length

The KV cache is the model's working memory for the conversation. For every token already processed, the model stores the attention keys and values so it does not recompute them. It grows with the number of tokens in the context, whereas the weights do not change at all. The lab's estimate is *KV (GB) = parameters in billions × context in K tokens × 0.02*, and the total is *(weights + KV) × 1.10*, where the 10% covers runtime overhead. The KV cache controls whether a model that fits at a short context keeps fitting as the conversation grows.

I applied it to Qwen3-8B. The weights stay at 4.67 GB, but the KV cache is 0.66 GB at 4K, 1.31 GB at 8K, 5.25 GB at 32K and 20.99 GB at 128K. The total therefore goes 5.86, 6.58, 10.91 and 28.23 GB. At 32K the model already stops fitting in my 10 GB usable budget (10.91 GB) even though it still fits in 16 GB installed; at 128K it fits nowhere. This is directly relevant to my assistant, because an agent keeps appending to the conversation: every tool result, every file it reads and every previous answer adds tokens. Qwen3 also reasons by default (its documentation says it thinks before responding), and those reasoning tokens occupy the context too. A twenty-page report can plausibly run to something like 10,000 tokens (my rough assumption of 500 tokens per page), so a naive "read the whole file" call can exceed an 8K window by itself.

If context is ignored, the agent works for a few steps and then slows to a crawl or fails when memory runs out, and the cause looks mysterious because the model "fit" at the start. The limitation here is that the 0.02 constant assumes a modern grouped-query-attention model with a 16-bit cache. A model with sliding-window or hybrid layers needs less, and an older architecture needs several times more. For gpt-oss-20b the formula over-predicts the cache because part of its attention is windowed, and for the Granite 4.0 hybrid models the memory grows more slowly with context than the formula says. Ollama also loads only a modest context by default; my own `ollama ps` showed a context of 4096 for the model I ran, not the 8K I used in my estimate.

### 1.4 Model card

A model card is the publisher's own page for a model (on Hugging Face and mirrored on the Ollama library page). It states the facts that decide *permission* and *capability*: the exact licence name, parameter count (total and active), context window, which sizes exist, intended use, known limitations and whether tool calling is supported. The card is the only authoritative place to read these facts, and it is dated by the day I read it.

I used the cards to fill the comparison table in section 2. Each of the four cards gave me the parameter count I fed into the estimator, and the licence I needed for the public release. For example, the Qwen3-8B card gives 32,768 tokens as the native context and 131,072 with YaRN, which told me what context I could even attempt; the Mistral-7B v0.3 card told me tool calling was new in that version, and the Ollama page for it shows the Apache licence text and a 4.4 GB download. I also used a card as a warning: the Ministral-8B card from the same publisher says it is released under a research licence and that commercial use needs a separate agreement, which is why I keep it out of my shortlist even though it looks attractive on size.

If the card is ignored, I could build a project on a model I am not allowed to publish, or assume a feature (tool calling, a long context) that the model does not have. The limitation on my scenario is that cards describe what the publisher claims, not how the model behaves on my tasks, and that third-party mirrors sometimes repeat the card with errors. I therefore read the publisher's card and the Ollama page, and I record the date because both can change.

### 1.5 Open-weight versus open-source licensing

"Open-weight" means the trained weights can be downloaded and run. "Open-source", in the strict sense used for software, means the licence allows anyone to use, study, modify and redistribute without discrimination, and the licence is OSI-approved. A model can be open-weight without being open-source: the weights are downloadable, but the licence may forbid commercial use, require a separate agreement above a usage threshold, or attach an acceptable-use policy. The licence name and its conditions decide **permission**, which is independent of whether the model fits.

In my scenario the licence is a gate applied before memory. Qwen3-8B, Granite 4.0 Micro, Mistral-7B v0.3 and gpt-oss-20b are all released under Apache 2.0, which allows commercial use, modification and redistribution, requires me to keep the licence and notices and to mark changes, and includes a patent grant. All four pass my gate. Ministral-8B fails it because its research licence does not give me commercial rights.

If the licence is ignored, the failure arrives late and is expensive: a public project or product built on a model I may not use has to be redone. The limitations are of two kinds. First, even an Apache 2.0 model is open-weight rather than fully open in the sense of releasing its training data, so I should not claim that I can reproduce the model. Second, a "permissive" licence can still come with a separate usage policy (I noted that gpt-oss ships with one and I have marked it for verification), and the licence on the weights does not change the licences of my code or my data.

---

## 2. Estimate table and comparison table

### 2.1 (a) Memory estimate table

Produced by `scenario_estimates.py` (also saved in `results/estimate_table.md`). Parameter counts are those on the model cards, precision is the Ollama default Q4_K_M, and the last two columns give the verdict against the installed and usable memory.

| Model | Params (B) | Precision | Context (K) | Weights (GB) | KV cache (GB) | Total (GB) | Fits in 16 GB (installed)? | Fits in 10 GB (usable)? |
|---|---|---|---|---|---|---|---|---|
| Granite 4.0 Micro | 3.0 | Q4_K_M | 8 | 1.71 | 0.48 | 2.41 | fits comfortably | fits comfortably |
| Qwen3-4B | 4.0 | Q4_K_M | 8 | 2.28 | 0.64 | 3.21 | fits comfortably | fits comfortably |
| Mistral-7B-Instruct v0.3 | 7.25 | Q4_K_M | 8 | 4.13 | 1.16 | 5.82 | fits comfortably | fits comfortably |
| Qwen3-8B | 8.2 | Q4_K_M | 8 | 4.67 | 1.31 | 6.58 | fits comfortably | fits comfortably |
| Qwen3-8B | 8.2 | Q4_K_M | 32 | 4.67 | 5.25 | 10.91 | fits comfortably | does NOT fit |
| Qwen3-14B | 14.8 | Q4_K_M | 8 | 8.44 | 2.37 | 11.88 | fits, but tight | does NOT fit |
| gpt-oss-20b | 21.0 | Q4_K_M | 8 | 11.97 | 3.36 | 16.86 | does NOT fit | does NOT fit |

The table already shows the three effects the task asks about. Weights scale with parameters (3B to 21B). The same Qwen3-8B passes from "comfortable" to "does not fit in 10 GB" only because the context grew from 8K to 32K. And the verdict depends on the budget I choose: Qwen3-14B "fits" in installed memory but not in the memory I can really use.

### 2.2 (b) Comparison table (checked 3 October 2026)

| Basis for comparison | Model 1 | Model 2 | Model 3 | Model 4 (extra) |
|---|---|---|---|---|
| Full model name and version | Qwen3-8B | IBM Granite 4.0 Micro (granite-4.0 family) | Mistral-7B-Instruct-v0.3 | gpt-oss-20b |
| Publisher | Alibaba (Qwen team) | IBM | Mistral AI | OpenAI |
| Total / active parameters (MoE?) | 8.2B / 8.2B, dense | 3B / 3B, dense (the family also has a 7B-total / 1B-active and a 32B-total / 9B-active hybrid MoE) | 7.25B / 7.25B, dense | 21B total / 3.6B active, MoE |
| Context window | 32,768 native, 131,072 with YaRN (Ollama lists 40K) | 128K validated (trained on samples up to 512K) | 32K | 131,072 |
| Licence (exact name) | Apache License 2.0 | Apache License 2.0 | Apache License 2.0 | Apache License 2.0 |
| Commercial use allowed? | Yes | Yes | Yes | Yes |
| Any extra conditions? | Standard Apache 2.0 terms only (keep licence and notices, mark changes) | Standard Apache 2.0; checkpoints are cryptographically signed | Standard Apache 2.0 (the same publisher's Ministral-8B is under a research licence, not Apache) | Apache 2.0; I believe it is accompanied by a usage policy (verify on the card) |
| Tool calling stated on the card? | Yes (function-calling documentation and tool-call parsing) | Yes (stated as an enhanced capability) | Yes (v0.3 adds function calling; Ollama tags it "tools") | Yes (function calling, browsing, Python execution, structured outputs) |
| GGUF / Ollama build available? | Yes (`qwen3:8b`) | Yes (`granite4`; check the exact tag) | Yes (`mistral:7b`) | Yes (`gpt-oss:20b`) |
| Download size at Q4 (Ollama) | 5.2 GB | about 2 GB (verify the tag) | 4.4 GB | about 14 GB, native MXFP4 (verify) |
| Your memory estimate (total, 8K, Q4_K_M) | 6.58 GB | 2.41 GB | 5.82 GB | 16.86 GB (formula high; see 1.3) |
| Fits your scenario's machine? | Yes (10 GB usable) | Yes | Yes | No: a 14 GB file leaves almost nothing of 16 GB for Windows and the cache |
| Date you checked the card | 3 Oct 2026 | 3 Oct 2026 | 3 Oct 2026 | 3 Oct 2026 |

Sizes and tags marked "verify" are the ones I could not confirm directly from the publisher page; I will open each page again and correct them before the final push.

**Licence observations.** Two sizes of one family had different licences in the Mistral family: Mistral-7B v0.3 is Apache 2.0 while Ministral-8B is under the Mistral Research License. All four models in the table can be used in a product without asking anyone, subject to Apache's notice requirements. The only model with real commercial conditions among those I looked at is Ministral-8B; the exact clause must be copied from its `LICENSE` file into my submission (screenshots/13), and I have not quoted it here from memory.

---

## 3. Context length and quantization observation

I chose **Qwen3-8B** (8.2B parameters) because it is the model I will most likely recommend. The study is produced by `context_quant_study.py` and saved in `results/context_quant_study.md`.

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

When the **context grew**, only the KV cache changed (0.66 GB to 20.99 GB); the weights stayed at 4.67 GB, and the total rose with the cache until the model no longer fit. When the **quantization changed**, only the weights changed (3.53 GB to 8.20 GB); the KV cache stayed at 1.31 GB, because in this estimate the cache depends on parameters and context, not on the weight precision. The largest context this model can use at Q4_K_M is about **26.9K tokens** before the estimate passes my 10 GB usable budget (the tight limit), and about **10K tokens** if I want to stay inside the comfortable 70% band; against all 16 GB the tight limit is about 60K. I would choose **Q4_K_M**: it is the best-quality precision that leaves room for a useful context at my usable budget, whereas Q5_K_M leaves only about 2.4 GB of headroom and Q8_0 does not fit. By choosing Q4 I give up a little accuracy compared with Q8 or FP16 (slightly weaker reasoning and tool-call precision), and I accept that I must keep the context to roughly 8K to 16K. At 16K the estimate is about 8.0 GB, which fits my 10 GB budget but is tight.

---

## 4. Estimate versus reality

The only model I have installed is a small one, `qwen2.5:1.5b`, pulled for this exercise (986 MB). The readings are in `screenshots/02` and `screenshots/03` and in `results/estimate_vs_reality.md`.

| Model | ollama list size | ollama ps size | Processor | Your estimate (weights / total) |
|---|---|---|---|---|
| qwen2.5:1.5b | 986 MB (0.96 GB) | 1.2 GB | 100% CPU | 0.85 GB / 1.20 GB at 8K context (1.07 GB at 4K) |

The estimate was **close**. The on-disk size is 0.96 GB against my 0.85 GB weights estimate, about 0.11 GB or 13% higher, which agrees with the pattern I saw in section 1.1 (the formula is a little low on weights). `ollama ps` shows 1.2 GB, with a context of 4096, against my 1.07 GB estimate for a 4K context. The 8K estimate (1.20 GB) happens to match numerically, but that is partly a coincidence, because Ollama actually loaded 4096 tokens, not 8K. Taking the 4K figure as the fair comparison, the gap is about 0.13 GB, nearly the same size as the weights gap (0.11 GB), so most of the difference seems to come from the weights being heavier than 0.57 bytes per parameter rather than from the cache or overhead. Other causes that could matter on other models are the quantization label of the build, the default context, runtime buffers and the model architecture.

The processor column reads **100% CPU**, meaning that no layer is on a GPU. For my scenario this has two consequences. First, the whole model and its cache live in system RAM, so the 16 GB (10 GB usable) budget is the right one to measure against. Second, generation speed on a CPU is limited mainly by how fast the weights can be read from RAM for every token, so a larger model is slower roughly in proportion to its size: the 8B model reads about 5 times as many bytes per token as this 1.5B model (4.6 to 5.2 GB against about 1 GB), so I should expect roughly a fifth of its speed. This is my reasoning, not a measurement; I will test it with `ollama run qwen3:8b --verbose` and report the real tokens per second. This matters because an agent makes many model calls per task.

---

## 5. Suitability analysis

**Recommendation: Qwen3-8B, Q4_K_M, 8K context (16K as a ceiling), Apache License 2.0.** The estimate is 6.58 GB at 8K, which sits inside the comfortable band of my 10 GB usable budget (the Ollama download is 5.2 GB), and about 8.0 GB at 16K, which still fits but tightly. Its card documents tool calling, which the assistant needs, and its licence is Apache 2.0, so the public demonstration and any later commercial use need no permission. The context observations tell me how to run it: keep the working context near 8K and handle long PDFs by splitting them into chunks and summarising chunk by chunk, instead of loading a whole report, because the memory cost of the KV cache grows with every token. The native context of 32K (131K only with YaRN, which the card says may hurt quality on shorter inputs) is more than I can afford in memory anyway.

**Runner-up: Granite 4.0 Micro (3B), Q4_K_M.** It needs only about 2.4 GB, supports a 128K context, lists tool calling and is also Apache 2.0, and it would be much faster on my CPU. I rejected it as the main model because at 3B I expect weaker reasoning and weaker tool-argument accuracy than an 8B model, and quality of tool calls is the part of the task I care about most; I would still keep it as a fast fallback. I rejected Mistral-7B v0.3 because its tool calling is older and it has a shorter context for no memory advantage, Qwen3-14B because 11.88 GB does not fit in my usable budget, gpt-oss-20b because the file alone nearly fills the whole 16 GB, and Ministral-8B on licence grounds.

**What would change the recommendation.** More memory (for example 32 GB, or a GPU with 12 GB or more of VRAM) would move me to Qwen3-14B at Q4_K_M, or to gpt-oss-20b for its speed. A need for very long documents in one pass would move me toward Granite 4.0, whose hybrid design grows more slowly with context, or toward a bigger machine. A commercial release changes nothing among the Apache 2.0 models, but it would rule out any research-only or custom-licence model. A requirement for dependable tool calling would make me run my own agent tests on the 8B and 3B models before settling, because model cards describe capability, not reliability.

---

## 6. Conclusion – when each factor should decide

The four factors play different roles, and I now think of them as two gates and two dials. **Licence** and **size** are gates: a model that is not permitted, or that cannot be loaded, is out whatever its quality. **Quantization** and **context length** are dials that I turn to get a model that passes the memory gate into the budget.

**Licence should decide** whenever the model leaves my own hands. A start-up that ships a product, a public GitHub project like this one, or a company that redistributes a fine-tuned model must start from the licence, because Mistral-7B (Apache 2.0) and Ministral-8B (research licence) are almost the same size and the first is usable in a product while the second needs a separate agreement. A student doing private coursework can relax this, and for a purely internal teaching server a research-only licence may be acceptable if its terms say so.

**Size (memory) should decide** when the hardware is fixed and small: a phone, an 8 GB laptop with no GPU, or a shared lab machine. There the question is which parameter count fits at all, and the 8B model's 6.4 GB estimate on an 8 GB machine leaves almost nothing for the operating system, so a 3B or 4B model is the honest answer however good a larger one is.

**Quantization should decide** at the margin: when a model nearly fits, a lower precision can bring it in at a modest quality cost, and when two options use about the same memory (a 14B at Q4 against an 8B at Q8) the comparison is really about which quantization is acceptable, which only a test on the real task can settle.

**Context length should decide** for anything that keeps accumulating text: agents that collect tool results, document question-answering, and multi-user servers where every simultaneous session carries its own cache. There a model that looks small on paper can be the wrong choice, and a hybrid or sliding-window design, a shorter working context, or chunking is worth more than extra parameters.

In short: check the licence first, check memory second at the context you really need, use quantization and context to make the model fit, and only then choose among the survivors by quality and features such as tool calling. And because every number here is an estimate made on a particular day from a particular card, the final step is always to run the model and measure.

---

## Appendix – how to reproduce

```
python run_all.py                 # estimator for 10 GB and 16 GB, scenario table, context/quant study
python vram_estimate.py --available 16
python scenario_estimates.py
python context_quant_study.py
python check_reality.py           # needs a model loaded: ollama run qwen2.5:1.5b in a second terminal
```
Outputs are written to `results/`; screenshots are in `screenshots/`.
