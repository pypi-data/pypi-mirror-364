import pytest
import torch
import fasthug
from transformers import AutoModelForCausalLM
from transformers.utils.quantization_config import BitsAndBytesConfig
import uuid

MODEL_ID = 'hf-internal-testing/tiny-random-gpt2'

try:
    import bitsandbytes  # if bitsandbytes is available, THEN init
    QUANTIZATION_CONFIGS = [
        BitsAndBytesConfig(load_in_8bit=True),
        BitsAndBytesConfig(load_in_4bit=True),
    ]
except ImportError:
    QUANTIZATION_CONFIGS = []

requires_cuda = pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required for bitsandbytes")


@pytest.fixture
def directory():
    return '/tmp/quantized' + str(uuid.uuid4())


@requires_cuda
@pytest.mark.parametrize("quantization_config", QUANTIZATION_CONFIGS)
def test_smoke_save_and_load_quantized(quantization_config, directory):
    model = fasthug.from_pretrained(MODEL_ID, quantization_config=quantization_config)
    model.save_pretrained(directory)
    model = fasthug.from_pretrained(directory)


@requires_cuda
@pytest.mark.parametrize("quantization_config", QUANTIZATION_CONFIGS)
def test_quantize_load_correctness(quantization_config):
    model_ref = AutoModelForCausalLM.from_pretrained(MODEL_ID, low_cpu_mem_usage=True, quantization_config=quantization_config)
    model = fasthug.from_pretrained(MODEL_ID, quantization_config=quantization_config)
    
    state_ref = model_ref.state_dict()
    state = model.state_dict()
    assert set(state.keys()) == set(state_ref.keys())
    for k in state:
        assert state[k].device == state_ref[k].device, k
        assert state[k].shape == state_ref[k].shape, k
        assert torch.equal(state[k].to(state_ref[k].dtype), state_ref[k]), k


@requires_cuda
@pytest.mark.parametrize("quantization_config", QUANTIZATION_CONFIGS)
def test_quantize_out_correctness(quantization_config):
    torch.manual_seed(0)
    inputs = torch.zeros(1, 1, dtype=torch.long).cuda()
    
    model_ref = AutoModelForCausalLM.from_pretrained(MODEL_ID, low_cpu_mem_usage=True, quantization_config=quantization_config)
    out_ref = model_ref(inputs).logits
    
    model = fasthug.from_pretrained(MODEL_ID, quantization_config=quantization_config).cuda()
    out = model(inputs).logits

    # TODO: match precision, so this can be more precise
    assert torch.allclose(out_ref, out.to(out_ref.dtype), atol=1e-2)


@requires_cuda
@pytest.mark.parametrize("quantization_config", QUANTIZATION_CONFIGS)
def test_quantized_load_correctness(quantization_config, directory):
    model_ref = AutoModelForCausalLM.from_pretrained(MODEL_ID, low_cpu_mem_usage=True, quantization_config=quantization_config)
    model_ref.save_pretrained(directory)
    model = fasthug.from_pretrained(directory).cuda()
    
    state_ref = model_ref.state_dict()
    state = model.state_dict()
    assert set(state.keys()) == set(state_ref.keys())
    for k in state:
        assert state[k].device == state_ref[k].device, k
        assert torch.equal(state[k], state_ref[k]), k


@requires_cuda
@pytest.mark.parametrize("quantization_config", QUANTIZATION_CONFIGS)
def test_quantized_out_correctness(quantization_config, directory):
    torch.manual_seed(0)
    inputs = torch.zeros(1, 1, dtype=torch.long).cuda()
    
    model_ref = AutoModelForCausalLM.from_pretrained(MODEL_ID, low_cpu_mem_usage=True, quantization_config=quantization_config)
    out_ref = model_ref(inputs).logits
    model_ref.save_pretrained(directory)
    
    model = fasthug.from_pretrained(directory).cuda()
    out = model(inputs).logits

    assert torch.allclose(out_ref, out)
