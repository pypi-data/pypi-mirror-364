# fasthug

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1j3_iaZ-p0xYXsTt0ktAA7xwntjuhmeaL?usp=sharing)

fasthug moves HuggingFace models from disk to GPU 5x faster. To get started, install:

```bash
pip install fasthug
```

To load a model with fasthug, use the `fasthug.from_pretrained` function, instead of `AutoModelForCausalLM.from_pretrained`:

```python
import fasthug
model = fasthug.from_pretrained("facebook/opt-125m").cuda() # 5x faster
```

fasthug currently only supports the `quantization_config` keyword argument, which you can use to quantize models on-the-fly.

```python
from transformers.utils.quantization_config import BitsAndBytesConfig
config = BitsAndBytesConfig(load_in_8bit=True)
model = fasthug.from_pretrained(model_id, quantization_config=config)  # 3x faster
```

For the fastest load times, save the quantized model, and load the pre-quantized model with fasthug.

```python
model.save_pretrained("/tmp/quantized")
model = fasthug.from_pretrained("/tmp/quantized") # 8x faster
```

The model is at this point a standard HuggingFace model, just like any other - and you can use it to generate text normally.

```python
from transformers import pipeline
import fasthug

model = fasthug.from_pretrained(MODEL_ID)
generator = pipeline("text-generation", model=model, tokenizer=MODEL_ID)
output = generator("Once upon a time", max_new_tokens=5)
print(output)
```

There are more example text generation examples in [`tests/test_generate.py`](tests/test_generate.py).

