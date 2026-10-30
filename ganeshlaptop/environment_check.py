#!/usr/bin/env python3
"""Print the exact runtime used for the reproducible experiment report."""
from __future__ import annotations

import importlib.metadata
import os
import platform
import sys
import torch

print("Point-cloud / 3D representation lab — runtime check")
print(f"Python: {platform.python_version()} ({sys.executable})")
for package in ("torch", "numpy", "scipy", "trimesh", "matplotlib", "reportlab", "Pillow", "tqdm"):
    try:
        print(f"{package}: {importlib.metadata.version(package)}")
    except importlib.metadata.PackageNotFoundError:
        print(f"{package}: NOT INSTALLED")
print(f"PyTorch CUDA build: {torch.version.cuda}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CPU cores visible: {os.cpu_count()}")
try:
    with open("/proc/meminfo", encoding="ascii") as f:
        mem_kb = int(next(line for line in f if line.startswith("MemTotal:")).split()[1])
    print(f"Host memory reported: {mem_kb / (1024**2):.2f} GiB")
except (OSError, StopIteration, ValueError):
    print("Host memory reported: unavailable")
print("Device selected for executed smoke tests: CPU")
