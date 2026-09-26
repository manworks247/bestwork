"""
End-to-end Business Entity Resolution pipeline.

Usage:
    python -m src.pipeline --data-dir dataset --out-dir output \
        --work-dir work --model-path models/matcher_lgbm.txt \
        [--train-sample 150000] [--top-k 12] [--skip-train]

Stages:
  1. TRAIN  : country-split train data -> blocking -> labelled pairs ->
              LightGBM -> threshold tuned for macro F_0.5 on a held-out split.
  2. PREDICT: country-split test data -> blocking (top-K candidates per S1) ->
              model scores -> matching_results.tsv + candidate_pairs.tsv.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
import time
from collections import defaultdict
from typing import Dict, List, Set, Tuple

import numpy as np
import lightgbm as lgb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ber_core import (
    Blocker, FEATURE_NAMES, f05, macro_f05, normalize_text,
    pair_features, read_part, read_source_tsv, split_by_country,
)

RANDOM_SEED = 42


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_ground_truth(path: str) -> Dict[str, Set[str]]:
    gt: Dict[str, Set[str]] = {}
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            s1, _, rest = line.rstrip("\n").partition("\t")
            ids = set(x for x in rest.split(",") if x) if rest.strip() else set()
            gt[s1] = ids
    return gt


def build_index_for_country(parts: Dict[str, str]) -> Blocker:
    """Index all Source-2/3 records of one country."""
    blocker = Blocker()
    for label in ("s2", "s3"):
        p = parts.get(label)
        if not p:
            continue
        for eid, name, addr in read_part(p):
            blocker.add(eid, normalize_text(name), normalize_text(addr))
    return blocker


def candidates_for_s1(
    blocker: Blocker, name: str, addr: str, top_k: int
) -> List[Tuple[str, str, str, float, int]]:
    """Return [(cand_id, cand_norm_name, cand_norm_addr, block_score, rank)]."""
    nn, na = normalize_text(name), normalize_text(addr)
    hits = blocker.query(nn, na, top_k)
    out = []
    for rank, (idx, score) in enumerate(hits):
        out.append((blocker.ids[idx], blocker.names[idx], blocker.addrs[idx], score, rank))
    return out


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def run_training(
    data_dir: str,
    work_dir: str,
    model_path: str,
    train_sample: int,
    top_k: int,
    val_frac: float = 0.2,
) -> Tuple[lgb.Booster, float]:
    t0 = time.time()
    rng = random.Random(RANDOM_SEED)
    print("[train] splitting train sources by country ...", flush=True)
    parts = split_by_country(
        {
            "s1": os.path.join(data_dir, "train", "train_source1.tsv"),
            "s2": os.path.join(data_dir, "train", "train_source2.tsv"),
            "s3": os.path.join(data_dir, "train", "train_source3.tsv"),
        },
        os.path.join(work_dir, "parts_train"),
        "train",
    )
    gt = load_ground_truth(os.path.join(data_dir, "train", "train_ground_truth.tsv"))
    print(f"[train] ground truth entities: {len(gt):,}", flush=True)

    # Sample S1 entities proportionally per country
    country_s1: Dict[str, List[Tuple[str, str, str]]] = {}
    total_s1 = 0
    for ck, p in parts.items():
        if "s1" not in p:
            continue
        recs = list(read_part(p["s1"]))
        country_s1[ck] = recs
        total_s1 += len(recs)
    frac = min(1.0, train_sample / max(1, total_s1))
    print(f"[train] S1 total {total_s1:,}; sampling ~{frac:.1%}", flush=True)

    X_rows: List[List[float]] = []
    y_rows: List[int] = []
    pair_meta: List[Tuple[str, str]] = []   # (s1_id, cand_id)
    entity_split: Dict[str, int] = {}       # s1_id -> 0 train / 1 val
    truth_by_entity: Dict[str, Set[str]] = {}

    for ck in sorted(country_s1, key=lambda c: len(country_s1[c])):
        s1_recs = country_s1[ck]
        sampled = [r for r in s1_recs if rng.random() < frac]
        if not sampled:
            continue
        print(f"[train] country={ck}: S1={len(s1_recs):,} sampled={len(sampled):,} "
              f"— building index ...", flush=True)
        blocker = build_index_for_country(parts[ck])
        print(f"[train]   index size: {len(blocker.ids):,} records, "
              f"{len(blocker.postings):,} keys", flush=True)
        for i, (s1_id, name, addr) in enumerate(sampled):
            truth = gt.get(s1_id, set())
            cands = candidates_for_s1(blocker, name, addr, top_k)
            split = 1 if rng.random() < val_frac else 0
            entity_split[s1_id] = split
            truth_by_entity[s1_id] = truth
            nn, na = normalize_text(name), normalize_text(addr)
            cache: dict = {}
            for cid, cname, caddr, bscore, brank in cands:
                feats = pair_features(nn, na, cname, caddr, bscore, brank,
                                      cid.startswith("S2-"), cache)
                X_rows.append(feats)
                y_rows.append(1 if cid in truth else 0)
                pair_meta.append((s1_id, cid))
            if (i + 1) % 20000 == 0:
                print(f"[train]   {i+1:,}/{len(sampled):,} queried "
                      f"({time.time()-t0:,.0f}s)", flush=True)
        del blocker

    X = np.asarray(X_rows, dtype=np.float32)
    y = np.asarray(y_rows, dtype=np.int8)
    is_val = np.asarray([entity_split[m[0]] for m in pair_meta], dtype=np.int8)
    print(f"[train] pairs: {len(y):,} (pos {int(y.sum()):,}) "
          f"val pairs {int((is_val==1).sum()):,}", flush=True)

    dtrain = lgb.Dataset(X[is_val == 0], label=y[is_val == 0],
                         feature_name=FEATURE_NAMES)
    dval = lgb.Dataset(X[is_val == 1], label=y[is_val == 1],
                       reference=dtrain, feature_name=FEATURE_NAMES)
    params = dict(
        objective="binary", metric="auc", learning_rate=0.07,
        num_leaves=63, min_data_in_leaf=40, feature_fraction=0.9,
        bagging_fraction=0.9, bagging_freq=1, seed=RANDOM_SEED, verbosity=-1,
        num_threads=os.cpu_count() or 2,
    )
    booster = lgb.train(
        params, dtrain, num_boost_round=600,
        valid_sets=[dval], valid_names=["val"],
        callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(100)],
    )
    print(f"[train] best iteration: {booster.best_iteration}", flush=True)

    # ---- threshold tuning on validation entities (macro F_0.5, incl. singletons)
    val_idx = np.where(is_val == 1)[0]
    probs = booster.predict(X[val_idx], num_iteration=booster.best_iteration)
    by_entity: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    for j, k in enumerate(val_idx):
        s1_id, cid = pair_meta[k]
        by_entity[s1_id].append((cid, float(probs[j])))
    val_truth = {e: t for e, t in truth_by_entity.items() if entity_split[e] == 1}

    best_t, best_score = 0.5, -1.0
    for t in np.arange(0.20, 0.96, 0.02):
        preds = {
            e: {cid for cid, p in by_entity.get(e, []) if p >= t}
            for e in val_truth
        }
        s = macro_f05(preds, val_truth)
        if s > best_score:
            best_score, best_t = s, float(t)
    print(f"[train] tuned threshold={best_t:.2f}  val macro-F0.5={best_score:.4f}",
          flush=True)

    os.makedirs(os.path.dirname(model_path) or ".", exist_ok=True)
    booster.save_model(model_path, num_iteration=booster.best_iteration)
    with open(model_path + ".meta.json", "w") as f:
        json.dump({"threshold": best_t, "val_macro_f05": best_score,
                   "top_k": top_k, "features": FEATURE_NAMES,
                   "best_iteration": booster.best_iteration}, f, indent=2)
    print(f"[train] model saved -> {model_path} ({time.time()-t0:,.0f}s total)",
          flush=True)
    return booster, best_t


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def run_inference(
    data_dir: str,
    work_dir: str,
    out_dir: str,
    model_path: str,
    top_k: int,
    batch_pairs: int = 200_000,
) -> None:
    t0 = time.time()
    booster = lgb.Booster(model_file=model_path)
    with open(model_path + ".meta.json") as f:
        meta = json.load(f)
    threshold = meta["threshold"]
    print(f"[predict] threshold={threshold:.2f} top_k={top_k}", flush=True)

    print("[predict] splitting test sources by country ...", flush=True)
    parts = split_by_country(
        {
            "s1": os.path.join(data_dir, "test", "test_source1.tsv"),
            "s2": os.path.join(data_dir, "test", "test_source2.tsv"),
            "s3": os.path.join(data_dir, "test", "test_source3.tsv"),
        },
        os.path.join(work_dir, "parts_test"),
        "test",
    )

    os.makedirs(out_dir, exist_ok=True)
    match_path = os.path.join(out_dir, "matching_results.tsv")
    cand_path = os.path.join(out_dir, "candidate_pairs.tsv")
    n_entities = n_matched = n_cand_total = 0

    with open(match_path, "w", encoding="utf-8") as fm, \
         open(cand_path, "w", encoding="utf-8") as fc:
        fm.write("source1_entity_id\tmatched_entity_ids\n")
        fc.write("source1_entity_id\tcandidate_entity_ids\n")

        for ck in sorted(parts, key=lambda c: os.path.getsize(parts[c].get("s1", parts[c].get("s2", "/dev/null"))) if parts[c] else 0):
            p = parts[ck]
            if "s1" not in p:
                continue
            print(f"[predict] country={ck}: building index ...", flush=True)
            blocker = build_index_for_country(p)
            print(f"[predict]   index: {len(blocker.ids):,} records", flush=True)

            # batched scoring to keep memory flat
            buf_feats: List[List[float]] = []
            buf_meta: List[Tuple[str, str]] = []
            buf_entities: List[Tuple[str, List[str]]] = []  # (s1_id, cand_ids)

            def flush():
                nonlocal n_matched
                if not buf_entities:
                    return
                if buf_feats:
                    probs = booster.predict(
                        np.asarray(buf_feats, dtype=np.float32),
                        num_iteration=booster.best_iteration or None)
                else:
                    probs = np.zeros(0)
                pos = 0
                by_entity: Dict[str, List[Tuple[str, float]]] = {}
                for (s1_id, cid) in buf_meta:
                    by_entity.setdefault(s1_id, []).append((cid, float(probs[pos])))
                    pos += 1
                for s1_id, cand_ids in buf_entities:
                    scored = by_entity.get(s1_id, [])
                    matched = [cid for cid, pr in scored if pr >= threshold]
                    n_matched += len(matched)
                    fm.write(f"{s1_id}\t{','.join(matched)}\n")
                    fc.write(f"{s1_id}\t{','.join(cand_ids)}\n")
                buf_feats.clear(); buf_meta.clear(); buf_entities.clear()

            count = 0
            for s1_id, name, addr in read_part(p["s1"]):
                nn, na = normalize_text(name), normalize_text(addr)
                hits = blocker.query(nn, na, top_k)
                cand_ids = []
                cache: dict = {}
                for rank, (idx, score) in enumerate(hits):
                    cid = blocker.ids[idx]
                    cand_ids.append(cid)
                    buf_feats.append(pair_features(
                        nn, na, blocker.names[idx], blocker.addrs[idx],
                        score, rank, cid.startswith("S2-"), cache))
                    buf_meta.append((s1_id, cid))
                buf_entities.append((s1_id, cand_ids))
                n_entities += 1
                n_cand_total += len(cand_ids)
                count += 1
                if len(buf_feats) >= batch_pairs:
                    flush()
                if count % 100000 == 0:
                    print(f"[predict]   {count:,} S1 done "
                          f"({time.time()-t0:,.0f}s)", flush=True)
            flush()
            del blocker
            print(f"[predict] country={ck} done ({time.time()-t0:,.0f}s)", flush=True)

    print(f"[predict] wrote {match_path} and {cand_path}", flush=True)
    print(f"[predict] entities={n_entities:,} matches={n_matched:,} "
          f"avg candidates/entity={n_cand_total/max(1,n_entities):.2f}", flush=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Business Entity Resolution pipeline")
    ap.add_argument("--data-dir", required=True,
                    help="folder containing train/ and test/ subfolders")
    ap.add_argument("--out-dir", default="output")
    ap.add_argument("--work-dir", default="work")
    ap.add_argument("--model-path", default="models/matcher_lgbm.txt")
    ap.add_argument("--train-sample", type=int, default=150_000,
                    help="number of S1 training entities to sample")
    ap.add_argument("--top-k", type=int, default=12,
                    help="candidates kept per S1 entity (blocking output)")
    ap.add_argument("--skip-train", action="store_true",
                    help="reuse an existing model file")
    ap.add_argument("--skip-predict", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.work_dir, exist_ok=True)
    if not args.skip_train:
        run_training(args.data_dir, args.work_dir, args.model_path,
                     args.train_sample, args.top_k)
    if not args.skip_predict:
        run_inference(args.data_dir, args.work_dir, args.out_dir,
                      args.model_path, args.top_k)


if __name__ == "__main__":
    main()
