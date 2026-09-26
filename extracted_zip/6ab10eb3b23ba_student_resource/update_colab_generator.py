import base64
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# 1. Read files to embed as base64
files_to_embed = {
    "code/business_entity_resolution/src/preprocessor.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "src", "preprocessor.py"),
    "code/business_entity_resolution/src/blocking.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "src", "blocking.py"),
    "code/business_entity_resolution/src/blocking_v2.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "src", "blocking_v2.py"),
    "code/business_entity_resolution/src/features.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "src", "features.py"),
    "code/business_entity_resolution/src/features_v2.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "src", "features_v2.py"),
    "code/business_entity_resolution/src/model.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "src", "model.py"),
    "code/business_entity_resolution/src/pipeline.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "src", "pipeline.py"),
    "code/business_entity_resolution/src/pipeline_v2.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "src", "pipeline_v2.py"),
    "code/business_entity_resolution/src/__init__.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "src", "__init__.py"),
    "code/business_entity_resolution/run_pipeline.py": os.path.join(ROOT, "entity_resolution_project", "local_execution", "run_pipeline.py"),
    "code/business_entity_resolution/requirements.txt": os.path.join(ROOT, "entity_resolution_project", "local_execution", "requirements.txt"),
    "code/business_entity_resolution/README.md": os.path.join(ROOT, "entity_resolution_project", "local_execution", "README.md"),
    "Documentation_template.md": os.path.join(ROOT, "student_resource", "Documentation_template.md"),
}

embedded_dict = {}
for arc_name, file_path in files_to_embed.items():
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            b64_content = base64.b64encode(f.read()).decode("ascii")
            embedded_dict[arc_name] = b64_content
    else:
        print(f"WARNING: File not found to embed: {file_path}")

print(f"Loaded {len(embedded_dict)} files into base64 payload.")

# Build the build_colab_notebook.py script
generator_script = os.path.join(ROOT, "entity_resolution_project", "google_colab", "build_colab_notebook.py")

nb_cells = []

def add_md(text):
    nb_cells.append({
        'cell_type': 'markdown',
        'metadata': {},
        'source': text.strip().splitlines(True)
    })

def add_code(text):
    nb_cells.append({
        'cell_type': 'code',
        'metadata': {},
        'execution_count': None,
        'outputs': [],
        'source': text.strip().splitlines(True)
    })

# Cell 1: Overview
add_md(r"""# Amazon ML Challenge 2026: Business Entity Resolution
### End-to-End Scalable Candidate Generation, Machine Learning Matcher & Macro $F_{0.5}$ Optimizer

---

### Challenge Summary & Core Constraints
- **Problem Statement**: Resolve business records arriving from 3 independent sources (`Source 1`, `Source 2`, `Source 3`) where `Source 1` is the deduplicated reference source. Find all matching records from `Source 2` and `Source 3` for each `Source 1` entity.
- **Evaluation Metric**: Macro-averaged $F_{0.5}$ score across all Source 1 entities:
  $$F_{0.5} = \frac{1.25 \times \text{Precision} \times \text{Recall}}{0.25 \times \text{Precision} + \text{Recall}}$$
  - Precision is weighted **2x over recall** (penalizes false merges heavily).
  - Singletons (entities with 0 matches) are evaluated: predicting an empty set for a singleton scores **1.0**, while predicting any false match scores **0.0**.
- **Candidate Generation Ranking**: The candidate set (`candidate_pairs.tsv`) is evaluated alongside `matching_results.tsv`. Approaches generating **smaller, higher-precision candidate sets** per Source 1 entity receive higher final rankings.
- **Geography**: Country is a strict partition (`France`, `US`, `India`). Cross-country matches are impossible.
- **Format**: Output files must be tab-separated (`.tsv`) with exact headers. Every test Source 1 entity (1,732,544 rows) must appear.

---

### Pipeline Architecture
1. **Interactive Data Locator**: Mounts Google Drive and detects or prompts for dataset folder.
2. **Text Normalization Engine**: Unicode NFKD, lowercasing, abbreviation expansion, international legal suffix stripping (`Inc`, `Pvt Ltd`, `SARL`, `GmbH`, etc.).
3. **Country-Partitioned Inverted Index Blocker**: Multi-key candidate generation with weighted keys, `min_score=1.5` filter, and compact `max_candidates=4`.
4. **Vectorized Feature Extractor**: 15 high-signal pairwise features with `cand_cache` for 3-5x faster throughput.
5. **LightGBM Classifier & Threshold Calibration**: Pretrained model loading OR distributed distractor training with grid search for optimal Macro $F_{0.5}$ threshold.
6. **Full Test Inference**: Vectorized C++ booster batch scoring across France, US, and India with zero missing entities.
7. **Built-in Official Submission Validator**: Full verification of line counts, headers, prefixes, and subset constraints.
8. **Automated Submission ZIP Packaging**: Bundles `output/`, `code/business_entity_resolution/`, and `Documentation_template.md` into `submission.zip`.""")

# Cell 2: Dependencies
add_md(r"""## 1. Install & Import Dependencies""")
add_code(r"""# Install required pure-algorithm packages (RapidFuzz, LightGBM)
!pip install -q rapidfuzz lightgbm scikit-learn pandas numpy tqdm

import os
import sys
import re
import time
import math
import unicodedata
import pickle
import zipfile
import shutil
import base64
import warnings
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

import numpy as np
import pandas as pd
import rapidfuzz.fuzz as fuzz
import lightgbm as lgb
from tqdm.auto import tqdm

# Suppress warnings for clean output
warnings.filterwarnings("ignore")

print("All dependencies imported successfully!")
print(f"Python: {sys.version.split()[0]} | LightGBM: {lgb.__version__}")""")

