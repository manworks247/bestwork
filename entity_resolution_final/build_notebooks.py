#!/usr/bin/env python3
"""Generate the Google Colab and SageMaker notebooks from the canonical
pipeline sources so all three environments share identical code."""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "code", "business_entity_resolution", "src")

core = open(os.path.join(SRC, "ber_core.py")).read()
pipe = open(os.path.join(SRC, "pipeline.py")).read()
validator = open(os.path.join(HERE, "utils", "validate_submission.py")).read()

DRIVE_FILE_IDS = {
    "train/train_source1.tsv":      "17iDDtk9AzDanNhBTCBuOuEGyuD7Hm1RZ",
    "train/train_source2.tsv":      "1mxUeH9v97X9nJpRA-gHFMOjeT5UbwpKK",
    "train/train_source3.tsv":      "1mYkKYF07auePjI0X74PxTCqR42Nnua9X",
    "train/train_ground_truth.tsv": "1YEMGKmoXSvLRJJ7e_-fhbfXpgNTb8GwX",
    "test/test_source1.tsv":        "1eezHtRDobL9HSSszU_JdiDEgjFN3HLrE",
    "test/test_source2.tsv":        "1caUOZ8OPejc8UqlrCX2nJRtXtNOQXfcf",
    "test/test_source3.tsv":        "1XRU_mlvUJVCEeUkoDhtC34hRdY79OjdU",
}
EXPECTED_SIZES = {
    "train/train_source1.tsv": 210069713, "train/train_source2.tsv": 489301488,
    "train/train_source3.tsv": 503705637, "train/train_ground_truth.tsv": 127015583,
    "test/test_source1.tsv": 175022086, "test/test_source2.tsv": 509456422,
    "test/test_source3.tsv": 506002772,
}


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": text.splitlines(keepends=True)}


def notebook(cells):
    return {
        "nbformat": 4, "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "cells": cells,
    }


writefile_core = "%%writefile src/ber_core.py\n" + core
writefile_pipe = "%%writefile src/pipeline.py\n" + pipe
writefile_val = "%%writefile utils/validate_submission.py\n" + validator

ids_py = json.dumps(DRIVE_FILE_IDS, indent=4)
sizes_py = json.dumps(EXPECTED_SIZES, indent=4)

download_cell = f'''# ============================================================
# STEP 2 — Get the dataset
# Option A (default): download straight from the shared Google Drive dataset
#   folder (https://drive.google.com/drive/folders/1kYWqTFLyT-6d5kql3dbubDRIWBy_eek0)
# Option B: if you already have the dataset in YOUR Drive, set
#   DATASET_DIR_IN_DRIVE below (folder containing train/ and test/) and the
#   files are copied from there instead.
# ============================================================
import os, shutil

DATASET_DIR_IN_DRIVE = ""   # e.g. "/content/drive/MyDrive/dataset" (optional)

DATA_DIR = "/content/dataset"
FILE_IDS = {ids_py}
EXPECTED = {sizes_py}

os.makedirs(DATA_DIR + "/train", exist_ok=True)
os.makedirs(DATA_DIR + "/test", exist_ok=True)

if DATASET_DIR_IN_DRIVE:
    for rel in FILE_IDS:
        srcp = os.path.join(DATASET_DIR_IN_DRIVE, rel)
        dstp = os.path.join(DATA_DIR, rel)
        if not os.path.exists(dstp):
            print("copy", srcp)
            shutil.copy(srcp, dstp)
else:
    import gdown
    for rel, fid in FILE_IDS.items():
        dstp = os.path.join(DATA_DIR, rel)
        if os.path.exists(dstp) and os.path.getsize(dstp) == EXPECTED[rel]:
            print("have", rel)
            continue
        print("downloading", rel, "...")
        gdown.download(id=fid, output=dstp, quiet=False)

for rel in FILE_IDS:
    p = os.path.join(DATA_DIR, rel)
    ok = os.path.exists(p) and os.path.getsize(p) == EXPECTED[rel]
    print(("OK  " if ok else "BAD "), rel,
          os.path.getsize(p) if os.path.exists(p) else "missing")
'''

