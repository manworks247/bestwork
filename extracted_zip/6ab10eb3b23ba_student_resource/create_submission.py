#!/usr/bin/env python3
"""
Creates the final submission.zip for the Amazon ML Challenge 2026.

Contents:
  submission/
    output/
      matching_results.tsv
      candidate_pairs.tsv
    Documentation_template.md
    code/
      business_entity_resolution/
        src/
          blocking.py
          blocking_v2.py
          features.py
          features_v2.py
          model.py
          pipeline.py
          pipeline_v2.py
          preprocessor.py
          __init__.py
        run_pipeline.py
        requirements.txt
        README.md
"""

import os
import zipfile
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def create_submission():
    output_dir = os.path.join(ROOT, "student_resource", "output")
    code_dir = os.path.join(ROOT, "student_resource", "code", "business_entity_resolution")
    doc_path = os.path.join(ROOT, "student_resource", "Documentation_template.md")
    zip_path = os.path.join(ROOT, "submission.zip")

    # Verify required files exist
    required_files = [
        (os.path.join(output_dir, "matching_results.tsv"), "output/matching_results.tsv"),
        (os.path.join(output_dir, "candidate_pairs.tsv"), "output/candidate_pairs.tsv"),
    ]

    for fpath, _ in required_files:
        if not os.path.exists(fpath):
            print(f"ERROR: Required file not found: {fpath}")
            sys.exit(1)

    print("Creating submission.zip...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Output files
        for fpath, arcname in required_files:
            zf.write(fpath, arcname)
            sz = os.path.getsize(fpath)
            print(f"  Added {arcname} ({sz:,} bytes)")

        # Optional CSV format
        csv_path = os.path.join(output_dir, "matching_pairs.csv")
        if os.path.exists(csv_path):
            zf.write(csv_path, "output/matching_pairs.csv")
            print(f"  Added output/matching_pairs.csv ({os.path.getsize(csv_path):,} bytes)")

        # 2. Documentation
        if os.path.exists(doc_path):
            zf.write(doc_path, "Documentation_template.md")
            print(f"  Added Documentation_template.md")

        # 3. Code directory
        for dirpath, dirnames, filenames in os.walk(code_dir):
            # Skip __pycache__ directories
            dirnames[:] = [d for d in dirnames if d != '__pycache__']
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                arcname = os.path.join("code", "business_entity_resolution",
                                       os.path.relpath(fpath, code_dir))
                zf.write(fpath, arcname)
                print(f"  Added {arcname}")

    zip_size = os.path.getsize(zip_path)
    print(f"\nSUCCESS: Created {zip_path} ({zip_size:,} bytes)")

    # List contents
    print("\nZip contents:")
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            print(f"  {info.filename:60s} {info.file_size:>12,} bytes")


if __name__ == "__main__":
    create_submission()
