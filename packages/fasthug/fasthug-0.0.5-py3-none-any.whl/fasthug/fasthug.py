import os
import glob
import warnings
from typing import Any, Optional
import resource

try:
    from bitsandbytes.nn import Int8Params, Linear4bit, Params4bit, Linear8bitLt
    BITSANDBYTES_AVAILABLE = True
except ImportError:
    Int8Params = Linear4bit = Params4bit = Linear8bitLt = None  # type: ignore
    BITSANDBYTES_AVAILABLE = False
import torch
import torch.nn as nn
from accelerate import init_empty_weights
from transformers import AutoConfig, AutoModelForCausalLM
from contextlib import ExitStack
from transformers import pytorch_utils
from transformers.utils.quantization_config import BitsAndBytesConfig
from transformers.utils.hub import TRANSFORMERS_CACHE
from huggingface_hub import snapshot_download
from unittest.mock import patch


INT8_MODULE_PARAMS = (".SCB", ".CB")
INT4_MODULE_PARAMS = (
    ".weight.absmax",
    ".weight.quant_map",
    ".weight.nested_absmax",
    ".weight.nested_quant_map",
    ".weight.quant_state.bitsandbytes__fp4",
)

MAJOR_PAGEFAULT_WARN_THRESHOLD = 1000


def download_model(
    model_id: str,
    cache_dir: str | None = TRANSFORMERS_CACHE,
) -> str:
    """Check for model weights in the cache directory, downloading if necessary.
    
    Download model weights, preferring safetensors format when available.
    """

    def _try_download_model(pattern: str, local_files_only: bool = False) -> str | None:
        """Try downloading model weights with the given pattern.
        
        Pass `local_files_only=True` to only look for files in the cache directory."""
        try:
            cache = snapshot_download(
                model_id,
                cache_dir=cache_dir,
                allow_patterns=[pattern],
                local_files_only=local_files_only,
            )
            files = glob.glob(os.path.join(cache, pattern))
            if files:
                return cache
        except Exception:
            pass
    
    return (
        _try_download_model("*.safetensors", local_files_only=True) or
        _try_download_model("*.bin", local_files_only=True) or
        _try_download_model("*.safetensors") or
        _try_download_model("*.bin")
    )


def find_submodule(model: nn.Module, mod_path: list[str]) -> nn.Module | None:
    """
    Find the submodule corresponding to the parameter or buffer.
    """
    submod = model
    for p in mod_path:
        if not hasattr(submod, p):
            submod = None
            break
        submod = getattr(submod, p)
    return submod


def _warn_if_insufficient_memory(total_bytes: int) -> None:
    """Warn if ``total_bytes`` exceeds available system memory."""
    try:
        import psutil

        mem = psutil.virtual_memory()
        if total_bytes > mem.available:
            warnings.warn(
                "Detected insufficient system memory for memory-mapped loading. "
                "This may cause heavy paging. Consider killing this run and "
                "loading without fasthug."
            )
    except ImportError:
        warnings.warn("psutil is not installed, skipping memory check.")


def get_state_dict_mmap(cache: str) -> dict[str, torch.Tensor]:
    # Handle sharded safetensors and PyTorch bin files
    safetensor_files = sorted(glob.glob(os.path.join(cache, "*.safetensors")))
    bin_files = sorted(glob.glob(os.path.join(cache, "pytorch_model*.bin")))
    files = safetensor_files or bin_files
    if files:
        total_size = sum(os.path.getsize(f) for f in files)
        _warn_if_insufficient_memory(total_size)
    if safetensor_files:
        from safetensors.torch import load_file as _load_safetensors
        state_dict: dict[str, torch.Tensor] = {}
        for file_path in safetensor_files:
            part = _load_safetensors(file_path)
            state_dict.update(part)
    elif bin_files:
        state_dict: dict[str, torch.Tensor] = {}
        for file_path in bin_files:
            part = torch.load(file_path, mmap=True, map_location="cpu")
            state_dict.update(part)
    else:
        raise UserWarning(
            f"Did not find .bin or .safetensors files in {cache}."
        )
    return state_dict


def _Int8Params_from_prequantized(state_dict: dict[str, torch.Tensor], prefix: str):
    local_state_dict = {k.replace(prefix, ''): v for k, v in state_dict.items() if k.startswith(prefix)}
    assert 'SCB' in local_state_dict, \
        f"Are you sure this Linear8bitLt {prefix} is prequantized? It's missing the scales."
    weight = local_state_dict['weight'].cuda()
    SCB = local_state_dict['SCB'].cuda()
    
    new_param = Int8Params(weight, requires_grad=False)
    new_param.SCB = SCB
    new_param.CB = weight
    return new_param