To get started, try the fasthug demo in a [Colab notebook here](https://colab.research.google.com/drive/1j3_iaZ-p0xYXsTt0ktAA7xwntjuhmeaL?usp=sharing).

## Benchmarks

fasthug provides a consistent 3-5x speedup across a range of models, GPUs, and quantization settings, relative to the default HuggingFace model loader. Under the special case where weights are already pre-quantized, fasthug provides an 8x speedup relative to HuggingFace.

<img width="49%" src="https://github.com/user-attachments/assets/2fbf7df8-b001-4de1-b4d0-1c37897f042e">
<img width="49%" src="https://github.com/user-attachments/assets/56d63f3d-5233-4ee1-abd2-dd68960fb32c">
<sub><b>(Left) Model Load Time Speedups:</b> fasthug loads models anywhere from 3x to 11x faster than Huggingface based on the model size and quantization setting. <b>(Right) Absolute Model Load Times:</b> fasthug model load times grow more slowly than Huggingface's model load times do.</sub>

------------------------------------------------

For more detailed benchmark results, experimental setup, and commands to reproduce, see the below.

<details>
<summary>&nbsp;<b>5x speedup, 2x less memory</b> loading full-precision models on server-grade GPUs (H100)</summary><br/>

> The below benchmarks compare these two lines:
> 
> ```python
> model = AutoModelForCausalLM.from_pretrained(model_id, low_cpu_mem_usage=True).cuda()
> model = fasthug.from_pretrained(model_id).cuda()
> ```
> 
> To rerun these benchmarks, use the following command to launch benchmarks remotely.
> 
> ```bash
> modal run utils/app.py::run_model --model-id facebook/opt-1.3b
> ```
> 
> | Model             | GPU  | HF (s)          | Mem (GiB) | fasthug (s)  | Mem (GiB) | Speedup |
> |-------------------|------|-----------------|-----------|--------------|-----------|---------|
> | facebook/opt-13b  | H100 | 26.20 ± 0.49    | 49.03     | 5.83 ± 0.46  | 24.52     | 4.5x    |
> | facebook/opt-6.7b | H100 | 10.79 ± 0.23    | 25.40     | 2.44 ± 0.01  | 12.70     | 4.4x    |
> | facebook/opt-2.7b | H100 | 7.07 ± 0.06     | 10.24     | 1.09 ± 0.05  | 5.12      | 6.5x    |
> | facebook/opt-1.3b | H100 | 3.10 ± 0.37     | 5.02      | 0.61 ± 0.00  | 2.51      | 5.1x    |
> 
> If we instead use `load_cpu_mem_usage=False`, HuggingFace is overall slower to load.
> 
> | Model             | GPU  | HF (s)          | Mem (GiB) | fasthug (s) | Mem (GiB) | Speedup |
> |-------------------|------|-----------------|-----------|--------------|-----------|---------|
> | facebook/opt-13b  | H100 | 45.33 ± 2.75    | 49.03     | 5.83 ± 0.46  | 24.52     | 4.5x    |
> | facebook/opt-6.7b | H100 | 23.12 ± 3.22    | 25.40     | 2.44 ± 0.01  | 12.70     | 4.4x    |
> | facebook/opt-2.7b | H100 | 6.85 ± 0.32     | 10.24     | 1.09 ± 0.05  | 5.12      | 6.3x    |
> | facebook/opt-1.3b | H100 | 4.12 ± 0.14     | 5.02      | 0.61 ± 0.00  | 2.51      | 6.7x    |

</details>

<details>
<summary>&nbsp;<b>3x speedup, 2x less memory</b> loading full-precision models on consumer GPUs (T4, 3060, M3).</summary><br/>

> The below benchmarks compare these two lines on Nvidia T4, Nvidia RTX 3060, and the Apple M3:
>
> ```python
> model = AutoModelForCausalLM.from_pretrained(model_id, low_cpu_mem_usage=True).cuda()
> model = fasthug.from_pretrained(model_id).cuda()
> ```
> 
> To rerun these benchmarks, use the following command, locally.
> 
> ```bash
> fhb facebook/opt-1.3b
> ```
> 
> | Model             | GPU  | HF (s)          | Mem (GiB) | fasthug (s)  | Mem (GiB) | Speedup |
> |-------------------|------|-----------------|-----------|--------------|-----------|---------|
> | facebook/opt-1.3b | T4   | 9.09 ± 1.43     | 5.02      | 6.07 ± 0.39  | 2.51      | 1.5x    |
> | facebook/opt-350m | T4   | 2.57 ± 1.04     | 1.26      | 1.19 ± 0.49  | 0.63      | 2.2x    |
> | facebook/opt-125m | T4   | 1.06 ± 0.04     | 0.48      | 0.27 ± 0.00  | 0.25      | 3.9x    |
> |                   |      |                 |           |              |           |         |
> | facebook/opt-1.3b | 3060 | 6.96 ± 0.03     | 5.02      | 1.66 ± 0.02  | 2.51      | 4.2x    |
> | facebook/opt-350m | 3060 | 1.09 ± 0.06     | 1.26      | 0.39 ± 0.00  | 0.63      | 2.2x    |
> | facebook/opt-125m | 3060 | 0.73 ± 0.06     | 0.48      | 0.20 ± 0.01  | 0.25      | 3.9x    |
> |                   |      |                 |           |              |           |         |
> | facebook/opt-1.3b | M3   | 11.9 ± 1.17     | -         | 2.65 ± 0.62  | -         | 4.5x    |
> | facebook/opt-350m | M3   | 1.49 ± 0.22     | -         | 0.49 ± 0.22  | -         | 3.0x    |
> | facebook/opt-125m | M3   | 0.78 ± 0.12     | -         | 0.27 ± 0.02  | -         | 2.9x    |

</details>


<details>
<summary>&nbsp;<b>3x speedup, 200MB less memory</b> loading and quantizing models on-the-fly</summary><br/>

> The below benchmarks compare these lines:
> 
> ```python
> kw = {'quantization_config': BitsAndBytesConfig(load_in_8bit=True)}
> model = AutoModelForCausalLM.from_pretrained(model_id, low_cpu_mem_usage=True, **kw)
> model = fasthug.from_pretrained(model_id, **kw)
> ```
> 
> To rerun these benchmarks for 8bit quantization, use the following command.
> 
> ```bash
> modal run utils/app.py::run_model --model-id facebook/opt-1.3b --load-in-8bit
> ```
> 
> | Model             | GPU  | HF (s)          | Mem (GiB) | fasthug (s)  | Mem (GiB) | Speedup |
> |-------------------|------|-----------------|-----------|--------------|-----------|---------|
> | facebook/opt-13b  | H100 | 18.35 ± 0.17    | 12.9      | 5.13 ± 0.03  | 12.7      | 3.6x    |
> | facebook/opt-6.7b | H100 | 8.07 ± 0.07     | 6.82      | 2.30 ± 0.01  | 6.69      | 3.5x    |
> | facebook/opt-2.7b | H100 | 3.58 ± 0.10     | 2.91      | 1.13 ± 0.01  | 2.71      | 3.2x    |
> | facebook/opt-1.3b | H100 | 3.20 ± 0.37     | 1.56      | 0.64 ± 0.00  | 1.39      | 5.0x    |
> 
> 
> The next benchmarks compare quantization to 4bit on-the-fly, which compares these lines:
> 
> ```python
> kw = {'quantization_config': BitsAndBytesConfig(load_in_4bit=True)}
> model = AutoModelForCausalLM.from_pretrained(model_id, low_cpu_mem_usage=True, **kw)
> model = fasthug.from_pretrained(model_id, **kw)
> ```
> 
> To rerun these benchmarks for 4bit quantization, use the following command.
> 
> ```bash
> modal run utils/app.py::run_model --model-id facebook/opt-1.3b --load-in-4bit
> ```
> 
> *Note*: Peak memory usage fluctuates wildly for these 4 bit benchmarks. Additionally, they're much larger than
> the peak memory usage from 8 bit benchmarks. This is definitely a bug. Whether in fasthug or in bitsandbytes,
> I'm not sure at the moment.
> 
> | Model             | GPU  | HF (s)          | Mem (GiB) | fasthug (s)  | Mem (GiB) | Speedup |
> |-------------------|------|-----------------|-----------|--------------|-----------|---------|
> | facebook/opt-13b  | H100 | 15.60 ± 0.21    | 21.2      | 4.53 ± 0.14  | 27.7      | 3.4x    |
> | facebook/opt-6.7b | H100 | 8.39 ± 0.08     | 11.0      | 2.47 ± 0.06  | 10.9      | 3.4x    |
> | facebook/opt-2.7b | H100 | 3.58 ± 0.10     | 5.91      | 1.13 ± 0.01  | 7.07      | 3.2x    |
> | facebook/opt-1.3b | H100 | 3.58 ± 0.70     | 3.00      | 0.85 ± 0.18  | 2.83      | 4.2x    |

</details>

<details>
<summary>&nbsp;<b>8x speedup, 150MB less memory</b> loading previously-quantized models</summary><br/>

> The below benchmarks compare these lines:
> 
> ```python
> # save the quantized checkpoint first
> kwargs = {'quantization_config': BitsAndBytesConfig(load_in_8bit=True)}
> model = AutoModelForCausalLM.from_pretrained(model_id, low_cpu_mem_usage=True, **kwargs)
> model.save_pretrained('/tmp/quantized')
> 
> # compare these two lines
> model = AutoModelForCausalLM.from_pretrained('/tmp/quantized', low_cpu_mem_usage=True)
> model = fasthug.from_pretrained('/tmp/quantized')
> ```
> 
> To rerun these benchmarks, use the following command.
> 
> ```
> modal run utils/app.py::run_model --model-id facebook/opt-1.3b --use-8bit-checkpoint
> ```
> 
> If you see an error like the following, just run the same command again. Modal's container
> just hasn't loaded an updated copy of the on-disk cache.
> 
> ```
> OSError: Error no file named pytorch_model.bin, model.safetensors, tf_model.h5, 
> model.ckpt.index or flax_model.msgpack found in directory
> ```
> 
> | Model             | GPU  | HF (s)          | Mem (GiB) | fasthug (s)  | Mem (GiB) | Speedup |
> |-------------------|------|-----------------|-----------|--------------|-----------|---------|
> | facebook/opt-13b  | H100 | 35.50 ± 0.40    | 12.7      | 3.09 ± 0.10  | 12.5      | 11.2x   |
> | facebook/opt-6.7b | H100 | 14.14 ± 0.53    | 6.69      | 1.50 ± 0.01  | 6.56      | 9.4x    |
> | facebook/opt-2.7b | H100 | 6.16 ± 0.14     | 2.71      | 0.70 ± 0.01  | 2.66      | 8.8x    |
> | facebook/opt-1.3b | H100 | 2.40 ± 0.08     | 1.39      | 0.49 ± 0.03  | 1.36      | 4.9x    |

</details>


## Customization

Fasthug only supports the `quantization_config` kwarg, to stay minimal and lightweight. The
eventual goal is to support other commonly-used arguments for model development.

```python
import fasthug
import torch
from transformers import AutoModelForCausalLM
from transformers.utils.quantization_config import BitsAndBytesConfig

# If you pass args that fasthug doesn't support, pass `skip_unsupported_check=True`
model = fasthug.from_pretrained(
    "facebook/opt-125m",
    torch_dtype=torch.float16,
    skip_unsupported_check=True
)

# For args that fasthug doesn't support, initialize a model 'normally', save, then fasthug
model = AutoModelForCausalLM.from_pretrained("facebook/opt-125m", torch_dtype=torch.float16)
model.save_pretrained('/tmp/half')
model = fasthug.from_pretrained("/tmp/half")
```

<details><summary>&nbsp;Expand for more example usage</summary><br/>

```python
import fasthug
from transformers import AutoModelForCausalLM
from transformers.utils.quantization_config import BitsAndBytesConfig

# Load model on GPU
model = fasthug.from_pretrained("facebook/opt-125m").cuda()

# Load and quantize model in 8 bits per weight
cfg8b = BitsAndBytesConfig(load_in_8bit=True)
model = fasthug.from_pretrained("facebook/opt-125m", quantization_config=cfg8b)

# Load already-quantized 8-bit model. Quantization settings are already saved in
# checkpoint, so we don't need to pass quantization_config again.
model = fasthug.from_pretrained("facebook/opt-125m", quantization_config=cfg8b)
model.save_pretrained('/tmp/quantized')
model = fasthug.from_pretrained("/tmp/quantized")  # notice no quantization_config
```

4-bit on-the-fly quantization sees wildly fluctuating and larger peak memory usage than even
8-bit quantized models. This is true of both the baseline transformer model *and* the fasthug-
loaded models.

```python
# Can do all of the above using 4 bit quantization too.
cfg4b = BitsAndBytesConfig(load_in_4bit=True)
model = fasthug.from_pretrained("facebook/opt-125m", quantization_config=cfg4b)

model = fasthug.from_pretrained("facebook/opt-125m", quantization_config=cfg4b)
model.save_pretrained('/tmp/quantized')
model = fasthug.from_pretrained("/tmp/quantized")

model = AutoModelForCausalLM.from_pretrained("facebook/opt-125m", quantization_config=cfg4b)
model.save_pretrained('/tmp/quantized')
model = fasthug.from_pretrained("/tmp/quantized")
```
</details>

## Development

### Benchmarks

To run benchmarks locally, you can use the `fhb` utility. To run benchmarks remotely, use the Modal launcher script in `utils/app.py`.

```bash
# run benchmarks locally
fhb facebook/opt-125m
fhb facebook/opt-125m --load-in-8bit  # on Nvidia GPUs

# run benchmarks remotely
modal run utils/app.py::run_model --model-id facebook/opt-125m
modal run utils/app.py::run_model --model-id facebook/opt-125m --load-in-8bit
modal run utils/app.py::run_model --model-id facebook/opt-125m --use-8bit-checkpoint
```

<details>
<summary>&nbsp;Expand for details on running local benchmarks using <code>fhb</code>.</summary><br/>

The utility is also available as `fhbench` or `fasthugbench`. In short, it compares the
loading speed of `fasthug` vs HuggingFace. For Nvidia GPUs, this script also records peak
memory usage.

```bash
usage: fhb [-h] [-n NUM_TRIALS] [-d {cpu,cuda,mps,none}] [-w WARMUP]
           [--load-in-8bit] [--load-in-4bit]
           [--quantization-config QUANTIZATION_CONFIG]
           model_id

Benchmark fasthug vs HuggingFace

positional arguments:
  model_id              Model identifier, e.g. facebook/opt-125m

options:
  -h, --help            show this help message and exit
  -n NUM_TRIALS, --num-trials NUM_TRIALS
                        Number of times to run each benchmark
  -d {cpu,cuda,mps,none}, --device {cpu,cuda,mps,none}
                        Device to load the model on (e.g., 'cuda', 'cpu', 'mps' or
                        'none' to automatically select)
  -w WARMUP, --warmup WARMUP
                        Number of warmup runs
  --load-in-8bit        Quantize the model to 8-bit using bitsandbytes
  --load-in-4bit        Quantize the model to 4-bit using bitsandbytes
  --quantization-config QUANTIZATION_CONFIG
                        Path to a quantization config file
```
</details>

<details>
<summary>&nbsp;Expand for details on running remote benchmarks using the Modal script</summary><br/>

The command above will spin up a CPU Modal instance to download the weights
to a persisted volume, then spin up a GPU Modal instance to benchmark the model
loading itself.

For the `--use-8bit-checkpoint` flag, we similarly first load and quantize an 8bit
checkpoint on a CPU job first, then benchmark loading that checkpoint on a GPU job.

```bash
Usage: modal run utils/app.py::run_model [OPTIONS]

Options:
  --use-8bit-checkpoint / --no-use-8bit-checkpoint
  --load-in-4bit / --no-load-in-4bit
  --load-in-8bit / --no-load-in-8bit
  --num-trials INTEGER
  --warmup INTEGER
  --device TEXT
  --model-id TEXT                 [required]
  --help                          Show this message and exit.
```
</details>

### Tests

Run tests using the following

```bash
modal run utils/app.py::run_tests  # remotely
pytest tests  # locally
```

## How it Works

fasthug uses existing PyTorch and safetensors implementations of memory mapping to load model weights into CPU.

- For full-precision models, the user can later move these weights to GPU.
- To quantize models on-the-fly, we simply use bitsandbytes normally to move and quantize weights.
- To load pre-quantized models, we move weights to GPU immediately, so that bitsandbytes recognizes that the weights are pre-quantized. The baseline Huggingface load is particularly slow for pre-quantized weights only because it (a) first quantizes and moves random weights, *then* (b) moves the pre-quantized weights to GPU.

The goal is to make loading models as fast as possible, to shorten the dev cycle in a non-interactive (e.g., not in a jupyter notebook) environment.