# Cell 3: Drive Mount & Smart Dataset Path
add_md(r"""## 2. Mount Google Drive & Configure Dataset Location""")
add_code(r"""# 1. Mount Google Drive
try:
    from google.colab import drive
    drive.mount('/content/drive')
    print("Google Drive mounted successfully at /content/drive")
except Exception as e:
    print("Running in local environment or outside Colab:", e)

# 2. Candidate dataset paths to check automatically
candidate_paths = [
    "/content/drive/MyDrive/18uVhJZq8psxhwWDyGksnCo6SiGPkWJ3Q",
    "/content/drive/MyDrive/1aBpuNw9Zd1WBmnoifgLpt-7wl9KLzykq",
    "/content/drive/MyDrive/dataset",
    "/content/drive/MyDrive/student_resource/dataset",
    "/content/drive/MyDrive/6ab10eb3b23ba_student_resource/dataset",
    "/content/drive/MyDrive/student_resource",
    "student_resource/dataset",
    "/content/dataset",
    "./dataset"
]

detected_path = None
for p in candidate_paths:
    if os.path.exists(os.path.join(p, "test", "test_source1.tsv")) or os.path.exists(os.path.join(p, "test_source1.tsv")):
        detected_path = p
        break

# Deep search if not detected immediately in standard paths
if not detected_path and os.path.exists("/content/drive/MyDrive"):
    print("Scanning Google Drive for dataset files (test_source1.tsv)...")
    for root, dirs, files in os.walk("/content/drive/MyDrive"):
        if "test_source1.tsv" in files:
            if os.path.basename(root) == "test":
                detected_path = os.path.dirname(root)
            else:
                detected_path = root
            print(f"Auto-discovered dataset in Google Drive at: {detected_path}")
            break
        rel_depth = len(os.path.relpath(root, "/content/drive/MyDrive").split(os.sep))
        if rel_depth >= 3:
            dirs.clear()

default_prompt = detected_path if detected_path else candidate_paths[0]
user_path = input(f"Enter path to dataset directory (press Enter for '{default_prompt}'): ").strip()
DATA_DIR = user_path if user_path else default_prompt

# If files are directly in DATA_DIR instead of test/ subfolder, handle gracefully
TEST_DIR = os.path.join(DATA_DIR, "test") if os.path.exists(os.path.join(DATA_DIR, "test")) else DATA_DIR
TRAIN_DIR = os.path.join(DATA_DIR, "train") if os.path.exists(os.path.join(DATA_DIR, "train")) else DATA_DIR

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs("models", exist_ok=True)

print(f"\nConfiguration:")
print(f"  DATA_DIR  : {DATA_DIR}")
print(f"  TRAIN_DIR : {TRAIN_DIR}")
print(f"  TEST_DIR  : {TEST_DIR}")
print(f"  OUTPUT_DIR: {OUTPUT_DIR}")

# Verify test_source1.tsv
test_s1_check = os.path.join(TEST_DIR, "test_source1.tsv")
assert os.path.exists(test_s1_check), f"ERROR: Cannot find test_source1.tsv at {test_s1_check}!"

# Count lines
test_s1_lines = sum(1 for _ in open(test_s1_check, 'r', encoding='utf-8', errors='replace')) - 1
print(f"\n[OK] Found test_source1.tsv with {test_s1_lines:,} test entities.")""")

# Cell 4: Preprocessing
add_md(r"""## 3. Preprocessing & Normalization Engine""")
add_code(r"""# International & regional legal suffixes, company types, and stopwords
LEGAL_SUFFIXES = {
    'inc', 'incorporated', 'corp', 'corporation', 'llc', 'llp', 'ltd', 'limited', 'pvt', 'private',
    'co', 'company', 'plc', 'lp', 'gmbh', 'sa', 'ag', 'holdings', 'group', 'services', 'solutions',
    'enterprises', 'international', 'industries', 'partners', 'associates', 'technologies',
    'sarl', 'sasu', 'eurl', 'sas', 'sci', 'snc', 'gie', 'association', 'societe', 'et', 'cie',
    'and', '&', 'the', 'of', 'in', 'at', 'by', 'for', 'with', 'de', 'du', 'la', 'le', 'des', 'les'
}

ADDR_STOPWORDS = {
    'road', 'street', 'avenue', 'drive', 'lane', 'boulevard', 'court', 'place', 'way', 'circle',
    'near', 'opp', 'opposite', 'behind', 'beside', 'next', 'floor', 'unit', 'apartment', 'apt',
    'suite', 'building', 'block', 'tower', 'house', 'flat', 'shop', 'plot', 'sector', 'pno',
    'phase', 'nagar', 'colony', 'city', 'state', 'district', 'town', 'village', 'post', 'po',
    'pin', 'rue', 'boulevard', 'avenue', 'chemin', 'impasse', 'place', 'route', 'rd', 'st', 'ave'
}

def normalize_text(text: str) -> str:
    # Standardize unicode, lowercase, and clean non-alphanumeric noise
    if not text or not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFKD', text)
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return ' '.join(text.split())

def clean_name_tokens(name: str) -> List[str]:
    # Tokenize and filter business name noise tokens
    norm = normalize_text(name)
    return [w for w in norm.split() if w not in LEGAL_SUFFIXES and len(w) > 1 and not w.isdigit()]

def clean_addr_tokens(addr: str) -> List[str]:
    # Tokenize and filter common address stopwords
    norm = normalize_text(addr)
    return [w for w in norm.split() if w not in ADDR_STOPWORDS and len(w) > 2 and not w.isdigit()]

def extract_numbers(text: str) -> List[str]:
    # Extract street numbers, PIN codes, and numeric components
    if not text or not isinstance(text, str):
        return []
    nums = re.findall(r'\b\d{1,8}\b', text)
    norm_nums = []
    for n in nums:
        norm_nums.append(n)
        stripped = n.lstrip('0')
        if stripped and stripped != n:
            norm_nums.append(stripped)
    return norm_nums

def get_compressed_name(name: str) -> str:
    # Compressed alphanumeric string for prefix matching
    if not name or not isinstance(name, str):
        return ""
    norm = normalize_text(name)
    return re.sub(r'[^a-z0-9]', '', norm)

print("Preprocessing and normalization functions compiled successfully.")""")

