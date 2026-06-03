---
name: gemma-vision
description: >
  Run image analysis using Google's Gemma 4 E4B model (google/gemma-4-E4B-it)
  locally via Hugging Face Transformers or a compatible API endpoint. Use this
  skill when the user wants to run image analysis offline, on edge hardware,
  without the Anthropic API, or explicitly asks to use Gemma. Also use when
  the user mentions: "run locally", "no API", "edge device", "Gemma vision",
  "gemma image", "offline image analysis", "Raspberry Pi vision",
  "gemma 4 E4B", "local image analysis", "edge image analysis",
  "analyze image with gemma".
---

# Gemma Vision Skill

You are helping the user run image analysis using `google/gemma-4-E4B-it`,
Google's efficient 4B multimodal model, either locally or via an API endpoint.

## Step 1 — Determine runtime

Ask the user (or infer from context) which runtime to use:

| Option | Description |
|--------|-------------|
| **Local (Transformers)** | Run on this machine via `pip install transformers` |
| **API endpoint** | Gemma served via Ollama, vLLM, LM Studio, or similar |
| **Google AI Studio** | Use the hosted Gemma 4 via Google's API |

If not stated, assume **local Transformers** and proceed — the script handles
the check.

## Step 2 — Check environment

Run the environment check script:

```bash
python3 .claude/skills/gemma-vision/scripts/check_env.py
```

This script verifies:
- Python ≥ 3.10
- `transformers` ≥ 5.5.0 installed
- `torch` installed
- Available VRAM / RAM (E4B needs ~4–5GB VRAM (Q4 quantized) or ~5GB+ RAM for CPU)
- Whether the model is already cached locally

If the environment check fails, output the exact install commands needed.

## Step 3 — Run inference

Use the inference script with the user's image and prompt:

```bash
python3 .claude/skills/gemma-vision/scripts/gemma_infer.py \
  --image "<path_or_url>" \
  --prompt "<user's question or analysis goal>" \
  [--endpoint "<url>"]  # optional: use an API endpoint instead of local model
```

### Script behavior
- If `--endpoint` is provided: sends a multimodal chat request to that URL
- If no endpoint: loads `google/gemma-4-E4B-it` from Hugging Face cache (or
  downloads on first run — ~5–15GB depending on quantization)
- Outputs the model's response to stdout
- Prints inference time and token count to stderr

## Step 4 — Present results

Format the output:

```
## Gemma 4 E4B — Image Analysis

**Image:** [filename or URL]
**Prompt:** [what was asked]
**Runtime:** [Local Transformers | API endpoint | Google AI Studio]
**Inference time:** [X.Xs]

---

[Model output here]

---

### Notes
- Model: google/gemma-4-E4B-it
- E4B is optimized for speed over depth; for complex reasoning consider Claude
- First run downloads ~5–15GB of model weights (Q4_K_M≈5.4GB, BF16≈15GB)
```

## Step 5 — Offer follow-up

After analysis, offer:
1. Run again with a different/more specific prompt
2. Batch process multiple images (use `--batch` flag with a directory path)
3. Switch to Claude's native vision for deeper reasoning on the same image

## Limitations to communicate

- E4B is fast but trades reasoning depth for efficiency
- First load takes 30–60 seconds (model loading); subsequent runs are fast
- CPU inference is ~10–30x slower than GPU
- The model cannot identify real people by face
- For production use, consider a persistent server (Ollama, vLLM) over
  one-shot subprocess calls

## Reference: Key Gemma 4 E4B facts

- Parameters: 4B effective (MatMul-Free efficient architecture)
- Context: 128K tokens
- Image input: variable aspect ratios, up to 896×896 per tile
- Audio: supported natively (E2B and E4B models)
- Quantization: Q4_K_M recommended for ≤6GB VRAM (~5.4GB); BF16 full precision needs ~15GB
- License: Gemma Terms of Service (commercial use allowed with restrictions)
- HuggingFace: `google/gemma-4-E4B-it`
