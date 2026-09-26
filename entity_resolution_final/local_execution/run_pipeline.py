#!/usr/bin/env python3
"""
Local runner for the Business Entity Resolution pipeline.

Usage:
    python run_pipeline.py --data-dir C:/path/to/student_resource/dataset
    (the folder must contain train/ and test/ subfolders)

Optional:
    --skip-train        reuse models/matcher_lgbm.txt
    --train-sample N    number of S1 training entities to sample (default 150000)
    --top-k K           candidates per S1 entity (default 12)
"""

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.normpath(os.path.join(HERE, "..", "code", "business_entity_resolution"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=False, default=None)
    ap.add_argument("--train-sample", type=int, default=150_000)
    ap.add_argument("--top-k", type=int, default=12)
    ap.add_argument("--skip-train", action="store_true")
    args = ap.parse_args()

    data_dir = args.data_dir
    if not data_dir:
        data_dir = input("Enter path to the dataset folder (contains train/ and test/): ").strip().strip('"')
    if not os.path.isdir(os.path.join(data_dir, "train")) or \
       not os.path.isdir(os.path.join(data_dir, "test")):
        sys.exit(f"ERROR: {data_dir} must contain train/ and test/ subfolders")

    cmd = [
        sys.executable, "-m", "src.pipeline",
        "--data-dir", data_dir,
        "--out-dir", os.path.join(HERE, "output"),
        "--work-dir", os.path.join(HERE, "work"),
        "--model-path", os.path.join(HERE, "models", "matcher_lgbm.txt"),
        "--train-sample", str(args.train_sample),
        "--top-k", str(args.top_k),
    ]
    if args.skip_train:
        cmd.append("--skip-train")
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=CODE_DIR)
    print("\nDone. Outputs in", os.path.join(HERE, "output"))


if __name__ == "__main__":
    main()
