#!/usr/bin/env python3
"""Run the section 7.3 mesh-to-voxel + 3D CNN forward-pass smoke test."""
from __future__ import annotations

from pathlib import Path
import argparse
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from geometry_utils import load_triangle_mesh, mesh_to_voxel
from prepare_fixtures import prepare

ROOT = Path(__file__).resolve().parent


class VoxelCNN(nn.Module):
    """The compact 32^3 3D CNN architecture in the supplied lab section."""
    def __init__(self, num_classes: int = 10):
        super().__init__()
        self.conv1 = nn.Conv3d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv3d(32, 64, kernel_size=3, padding=1)
        self.pool = nn.MaxPool3d(2)
        self.fc1 = nn.Linear(64 * 8 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.reshape(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid-size", type=int, default=32)
    args = parser.parse_args()

    fixture = prepare(ROOT)
    mesh_path = fixture["off_mesh"]
    mesh = load_triangle_mesh(mesh_path)
    vox = mesh_to_voxel(mesh_path, grid_size=args.grid_size)
    vox_tensor = torch.from_numpy(vox).unsqueeze(0).unsqueeze(0)

    torch.manual_seed(23)
    torch.set_num_threads(1)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = VoxelCNN(num_classes=10).to(device).eval()
    with torch.inference_mode():
        output = model(vox_tensor.to(device))

    print("Section 7.3 | mesh-to-voxel + CNN forward pass")
    print(f"Mesh fixture: {mesh_path.relative_to(ROOT)} (synthetic closed cube, {len(mesh.faces)} triangles)")
    print(f"Voxel grid: {vox.shape}; occupied cells: {int(vox.sum())}/{vox.size} ({100.0 * vox.mean():.2f}%)")
    print(f"Tensor shape (B,C,D,H,W): {tuple(vox_tensor.shape)}; dtype={vox_tensor.dtype}")
    print(f"Device: {device}; CUDA available: {torch.cuda.is_available()}")
    print(f"Output logits shape: {tuple(output.shape)} (10 classes)")
    print(f"Predicted class index (untrained demo head): {int(output.argmax(dim=1).item())}")
    print("STATUS: PASS — conversion and forward shape checked; synthetic fixture only, no ModelNet10 accuracy claimed.")


if __name__ == "__main__":
    main()
