# Entity Resolution — Final Project

Complete, runnable Business Entity Resolution solution in three environments:

| Folder | Use |
|---|---|
| `local_execution/` | run on your own machine (`python run_pipeline.py --data-dir <dataset>`) |
| `google_colab/`    | `BER_Colab_End_to_End.ipynb` — fully self-contained Colab notebook (Runtime ▸ Run all) |
| `amazon_sagemaker/`| `BER_SageMaker_End_to_End.ipynb` — same pipeline for SageMaker notebook instances / Studio |
| `code/business_entity_resolution/` | canonical pipeline source (`src/ber_core.py`, `src/pipeline.py`) — this is what goes in the submission zip |
| `utils/` | official submission validator |
| `output/` | generated `matching_results.tsv` + `candidate_pairs.tsv` |

`build_notebooks.py` regenerates both notebooks from the canonical source so
all three environments always run identical code.

Dataset: the challenge `dataset/` folder with `train/` and `test/` subfolders
(tab-separated files). The Colab/SageMaker notebooks can download it
automatically from the shared Google Drive folder, or use a path you provide.
