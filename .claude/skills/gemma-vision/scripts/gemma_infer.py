#!/usr/bin/env python3
"""
Run image analysis using google/gemma-4-E4B-it.

Usage:
  # Local model
  python gemma_infer.py --image path/to/image.jpg --prompt "Describe this image"

  # API endpoint (Ollama, vLLM, LM Studio, etc.)
  python gemma_infer.py --image path/to/image.jpg --prompt "..." --endpoint http://localhost:11434

  # Batch mode
  python gemma_infer.py --batch ./images/ --prompt "Describe this image" --output results.json
"""
import argparse
import base64
import json
import sys
import time
from pathlib import Path


MODEL_ID = "google/gemma-4-E4B-it"


def load_image_as_url(path_or_url: str) -> str:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    path = Path(path_or_url)
    if not path.exists():
        print(f"[ERROR] Image not found: {path_or_url}", file=sys.stderr)
        sys.exit(1)
    suffix = path.suffix.lower().lstrip(".")
    mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif", "webp": "webp"}.get(suffix, "jpeg")
    data = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/{mime};base64,{data}"


def infer_local(image_url: str, prompt: str) -> tuple[str, float]:
    from transformers import pipeline

    print(f"[INFO] Loading {MODEL_ID} (first run downloads ~3GB)...", file=sys.stderr)
    t0 = time.time()
    pipe = pipeline(
        task="image-text-to-text",
        model=MODEL_ID,
        device_map="auto",
    )
    load_time = time.time() - t0
    print(f"[INFO] Model loaded in {load_time:.1f}s", file=sys.stderr)

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "url": image_url},
                {"type": "text", "text": prompt},
            ],
        }
    ]

    t1 = time.time()
    output = pipe(messages, max_new_tokens=1024)
    infer_time = time.time() - t1
    print(f"[INFO] Inference time: {infer_time:.2f}s", file=sys.stderr)

    # Extract text from output
    result = output[0] if isinstance(output, list) else output
    if isinstance(result, dict):
        text = result.get("generated_text", str(result))
    else:
        text = str(result)

    # Strip the input messages if echoed back
    if isinstance(text, list):
        for msg in reversed(text):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                content = msg.get("content", "")
                if isinstance(content, list):
                    text = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
                else:
                    text = str(content)
                break

    return str(text), infer_time


def infer_endpoint(endpoint: str, image_url: str, prompt: str) -> tuple[str, float]:
    import urllib.request

    # Detect endpoint type
    if "ollama" in endpoint or ":11434" in endpoint:
        return _infer_ollama(endpoint, image_url, prompt)
    else:
        return _infer_openai_compat(endpoint, image_url, prompt)


def _infer_ollama(endpoint: str, image_url: str, prompt: str) -> tuple[str, float]:
    import urllib.request

    base = endpoint.rstrip("/")
    payload = {
        "model": "gemma4:4b",
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [image_url.split(",", 1)[-1] if "base64," in image_url else image_url],
            }
        ],
        "stream": False,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(f"{base}/api/chat", data=data, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    elapsed = time.time() - t0
    text = result.get("message", {}).get("content", str(result))
    return text, elapsed


def _infer_openai_compat(endpoint: str, image_url: str, prompt: str) -> tuple[str, float]:
    import urllib.request

    base = endpoint.rstrip("/")
    payload = {
        "model": MODEL_ID,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        "max_tokens": 1024,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{base}/v1/chat/completions",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
    elapsed = time.time() - t0
    text = result["choices"][0]["message"]["content"]
    return text, elapsed


def process_single(image: str, prompt: str, endpoint: str | None) -> dict:
    image_url = load_image_as_url(image)
    if endpoint:
        print(f"[INFO] Using endpoint: {endpoint}", file=sys.stderr)
        text, elapsed = infer_endpoint(endpoint, image_url, prompt)
    else:
        text, elapsed = infer_local(image_url, prompt)
    return {"image": image, "prompt": prompt, "result": text, "inference_seconds": round(elapsed, 2)}


def main():
    parser = argparse.ArgumentParser(description="Gemma 4 E4B image analysis")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image", help="Path or URL to a single image")
    group.add_argument("--batch", help="Directory of images to process")
    parser.add_argument("--prompt", required=True, help="Analysis prompt")
    parser.add_argument("--endpoint", help="API endpoint URL (Ollama, vLLM, LM Studio)")
    parser.add_argument("--output", help="Write results as JSON to this file")
    args = parser.parse_args()

    if args.image:
        result = process_single(args.image, args.prompt, args.endpoint)
        print(result["result"])
        if args.output:
            Path(args.output).write_text(json.dumps([result], indent=2))
    else:
        batch_dir = Path(args.batch)
        extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        images = [p for p in batch_dir.iterdir() if p.suffix.lower() in extensions]
        if not images:
            print(f"[ERROR] No images found in {args.batch}", file=sys.stderr)
            sys.exit(1)
        print(f"[INFO] Processing {len(images)} images...", file=sys.stderr)
        results = []
        for i, img in enumerate(sorted(images), 1):
            print(f"[INFO] [{i}/{len(images)}] {img.name}", file=sys.stderr)
            r = process_single(str(img), args.prompt, args.endpoint)
            results.append(r)
            print(f"--- {img.name} ---\n{r['result']}\n")
        if args.output:
            Path(args.output).write_text(json.dumps(results, indent=2))
            print(f"[INFO] Results saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
