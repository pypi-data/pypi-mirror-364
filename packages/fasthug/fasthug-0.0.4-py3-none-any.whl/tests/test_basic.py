import fasthug
import pytest
from transformers import AutoModelForCausalLM
import torch
import warnings
import sys
from types import SimpleNamespace


MODEL_ID = 'hf-internal-testing/tiny-random-gpt2'
requires_cuda = pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA required for bitsandbytes")


def test_from_pretrained():
    model = fasthug.from_pretrained('hf-internal-testing/tiny-random-gpt2')
    assert model.state_dict()['transformer.wte.weight'].shape == (1000, 32)


def test_unsupported_kwarg():
    with pytest.raises(NotImplementedError):
        fasthug.from_pretrained('hf-internal-testing/tiny-random-gpt2', foo='bar')
    
    model = fasthug.from_pretrained('hf-internal-testing/tiny-random-gpt2', foo='bar', skip_unsupported_check=True)
    assert model.state_dict()['transformer.wte.weight'].shape == (1000, 32)
    

def test_weight_correctness():
    model = fasthug.from_pretrained(MODEL_ID)
    model_ref = AutoModelForCausalLM.from_pretrained(MODEL_ID)
    assert all(torch.equal(model.state_dict()[k], model_ref.state_dict()[k]) for k in model.state_dict().keys())


def test_out_correctness():
    model = fasthug.from_pretrained(MODEL_ID)
    model_ref = AutoModelForCausalLM.from_pretrained(MODEL_ID)

    inputs = torch.zeros(1, 1, dtype=torch.long)
    assert torch.allclose(model(inputs).logits, model_ref(inputs).logits)


def test_warn_insufficient_memory(monkeypatch, tmp_path):
    psutil_mock = SimpleNamespace(virtual_memory=lambda: SimpleNamespace(available=0))
    monkeypatch.setitem(sys.modules, "psutil", psutil_mock)

    file_path = tmp_path / "pytorch_model.bin"
    torch.save({"foo": torch.zeros(1)}, file_path)

    with warnings.catch_warnings(record=True) as w:
        fasthug.fasthug.get_state_dict_mmap(tmp_path)
        assert any("insufficient system memory" in str(wi.message).lower() for wi in w)