run_cell = '''# ============================================================
# STEP 4 — Run the FULL pipeline (training + inference)
# On a standard Colab CPU runtime this takes roughly 1.5-3 hours.
# Progress is printed continuously. Re-run with --skip-train to reuse
# a trained model.
# ============================================================
!python -m src.pipeline \\
    --data-dir /content/dataset \\
    --out-dir  output \\
    --work-dir work \\
    --model-path models/matcher_lgbm.txt \\
    --train-sample 150000 \\
    --top-k 12
'''

validate_cell = '''# ============================================================
# STEP 5 — Validate the submission files (official validator rules)
# ============================================================
!python3 utils/validate_submission.py \\
    --matching output/matching_results.tsv \\
    --candidate output/candidate_pairs.tsv \\
    --test-dir /content/dataset/test
'''

save_cell = '''# ============================================================
# STEP 6 — Save results to YOUR Google Drive + build the submission zip
# Outputs are copied to OUTPUT_DRIVE_DIR (created if missing).
# ============================================================
import os, shutil, zipfile

OUTPUT_DRIVE_DIR = "/content/drive/MyDrive/BER_submission"

os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
for f in ["matching_results.tsv", "candidate_pairs.tsv"]:
    shutil.copy(f"output/{f}", os.path.join(OUTPUT_DRIVE_DIR, f))
shutil.copy("models/matcher_lgbm.txt", os.path.join(OUTPUT_DRIVE_DIR, "matcher_lgbm.txt"))
shutil.copy("models/matcher_lgbm.txt.meta.json", os.path.join(OUTPUT_DRIVE_DIR, "matcher_lgbm.txt.meta.json"))

# submission zip: output/ + code/ + documentation
zip_path = os.path.join(OUTPUT_DRIVE_DIR, "team_submission.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write("output/matching_results.tsv", "output/matching_results.tsv")
    z.write("output/candidate_pairs.tsv", "output/candidate_pairs.tsv")
    z.write("src/ber_core.py", "code/business_entity_resolution/src/ber_core.py")
    z.write("src/pipeline.py", "code/business_entity_resolution/src/pipeline.py")
    z.write("utils/validate_submission.py",
            "code/business_entity_resolution/utils/validate_submission.py")
    reqs = "numpy==1.26.4\\npandas==2.2.2\\nscikit-learn==1.5.1\\nlightgbm==4.5.0\\nrapidfuzz==3.9.6\\ntqdm==4.66.4\\n"
    z.writestr("code/business_entity_resolution/requirements.txt", reqs)
print("Saved to", OUTPUT_DRIVE_DIR)
print("Zip:", zip_path)
'''

# ------------------------- Colab notebook ---------------------------------
colab_cells = [
    md("# Business Entity Resolution — Complete End-to-End Pipeline (Google Colab)\n"
       "\n"
       "**Run all cells top to bottom (Runtime ▸ Run all).** This notebook is fully\n"
       "self-contained: it installs dependencies, fetches the dataset, trains the\n"
       "LightGBM matcher, generates `matching_results.tsv` + `candidate_pairs.tsv`,\n"
       "validates them, and saves everything (plus a submission zip) to your Google\n"
       "Drive.\n\n"
       "*Pipeline:* country partitioning → multi-key inverted-index blocking\n"
       "(top-12 candidates per Source-1 entity) → 18 RapidFuzz/token features →\n"
       "LightGBM classifier → threshold tuned for macro F₀.₅ (singletons included).\n"),
    code("# STEP 0 — Install dependencies\n"
         "!pip -q install rapidfuzz lightgbm gdown\n"
         "import os\n"
         "for d in ['src', 'utils', 'output', 'models', 'work']:\n"
         "    os.makedirs(d, exist_ok=True)\n"
         "print('ready')\n"),
    code("# STEP 1 — Mount Google Drive (used to SAVE results; dataset download\n"
         "# does not require it, but saving results does)\n"
         "from google.colab import drive\n"
         "drive.mount('/content/drive')\n"),
    code(download_cell),
    md("## STEP 3 — Write the pipeline source code\n"
       "The next three cells write the exact same code that ships in the\n"
       "submission package (`code/business_entity_resolution/`).\n"),
    code(writefile_core),
    code(writefile_pipe),
    code(writefile_val),
    code("open('src/__init__.py','w').close()\nprint('src package ready')\n"),
    code(run_cell),
    code(validate_cell),
    code("# Quick look at the outputs\n"
         "!head -5 output/matching_results.tsv\n"
         "!head -5 output/candidate_pairs.tsv\n"
         "!wc -l output/matching_results.tsv output/candidate_pairs.tsv\n"),
    code(save_cell),
]

