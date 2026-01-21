## 5.1 Serving Architecture

### Proposed Architecture

```
Client
  ↓
Async API (FastAPI)
  ↓
vLLM Inference Engine
  ↓
Fine-tuned LLM (LoRA adapters)
```

### Key Characteristics

- **Async request handling**
- **Continuous batching** (vLLM)
- **Single model instance** serving multiple requests
- **LoRA adapters** loaded on top of base model

### Output Validation Pipeline

A JSON schema validator runs post-generation to:
- Reject invalid outputs
- Enforce schema correctness before returning responses

---

## 5.2 Quality Gates

The following quality thresholds would be enforced before deployment:

| Metric | Threshold |
|--------|-----------|
| JSON validity rate | ≥ 99% |
| Script compliance (Devanagari / Latin) | ≥ 97% |
| Slot F1 / exact match | ≥ 85% |
| Empty / hallucinated fields | ≤ 2% |

### Handling Validation Failures

Requests failing validation:
- Are logged (PII-safe)
- Do not reach downstream systems

---

## 5.3 Data Flywheel & Continuous Improvement

### Logging (PII-safe)

Log only:
- Normalized input text
- Validation errors (JSON / script / schema)
- **No raw personal data stored**

### Active Learning Triggers

- JSON parsing failures
- Script violations (Latin → Hindi / Devanagari → English)
- New unseen entity patterns

### Release Process

- Regression test suite on stress cases
- Schema compatibility checks
- Canary rollout before full deployment