def _Linear8bitLt_load_from_state_dict(self, state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs):
    local_state_dict = {k.replace(prefix, ''): v for k, v in state_dict.items() if k.startswith(prefix)}
    
    assert 'weight' in local_state_dict, f"Linear8bitLt {prefix} is missing weight"
    if 'SCB' in local_state_dict:
        self.weight = _Int8Params_from_prequantized(state_dict, prefix)
    else:
        weight = local_state_dict['weight']
        if getattr(self, '_fasthug_requires_transpose', False):
            weight = weight.T
        self.weight = Int8Params(weight, requires_grad=False)

    if 'bias' in local_state_dict:
        bias = local_state_dict['bias'].cuda()
        self.bias = nn.Parameter(bias, requires_grad=False)


def _Linear4bit_load_from_state_dict(self, state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs):
    local_state_dict = {k.replace(prefix, ''): v for k, v in state_dict.items() if k.startswith(prefix)}
    
    if 'bias' in local_state_dict:
        bias = local_state_dict.pop('bias').cuda()
        self.bias = nn.Parameter(bias, requires_grad=False)

    assert 'weight' in local_state_dict, f"Linear4bit {prefix} is missing weight"
    if len(local_state_dict) > 1:
        weight = local_state_dict.pop('weight').cuda()
        self.weight = Params4bit.from_prequantized(weight, quantized_stats=local_state_dict)
    else:
        weight = local_state_dict.pop('weight')
        if getattr(self, '_fasthug_requires_transpose', False):
            weight = weight.T
        self.weight = Params4bit(
            weight.to(torch.float16),
            requires_grad=False,
            compress_statistics=False,
            quant_type=self.weight.quant_type,
            quant_storage=self.weight.quant_storage,
            module=self,
        )


def _replace_linear_with_bnb(
    Linear: type[nn.Linear],
    model: nn.Module,
    modules: set[str] | None = None,
    prefix: str = "",
    layer_kwargs: dict[str, Any] = {},
) -> nn.Module:
    """
    Replace all linear layers with quantized equivalents.
    
    If ``modules`` is provided, only modules whose dot-separated
    name appears in this set are replaced.
    """
    for name, module in model.named_children():
        full_name = f"{prefix}.{name}" if prefix else name
        if isinstance(module, nn.Embedding):
            continue
        if isinstance(module, nn.Linear) and (modules is None or full_name in modules):
            with init_empty_weights():
                quantized = Linear(
                    module.in_features,
                    module.out_features,
                    bias=module.bias is not None,
                    **layer_kwargs,
                )
            setattr(model, name, quantized)
        elif isinstance(module, pytorch_utils.Conv1D) and (modules is None or full_name in modules):
            with init_empty_weights():
                quantized = Linear(
                    module.nx,
                    module.nf,
                    bias=module.bias is not None,
                    **layer_kwargs,
                )
                quantized._fasthug_requires_transpose = True
            setattr(model, name, quantized)
        else:
            _replace_linear_with_bnb(Linear, module, modules, full_name, layer_kwargs)
    return model


def _replace_linear_with_8bit(
    model: nn.Module,
    modules: set[str] | None = None,
    quantization_config=None,  # NOTE: not currently used
) -> nn.Module:
    import bitsandbytes as bnb
    return _replace_linear_with_bnb(bnb.nn.Linear8bitLt, model, modules, layer_kwargs={
        "has_fp16_weights": False,
    })


def _replace_linear_with_4bit(
    model: nn.Module,
    modules: set[str] | None = None,
    quantization_config=None,
) -> nn.Module:
    """Quantize ``nn.Linear`` layers in ``model`` to 4bit in place."""
    import bitsandbytes as bnb
    compute_dtype = getattr(quantization_config, "bnb_4bit_compute_dtype", torch.float32)
    quant_type = getattr(quantization_config, "bnb_4bit_quant_type", "fp4")
    quant_storage = getattr(quantization_config, "bnb_4bit_quant_storage", torch.uint8)
    return _replace_linear_with_bnb(bnb.nn.Linear4bit, model, modules, layer_kwargs={
        "compute_dtype": compute_dtype,
        "quant_type": quant_type,
        "quant_storage": quant_storage,
    })


def _find_module_by_parameter(state_dict: dict[str, torch.Tensor], suffixes: list[str]) -> set[str]:
    modules: set[str] = set()
    for k in state_dict.keys():
        for suffix in suffixes:
            if k.endswith(suffix):
                base = k[: -len(suffix)]
                modules.add(base)
                break
    return modules


def initialize_quantized_layers(
    model: nn.Module,
    quantization_config: BitsAndBytesConfig,
    int8_modules: set[str],
    int4_modules: set[str],
):
    if quantization_config and not (int8_modules or int4_modules):
        # If a quantization_config is passed in, but no int8 or int4 modules are found, 
        # then we need to find the modules to quantize.
        skip_modules = quantization_config.llm_int8_skip_modules or ('lm_head',)
        modules = {
            name for name, module in model.named_modules()
            if isinstance(module, (nn.Linear, pytorch_utils.Conv1D)) and \
                not any(name.startswith(skip_module) for skip_module in skip_modules)
        }
        int8_modules = modules if quantization_config.load_in_8bit else set()
        int4_modules = modules if quantization_config.load_in_4bit else set()

    if int8_modules:
        model = _replace_linear_with_8bit(model, modules=int8_modules, quantization_config=quantization_config)
    if int4_modules:
        model = _replace_linear_with_4bit(model, modules=int4_modules, quantization_config=quantization_config)
    return model