with open(os.path.join(HERE, "google_colab", "BER_Colab_End_to_End.ipynb"), "w") as f:
    json.dump(notebook(colab_cells), f, indent=1)

# ------------------------- SageMaker notebook ------------------------------
sm_download = download_cell.replace("/content/dataset", "dataset").replace(
    '# Option B: if you already have the dataset in YOUR Drive, set\n#   DATASET_DIR_IN_DRIVE below (folder containing train/ and test/) and the\n#   files are copied from there instead.',
    '# Option B: if you uploaded the dataset to this notebook instance (via the\n#   Jupyter "Upload" button) or to S3, set DATASET_DIR_IN_DRIVE to that local\n#   folder (containing train/ and test/) and files are copied from there.')

sm_cells = [
    md("# Business Entity Resolution — Complete End-to-End Pipeline (Amazon SageMaker)\n"
       "\n"
       "Run on a SageMaker **notebook instance or Studio** (e.g. `ml.m5.2xlarge`,\n"
       "CPU is enough). Run all cells top to bottom. The notebook installs\n"
       "dependencies, fetches the dataset (or uses files you uploaded via the\n"
       "Jupyter upload button), trains the model, writes\n"
       "`output/matching_results.tsv` + `output/candidate_pairs.tsv`, validates\n"
       "them and optionally uploads everything to S3.\n"),
    code("# STEP 0 — Install dependencies\n"
         "%pip -q install rapidfuzz lightgbm gdown\n"
         "import os\n"
         "for d in ['src', 'utils', 'output', 'models', 'work', 'dataset/train', 'dataset/test']:\n"
         "    os.makedirs(d, exist_ok=True)\n"
         "print('ready')\n"),
    code(sm_download),
    md("## Write the pipeline source code (identical to the submission package)\n"),
    code(writefile_core),
    code(writefile_pipe),
    code(writefile_val),
    code("open('src/__init__.py','w').close()\nprint('src package ready')\n"),
    code(run_cell.replace("/content/dataset", "dataset")),
    code(validate_cell.replace("/content/dataset", "dataset")),
    code("# Optional — upload results to S3\n"
         "UPLOAD_TO_S3 = False\n"
         "S3_BUCKET = 'your-bucket-name'\n"
         "S3_PREFIX = 'ber-submission'\n"
         "if UPLOAD_TO_S3:\n"
         "    import boto3\n"
         "    s3 = boto3.client('s3')\n"
         "    for f in ['output/matching_results.tsv', 'output/candidate_pairs.tsv',\n"
         "              'models/matcher_lgbm.txt', 'models/matcher_lgbm.txt.meta.json']:\n"
         "        s3.upload_file(f, S3_BUCKET, f'{S3_PREFIX}/{f}')\n"
         "        print('uploaded', f)\n"),
]

with open(os.path.join(HERE, "amazon_sagemaker", "BER_SageMaker_End_to_End.ipynb"), "w") as f:
    json.dump(notebook(sm_cells), f, indent=1)

print("notebooks written")