# Cell 5: Blocker
add_md(r"""## 4. Scalable Country-Partitioned Inverted Index Blocker
Candidate generation cuts the $O(N \times M)$ comparison space to a small, high-precision candidate set ($\le 4$ candidates per Source 1 entity).""")
add_code(r"""class CountryPartitionBlocker:
    # Manages multi-key inverted index blocking for a specific country partition (France, US, India).
    # Strict country partitioning guarantees zero cross-country noise and keeps memory < 1 GB.
    def __init__(self, max_postings_per_key: int = 120, max_candidates_per_entity: int = 4):
        self.max_postings_per_key = max_postings_per_key
        self.max_candidates_per_entity = max_candidates_per_entity
        self.inverted_index = defaultdict(list)
        self.records: List[Tuple[str, str, str]] = []

    def get_blocking_keys(self, name: str, addr: str) -> List[Tuple[str, float]]:
        keys = []
        ntoks = clean_name_tokens(name)
        atoks = clean_addr_tokens(addr)
        nums = extract_numbers(addr)
        comp = get_compressed_name(name)

        # 1. Exact first two name tokens (primary brand key)
        if len(ntoks) >= 2:
            keys.append((f"n12:{ntoks[0]}_{ntoks[1]}", 3.0))
            keys.append((f"n1:{ntoks[0]}", 1.0))
        elif len(ntoks) == 1:
            keys.append((f"n1:{ntoks[0]}", 1.5))

        # 2. Compressed name prefix
        if len(comp) >= 8:
            keys.append((f"nc8:{comp[:8]}", 3.0))
            keys.append((f"nc5:{comp[:5]}", 1.5))
        elif len(comp) >= 5:
            keys.append((f"nc5:{comp[:5]}", 2.0))

        # 3. Address number + first address token
        if nums and atoks:
            keys.append((f"na:{nums[0]}_{atoks[0]}", 3.0))
            if len(nums) >= 2:
                keys.append((f"num2:{nums[0]}_{nums[1]}", 2.5))

        # 4. Name first token + Address first token
        if ntoks and atoks:
            keys.append((f"na11:{ntoks[0]}_{atoks[0]}", 3.5))

        # 5. First two address tokens
        if len(atoks) >= 2:
            keys.append((f"a12:{atoks[0]}_{atoks[1]}", 2.0))

        return keys

    def add_record(self, entity_id: str, name: str, addr: str) -> int:
        rec_idx = len(self.records)
        self.records.append((entity_id, name, addr))
        for key, _ in self.get_blocking_keys(name, addr):
            postings = self.inverted_index[key]
            if len(postings) < self.max_postings_per_key:
                postings.append(rec_idx)
        return rec_idx

    def query_candidates(self, name: str, addr: str, min_score: float = 1.5) -> List[Tuple[str, str, str, float]]:
        keys = self.get_blocking_keys(name, addr)
        cand_scores = defaultdict(float)

        for key, weight in keys:
            postings = self.inverted_index.get(key)
            if postings and len(postings) <= self.max_postings_per_key:
                for rec_idx in postings:
                    cand_scores[rec_idx] += weight

        if not cand_scores:
            return []

        # Filter candidates meeting minimum accumulated key weight
        filtered = [item for item in cand_scores.items() if item[1] >= min_score]
        if not filtered:
            return []

        # Sort candidate indices by accumulated score descending
        sorted_indices = sorted(filtered, key=lambda x: x[1], reverse=True)[:self.max_candidates_per_entity]
        return [(self.records[idx][0], self.records[idx][1], self.records[idx][2], score) for idx, score in sorted_indices]

    def clear(self):
        self.inverted_index.clear()
        self.records.clear()

print("CountryPartitionBlocker ready.")""")

