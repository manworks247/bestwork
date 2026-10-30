#!/usr/bin/env python3
"""Create tiny, deterministic fixtures for CPU smoke tests (never benchmark data)."""
from __future__ import annotations

from pathlib import Path
import argparse
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent
MODELNET40_CLASSES = [
    "airplane", "bathtub", "bed", "bench", "bookshelf", "bottle", "bowl", "car",
    "chair", "cone", "cup", "curtain", "desk", "door", "dresser", "flower_pot",
    "glass_box", "guitar", "keyboard", "lamp", "laptop", "mantel", "monitor",
    "night_stand", "person", "piano", "plant", "radio", "range_hood", "sink",
    "sofa", "stairs", "stool", "table", "tent", "toilet", "tv_stand", "vase",
    "wardrobe", "xbox",
]


def synthetic_cloud(class_index: int, seed: int, count: int = 512) -> np.ndarray:
    """A class-conditioned ellipsoid surface; solely for pipeline smoke tests."""
    rng = np.random.default_rng(seed)
    directions = rng.normal(size=(count, 3)).astype(np.float32)
    directions /= np.maximum(np.linalg.norm(directions, axis=1, keepdims=True), 1e-8)
    phase = 2.0 * np.pi * class_index / 40.0
    radii = np.array([
        0.78 + 0.18 * (0.5 + 0.5 * np.sin(phase)),
        0.72 + 0.22 * (0.5 + 0.5 * np.cos(phase)),
        0.70 + 0.24 * ((class_index % 7) / 6.0),
    ], dtype=np.float32)
    cloud = directions * radii
    # Small independent perturbation avoids perfectly duplicated test examples.
    cloud += rng.normal(0.0, 0.008, size=cloud.shape).astype(np.float32)
    return cloud


def write_off_cube(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    vertices = [
        (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
    ]
    faces = [
        (0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    with path.open("w", encoding="utf-8") as f:
        f.write("OFF\n8 6 0\n")
        for xyz in vertices:
            f.write("%.6f %.6f %.6f\n" % xyz)
        for face in faces:
            f.write("4 " + " ".join(map(str, face)) + "\n")


def prepare(root: Path = ROOT) -> dict[str, Path]:
    data_root = root / "data"
    modelnet_root = data_root / "synthetic_modelnet40_normal_resampled"
    modelnet_root.mkdir(parents=True, exist_ok=True)
    (modelnet_root / "modelnet40_shape_names.txt").write_text(
        "\n".join(MODELNET40_CLASSES) + "\n", encoding="utf-8"
    )

    # Two train examples are enough for one batch (batch size 2). The test split
    # contains one synthetic example per output class to exercise full metrics.
    train_ids = []
    for class_index in (0, 1):
        name = MODELNET40_CLASSES[class_index]
        shape_id = f"{name}_0001"
        train_ids.append(shape_id)
        class_dir = modelnet_root / name
        class_dir.mkdir(parents=True, exist_ok=True)
        np.savetxt(class_dir / f"{shape_id}.txt", synthetic_cloud(class_index, 700 + class_index),
                   delimiter=",", fmt="%.7f")
    (modelnet_root / "modelnet40_train.txt").write_text("\n".join(train_ids) + "\n", encoding="utf-8")

    test_ids = []
    for class_index, name in enumerate(MODELNET40_CLASSES):
        shape_id = f"{name}_0002"
        test_ids.append(shape_id)
        class_dir = modelnet_root / name
        class_dir.mkdir(parents=True, exist_ok=True)
        np.savetxt(class_dir / f"{shape_id}.txt", synthetic_cloud(class_index, 1700 + class_index),
                   delimiter=",", fmt="%.7f")
    (modelnet_root / "modelnet40_test.txt").write_text("\n".join(test_ids) + "\n", encoding="utf-8")

    off_path = data_root / "ModelNet10" / "chair" / "train" / "chair_0001.off"
    write_off_cube(off_path)

    mesh_dir = data_root / "meshcnn_fixture"
    mesh_dir.mkdir(parents=True, exist_ok=True)
    mesh_path = mesh_dir / "icosphere.obj"
    if not mesh_path.exists():
        sphere = trimesh.creation.icosphere(subdivisions=1, radius=1.0)
        sphere.export(mesh_path)

    print("Deterministic smoke-test fixtures prepared (not ModelNet/SHREC data).")
    print(f"  Synthetic ModelNet40 layout: {modelnet_root}")
    print(f"  Train examples: {len(train_ids)} across 2 classes; test examples: {len(test_ids)} across 40 classes")
    print(f"  ModelNet10-style OFF mesh: {off_path}")
    print(f"  MeshCNN triangular OBJ: {mesh_path}")
    return {"modelnet40": modelnet_root, "off_mesh": off_path, "obj_mesh": mesh_path}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="project folder (default: this script's folder)")
    args = parser.parse_args()
    prepare(args.root.resolve())
