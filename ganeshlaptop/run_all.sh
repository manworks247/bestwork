#!/usr/bin/env bash
# Re-run the CPU smoke tests and rebuild all screenshots + the submission PDF.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PYTHON="${PYTHON:-python3}"
EXTERNAL="${EXTERNAL_ROOT:-$ROOT/external}"
POINTNET2_ROOT="${POINTNET2_ROOT:-$EXTERNAL/Pointnet_Pointnet2_pytorch}"
MESH_CNN_ROOT="${MESH_CNN_ROOT:-$EXTERNAL/MeshCNN}"
mkdir -p "$ROOT/outputs/logs" "$ROOT/outputs/screenshots" "$ROOT/outputs/figures" "$EXTERNAL"

if ! "$PYTHON" -c 'import torch, numpy, scipy, trimesh, matplotlib, reportlab, PIL' >/dev/null 2>&1; then
  echo "Missing experiment/report packages. Install: $PYTHON -m pip install -r '$ROOT/requirements.txt'" >&2
  exit 2
fi

"$PYTHON" environment_check.py 2>&1 | tee "$ROOT/outputs/logs/00_environment.log"
"$PYTHON" prepare_fixtures.py 2>&1 | tee "$ROOT/outputs/logs/00_fixture_generation.log"

if [[ ! -d "$POINTNET2_ROOT/.git" ]]; then
  git clone --depth 1 https://github.com/yanx27/Pointnet_Pointnet2_pytorch.git "$POINTNET2_ROOT"
fi
if [[ ! -d "$MESH_CNN_ROOT/.git" ]]; then
  git clone --depth 1 https://github.com/ranahanocka/MeshCNN.git "$MESH_CNN_ROOT"
fi

# Record and verify the expected upstream-dataset failure only when the clone
# does not already contain a real dataset. Never overwrite a user's dataset.
if [[ ! -e "$POINTNET2_ROOT/data/modelnet40_normal_resampled" && ! -L "$POINTNET2_ROOT/data/modelnet40_normal_resampled" ]]; then
  set +e
  (cd "$POINTNET2_ROOT" && OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    "$PYTHON" train_classification.py --model pointnet2_cls_ssg --log_dir pointnet2_modelnet40 \
    --num_category 40 --epoch 200 --batch_size 24 --use_cpu) \
    > "$ROOT/outputs/logs/02_full_pointnet_attempt.log" 2>&1
  full_status=$?
  set -e
  echo "EXIT_CODE=$full_status" >> "$ROOT/outputs/logs/02_full_pointnet_attempt.log"
fi

# Use only the reproducible miniature fixture for this smoke run.
mkdir -p "$POINTNET2_ROOT/data"
DATA_LINK="$POINTNET2_ROOT/data/modelnet40_normal_resampled"
if [[ -e "$DATA_LINK" || -L "$DATA_LINK" ]]; then
  if [[ -L "$DATA_LINK" && "$(readlink -f "$DATA_LINK" || true)" == "$(readlink -f "$ROOT/data/synthetic_modelnet40_normal_resampled")" ]]; then
    rm -f "$DATA_LINK"
  else
    echo "Refusing to replace existing ModelNet40 data at $DATA_LINK" >&2
    echo "Use a clean clone for the smoke test, or set POINTNET2_ROOT to another directory." >&2
    exit 3
  fi
fi
ln -s "$ROOT/data/synthetic_modelnet40_normal_resampled" "$DATA_LINK"
rm -rf "$POINTNET2_ROOT/log/classification/pointnet2_synthetic_smoke"
set +e
(cd "$POINTNET2_ROOT" && OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONUNBUFFERED=1 \
  "$PYTHON" train_classification.py --model pointnet2_cls_ssg --log_dir pointnet2_synthetic_smoke \
  --num_category 40 --epoch 1 --batch_size 2 --num_point 512 --use_cpu) \
  > "$ROOT/outputs/logs/03_pointnet_smoke.log" 2>&1
pointnet_status=$?
set -e
echo "EXIT_CODE=$pointnet_status" >> "$ROOT/outputs/logs/03_pointnet_smoke.log"
rm -f "$POINTNET2_ROOT/data/modelnet40_normal_resampled"
if [[ $pointnet_status -ne 0 ]]; then cat "$ROOT/outputs/logs/03_pointnet_smoke.log"; exit "$pointnet_status"; fi

OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "$PYTHON" run_voxel_demo.py --grid-size 32 \
  > "$ROOT/outputs/logs/04_voxel_demo.log" 2>&1 || { cat "$ROOT/outputs/logs/04_voxel_demo.log"; exit 1; }
echo "EXIT_CODE=0" >> "$ROOT/outputs/logs/04_voxel_demo.log"
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 "$PYTHON" run_meshcnn_smoke.py --meshcnn-root "$MESH_CNN_ROOT" \
  > "$ROOT/outputs/logs/05_meshcnn_smoke.log" 2>&1 || { cat "$ROOT/outputs/logs/05_meshcnn_smoke.log"; exit 1; }
echo "EXIT_CODE=0" >> "$ROOT/outputs/logs/05_meshcnn_smoke.log"
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 "$PYTHON" run_conversions.py --grid-size 32 \
  > "$ROOT/outputs/logs/06_conversions.log" 2>&1 || { cat "$ROOT/outputs/logs/06_conversions.log"; exit 1; }
echo "EXIT_CODE=0" >> "$ROOT/outputs/logs/06_conversions.log"

"$PYTHON" render_terminal_screenshots.py
"$PYTHON" build_report.py --pointnet-root "$POINTNET2_ROOT" --meshcnn-root "$MESH_CNN_ROOT"
echo "Done. PDF: $ROOT/Point_Cloud_and_3D_Representations_Lab_Report_J_GANESH_KUMAR_REDDY_23BDS024.pdf"
