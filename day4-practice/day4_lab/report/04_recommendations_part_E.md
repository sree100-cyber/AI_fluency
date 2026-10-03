# Part E – Recommendations

**1. Student with an 8 GB laptop, no GPU, Unit 1 agent labs.**
We recommend Qwen3-4B (Apache 2.0, 4B dense) at Q4_K_M: the formula gives about 3.2 GB with an 8K context
((4x0.57 + 4x8x0.02) x 1.10), which leaves room for the operating system on a CPU-only 8 GB machine, and the Qwen3 documentation describes function calling,
which the agent labs need. An 8B Apache 2.0 model such as Qwen3-8B at Q4_K_M (6.4 GB at 8K) is the upgrade only if the context is limited to 4K and other programs are closed.
Granite 4.0 Micro (3B, Apache 2.0, about 2.4 GB) is the lightest option that also lists tool calling.

**2. Department server, one 24 GB GPU, 20 students at once.**
We recommend gpt-oss-20b (Apache 2.0, 21B total / 3.6B active, native MXFP4). Its weights take about 14 GB, leaving roughly 10 GB for the KV caches of
the simultaneous sessions, and because only 3.6B parameters are active per token it generates quickly, which matters when 20 people share one GPU.
Cap each session at 8K tokens and limit parallel requests, since context length times users is what fills the remaining memory. A fallback is Qwen3-14B at Q4_K_M
(about 8 GB of weights), which is easier on memory but slower per token. The lab formula is only a guide here: load-test with 20 real sessions before term starts.

**3. Capstone project published on GitHub and demonstrated publicly.**
The licence decides, so we choose from the Apache 2.0 family only. We recommend IBM Granite 4.0 (Apache 2.0, Micro 3B or H-Small 32B-A9B depending on hardware, Q4_K_M),
because its card states the licence plainly with no extra riders, it lists tool calling and 128K context, and its checkpoints are cryptographically signed,
which makes provenance easy to document. Qwen3 is an equally clear alternative. We avoid the Mistral Research License models (such as Ministral-8B)
because their commercial terms are not open, and we include the Apache 2.0 LICENSE and NOTICE files in our repository.
