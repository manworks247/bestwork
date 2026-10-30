# 3D Shape Representation Lab — Sections 7.2–7.5

**Student:** J GANESH KUMAR REDDY  
**ID:** 23BDS024  
**Report:** `Point_Cloud_and_3D_Representations_Lab_Report_J_GANESH_KUMAR_REDDY_23BDS024.pdf`

This folder contains a submission report, terminal transcript screenshots (black background), raw command logs, the small smoke-test source scripts, and the generated mesh/point-cloud/voxel conversion artifacts.

## Important scope statement

The sandbox had Python 3.11.2, two visible CPU cores, and no available CUDA device. The upstream instructions request older Python/CUDA stacks. The ModelNet40 and ModelNet10 archive endpoints could not be reached from this environment; the upstream MeshCNN SHREC script likewise obtains its archive from Dropbox. Therefore this is **not** a ModelNet40/SHREC benchmark report: no full 200-epoch ModelNet40 run, ModelNet10 result, SHREC training, or benchmark accuracy is claimed.

To execute meaningful code paths without fabricating benchmark results, the report includes (a) a one-epoch smoke run of the upstream PointNet++ training script on deterministic synthetic clouds, (b) a 3D CNN forward pass on a generated cube mesh, (c) one MeshCNN optimizer step on an icosphere fixture, and (d) all four representation conversions. The PointNet++ and MeshCNN source checkouts used for the captured run are identified by commit in the report. The smoke fixtures are generated locally by `prepare_fixtures.py` and are explicitly not ModelNet/SHREC samples.

## Re-run smoke tests

Use Python 3.11+ and the dependencies in `requirements.txt`. Set `POINTNET2_ROOT` / `MESH_CNN_ROOT` to existing upstream clones if preferred; otherwise `run_all.sh` clones the repositories under ignored `external/`.

```bash
python -m pip install -r requirements.txt
./run_all.sh
```

The run script records output in `outputs/logs/`, renders black terminal transcript screenshots in `outputs/screenshots/`, and rebuilds the PDF. It does not replace a real dataset found inside an upstream checkout.

## Real-data commands (when the official data and a compatible machine are available)

### PointNet++ / ModelNet40

Download and unpack the aligned normal-resampled ModelNet40 release so that `data/modelnet40_normal_resampled/` contains `modelnet40_shape_names.txt`, `modelnet40_train.txt`, `modelnet40_test.txt`, and class folders with point files. From the PointNet++ repository root, run:

```bash
python train_classification.py \
  --model pointnet2_cls_ssg \
  --log_dir pointnet2_modelnet40 \
  --num_category 40 \
  --epoch 200 \
  --batch_size 24
python test_classification.py --log_dir pointnet2_modelnet40
```

The smoke-test source runs with `--use_cpu`; use a GPU-enabled install for the full experiment when available. From this folder, the helper can be invoked as `POINTNET2_ROOT=/path/to/Pointnet_Pointnet2_pytorch ./run_full_pointnet2.sh`. The upstream test script currently allocates its vote pool with `.cuda()` unconditionally, so its CPU-only test path needs a small upstream fix.

### MeshCNN / SHREC

Clone `https://github.com/ranahanocka/MeshCNN`, install the versions in its environment file or a compatible PyTorch environment, and provide the SHREC16 archive in the expected directory. Then run the repository's `scripts/shrec/train.sh`, `test.sh`, and `view.sh`. No SHREC data or SHREC metrics are included in this submission. When SHREC16 is available, `MESH_CNN_ROOT=/path/to/MeshCNN ./run_full_meshcnn.sh` runs the upstream train/test/view scripts.

## Artifact map

- `Point_Cloud_and_3D_Representations_Lab_Report_...pdf` — submission-ready report with findings and all terminal evidence screenshots.
- `outputs/logs/` — saved stdout/stderr transcripts for the executed commands.
- `outputs/screenshots/` — black terminal transcript screenshots rendered from those saved logs.
- `outputs/figures/representation_conversion.png` — visual summary of the conversions.
- `outputs/sampled_cube_4096.xyz`, `outputs/voxel_occupied_centers.xyz`, `outputs/convex_hull_reconstruction.obj` — generated demonstration outputs.
- `prepare_fixtures.py`, `run_voxel_demo.py`, `run_meshcnn_smoke.py`, `run_conversions.py` — reproducible experiment scripts.
