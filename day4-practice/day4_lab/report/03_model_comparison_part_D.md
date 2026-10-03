# Part D – Compare Four Model Cards

**Date looked: 3 October 2026.** Compiled from the model cards and their mirrors. Before you submit, open each Hugging Face
card and Ollama page yourself, confirm every cell marked (verify) and write your own date. Model cards and licences change.

## 9.1 Comparison worksheet
| What to record | Model 1 | Model 2 | Model 3 | Model 4 |
|---|---|---|---|---|
| Full model name and version | Qwen3-8B | Mistral-7B-Instruct-v0.3 | Granite 4.0 Micro (family: granite-4.0) | gpt-oss-20b |
| Publisher | Alibaba (Qwen team) | Mistral AI (France) | IBM | OpenAI |
| Sizes available | 0.6B, 1.7B, 4B, 8B, 14B, 32B dense; 30B-A3B and 235B-A22B MoE (verify) | 7B on Ollama (family also has Ministral 3B/8B and larger models) | 3B (Micro / H-Micro), 7B (H-Tiny), 32B (H-Small) (verify) | 20B and 120B |
| Size you would use | 8B (or 4B on 8 GB) | 7B | 3B Micro | 20B |
| Total / active parameters (MoE?) | 8.2B / 8.2B, dense | 7.25B / 7.25B, dense | 3B / 3B dense (Micro); H-Small is 32B total / 9B active hybrid MoE | 21B total / 3.6B active, MoE |
| Context window | 32,768 native; 131,072 with YaRN | 32K | 128K validated (trained on up to 512K samples) | 131,072 (128K) |
| Licence (exact name) | Apache License 2.0 | Apache License 2.0 | Apache License 2.0 | Apache License 2.0 |
| Commercial use allowed? | Yes | Yes | Yes | Yes |
| Any extra conditions? | Standard Apache 2.0 only: keep licence and notices, state changes | Standard Apache 2.0 only (note: Ministral 8B from the same publisher is NOT Apache) | Standard Apache 2.0; checkpoints are cryptographically signed | Apache 2.0 with OpenAI's gpt-oss usage policy attached (verify on the card) |
| Tool calling stated on the card? | Yes (function-calling guide; tool-call parsing documented) | Yes (v0.3 adds function calling) | Yes (stated as a core, enhanced capability) | Yes (function calling, browsing, Python execution, structured outputs) |
| GGUF / Ollama build available? | Yes (`qwen3`) | Yes (`mistral`, tagged tools) | Yes (`granite4`) | Yes (`gpt-oss:20b`) |
| Download size at Q4 (Ollama) | about 5.2 GB (verify) | 4.4 GB (as listed on Ollama) | about 2 GB (verify) | about 14 GB, native MXFP4 (verify) |
| Your memory estimate (total, 8K ctx, Q4_K_M) | 6.58 GB | 5.82 GB | 2.41 GB | 16.86 GB (formula overestimates: see note) |
| Runs on your machine? (Y/N) | 8 GB: Y, tight / 16 GB: Y | 8 GB: Y, tight / 16 GB: Y | Y on both | 8 GB: N / 16 GB: only just (card says 16 GB) / 24 GB: Y |

Note on gpt-oss: it is a mixture-of-experts model, so the memory is set by the 21B TOTAL parameters (all experts must be loaded),
while the speed is set by the 3.6B ACTIVE parameters. The KV term of the lab formula is a guess based on parameter count,
and for this model it is too high because its attention layers are partly sliding-window; trust the Ollama page size (about 14 GB) more than the formula.

Fill in "Runs on your machine?" with your own RAM before submitting.

## 9.2 Licence questions

**4. Did two sizes within one family have different licences?**
Yes, in the Mistral family: Mistral-7B-Instruct-v0.3 is Apache 2.0, but Ministral-8B-Instruct-2410 is released under the Mistral Research License,
and its card tells you to contact Mistral for commercial use. (From my memory of the Qwen2.5 generation, the 3B and 72B sizes also
had licences other than Apache 2.0, while Qwen3 is Apache 2.0 throughout. Verify this on the cards before writing it in your report.)

**5. Which of the four could you use in a product you sell without asking anyone?**
All four, because all four are Apache 2.0 (Qwen3-8B, Mistral-7B v0.3, Granite 4.0, gpt-oss-20b). Apache 2.0 allows commercial use, modification and
redistribution with no royalties. You still must ship the licence text and notices and mark any changes you make. For gpt-oss also read its usage policy.

**6. Which has conditions attached, and what exactly are they?**
Of my four, none beyond standard Apache 2.0 terms (the obligations above, plus the patent-termination clause) and gpt-oss's accompanying usage policy.
The model with real conditions in this family is Ministral-8B (Mistral Research License): research and non-commercial use; commercial use needs a separate licence from Mistral.
**Action for you:** open the LICENSE file in the repository and copy the exact clause here, in quotation marks:
"_________________________________________".

**7. Which cards mention tool calling explicitly, and which stay silent?**
All four mention it: Granite and gpt-oss state it as a headline feature, Mistral v0.3 states function calling as the new feature of that version
(Ollama marks it with the `tools` tag and its page documents a raw-mode prompt format), and Qwen3 documents tool calling in its deployment guides.
No card of the four is silent. Quality differs, though: IBM and OpenAI position the feature as core, so I would test Mistral v0.3 and Qwen3 tool calls more carefully with your Unit 1 agent.

**8. Which card gives the most honest account of limitations?**
In my reading, the Qwen3 card. It says the native context is 32K, that the 131K setting uses YaRN, that YaRN is applied statically
in common frameworks and can therefore hurt performance on shorter texts, and it advises enabling it only when you need long inputs.
gpt-oss is also candid that its chain of thought is not meant to be shown to end users. This raises my trust in Qwen3: a card that tells me when NOT to use a feature is one I can plan around.
(Change this if your own reading of the cards differs.)
