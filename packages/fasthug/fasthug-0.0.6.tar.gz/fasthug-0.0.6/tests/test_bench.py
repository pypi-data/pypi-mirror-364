from fasthug.bench import _choose_device


def test_choose_device_cpu(monkeypatch):
    monkeypatch.setattr("torch.cuda.is_available", lambda: False)
    monkeypatch.setattr("torch.backends.mps.is_available", lambda: False)
    assert _choose_device(None) == "cpu"
    assert _choose_device("none") == "cpu"


def test_choose_device_cuda(monkeypatch):
    monkeypatch.setattr("torch.cuda.is_available", lambda: True)
    monkeypatch.setattr("torch.backends.mps.is_available", lambda: False)
    assert _choose_device(None) == "cuda"


def test_choose_device_mps(monkeypatch):
    monkeypatch.setattr("torch.cuda.is_available", lambda: False)
    monkeypatch.setattr("torch.backends.mps.is_available", lambda: True)
    assert _choose_device(None) == "mps"