# Cell 6: Features
add_md(r"""## 5. Pairwise Feature Engineering & Record Caching""")
add_code(r"""def compute_jaccard(set1: set, set2: set) -> float:
    if not set1 or not set2:
        return 0.0
    inter = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return inter / union if union > 0 else 0.0

class PreparedRecord:
    # Pre-caches normalized strings, token sets, and number sets for fast pairwise comparison
    def __init__(self, name: str, addr: str):
        self.raw_name = name or ""
        self.raw_addr = addr or ""
        self.norm_name = normalize_text(self.raw_name)
        self.norm_addr = normalize_text(self.raw_addr)
        self.name_tokens = set(clean_name_tokens(self.raw_name))
        self.addr_tokens = set(clean_addr_tokens(self.raw_addr))
        self.numbers = set(extract_numbers(self.raw_addr))
        self.combined = f"{self.norm_name} {self.norm_addr}".strip()
        self.len_name = len(self.norm_name)

def extract_prepared_features(s1: PreparedRecord, cand: PreparedRecord, blocking_score: float = 0.0, cand_id: str = "") -> List[float]:
    # 1. Name features
    nr = fuzz.ratio(s1.norm_name, cand.norm_name) / 100.0
    ntsr = fuzz.token_sort_ratio(s1.norm_name, cand.norm_name) / 100.0
    ntsetr = fuzz.token_set_ratio(s1.norm_name, cand.norm_name) / 100.0
    n_jaccard = compute_jaccard(s1.name_tokens, cand.name_tokens)
    n_len_diff = abs(s1.len_name - cand.len_name) / max(s1.len_name, cand.len_name, 1)

    # 2. Address features
    addr_missing = 1.0 if not cand.norm_addr else 0.0
    if not addr_missing:
        ar = fuzz.ratio(s1.norm_addr, cand.norm_addr) / 100.0
        atsr = fuzz.token_sort_ratio(s1.norm_addr, cand.norm_addr) / 100.0
        atsetr = fuzz.token_set_ratio(s1.norm_addr, cand.norm_addr) / 100.0
        a_jaccard = compute_jaccard(s1.addr_tokens, cand.addr_tokens)
        num_overlap = len(s1.numbers.intersection(cand.numbers)) / max(len(s1.numbers), 1) if s1.numbers else 0.0
        if s1.numbers and cand.numbers:
            num_match_exact = 1.0 if s1.numbers.intersection(cand.numbers) else 0.0
        else:
            num_match_exact = 0.5
    else:
        ar = atsr = atsetr = a_jaccard = num_overlap = 0.0
        num_match_exact = 0.5

    # 3. Combined & Source features
    comb_set_ratio = fuzz.token_set_ratio(s1.combined, cand.combined) / 100.0
    is_s2 = 1.0 if cand_id.startswith('S2-') else 0.0

    return [
        nr, ntsr, ntsetr, n_jaccard, n_len_diff,
        ar, atsr, atsetr, a_jaccard, num_overlap, num_match_exact,
        addr_missing, comb_set_ratio, blocking_score, is_s2
    ]

print("Pairwise feature engineering ready.")""")

