"""
Download and benchmark models using Modal. Run from the root of the
repository.

Usage:
    modal run utils/app.py::run_model --model-id facebook/opt-125m

If you would like to debug either function in isolation, you can run
the functions separately:

    modal run utils/app.py::download_model --model-id facebook/opt-125m
    modal run utils/app.py::benchmark_model --model-id facebook/opt-125m
"""

import warnings
import modal

download_image = (
    modal.Image.debian_slim()
        .pip_install(["transformers", "torch", "accelerate", "bitsandbytes", "tabulate"])
        .add_local_python_source("fasthug")
)

test_image = (
    modal.Image.debian_slim()
        .pip_install(["transformers", "torch", "accelerate", "bitsandbytes", "tabulate", "pytest"])
        .add_local_python_source("fasthug")
        .add_local_dir("./tests", remote_path="/model/tests")
)

MODAL_CACHE_DIR = "/models/cache"

def _quantized_path(model_id: str, cache_dir: str=MODAL_CACHE_DIR) -> str:
    """Return path for storing an 8bit checkpoint for ``model_id``."""
    safe_id = model_id.replace("/", "--")
    return f"{cache_dir}/{safe_id}-8bit"

app = modal.App()

@app.function(
    timeout=1800,
    image=download_image,
    volumes={"/models": modal.Volume.from_name("model-vol", create_if_missing=True)}
)
def download_model(model_id: str):
    """Download a model to the modal volume."""
    from fasthug import download_model

    download_model(model_id, cache_dir=MODAL_CACHE_DIR)


@app.function(
    timeout=1800,
    gpu="T4",  # cheap GPU for quantization
    image=download_image,
    volumes={"/models": modal.Volume.from_name("model-vol", create_if_missing=True)}
)
def save_8bit_checkpoint(model_id: str, cache_dir: str = MODAL_CACHE_DIR):
    """Save an 8bit quantized checkpoint to the modal volume."""
    from fasthug import from_pretrained
    from transformers.utils.quantization_config import BitsAndBytesConfig

    model = from_pretrained(
        model_id,
        quantization_config=BitsAndBytesConfig(load_in_8bit=True),
        cache_dir=cache_dir,
    )
    model.save_pretrained(_quantized_path(model_id, cache_dir=cache_dir))
    

@app.function(
    gpu="H100",
    timeout=900,
    image=download_image,
    volumes={"/models": modal.Volume.from_name("model-vol")}
)
def benchmark_model(
    model_id: str,
    device: str | None = None,
    warmup: int = 2,
    num_trials: int = 3,
    load_in_8bit: bool = False,
    load_in_4bit: bool = False,
    quantization_config: str | None = None,
):
    """Benchmark loading a model with and without ``load_weights_fast``."""
    from fasthug import benchmark
    from fasthug.bench import create_quantization_config
    
    quantization_config = create_quantization_config(
        load_in_4bit=load_in_4bit,
        load_in_8bit=load_in_8bit,
        quantization_config=quantization_config,
    )

    benchmark(
        model_id,
        device=device,
        warmup=warmup,
        num_trials=num_trials,
        cache_dir=MODAL_CACHE_DIR,
        quantization_config=quantization_config,
    )


@app.local_entrypoint()
def run_model(
    model_id: str,
    device: str | None = None,
    warmup: int = 2,
    num_trials: int = 3,
    load_in_8bit: bool = False,
    load_in_4bit: bool = False,
    quantization_config: str | None = None,
    use_8bit_checkpoint: bool = False,
):
    # TODO: simplify me. externalize?
    if use_8bit_checkpoint and load_in_8bit:
        warnings.warn(
            "--load-in-8bit is ignored when --use-8bit-checkpoint is set"
        )
        
    download_model.remote(model_id)
    if use_8bit_checkpoint:
        save_8bit_checkpoint.remote(model_id, cache_dir=MODAL_CACHE_DIR)
        quant_path = _quantized_path(model_id, cache_dir=MODAL_CACHE_DIR)
        benchmark_model.remote(
            quant_path,
            device=device,
            warmup=warmup,
            num_trials=num_trials,
            load_in_8bit=True,
        )
    else:
        benchmark_model.remote(
            model_id,
            device=device,
            warmup=warmup,
            num_trials=num_trials,
            load_in_8bit=load_in_8bit,
            load_in_4bit=load_in_4bit,
            quantization_config=quantization_config,
        )


@app.function(
    image=test_image,
    timeout=1800,
    gpu="T4",  # cheap GPU
)
def run_tests(test_dir: str = "/model/tests"):
    """Run pytest on the baked-in tests directory."""
    import pytest
    
    exit_code = pytest.main([test_dir, "-q"])
    if exit_code != 0:
        raise RuntimeError(f"❌ Tests failed (exit code {exit_code})")
    print("✅ Tests passed!")