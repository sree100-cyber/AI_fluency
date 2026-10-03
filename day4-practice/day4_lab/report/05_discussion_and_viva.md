# Discussion Questions and Viva – model answers

## Discussion
1. **Weights never change, yet it stops fitting.** Think of weights as the textbook, which is always the same size, and the context as your notebook,
   which grows as the conversation goes on. The model keeps a KV cache for every token it has seen. A longer conversation means more cache, so total memory
   rises while the weights stay fixed, until the total passes the memory you have.
2. **14B at Q4 or 8B at Q8?** Their weights are about the same (14x0.57 = 7.98 GB vs 8x1.00 = 8 GB) but the 14B also has a larger KV cache. A larger model at Q4 is usually
   better than a smaller one at Q8, but I would test: (a) my own Unit 1 tasks and tool-call success rate, (b) tokens per second, (c) the context length I need, (d) whether both fit with that context.
3. **Estimate vs `ollama ps` disagree (not arithmetic):** (a) Ollama loads a smaller default context than I assumed; (b) the real KV cache depends on the architecture
   (grouped-query attention, sliding windows, KV quantization), not on parameter count; (c) some layers (embeddings, output) are stored at higher precision and the file differs from the nominal
   quantization; (d) MoE or partial GPU offload splits memory between VRAM and RAM; (e) runtime buffers differ.
4. **Open card, non-commercial licence.** Not useless: it is fine for learning, research and internal teaching. Of today's scenarios it could serve the department server (internal, non-commercial teaching),
   provided the licence allows it. It fails scenario 1 (needs Apache/MIT) and is risky for scenario 3 (public redistribution needs clear terms).
5. **Free cloud key for a 20B model, what you lose:** privacy (your prompts leave the machine), offline use, control over the exact version (the provider can change or retire it),
   and reliability (rate limits, outages). Also no hands-on understanding of memory limits.

## Viva
1. weights = B x bytes/param; KV = B x context(K) x 0.02; total = (weights + KV) x 1.10.
2. Q4_K_M: 0.57 bytes per parameter; FP16: 2.00 bytes per parameter.
3. The KV cache stores keys and values for every token in the context; it grows with the number of tokens, while weights are a fixed set of learned numbers.
4. M = "medium": the k-quant family mixes block types, with S (small), M (medium) and L (large) variants that trade size against quality.
5. Apache 2.0 and MIT: both allow commercial use, modification and redistribution without royalties and without asking permission (Apache 2.0 also gives an explicit patent grant).
6. Example condition from community licences (Llama): a company above a very large number of monthly active users must request a separate licence; also attribution and an acceptable-use policy.
7. A 30B MoE with 3B active still needs memory for ALL 30B parameters (about 17 GB at Q4_K_M), because any expert may be chosen for any token. Only the compute and speed are those of a 3B model.
8. 8 GB: choose a 4B model, or an 8B at Q3/Q4 only with a short context, because long documents inflate the KV cache. Better still, use retrieval or chunking to keep the live context at 4K to 8K, and prefer a model with a hybrid architecture such as Granite 4.0 Micro-H whose memory grows less with context.

## 15. Result (fill in the blank)
The observations show that the weights of a model set only the floor of its memory need, that the context length and the quantization decide whether it fits,
and that the licence, not the size, decides where a model may be used.