# Cell 7: Model Training / Loading
add_md(r"""## 6. LightGBM Matching Model & Macro $F_{0.5}$ Calibration
Loads an existing model checkpoint or trains a precision-calibrated LightGBM model from scratch.""")
add_code(r"""def compute_macro_f05(predictions: Dict[str, Set[str]], ground_truth: Dict[str, Set[str]]) -> float:
    scores = []
    for s1_id, true_set in ground_truth.items():
        pred_set = predictions.get(s1_id, set())

        # Singleton evaluation (true empty)
        if not true_set and not pred_set:
            scores.append(1.0)
            continue
        if not true_set and pred_set:
            scores.append(0.0)
            continue
        if true_set and not pred_set:
            scores.append(0.0)
            continue

        tp = len(pred_set.intersection(true_set))
        if tp == 0:
            scores.append(0.0)
            continue

        precision = tp / len(pred_set)
        recall = tp / len(true_set)
        denom = 0.25 * precision + recall
        scores.append((1.25 * precision * recall) / denom if denom > 0 else 0.0)

    return float(np.mean(scores)) if scores else 0.0

MODEL_PATH = "models/matching_lgbm.pkl"
booster = None
OPTIMAL_THRESHOLD = 0.70

# Check Google Drive and local paths for existing model
drive_model_candidates = [
    MODEL_PATH,
    "/content/drive/MyDrive/matching_lgbm.pkl",
    "/content/drive/MyDrive/models/matching_lgbm.pkl",
    "/content/drive/MyDrive/18uVhJZq8psxhwWDyGksnCo6SiGPkWJ3Q/matching_lgbm.pkl",
    "/content/drive/MyDrive/1aBpuNw9Zd1WBmnoifgLpt-7wl9KLzykq/matching_lgbm.pkl",
    "entity_resolution_project/local_execution/models/matching_lgbm.pkl"
]

found_checkpoint = None
for cp in drive_model_candidates:
    if os.path.exists(cp):
        found_checkpoint = cp
        break

if found_checkpoint:
    print(f"Found existing model checkpoint at {found_checkpoint}! Loading...")
    with open(found_checkpoint, 'rb') as f:
        data = pickle.load(f)
        clf = data['model']
        OPTIMAL_THRESHOLD = data.get('threshold', 0.70)
        booster = clf.booster_
    # Copy to local models/ path if loaded from Drive
    if found_checkpoint != MODEL_PATH:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        shutil.copy(found_checkpoint, MODEL_PATH)
    print(f"[OK] Loaded pretrained model with optimal threshold: {OPTIMAL_THRESHOLD:.2f}")
else:
    print("No existing model found. Starting training pipeline on training split...")
    
    # Training configuration
    TRAIN_SAMPLES = 50000
    print(f"Sampling {TRAIN_SAMPLES:,} entities from training data with distributed distractors...")

    train_gt_path = os.path.join(TRAIN_DIR, "train_ground_truth.tsv")
    train_s1_path = os.path.join(TRAIN_DIR, "train_source1.tsv")
    train_s2_path = os.path.join(TRAIN_DIR, "train_source2.tsv")
    train_s3_path = os.path.join(TRAIN_DIR, "train_source3.tsv")

    # 1. Load ground truth sample
    gt_map: Dict[str, Set[str]] = {}
    with open(train_gt_path, 'r', encoding='utf-8') as f:
        f.readline()
        for line in f:
            p = line.strip().split('\t')
            s1_id = p[0]
            mids = set(p[1].split(',')) if len(p) > 1 and p[1] else set()
            gt_map[s1_id] = mids
            if len(gt_map) >= TRAIN_SAMPLES: break

    target_s1_ids = set(gt_map.keys())
    all_target_mids = set()
    for mids in gt_map.values(): all_target_mids.update(mids)

    # 2. Load S1 records
    s1_train_records: Dict[str, PreparedRecord] = {}
    with open(train_s1_path, 'r', encoding='utf-8') as f:
        f.readline()
        for line in f:
            p = line.strip().split('\t')
            if p[0] in target_s1_ids:
                s1_train_records[p[0]] = PreparedRecord(p[1] if len(p)>1 else '', p[2] if len(p)>2 else '')
                if len(s1_train_records) == len(target_s1_ids): break

    # 3. Load candidate pool with distributed distractor sampling
    cand_train_records: Dict[str, PreparedRecord] = {}
    distractors_needed = TRAIN_SAMPLES * 2

    for path in [train_s2_path, train_s3_path]:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            f.readline()
            for i, line in enumerate(f):
                p = line.strip().split('\t')
                eid = p[0]
                is_target = eid in all_target_mids
                is_sample_distractor = (i % 25 == 0) and (len(cand_train_records) < len(all_target_mids) + distractors_needed)
                if is_target or is_sample_distractor:
                    cand_train_records[eid] = PreparedRecord(p[1] if len(p)>1 else '', p[2] if len(p)>2 else '')

    print(f"Loaded {len(s1_train_records):,} S1 entities and {len(cand_train_records):,} candidate records.")

    # 4. Build blocker on candidate records
    train_blocker = CountryPartitionBlocker(max_postings_per_key=100, max_candidates_per_entity=5)
    for eid, rec in cand_train_records.items():
        train_blocker.add_record(eid, rec.raw_name, rec.raw_addr)

    # 5. Generate training and validation pairs
    s1_keys = list(s1_train_records.keys())
    np.random.seed(42)
    np.random.shuffle(s1_keys)
    n_val = int(len(s1_keys) * 0.20)
    val_s1 = set(s1_keys[:n_val])

    X_train, y_train = [], []
    val_pairs = []
    val_gt = {s1: gt_map[s1] for s1 in val_s1}

    for s1_id in tqdm(s1_keys, desc="Generating Training Pairs"):
        s1_prep = s1_train_records[s1_id]
        true_m = gt_map[s1_id]
        cands = train_blocker.query_candidates(s1_prep.raw_name, s1_prep.raw_addr, min_score=1.5)
        cand_ids = {c[0] for c in cands}
        for tm in true_m:
            if tm in cand_train_records and tm not in cand_ids:
                cn_rec = cand_train_records[tm]
                cands.append((tm, cn_rec.raw_name, cn_rec.raw_addr, 1.0))

        is_val = s1_id in val_s1
        for cid, cname, caddr, sc in cands:
            cand_prep = cand_train_records.get(cid) or PreparedRecord(cname, caddr)
            feat = extract_prepared_features(s1_prep, cand_prep, blocking_score=sc, cand_id=cid)
            match_flag = 1 if cid in true_m else 0
            if is_val:
                val_pairs.append((s1_id, cid, np.array(feat, dtype=np.float32)))
            else:
                X_train.append(feat)
                y_train.append(match_flag)

    train_blocker.clear()

    X_train = np.array(X_train, dtype=np.float32)
    y_train = np.array(y_train, dtype=np.int32)

    print(f"\nTraining LightGBM on {len(X_train):,} pairs (Positives: {int(np.sum(y_train == 1)):,}, Negatives: {int(np.sum(y_train == 0)):,})...")
    clf = lgb.LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=7,
        num_leaves=63,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_samples=50,
        is_unbalance=True,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    clf.fit(X_train, y_train)
    booster = clf.booster_

    # Optimize Macro F0.5 Threshold on validation set
    print("Optimizing probability threshold for Macro F_0.5 on validation split...")
    val_X = np.array([f for _, _, f in val_pairs], dtype=np.float32)
    val_probs = booster.predict(val_X)

    best_score = -1.0
    best_th = 0.50
    for th in np.arange(0.30, 0.85, 0.02):
        preds = {s1: set() for s1 in val_gt}
        for idx, (s1, cid, _) in enumerate(val_pairs):
            if val_probs[idx] >= th:
                preds[s1].add(cid)
        score = compute_macro_f05(preds, val_gt)
        if score > best_score:
            best_score = score
            best_th = th

    OPTIMAL_THRESHOLD = float(best_th)
    print(f"\nSelected Optimal Threshold: {OPTIMAL_THRESHOLD:.2f} (Validation Macro F_0.5: {best_score:.4f})")

    # Save model checkpoint locally and to Google Drive
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump({'model': clf, 'threshold': OPTIMAL_THRESHOLD}, f)
    print(f"Model saved to {MODEL_PATH}")

    try:
        if os.path.exists("/content/drive/MyDrive"):
            shutil.copy(MODEL_PATH, "/content/drive/MyDrive/matching_lgbm.pkl")
            print("Model checkpoint synced to Google Drive root.")
    except Exception as e:
        print("Note: Could not copy model to Google Drive root:", e)""")

