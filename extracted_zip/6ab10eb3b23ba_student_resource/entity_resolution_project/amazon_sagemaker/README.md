# Amazon SageMaker - Business Entity Resolution Pipeline

This folder contains the complete, self-contained pipeline adapted for execution in **Amazon SageMaker Studio**, **SageMaker Notebook Instances**, and **SageMaker Processing / Training Jobs**.

## Architecture Overview
- **Blocking / Candidate Generation**: Multi-key lexical inverted index partitioned by country (`France`, `US`, `India`).
- **Feature Extraction**: RapidFuzz string, token, and numeric alignment metrics.
- **Model Classifier**: LightGBM GBDT with probability threshold calibrated for Macro $F_{0.5}$.
- **Inference**: High-throughput vectorized C++ booster predict.

## Files
- `sagemaker_train_and_inference.py`: Master SageMaker entrypoint script accepting `--train`, `--test`, `--model-dir`, and `--output-data-dir` arguments. Supports `--version 1` and `--version 2`.
- `sagemaker_pipeline.ipynb`: Interactive Jupyter Notebook for executing the pipeline step-by-step within SageMaker Studio or Notebook instances.
- `src/`: Modular source code for blocking, feature extraction, model definition, and end-to-end orchestration.
- `requirements.txt`: Environment dependencies pinned for SageMaker.

## Execution

### Option 1: Direct Studio / Terminal Run
```bash
pip install -r requirements.txt

# Run complete end-to-end pipeline (train + test inference)
python sagemaker_train_and_inference.py \
    --train /opt/ml/input/data/train \
    --test /opt/ml/input/data/test \
    --model-dir /opt/ml/model \
    --output-data-dir /opt/ml/output/data \
    --mode all
```

### Option 2: SageMaker Estimator (Cloud Training Job)
```python
import sagemaker
from sagemaker.pytorch import PyTorch

estimator = PyTorch(
    entry_point="sagemaker_train_and_inference.py",
    source_dir="src",
    role=sagemaker.get_execution_role(),
    instance_count=1,
    instance_type="ml.c5.4xlarge",
    framework_version="2.0.0",
    py_version="py310",
    hyperparameters={
        "mode": "all",
        "sample-entities": 50000,
        "version": 1
    }
)
estimator.fit({"train": "s3://my-bucket/dataset/train", "test": "s3://my-bucket/dataset/test"})
```

### Validation
```bash
python utils/validate_submission.py \
    --matching output/matching_results.tsv \
    --candidate output/candidate_pairs.tsv \
    --test-dir dataset/test
```
