#!/usr/bin/env bash
# Full benchmark command (run only after installing the real aligned ModelNet40 data).
set -euo pipefail
POINTNET2_ROOT="${POINTNET2_ROOT:-$PWD}"
if [[ ! -f "$POINTNET2_ROOT/train_classification.py" ]]; then
  echo "Set POINTNET2_ROOT to a cloned yanx27/Pointnet_Pointnet2_pytorch repository." >&2
  exit 2
fi
cd "$POINTNET2_ROOT"
if [[ ! -f data/modelnet40_normal_resampled/modelnet40_shape_names.txt ]]; then
  echo "ModelNet40 normal_resampled data is missing. See the ganeshlaptop README for the required layout." >&2
  exit 2
fi
python train_classification.py \
  --model pointnet2_cls_ssg \
  --log_dir pointnet2_modelnet40 \
  --num_category 40 \
  --epoch 200 \
  --batch_size 24
# On a CPU-only host, add: --use_cpu
# After training, upstream test_classification.py currently assumes CUDA for vote_pool;
# use the full dataset's best checkpoint with the upstream environment/GPU, or patch that line.
python test_classification.py --log_dir pointnet2_modelnet40