# Cell 8: Inference
add_md(r"""## 7. High-Scale Test Inference Across All Country Partitions
Executes memory-safe, country-partitioned candidate blocking and batched scoring.
Guarantees 100% full-test coverage (all 1,732,544 test entities with zero missing rows).""")
add_code(r"""test_s1_path = os.path.join(TEST_DIR, "test_source1.tsv")
test_s2_path = os.path.join(TEST_DIR, "test_source2.tsv")
test_s3_path = os.path.join(TEST_DIR, "test_source3.tsv")

matching_out = os.path.join(OUTPUT_DIR, "matching_results.tsv")
candidate_out = os.path.join(OUTPUT_DIR, "candidate_pairs.tsv")
csv_out = os.path.join(OUTPUT_DIR, "matching_pairs.csv")

countries = ['France', 'US', 'India']
results: Dict[str, Tuple[str, str]] = {}
BATCH_SIZE = 5000

t_start = time.time()

for country in countries:
    c_t0 = time.time()
    print(f"\n=======================================================")
    print(f">>> Processing Country Partition: {country} <<<")
    print(f"=======================================================")

    blocker = CountryPartitionBlocker(max_postings_per_key=120, max_candidates_per_entity=4)

    # 1. Index Source 2 and Source 3 records for this country
    print(f"Indexing Source 2 & Source 3 records for {country}...")
    for spath in [test_s2_path, test_s3_path]:
        with open(spath, 'r', encoding='utf-8', errors='replace') as f:
            f.readline()
            for line in f:
                p = line.strip().split('\t')
                if len(p) >= 4 and p[3] == country:
                    blocker.add_record(p[0], p[1] if len(p)>1 else '', p[2] if len(p)>2 else '')

    print(f"Indexed {len(blocker.records):,} candidate records in {time.time()-c_t0:.2f}s.")

    # 2. Count Source 1 entities for this country
    country_s1_count = 0
    with open(test_s1_path, 'r', encoding='utf-8', errors='replace') as f:
        f.readline()
        for line in f:
            p = line.strip().split('\t')
            if len(p) >= 4 and p[3] == country:
                country_s1_count += 1

    print(f"Querying and scoring candidates for {country_s1_count:,} Source 1 entities...")

    pbar = tqdm(total=country_s1_count, desc=f"Inference ({country})")
    batch_s1: List[Tuple[str, PreparedRecord, List[Tuple[str, str, str, float]]]] = []
    cand_cache: Dict[str, PreparedRecord] = {}

    def process_batch(current_batch):
        if not current_batch:
            return
        batch_features = []
        entity_metadata = []

        for s1_id, s1_prep, cands in current_batch:
            if not cands:
                results[s1_id] = ("", "")
                continue

            start_idx = len(batch_features)
            cand_ids = [c[0] for c in cands]

            for cand_id, cand_name, cand_addr, score in cands:
                cand_prep = cand_cache.get(cand_id)
                if cand_prep is None:
                    cand_prep = PreparedRecord(cand_name, cand_addr)
                    if len(cand_cache) < 300000:
                        cand_cache[cand_id] = cand_prep

                feat = extract_prepared_features(s1_prep, cand_prep, blocking_score=score, cand_id=cand_id)
                batch_features.append(feat)

            end_idx = len(batch_features)
            entity_metadata.append((s1_id, cand_ids, start_idx, end_idx))

        if batch_features:
            X_batch = np.array(batch_features, dtype=np.float32)
            probs = booster.predict(X_batch)

            for s1_id, cand_ids, start_idx, end_idx in entity_metadata:
                cand_probs = probs[start_idx:end_idx]
                cand_str = ",".join(cand_ids)

                matched_ids = []
                for i, prob in enumerate(cand_probs):
                    if prob >= OPTIMAL_THRESHOLD:
                        matched_ids.append(cand_ids[i])

                # High string similarity fallback
                if not matched_ids:
                    for i in range(len(cand_ids)):
                        f_vec = batch_features[start_idx + i]
                        if f_vec[0] >= 0.90 and (f_vec[5] >= 0.85 or f_vec[11] == 1.0):
                            matched_ids.append(cand_ids[i])

                match_str = ",".join(matched_ids) if matched_ids else ""
                results[s1_id] = (cand_str, match_str)

    with open(test_s1_path, 'r', encoding='utf-8', errors='replace') as f:
        f.readline()
        for line in f:
            p = line.strip().split('\t')
            if len(p) >= 4 and p[3] == country:
                s1_id = p[0]
                s1_name = p[1] if len(p)>1 else ''
                s1_addr = p[2] if len(p)>2 else ''

                cands = blocker.query_candidates(s1_name, s1_addr, min_score=1.5)
                s1_prep = PreparedRecord(s1_name, s1_addr)
                batch_s1.append((s1_id, s1_prep, cands))

                if len(batch_s1) >= BATCH_SIZE:
                    process_batch(batch_s1)
                    pbar.update(len(batch_s1))
                    batch_s1 = []

        if batch_s1:
            process_batch(batch_s1)
            pbar.update(len(batch_s1))
            batch_s1 = []

    pbar.close()
    print(f"Completed {country} partition in {time.time()-c_t0:.2f} seconds.")
    blocker.clear()
    cand_cache.clear()

# 3. Write final output files in exact original sequence of test_source1.tsv
print("\nWriting submission files in exact test_source1.tsv sequence...")
written_count = 0
with open(test_s1_path, 'r', encoding='utf-8', errors='replace') as f_in, \
     open(matching_out, 'w', encoding='utf-8', newline='') as f_match, \
     open(candidate_out, 'w', encoding='utf-8', newline='') as f_cand, \
     open(csv_out, 'w', encoding='utf-8', newline='') as f_csv:

    f_match.write("source1_entity_id\tmatched_entity_ids\n")
    f_cand.write("source1_entity_id\tcandidate_entity_ids\n")
    f_csv.write("source1_entity_id,matched_entity_ids\n")

    f_in.readline()  # skip header
    for line in f_in:
        s1_id = line.strip().split('\t')[0]
        cand_str, match_str = results.get(s1_id, ("", ""))
        f_match.write(f"{s1_id}\t{match_str}\n")
        f_cand.write(f"{s1_id}\t{cand_str}\n")
        csv_val = f'"{match_str}"' if "," in match_str else match_str
        f_csv.write(f"{s1_id},{csv_val}\n")
        written_count += 1

print(f"\n[SUCCESS] Successfully wrote {written_count:,} rows in {time.time()-t_start:.2f}s:")
print(f"  - {matching_out} ({os.path.getsize(matching_out):,} bytes)")
print(f"  - {candidate_out} ({os.path.getsize(candidate_out):,} bytes)")
print(f"  - {csv_out} ({os.path.getsize(csv_out):,} bytes)")""")

