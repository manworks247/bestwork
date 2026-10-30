# 3D Shape Representation Lab — Sections 7.2–7.5

**Student:** J GANESH KUMAR REDDY  
**ID:** 23BDS024  
**Revised report:** `Point_Cloud_and_3D_Representations_Lab_Report_J_GANESH_KUMAR_REDDY_23BDS024.pdf` (25 pages)

This folder contains the revised submission report, local black-background terminal screenshots, raw command logs, deterministic synthetic smoke-test scripts, conversion outputs, and a page-by-page audit of both supplied reports (25 pages and 11 pages) plus the tutorial excerpt (`reference_report_analysis.md`). The report has a new DejaVu typography and visual system and repeats the student's exact name and ID in the running header/footer on every page.

## Important evidence and attribution statement

The report keeps three evidence tracks distinct:

1. **Local execution:** Python 3.11.2 / PyTorch 2.2.2, two visible CPU cores, 3.85 GiB host memory and no available CUDA device. Official ModelNet40/ModelNet10 data could not be accessed in this sandbox; SHREC data was not downloaded. Local demos use generated fixtures only.
2. **Report [9]:** selected ModelNet40/10 and SHREC metrics, class findings, timings, methods and chair-conversion values are attributed to Aggimalla Abhishek's 23BDS004 PDF; they were not rerun here.
3. **Report [11]:** Anjan Kothapally's 23BCS071 PDF reports Colab/CUDA results and conversion outputs. Its ModelNet10 count is exactly double report [9]'s standard split, its VoxelCNN score is a perfect 100% already at epoch one, and its MeshCNN training is explicitly skipped. These are source claims with validation caveats, not verified local benchmarks.

Consequently, this is **not** a local ModelNet40, ModelNet10 or SHREC benchmark report. Synthetic smoke tests must not be cited as benchmark results.

## Local smoke-test summary

- PointNet++: one-epoch upstream-code smoke on 2 synthetic train / 40 synthetic test examples; 512 points; test instance/class accuracy 0.025. The full attempt exited because `modelnet40_shape_names.txt` was missing.
- VoxelCNN: generated cube converted to a 32³ grid with 24,389 occupied cells (74.43%); untrained network logits `(1, 10)`, predicted index 7.
- MeshCNN: generated icosphere (42 vertices, 80 triangles, 120 edges); one forward pass and optimizer update; loss 3.177232. No SHREC result.
- Conversions: 4,096 sampled surface points; convex hull with 106 vertices / 208 faces; 24,389 occupied voxels and occupied-cell centers. No local Chamfer benchmark was run.

## Rebuild the revised report

Use Python 3.11+ with the dependencies in `requirements.txt` and system DejaVu Sans fonts available at `/usr/share/fonts/truetype/dejavu/` (the builder has a Helvetica fallback):

```bash
python build_report.py
```

The builder produces the 25-page PDF and three original charts derived from the reference-reported values in `outputs/figures/`. The PDF includes the original tutorial's PointNet++ setup, data layout and flags, voxel/model commands, MeshCNN workflow, conversion sampler, both source-report audits and a cross-report validation table. All source claims are distinguished from local execution. The page-by-page analyses are in `reference_report_analysis.md`.

## Re-run the local smoke suite

```bash
python -m pip install -r requirements.txt
./run_all.sh
```

The run script records output in `outputs/logs/`, renders black-background transcript images in `outputs/screenshots/`, and rebuilds the PDF. It does not replace a real dataset found inside an upstream checkout.

## Official-data commands for a suitable machine

These commands are provided for future real-data runs only. They were not executed successfully in this sandbox and do not generate benchmark numbers quoted from either supplied report.

### PointNet++ / ModelNet40

Download and unpack the aligned normal-resampled ModelNet40 release so `data/modelnet40_normal_resampled/` contains the shape-name and split files plus class point files. From the PointNet++ repository root:

```bash
python train_classification.py \
  --model pointnet2_cls_ssg \
  --log_dir pointnet2_modelnet40 \
  --num_category 40 \
  --epoch 200 \
  --batch_size 24
python test_classification.py --log_dir pointnet2_modelnet40
```

The full 200-epoch schedule is the tutorial target. The 15-epoch result in report [9] and the separate 5-epoch result in report [11] belong to those cited sources, not this local run. The upstream test script's unconditional CUDA allocations require an appropriate device or a compatible device-agnostic change.

### MeshCNN / SHREC'16

Clone `https://github.com/ranahanocka/MeshCNN`, install a compatible PyTorch environment and provide the SHREC16 archive in the expected directory. Then use the repository's `scripts/shrec/get_data.sh` and `scripts/shrec/train.sh`. No SHREC data or SHREC metrics are included in the local execution.

## Artifact map

- `Point_Cloud_and_3D_Representations_Lab_Report_...pdf` — revised submission report, reference audit, findings and all local terminal evidence screenshots.
- `reference_report_analysis.md` — page-by-page review of the 25-page 23BDS004 PDF and 11-page 23BCS071 PDF, tutorial integration notes, and discrepancy analysis.
- `outputs/logs/` — saved stdout/stderr transcripts for local commands.
- `outputs/screenshots/` — black-background terminal transcripts used in the report appendices.
- `outputs/figures/representation_conversion.png` — local synthetic-cube representation conversions.
- `outputs/figures/reference_benchmark_summary.png` — redrawn, explicitly attributed headline values from the reference report.
- `outputs/figures/reference_modelnet10_class_accuracy.png` — source-reported per-class values redrawn in the new style.
- `outputs/figures/reference_chamfer_comparison.png` — source-reported single-chair conversion errors redrawn in the new style.
- `outputs/results.json` — exact local synthetic smoke-test results and runtime metadata.
- `prepare_fixtures.py`, `run_voxel_demo.py`, `run_meshcnn_smoke.py`, `run_conversions.py` — reproducible local demonstration scripts.
