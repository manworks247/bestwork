#!/usr/bin/env bash
# Full SHREC16 training/evaluation/visualization sequence (requires SHREC data).
set -euo pipefail
MESH_CNN_ROOT="${MESH_CNN_ROOT:-$PWD}"
if [[ ! -f "$MESH_CNN_ROOT/train.py" || ! -f "$MESH_CNN_ROOT/scripts/shrec/train.sh" ]]; then
  echo "Set MESH_CNN_ROOT to a cloned ranahanocka/MeshCNN repository." >&2
  exit 2
fi
cd "$MESH_CNN_ROOT"
if [[ ! -d datasets/shrec_16 ]]; then
  echo "SHREC16 data is missing; run the repository's scripts/shrec/get_data.sh after obtaining the archive." >&2
  exit 3
fi
bash scripts/shrec/train.sh
bash scripts/shrec/test.sh
bash scripts/shrec/view.sh
