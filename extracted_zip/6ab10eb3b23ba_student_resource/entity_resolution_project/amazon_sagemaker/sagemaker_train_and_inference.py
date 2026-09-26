#!/usr/bin/env python3
"""
Amazon SageMaker Script Mode Entrypoint for Business Entity Resolution.
Supports training and inference on AWS SageMaker instances (ml.m5.xlarge, ml.c5.2xlarge, etc.).
"""

import argparse
import os
import sys

# SageMaker directories from environment variables
SM_MODEL_DIR = os.environ.get("SM_MODEL_DIR", "/opt/ml/model")
SM_CHANNEL_TRAIN = os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train")
SM_CHANNEL_TEST = os.environ.get("SM_CHANNEL_TEST", "/opt/ml/input/data/test")
SM_OUTPUT_DATA_DIR = os.environ.get("SM_OUTPUT_DATA_DIR", "/opt/ml/output/data")

# Add script directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import train_pipeline, inference_pipeline
from src.pipeline_v2 import train_pipeline_v2, inference_pipeline_v2


def main():
    parser = argparse.ArgumentParser(description="AWS SageMaker Business Entity Resolution")
    parser.add_argument(
        "--version",
        type=int,
        choices=[1, 2],
        default=1,
        help="Pipeline version: 1 (Lexical + RapidFuzz + LightGBM) or 2 (TF-IDF + BGE + LightGBM)",
    )
    parser.add_argument("--train", type=str, default=SM_CHANNEL_TRAIN, help="Path to training data")
    parser.add_argument("--test", type=str, default=SM_CHANNEL_TEST, help="Path to test data")
    parser.add_argument("--model-dir", type=str, default=SM_MODEL_DIR, help="Path to model directory")
    parser.add_argument(
        "--output-data-dir", type=str, default=SM_OUTPUT_DATA_DIR, help="Path to output directory"
    )
    parser.add_argument(
        "--train-samples", type=int, default=50000, help="Number of training samples"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="all",
        choices=["train", "infer", "all"],
        help="Pipeline execution mode",
    )

    args, _ = parser.parse_known_args()

    # Determine parent data_dir containing train/ and test/
    # If passed directly as train channel, construct data_dir
    if os.path.exists(os.path.join(args.train, "train_source1.tsv")):
        # args.train is the train folder itself
        data_dir = os.path.dirname(os.path.abspath(args.train))
    else:
        data_dir = args.train

    model_file = os.path.join(args.model_dir, "matching_model.pkl")

    # 1. Training Phase
    if args.mode in ["train", "all"]:
        print(f"SageMaker Training (Version {args.version}): data_dir={data_dir}, model_file={model_file}")
        if args.version == 2:
            train_pipeline_v2(
                data_dir=data_dir,
                model_save_path=model_file,
                sample_entities=args.train_samples,
            )
        else:
            train_pipeline(
                data_dir=data_dir,
                model_save_path=model_file,
                sample_entities=args.train_samples,
            )

    # 2. Inference Phase
    if args.mode in ["infer", "all"]:
        print(f"SageMaker Inference (Version {args.version}): test_dir={args.test}, output_dir={args.output_data_dir}")
        if args.version == 2:
            inference_pipeline_v2(
                data_dir=data_dir,
                model_path=model_file,
                output_dir=args.output_data_dir,
            )
        else:
            inference_pipeline(
                data_dir=data_dir,
                model_path=model_file,
                output_dir=args.output_data_dir,
            )

    print("SageMaker process completed successfully.")


if __name__ == "__main__":
    main()