def from_pretrained(
    model_id: str,
    cache_dir: str | None = TRANSFORMERS_CACHE,
    quantization_config=None,
    skip_unsupported_check: bool = False,
    **model_kwargs,
) -> AutoModelForCausalLM:
    """Load a model using memory-mapped loading for safetensors or PyTorch .bin files.
    
    Just like with `AutoModelForCausalLM.from_pretrained`, full-precision models are only loaded on the CPU by
    default, and quantized models are automatically loaded onto the GPU.
    
    Args:
        model_id: Path to a directory containing a model or a model identifier from the Huggingface model hub.
        cache_dir: Directory to cache the model in.
        quantization_config: Quantization configuration. If provided, the model will be quantized. If the
                             loaded model is already quantized, this will be ignored.
        skip_unsupported_check: If True, allow unsupported arguments to be passed to the model. Otherwise,
                                an error will be raised if any unsupported arguments are passed.
        **model_kwargs: Additional keyword arguments to pass to the model.
    """
    if os.path.exists(model_id):
        cache = model_id
    else:
        cache = download_model(model_id, cache_dir)

    # NOTE: Even if you pass state_dict, model_id still needs to be a valid one,
    # so that the model is configured correctly
    state_dict = model_kwargs.pop('state_dict', get_state_dict_mmap(cache))

    # Check if we need bitsandbytes - either ckpt is quantized or user wants to quantize
    int8_modules = _find_module_by_parameter(state_dict, INT8_MODULE_PARAMS)
    int4_modules = _find_module_by_parameter(state_dict, INT4_MODULE_PARAMS)
    requires_bnb = bool(quantization_config) or bool(int8_modules or int4_modules)
    if requires_bnb and not BITSANDBYTES_AVAILABLE:
        raise ImportError(
            "bitsandbytes is required for quantization. Please install it with `pip install bitsandbytes`."
        )
    
    if model_kwargs and not skip_unsupported_check:
        raise NotImplementedError(
            "There are unsupported argument(s) that may not be compatible with"
            f"memory-mapped loading: {', '.join(model_kwargs.keys())}. Pass "
            "`skip_unsupported_check=True` to skip this check or use "
            "`transformers.AutoModelForCausalLM.from_pretrained` instead."
        )

    # Load model configuration and initialize just the architecture. All parameters
    # are loaded on the meta device (e.g., empty tensors).
    config = AutoConfig.from_pretrained(model_id, **model_kwargs)
    if quantization_config and getattr(config, 'quantization_config', None):
        warnings.warn("Quantization config provided but config already has quantization config. Using provided config.")
    if getattr(config, 'quantization_config', None):
        assert config.quantization_config['quant_method'] == 'bitsandbytes', 'Only supports bitsandbytes quantization'
        quantization_config = BitsAndBytesConfig(**config.quantization_config)
    with init_empty_weights():
        model = AutoModelForCausalLM.from_config(config)

    if BITSANDBYTES_AVAILABLE and requires_bnb:
        model = initialize_quantized_layers(model, quantization_config, int8_modules, int4_modules)
    model.eval()

    majflt_before = resource.getrusage(resource.RUSAGE_SELF).ru_majflt
    
    # Load and tie shared weights for models supporting it (e.g., embeddings ↔ LM head)
    if hasattr(model, 'model') and not list(state_dict.keys())[0].startswith('model.'):
        state_dict = {f"model.{k}": v for k, v in state_dict.items() if not k.startswith('lm_head')}
    with ExitStack() as stack:
        if BITSANDBYTES_AVAILABLE and requires_bnb:
            stack.enter_context(patch.object(Linear8bitLt, "_load_from_state_dict", _Linear8bitLt_load_from_state_dict))
            stack.enter_context(patch.object(Linear4bit, "_load_from_state_dict", _Linear4bit_load_from_state_dict))
        model.load_state_dict(state_dict, assign=True, strict=False)
    if hasattr(model, "tie_weights"):
        model.tie_weights()

    majflt_after = resource.getrusage(resource.RUSAGE_SELF).ru_majflt
    if majflt_after - majflt_before > MAJOR_PAGEFAULT_WARN_THRESHOLD:
        warnings.warn(
            "Large number of page faults detected while loading the model. "
            "This usually indicates insufficient RAM and memmaped tensors "
            "are being swapped. Consider killing this run and loading the model "
            "without fasthug."
        )

    if quantization_config is not None and BITSANDBYTES_AVAILABLE:
        model = model.cuda()  # bnb quantizes on move to gpu

    # Ensure no tensors are still on the meta device
    for name, param in model.named_parameters():
        assert param.device.type != 'meta', name

    return model