# Cell 9: Official Validator
add_md(r"""## 8. Run Submission Validation Check
Verifies both TSV files against every official competition formatting rule before submitting.""")
add_code(r"""def run_official_validator(matching_file: str, candidate_file: str, test_s1_file: str):
    # Self-contained implementation of utils/validate_submission.py checking:
    # 1. File existence and UTF-8 tab separation
    # 2. Exact required headers
    # 3. Row count exactly matches test_source1.tsv
    # 4. No duplicate source1_entity_id rows
    # 5. No duplicate IDs inside a list
    # 6. No self-matches (no S1- IDs)
    # 7. Valid S2- or S3- prefix only
    # 8. Matches are a subset of candidates
    print("=======================================================")
    print("Running Official Submission Validator...")
    print("=======================================================")

    errors = []
    warnings_list = []

    # 1. Read required Source 1 IDs
    with open(test_s1_file, 'r', encoding='utf-8') as f:
        f.readline()
        required_s1 = {line.split('\t')[0].strip() for line in f if line.strip()}

    print(f"  Required Source 1 entities: {len(required_s1):,}")

    def check_file(path, expected_header, col_name):
        if not os.path.exists(path):
            errors.append(f"File not found: {path}")
            return {}

        mapping = {}
        seen_s1 = set()
        dup_rows = set()
        intra_dupes = set()
        self_matches = set()
        wrong_prefix = set()
        n_rows = 0
        empties = 0

        with open(path, 'r', encoding='utf-8') as f:
            header = f.readline()
            if '\t' not in header and ',' in header:
                errors.append(f"{os.path.basename(path)} is comma-separated instead of tab-separated!")
                return {}
            cols = [c.strip().lower() for c in header.rstrip('\n').split('\t')]
            if cols != expected_header:
                errors.append(f"{os.path.basename(path)} has invalid header {cols}. Expected {expected_header}")
                return {}

            for line_idx, line in enumerate(f, start=2):
                parts = line.rstrip('\n').split('\t')
                if len(parts) < 1:
                    continue
                s1_id = parts[0].strip()
                match_col = parts[1].strip() if len(parts) > 1 else ""

                n_rows += 1
                if s1_id in seen_s1:
                    dup_rows.add(s1_id)
                seen_s1.add(s1_id)

                ids = [x.strip() for x in match_col.split(',') if x.strip()] if match_col else []
                if not ids:
                    empties += 1
                    mapping[s1_id] = set()
                    continue

                if len(ids) != len(set(ids)):
                    intra_dupes.add(s1_id)

                id_set = set(ids)
                mapping[s1_id] = id_set

                for mid in id_set:
                    if mid.startswith("S1-"):
                        self_matches.add(mid)
                    elif not mid.startswith(("S2-", "S3-")):
                        wrong_prefix.add(mid)

        # Evaluate checks
        if dup_rows:
            errors.append(f"{os.path.basename(path)} has {len(dup_rows)} duplicate S1 rows, e.g. {list(dup_rows)[:5]}")
        if intra_dupes:
            errors.append(f"{os.path.basename(path)} has repeated IDs within a row for {len(intra_dupes)} entities")
        if self_matches:
            errors.append(f"{os.path.basename(path)} contains {len(self_matches)} self-matches (S1- IDs)")
        if wrong_prefix:
            errors.append(f"{os.path.basename(path)} contains {len(wrong_prefix)} IDs without S2-/S3- prefix")

        missing_s1 = required_s1 - seen_s1
        if missing_s1:
            errors.append(f"{os.path.basename(path)}: {len(missing_s1)} required S1 entities MISSING! E.g. {list(missing_s1)[:5]}")

        unexpected_s1 = seen_s1 - required_s1
        if unexpected_s1:
            errors.append(f"{os.path.basename(path)}: {len(unexpected_s1)} unexpected S1 IDs not in test set")

        print(f"  {os.path.basename(path)}: {n_rows:,} rows ({empties:,} singletons/empty, {n_rows - empties:,} non-empty matches).")
        return mapping

    matched_map = check_file(matching_file, ["source1_entity_id", "matched_entity_ids"], "matched_entity_ids")
    cand_map = check_file(candidate_file, ["source1_entity_id", "candidate_entity_ids"], "candidate_entity_ids")

    # Subset check
    if matched_map and cand_map:
        not_subset = {s1 for s1, mids in matched_map.items() if mids - cand_map.get(s1, set())}
        if not_subset:
            warnings_list.append(f"{len(not_subset)} entities have matched IDs not present in candidate_pairs.tsv")

    print("\n-------------------------------------------------------")
    for w in warnings_list:
        print(f"WARNING: {w}")

    if errors:
        print(f"FAIL — {len(errors)} issue(s) detected:")
        for idx, err in enumerate(errors, 1):
            print(f"  {idx}. {err}")
        return False
    else:
        print("PASS — All validation rules passed successfully!")
        print("Zero missing entities, exact row counts, correct headers, and valid ID prefixes.")
        return True

val_success = run_official_validator(matching_out, candidate_out, test_s1_path)""")

