import argparse
import os
import sys

from .bench import benchmark, create_quantization_config


def main(argv: list[str] | None = None) -> None:
    """Entry point for the ``flb`` command."""
    parser = argparse.ArgumentParser(
        prog=os.path.basename(sys.argv[0]),
        description="Benchmark fasthug vs HuggingFace",
    )
    parser.add_argument(
        "model_id",
        help="Model identifier, e.g. facebook/opt-125m",
    )
    parser.add_argument(
        "-n",
        "--num-trials",
        type=int,
        default=3,
        help="Number of times to run each benchmark",
    )
    parser.add_argument(
        "-d",
        "--device",
        choices=["cpu", "cuda", "mps", "none"],
        default=None,
        help=(
            "Device to load the model on (e.g., 'cuda', 'cpu', 'mps' or 'none' "
            "to automatically select)"
        ),
    )
    parser.add_argument(
        "-w",
        "--warmup",
        type=int,
        default=2,
        help="Number of warmup runs",
    )
    parser.add_argument(
        "--load-in-8bit",
        action="store_true",
        help="Quantize the model to 8-bit using bitsandbytes",
    )
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        help="Quantize the model to 4-bit using bitsandbytes",
    )
    parser.add_argument(
        "--quantization-config",
        type=str,
        default=None,
        help="Path to a quantization config file",
    )
    args = parser.parse_args(argv)
    
    benchmark(
        args.model_id,
        device=args.device,
        num_trials=args.num_trials,
        warmup=args.warmup,
        quantization_config=create_quantization_config(
            load_in_4bit=args.load_in_4bit,
            load_in_8bit=args.load_in_8bit,
            quantization_config=args.quantization_config,
        ),
    )


if __name__ == "__main__":
    main()
