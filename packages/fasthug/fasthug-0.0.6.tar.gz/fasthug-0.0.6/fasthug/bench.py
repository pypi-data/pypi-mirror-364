from __future__ import annotations

import time

import torch
from typing import Callable
from transformers import AutoModelForCausalLM
from transformers.utils.hub import TRANSFORMERS_CACHE
from transformers.utils.quantization_config import BitsAndBytesConfig
import json
import fasthug
from tabulate import tabulate


def _choose_device(device: str | None) -> str:
    """Return the device to use for benchmarking."""
    if device in (None, "none"):
        if torch.cuda.is_available():
            return "cuda"
        elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    return device


def _run(
    model_id: str, from_pretrained: Callable, device: str, **kwargs
) -> tuple[float, float]:
    """Return load time (s) and peak memory usage (MiB) for ``from_pretrained``."""

    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()

    t0 = time.perf_counter()
    model = from_pretrained(model_id, **kwargs)
    if not kwargs.get('quantization_config'):
        model = model.to(device)
    elapsed = time.perf_counter() - t0

    peak_mem = (
        torch.cuda.max_memory_allocated() / 1024**2 if device == "cuda" else 0.0
    )

    del model
    return elapsed, peak_mem


def create_quantization_config(
    load_in_4bit: bool = False,
    load_in_8bit: bool = False,
    quantization_config: str | None = None,
) -> BitsAndBytesConfig:
    if not load_in_4bit and not load_in_8bit and not quantization_config:
        return None

    cfg = {
        "load_in_4bit": load_in_4bit,
        "load_in_8bit": load_in_8bit,
    }
    if quantization_config:
        with open(quantization_config) as f:
            cfg.update(json.load(f))
    quantization_config = BitsAndBytesConfig.from_dict(cfg)
    return quantization_config


def benchmark(model_id: str, device: str | None = None, warmup: int = 2, num_trials: int = 3, **kwargs) -> None:
    """Benchmark loading a model with and without ``load_weights_fast``.

    If ``device`` is ``None`` or ``"none"``, the fastest available device is
    selected in the order ``cuda`` → ``mps`` → ``cpu``.
    """
    device = _choose_device(device)
    print(f"Benchmarking: {model_id=}, {device=}, {warmup=}, {num_trials=}")
    
    # Ensure model weights are downloaded before benchmarking
    fasthug.download_model(model_id, cache_dir=kwargs.get("cache_dir", TRANSFORMERS_CACHE))
    
    hf_times: list[float] = []
    hf_mems: list[float] = []
    fast_times: list[float] = []
    fast_mems: list[float] = []
    
    print("-------------------  -------------------")
    print("Huggingface          Fastload")
    print("Time (s)  Mem (MiB)  Time (s)  Mem (MiB)")
    print("--------  ---------  --------  ---------")
    for _ in range(warmup + num_trials):
        t_hf, m_hf = _run(
            model_id,
            AutoModelForCausalLM.from_pretrained,
            device,
            low_cpu_mem_usage=True,
            **kwargs,
        )
        hf_times.append(t_hf)
        hf_mems.append(m_hf)
        t_fast, m_fast = _run(model_id, fasthug.from_pretrained, device, **kwargs)
        fast_times.append(t_fast)
        fast_mems.append(m_fast)
        print(f"{t_hf:8g}  {m_hf:9g}  {t_fast:8g}  {m_fast:9g}")

    def _stats(times: list[float]) -> tuple[float, float]:
        _times = times[warmup:]
        mean = sum(_times) / len(_times)
        std = (sum((t - mean) ** 2 for t in _times) / len(_times)) ** 0.5
        return mean, std

    hf_mean, hf_std = _stats(hf_times)
    fast_mean, fast_std = _stats(fast_times)
    hf_max_mem = max(hf_mems[warmup:], default=0.0)
    fast_max_mem = max(fast_mems[warmup:], default=0.0)

    print(f"\nSummary: ({model_id=}, {device=}, {warmup=}, {num_trials=})\n")
    table = [
        ["huggingface", f"{hf_mean:.2f} ± {hf_std:.2f}", f"{hf_max_mem:.2f}"],
        ["fasthug", f"{fast_mean:.2f} ± {fast_std:.2f}", f"{fast_max_mem:.2f}"],
    ]
    print(tabulate(table, headers=["Method", "Load (s)", "Peak Mem (MiB)"]))