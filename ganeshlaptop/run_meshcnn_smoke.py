#!/usr/bin/env python3
"""One-batch MeshCNN edge-convolution smoke test on a generated icosphere.

This imports the upstream MeshCNN implementation (not a reimplementation),
then checks edge feature extraction, MeshConv, classification logits and one
backprop/optimizer step. It is not training or evaluation on SHREC.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import argparse
import sys
import numpy as np
import torch

from prepare_fixtures import prepare

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meshcnn-root", type=Path, required=True,
                        help="path to a cloned ranahanocka/MeshCNN repository")
    args = parser.parse_args()
    repo = args.meshcnn_root.expanduser().resolve()
    if not (repo / "models" / "layers" / "mesh.py").is_file():
        raise FileNotFoundError(f"MeshCNN source not found under {repo}")
    sys.path.insert(0, str(repo))

    import trimesh
    from models.layers.mesh import Mesh
    from models.networks import MeshConvNet, get_norm_layer

    # The upstream 2019 code targets NumPy 1.15. Under NumPy >=1.24,
    # ragged per-vertex edge lists must be explicitly saved as object arrays,
    # and the deprecated np.bool alias is absent. Keep these compatibility
    # shims local to this smoke-test process; upstream source remains untouched.
    if "bool" not in np.__dict__:
        np.bool = bool  # type: ignore[attr-defined]
    original_savez_compressed = np.savez_compressed
    def savez_compressed_compat(file, *args, **kwargs):
        if "ve" in kwargs:
            kwargs["ve"] = np.asarray(kwargs["ve"], dtype=object)
        return original_savez_compressed(file, *args, **kwargs)
    np.savez_compressed = savez_compressed_compat  # type: ignore[assignment]

    fixture = prepare(ROOT)
    mesh_path = fixture["obj_mesh"]
    cache_dir = mesh_path.parent / "cache"
    if cache_dir.exists():
        for cache_file in cache_dir.glob("icosphere_*.npz"):
            cache_file.unlink()
    options = SimpleNamespace(num_aug=1)
    mesh = Mesh(file=str(mesh_path), opt=options, hold_history=False)
    features = np.asarray(mesh.extract_features(), dtype=np.float32)
    if features.ndim != 2 or features.shape[0] != 5:
        raise ValueError(f"Expected 5 x E MeshCNN edge features, got {features.shape}")
    edge_count = int(mesh.edges_count)

    torch.manual_seed(23)
    torch.set_num_threads(1)
    # Keep the canonical edge-neighborhood convolution and classification head,
    # but use a single small feature stage; pooling target == input edges.
    model = MeshConvNet(
        norm_layer=get_norm_layer("none"),
        nf0=features.shape[0],
        conv_res=[8],
        nclasses=30,
        input_res=edge_count,
        pool_res=[edge_count],
        fc_n=16,
        nresblocks=1,
    )
    x = torch.from_numpy(features).unsqueeze(0).unsqueeze(-1).requires_grad_(True)
    labels = torch.tensor([0], dtype=torch.long)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    model.train()
    optimizer.zero_grad(set_to_none=True)
    logits = model(x, [mesh])
    loss = criterion(logits, labels)
    loss.backward()
    optimizer.step()

    print("Section 7.4 | upstream MeshCNN CPU smoke test")
    print(f"MeshCNN source: {repo}")
    print(f"Fixture: {mesh_path.relative_to(ROOT)} (generated trimesh icosphere; not SHREC)")
    print(f"Topology: vertices={len(mesh.vs)}, triangles={len(trimesh.load(mesh_path, force='mesh').faces)}, edges={edge_count}")
    print(f"Edge feature tensor: {features.shape} (dihedral angle, opposite angles, ratios)")
    print(f"Input tensor: {tuple(x.shape)}; logits: {tuple(logits.shape)} (30-way SHREC-like head only)")
    print(f"Single synthetic-label cross-entropy: {loss.item():.6f}; backward/Adam step: PASS")
    print("STATUS: PASS — upstream MeshConv/connectivity path exercised; no SHREC training or accuracy claimed.")


if __name__ == "__main__":
    main()
