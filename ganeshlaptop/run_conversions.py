#!/usr/bin/env python3
"""Execute section 7.5 conversions using the generated ModelNet10-style mesh."""
from __future__ import annotations

from pathlib import Path
import argparse
import numpy as np
import trimesh
from scipy.spatial import ConvexHull
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from geometry_utils import load_triangle_mesh, mesh_to_voxel, voxel_centers
from prepare_fixtures import prepare

ROOT = Path(__file__).resolve().parent


def add_mesh(ax, mesh: trimesh.Trimesh, color: str) -> None:
    triangles = mesh.vertices[mesh.faces]
    collection = Poly3DCollection(triangles, facecolor=color, edgecolor="#243449", linewidth=0.22, alpha=0.82)
    ax.add_collection3d(collection)
    bounds = mesh.bounds
    center = bounds.mean(axis=0)
    radius = max(float(np.max(bounds[1] - bounds[0]) / 2.0), 1.0)
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_zlim(center[2] - radius, center[2] + radius)
    ax.set_box_aspect((1, 1, 1))


def hide_axes(ax) -> None:
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.set_xlabel(""); ax.set_ylabel(""); ax.set_zlabel("")
    ax.grid(False)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((1, 1, 1, 0))
        axis.pane.set_edgecolor((1, 1, 1, 0))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grid-size", type=int, default=32)
    args = parser.parse_args()
    fixture = prepare(ROOT)
    mesh_path = fixture["off_mesh"]
    mesh = load_triangle_mesh(mesh_path)

    np.random.seed(23)
    points, _ = trimesh.sample.sample_surface(mesh, 4096, seed=23)
    points = np.asarray(points, dtype=np.float32)
    out_dir = ROOT / "outputs"
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    np.savetxt(out_dir / "sampled_cube_4096.xyz", points, fmt="%.6f")

    hull = ConvexHull(points)
    hull_vertices = hull.vertices
    remap = np.full(len(points), -1, dtype=np.int64)
    remap[hull_vertices] = np.arange(len(hull_vertices))
    hull_faces = remap[hull.simplices]
    reconstructed = trimesh.Trimesh(vertices=points[hull_vertices], faces=hull_faces, process=True)
    reconstructed.export(out_dir / "convex_hull_reconstruction.obj")

    occupancy = mesh_to_voxel(mesh_path, grid_size=args.grid_size)
    vox_points = voxel_centers(occupancy, mesh_extent=2.0)
    np.savetxt(out_dir / "voxel_occupied_centers.xyz", vox_points, fmt="%.6f")

    print("Section 7.5 | representation conversions")
    print(f"Mesh -> point cloud: {mesh_path.relative_to(ROOT)} -> {points.shape[0]} area-uniform surface points")
    print(f"  Saved: outputs/sampled_cube_4096.xyz; array shape={points.shape}")
    print(f"Point cloud -> mesh: SciPy ConvexHull -> {len(reconstructed.vertices)} hull vertices, {len(reconstructed.faces)} triangular faces")
    print("  Method note: convex hull is used for a convex toy shape; it is not Poisson or Ball Pivoting.")
    print(f"Mesh -> voxel: occupancy shape={occupancy.shape}, active={int(occupancy.sum())} cells")
    print(f"Voxel -> point cloud: {len(vox_points)} occupied-cell centers; saved outputs/voxel_occupied_centers.xyz")
    print("STATUS: PASS — all four conversions executed on a synthetic cube fixture.")

    # A clear visual companion for the PDF: one panel for each representation.
    fig = plt.figure(figsize=(12.2, 8.2), facecolor="white")
    panels = [
        ("Triangle mesh", "#4F46E5"),
        ("Surface point cloud", "#0891B2"),
        ("Voxel occupancy centers", "#D97706"),
        ("Convex-hull reconstruction", "#059669"),
    ]
    axs = [fig.add_subplot(2, 2, i + 1, projection="3d") for i in range(4)]
    add_mesh(axs[0], mesh, panels[0][1])
    axs[0].view_init(elev=24, azim=35)
    sample_ids = np.linspace(0, len(points) - 1, min(1800, len(points)), dtype=int)
    axs[1].scatter(points[sample_ids, 0], points[sample_ids, 1], points[sample_ids, 2],
                   s=2.1, alpha=0.72, color=panels[1][1], depthshade=False)
    axs[1].set_xlim(-1.15, 1.15); axs[1].set_ylim(-1.15, 1.15); axs[1].set_zlim(-1.15, 1.15)
    axs[1].set_box_aspect((1, 1, 1)); axs[1].view_init(elev=24, azim=35)
    voxel_sample = vox_points
    if len(voxel_sample) > 1800:
        voxel_sample = voxel_sample[np.linspace(0, len(voxel_sample) - 1, 1800, dtype=int)]
    axs[2].scatter(voxel_sample[:, 0], voxel_sample[:, 1], voxel_sample[:, 2],
                   s=4.0, alpha=0.50, color=panels[2][1], depthshade=False)
    axs[2].set_xlim(-1.15, 1.15); axs[2].set_ylim(-1.15, 1.15); axs[2].set_zlim(-1.15, 1.15)
    axs[2].set_box_aspect((1, 1, 1)); axs[2].view_init(elev=24, azim=35)
    add_mesh(axs[3], reconstructed, panels[3][1])
    axs[3].view_init(elev=24, azim=35)
    for ax, (title, _) in zip(axs, panels):
        ax.set_title(title, fontsize=13, fontweight="semibold", pad=8, color="#172033")
        hide_axes(ax)
    fig.suptitle("Section 7.5 · Converting between 3D representations", fontsize=18,
                 fontweight="bold", color="#10253F", y=0.98)
    fig.text(0.5, 0.02, "Synthetic cube fixture · 4,096 surface samples · 32³ occupancy grid",
             ha="center", fontsize=10, color="#526477")
    fig.tight_layout(rect=(0.03, 0.05, 0.97, 0.94), w_pad=1.2, h_pad=1.6)
    fig.savefig(fig_dir / "representation_conversion.png", dpi=190, bbox_inches="tight")
    plt.close(fig)
    print("Figure saved: outputs/figures/representation_conversion.png")


if __name__ == "__main__":
    main()
