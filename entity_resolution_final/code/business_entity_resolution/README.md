# Business Entity Resolution — Pipeline

End-to-end pipeline for the ML Challenge 2026 Business Entity Resolution task:
for every Source-1 entity, find all matching Source-2/Source-3 records.

## Approach (summary)

1. **Country partitioning** — records are streamed and split per `country`
   (open set of labels; France or any unseen country is handled identically).
2. **Blocking / candidate generation** — an inverted index over Source-2/3
   records using multiple keys (full compressed name, name prefix, first-two
   core tokens, individual rare tokens, name-token + house-number). Each
   Source-1 record retrieves its top-K (default 12) candidates by accumulated,
   frequency-aware key weight. *This exact candidate set is written to
   `candidate_pairs.tsv`.*
3. **Matching model** — a LightGBM binary classifier over 18 RapidFuzz /
   token-overlap features per pair, trained on candidates generated the same
   way from the training split and labelled with `train_ground_truth.tsv`.
4. **Decision** — a global probability threshold tuned on a held-out 20% of
   training S1 entities to maximise **macro F_0.5** (singletons included).

No external data, APIs, geocoders or gazetteers are used — only the provided
records plus small hand-written normalization dictionaries. LightGBM is MIT
licensed and far below the 8B-parameter limit.

## Reproduce end-to-end

```bash
pip install -r requirements.txt

# dataset/ must contain train/ and test/ as distributed with the challenge
python -m src.pipeline \
    --data-dir /path/to/dataset \
    --out-dir  output \
    --work-dir work \
    --model-path models/matcher_lgbm.txt \
    --train-sample 150000 \
    --top-k 12
```

Outputs:

* `output/matching_results.tsv` — final matches (leaderboard file)
* `output/candidate_pairs.tsv` — blocking candidate set fed to the model
* `models/matcher_lgbm.txt` (+ `.meta.json` with the tuned threshold)

To re-run inference only with a saved model add `--skip-train`.

Validate before submitting:

```bash
python3 utils/validate_submission.py \
    --matching output/matching_results.tsv \
    --candidate output/candidate_pairs.tsv \
    --test-dir /path/to/dataset/test
```

## Hardware

Runs on a 2-core / 4 GB machine in a few hours (the pipeline is streamed and
country-partitioned so memory stays bounded); on an 8-core Colab/SageMaker
instance it is considerably faster. No GPU required.
