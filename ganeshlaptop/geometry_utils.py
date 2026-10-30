"""Geometry helpers shared by the voxel and representation-conversion demos."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import trimesh


def load_triangle_mesh(path: str | Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=True)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    if not isinstance(mesh, trimesh.Trimesh) or mesh.is_empty:
        raise ValueError(f"Could not load a non-empty triangle mesh from {path}")
    if len(mesh.faces) == 0:
        raise ValueError(f"Mesh contains no faces: {path}")
    return mesh


def mesh_to_voxel(path: str | Path, grid_size: int = 32) -> np.ndarray:
    """Center, isotropically scale, voxelize and fill a mesh into a fixed cube.

    Unlike a scalar zoom based on one dimension, this keeps the mesh's aspect
    ratio and pads it in a fixed grid. The returned occupancy array is float32
    with shape (grid_size, grid_size, grid_size).
    """
    if grid_size < 4:
        raise ValueError("grid_size must be at least 4")
    mesh = load_triangle_mesh(path).copy()
    bounds = mesh.bounds.astype(np.float64)
    center = bounds.mean(axis=0)
    extent = float(np.max(bounds[1] - bounds[0]))
    if not np.isfinite(extent) or extent <= 0:
        raise ValueError("Mesh has zero or invalid extent")
    mesh.apply_translation(-center)
    # Leave at least one empty cell around the largest dimension after voxelizing.
    mesh.apply_scale((grid_size - 3) / extent)

    voxel_grid = mesh.voxelized(pitch=1.0).fill()
    matrix = np.asarray(voxel_grid.matrix, dtype=bool)
    source_indices = np.argwhere(matrix)
    # Center the possibly non-cubic voxel matrix in the fixed cubic output.
    start = (grid_size - np.asarray(matrix.shape, dtype=np.int64)) // 2
    indices = source_indices + start
    inside = np.all((indices >= 0) & (indices < grid_size), axis=1)
    indices = indices[inside]
    occupancy = np.zeros((grid_size, grid_size, grid_size), dtype=np.float32)
    if len(indices):
        occupancy[indices[:, 0], indices[:, 1], indices[:, 2]] = 1.0
    return occupancy


def voxel_centers(occupancy: np.ndarray, mesh_extent: float = 2.0) -> np.ndarray:
    """Convert nonzero voxel indices into centered coordinates (demo units)."""
    occupied = np.argwhere(occupancy > 0)
    if len(occupied) == 0:
        return np.empty((0, 3), dtype=np.float32)
    size = np.asarray(occupancy.shape, dtype=np.float32)
    if not (size[0] == size[1] == size[2]):
        raise ValueError("voxel_centers expects a cubic occupancy grid")
    scale = mesh_extent / max(size[0] - 2.0, 1.0)
    return ((occupied.astype(np.float32) - (size - 1.0) / 2.0) * scale).astype(np.float32)