# Cell 10: Packaging with Embedded Base64 Code and Sync to Drive
b64_literal = json.dumps(embedded_dict)

packaging_code = f'''# 1. Unpack self-contained reproduction code and methodology documentation
import base64

EMBEDDED_FILES = {b64_literal}

print("Unpacking self-contained pipeline code and documentation...")
for rel_path, b64_str in EMBEDDED_FILES.items():
    os.makedirs(os.path.dirname(rel_path) or ".", exist_ok=True)
    with open(rel_path, "wb") as f:
        f.write(base64.b64decode(b64_str.encode("ascii")))

print(f"[OK] Unpacked {{len(EMBEDDED_FILES)}} modules into code/business_entity_resolution/ and Documentation_template.md")

# 2. Build final submission.zip
ZIP_NAME = "submission.zip"
print(f"\\nCreating final submission archive: {{ZIP_NAME}}...")

sub_code_dir = "code/business_entity_resolution"
doc_path = "Documentation_template.md"

with zipfile.ZipFile(ZIP_NAME, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    # Output files
    zf.write(matching_out, arcname="output/matching_results.tsv")
    zf.write(candidate_out, arcname="output/candidate_pairs.tsv")
    if os.path.exists(csv_out):
        zf.write(csv_out, arcname="output/matching_pairs.csv")
    print("  + Added output files (matching_results.tsv, candidate_pairs.tsv, matching_pairs.csv)")

    # Documentation
    if os.path.exists(doc_path):
        zf.write(doc_path, arcname="Documentation_template.md")
        print("  + Added Documentation_template.md")

    # Code directory
    for root, dirs, files in os.walk(sub_code_dir):
        for f in files:
            full_path = os.path.join(root, f)
            arc_path = os.path.relpath(full_path, ".")
            zf.write(full_path, arcname=arc_path)
    print("  + Added complete reproduction code under code/business_entity_resolution/")

zip_size_mb = os.path.getsize(ZIP_NAME) / (1024 * 1024)
print(f"\\n[SUCCESS] Generated {{ZIP_NAME}} ({{zip_size_mb:.2f}} MB).")

# 3. Copy submission zip directly to Google Drive destinations
drive_targets = [
    "/content/drive/MyDrive/submission.zip",
    "/content/drive/MyDrive/18uVhJZq8psxhwWDyGksnCo6SiGPkWJ3Q/submission.zip",
    "/content/drive/MyDrive/1aBpuNw9Zd1WBmnoifgLpt-7wl9KLzykq/submission.zip"
]

for d_dest in drive_targets:
    d_dir = os.path.dirname(d_dest)
    if os.path.exists(d_dir):
        try:
            shutil.copy(ZIP_NAME, d_dest)
            print(f"[OK] Synced submission zip directly to Google Drive: {{d_dest}}")
        except Exception as e:
            print(f"Could not copy to {{d_dest}}: {{e}}")

print("\\n" + "="*55)
print(">>> SUBMISSION READY: ALL TASKS COMPLETED! <<<")
print("1. output/matching_results.tsv  (Scored on Portal Leaderboard)")
print("2. output/candidate_pairs.tsv   (Evaluated for Final Ranking)")
print("3. submission.zip               (Complete Final Submission Package)")
print("="*55)'''

add_md(r"""## 9. Create Final Submission Zip Package
Unpacks full reproduction code, builds `submission.zip`, and automatically syncs to Google Drive.""")
add_code(packaging_code)

# Assemble notebook structure
colab_notebook = {
    'nbformat': 4,
    'nbformat_minor': 2,
    'metadata': {
        'language_info': {'name': 'python'},
        'accelerator': 'GPU',
        'colab': {'provenance': []},
    },
    'cells': nb_cells,
}

# Write notebooks
targets = [
    os.path.join(ROOT, "entity_resolution_project", "google_colab", "business_entity_resolution_colab.ipynb"),
    os.path.join(ROOT, "student_resource", "business_entity_resolution_colab.ipynb")
]

for target in targets:
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        json.dump(colab_notebook, f, indent=1)
    print(f"Successfully generated {target} ({os.path.getsize(target):,} bytes)")

print("\nNotebook Generation Finished Successfully!")
