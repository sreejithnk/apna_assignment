## 4.1 Measurement Status

Latency benchmarking using **vLLM** / **text-generation-inference** could not be completed due to GPU and environment constraints in Kaggle.

### Constraints Encountered:

- **Kaggle GPUs (P100 / T4)** do not expose `libcuda.so` required for FlashAttention / FlashInfer JIT compilation
- **vLLM engine initialization** failed consistently during kernel warm-up and KV cache setup
- **Unable to measure** TTFT, tokens/sec, and p50 / p95 latency at concurrency levels 1 / 8 / 32 reliably

---

## 4.2 Expected Performance (Reasoned)

- **LoRA fine-tuning** does not materially change model size
- **Expected latency delta:** Within ~3–5% of the base model

---

## 4.3 Proposed Improvements

### 1. **4-bit Quantization**
- Reduces memory footprint and KV cache pressure
- Improves TTFT and supported concurrency

### 2. **Prompt Shortening + Stop Tokens**
- Removes few-shot examples and redundant text
- Reduces prompt tokens → faster TTFT and more stable JSON completion

---

## 4.4 Production Benchmarking Note

With production infrastructure (e.g., **A100/L4 GPU**, precompiled kernels), **vLLM with continuous batching** would enable accurate TTFT and throughput measurement under realistic concurrency.