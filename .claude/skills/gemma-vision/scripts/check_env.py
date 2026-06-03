#!/usr/bin/env python3
"""Environment check for Gemma 4 E4B vision inference."""
import sys
import subprocess
import shutil

REQUIRED_TRANSFORMERS = (5, 5, 0)
MIN_RAM_GB = 5
MIN_VRAM_GB = 4


def check_python():
    major, minor = sys.version_info[:2]
    ok = (major, minor) >= (3, 10)
    status = "OK" if ok else "FAIL"
    print(f"[{status}] Python {major}.{minor} (need >=3.10)")
    return ok


def check_package(name, min_version=None):
    try:
        pkg = __import__(name)
        version = getattr(pkg, "__version__", "unknown")
        if min_version and version != "unknown":
            parts = tuple(int(x) for x in version.split(".")[:3])
            ok = parts >= min_version
        else:
            ok = True
        status = "OK" if ok else "FAIL"
        req = f">={'.'.join(str(x) for x in min_version)}" if min_version else ""
        print(f"[{status}] {name} {version} {req}")
        return ok
    except ImportError:
        print(f"[FAIL] {name} not installed — run: pip install {name}")
        return False


def check_ram():
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / 1e9
        ok = ram_gb >= MIN_RAM_GB
        status = "OK" if ok else "WARN"
        print(f"[{status}] RAM: {ram_gb:.1f}GB (need >={MIN_RAM_GB}GB for CPU inference)")
        return ok
    except ImportError:
        print("[SKIP] psutil not installed — skipping RAM check")
        return True


def check_vram():
    try:
        import torch
        if torch.cuda.is_available():
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            ok = vram_gb >= MIN_VRAM_GB
            name = torch.cuda.get_device_name(0)
            status = "OK" if ok else "WARN"
            print(f"[{status}] GPU: {name} — {vram_gb:.1f}GB VRAM (need >={MIN_VRAM_GB}GB)")
            return ok
        else:
            print(f"[WARN] No CUDA GPU found — will use CPU (slow)")
            return True
    except Exception as e:
        print(f"[WARN] Could not check VRAM: {e}")
        return True


def check_model_cache():
    import os
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    model_id = "models--google--gemma-4-E4B-it"
    cached = os.path.exists(os.path.join(cache_dir, model_id))
    status = "OK" if cached else "INFO"
    msg = "model cached locally" if cached else "not cached — first run will download ~5–15GB depending on quantization (Q4_K_M≈5.4GB, BF16≈15GB)"
    print(f"[{status}] google/gemma-4-E4B-it: {msg}")
    return True


def main():
    print("=== Gemma 4 E4B Environment Check ===\n")
    results = [
        check_python(),
        check_package("transformers", REQUIRED_TRANSFORMERS),
        check_package("torch"),
        check_package("accelerate"),
        check_ram(),
        check_vram(),
        check_model_cache(),
    ]
    print()
    if all(r is not False for r in results):
        print("Environment ready for Gemma 4 E4B inference.")
        sys.exit(0)
    else:
        print("Fix the issues above, then retry.")
        print("\nInstall command:")
        print("  pip install 'transformers>=5.5.0' torch accelerate pillow psutil")
        sys.exit(1)


if __name__ == "__main__":
    main()
