"""
Business Entity Resolution — core pipeline (blocking + features + LightGBM matcher).

Memory-efficient, country-partitioned design:
  1. Stream the source TSVs and split them into per-country part files.
  2. Per country: build an inverted blocking index over Source-2/3 records,
     query every Source-1 record, keep the top-K candidates (this exact set is
     what goes into candidate_pairs.tsv).
  3. Score every candidate pair with RapidFuzz similarity features and a
     LightGBM classifier; accept pairs above a threshold tuned for macro F_0.5.

Only pure-algorithm libraries are used (pandas / numpy / rapidfuzz / scikit-learn
/ lightgbm) — no external data, gazetteers, or lookup services.  LightGBM is a
gradient-boosted tree model (far under the 8B-parameter cap, MIT licensed).
"""

from __future__ import annotations

import csv
import os
import re
import sys
import time
import unicodedata
from array import array
from collections import defaultdict
from typing import Dict, Iterable, List, Sequence, Set, Tuple

import numpy as np
from rapidfuzz import fuzz

csv.field_size_limit(10_000_000)

# ---------------------------------------------------------------------------
# Normalisation (small hand-written dictionaries only — allowed by the rules)
# ---------------------------------------------------------------------------

LEGAL_SUFFIXES = {
    "inc", "incorporated", "corp", "corporation", "llc", "llp", "lp", "plc",
    "ltd", "limited", "pvt", "private", "co", "company", "pc", "pllc",
    "sarl", "sasu", "sas", "eurl", "sci", "snc", "gie", "cie",
    "gmbh", "ag", "sa", "lc",
}

NAME_STOPWORDS = {
    "the", "and", "of", "in", "at", "by", "for", "with", "a", "an",
    "et", "de", "du", "des", "la", "le", "les", "l", "d",
}

ABBREV = {
    # streets / addresses
    "st": "street", "rd": "road", "ave": "avenue", "av": "avenue",
    "dr": "drive", "ln": "lane", "blvd": "boulevard", "bd": "boulevard",
    "hwy": "highway", "ct": "court", "pl": "place", "sq": "square",
    "apt": "apartment", "ste": "suite", "fl": "floor", "flr": "floor",
    "bldg": "building", "opp": "opposite", "nr": "near",
    "n": "north", "s": "south", "e": "east", "w": "west",
}

ADDR_STOPWORDS = {
    "street", "road", "avenue", "drive", "lane", "boulevard", "court",
    "place", "way", "highway", "square", "near", "opposite", "behind",
    "beside", "next", "floor", "unit", "apartment", "suite", "building",
    "block", "tower", "house", "flat", "shop", "plot", "sector", "phase",
    "no", "number", "ho", "off",
    "nagar", "colony", "marg", "gali", "chowk", "vihar", "pura", "puram",
    "rue", "chemin", "impasse", "allee", "route", "bis",
}

_PUNCT_RE = re.compile(r"[^\w\s]")
_WS_RE = re.compile(r"\s+")
_NUM_RE = re.compile(r"\d{1,8}")
_NONALNUM_RE = re.compile(r"[^a-z0-9]")


def normalize_text(text: str) -> str:
    """Unicode-fold, lowercase, strip accents/punctuation, collapse spaces."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = text.replace("&", " and ")
    text = _PUNCT_RE.sub(" ", text)
    return _WS_RE.sub(" ", text).strip()


def name_core_tokens(norm_name: str) -> List[str]:
    """Significant name tokens: drop legal suffixes / stopwords / bare digits."""
    out = []
    for w in norm_name.split():
        if w in LEGAL_SUFFIXES or w in NAME_STOPWORDS:
            continue
        out.append(w)
    return out


def addr_tokens(norm_addr: str) -> List[str]:
    out = []
    for w in norm_addr.split():
        w = ABBREV.get(w, w)
        if w in ADDR_STOPWORDS or len(w) <= 1:
            continue
        out.append(w)
    return out


def compress(norm: str) -> str:
    return _NONALNUM_RE.sub("", norm)


def numbers_of(text: str) -> List[str]:
    return _NUM_RE.findall(text or "")


# ---------------------------------------------------------------------------
# Record container (memory-light: plain tuple layout)
# ---------------------------------------------------------------------------
# record = (entity_id, norm_name, norm_addr)


def read_source_tsv(path: str) -> Iterable[Tuple[str, str, str, str]]:
    """Yield (entity_id, business_name, business_address, country)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            eid = row[0].strip()
            name = row[1] if len(row) > 1 else ""
            addr = row[2] if len(row) > 2 else ""
            country = (row[3] if len(row) > 3 else "").strip()
            yield eid, name, addr, country


def split_by_country(src_paths: Dict[str, str], out_dir: str, tag: str) -> Dict[str, Dict[str, str]]:
    """Split each source file into per-country part files.

    Returns {country_key: {source_label: part_path}}.
    Country is treated as an open set of string labels.
    """
    os.makedirs(out_dir, exist_ok=True)
    handles: Dict[Tuple[str, str], object] = {}
    result: Dict[str, Dict[str, str]] = defaultdict(dict)

    def key_of(country: str) -> str:
        k = re.sub(r"[^A-Za-z0-9]+", "_", country.strip()) or "UNKNOWN"
        return k

    try:
        for label, path in src_paths.items():
            for eid, name, addr, country in read_source_tsv(path):
                ck = key_of(country)
                hk = (ck, label)
                if hk not in handles:
                    part = os.path.join(out_dir, f"{tag}_{label}_{ck}.tsv")
                    handles[hk] = open(part, "w", encoding="utf-8")
                    result[ck][label] = part
                handles[hk].write(f"{eid}\t{name}\t{addr}\n")
    finally:
        for h in handles.values():
            h.close()
    return dict(result)


def read_part(path: str) -> Iterable[Tuple[str, str, str]]:
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                yield parts[0], parts[1], parts[2]
            elif len(parts) == 2:
                yield parts[0], parts[1], ""


# ---------------------------------------------------------------------------
# Blocking
# ---------------------------------------------------------------------------

class Blocker:
    """Inverted-index blocking over Source-2/3 records of one country.

    Keys per record:
      * full compressed name             (weight 4)
      * compressed-name 8-char prefix    (weight 3)
      * first two core name tokens       (weight 3)
      * each core name token             (weight ~idf, capped postings)
      * rarest name token + addr number  (weight 2)
    Candidates are ranked by accumulated key weight; top-K survive.
    """

    MAX_POSTING = 400          # ignore keys more frequent than this at query time
    STORE_POSTING = 400        # stop storing beyond this many ids per key

    def __init__(self):
        self.postings: Dict[str, array] = defaultdict(lambda: array("i"))
        self.overflow: Set[str] = set()
        self.ids: List[str] = []
        self.names: List[str] = []
        self.addrs: List[str] = []

    # -- shared key generation ------------------------------------------------
    @staticmethod
    def keys_for(norm_name: str, norm_addr: str) -> List[Tuple[str, float]]:
        toks = name_core_tokens(norm_name)
        comp = compress(" ".join(toks) if toks else norm_name)
        keys: List[Tuple[str, float]] = []
        if comp:
            keys.append(("C:" + comp, 4.0))
            if len(comp) >= 8:
                keys.append(("P:" + comp[:8], 3.0))
            elif len(comp) >= 5:
                keys.append(("P:" + comp[:5], 2.0))
        if len(toks) >= 2:
            keys.append(("T2:" + toks[0] + "_" + toks[1], 3.0))
        for t in toks[:6]:
            if len(t) >= 3:
                keys.append(("T:" + t, 1.0))
        nums = numbers_of(norm_addr)
        if toks and nums:
            keys.append(("NA:" + toks[0] + "_" + nums[0], 2.0))
        return keys

    def add(self, eid: str, norm_name: str, norm_addr: str) -> None:
        idx = len(self.ids)
        self.ids.append(eid)
        self.names.append(norm_name)
        self.addrs.append(norm_addr)
        for key, _w in self.keys_for(norm_name, norm_addr):
            if key in self.overflow:
                continue
            post = self.postings[key]
            if len(post) >= self.STORE_POSTING:
                self.overflow.add(key)
                continue
            post.append(idx)

    def query(self, norm_name: str, norm_addr: str, top_k: int) -> List[Tuple[int, float]]:
        scores: Dict[int, float] = defaultdict(float)
        for key, w in self.keys_for(norm_name, norm_addr):
            if key in self.overflow:
                continue
            post = self.postings.get(key)
            if post is None:
                continue
            n = len(post)
            if n == 0 or n > self.MAX_POSTING:
                continue
            # frequency-aware weight: rare keys count more
            kw = w * (1.0 + 2.0 / (1.0 + 0.05 * n))
            for idx in post:
                scores[idx] += kw
        if not scores:
            return []
        items = sorted(scores.items(), key=lambda kv: -kv[1])[:top_k]
        # prune weak tail candidates: keeps the candidate set small without
        # hurting recall (they virtually never survive the matcher anyway)
        best = items[0][1]
        floor = max(2.0, 0.30 * best)
        return [it for it in items if it[1] >= floor]


# ---------------------------------------------------------------------------
# Pairwise features
# ---------------------------------------------------------------------------

FEATURE_NAMES = [
    "name_ratio", "name_token_sort", "name_token_set", "name_partial",
    "name_jaccard", "comp_ratio", "comp_prefix", "name_len_diff",
    "addr_ratio", "addr_token_set", "addr_token_sort", "addr_jaccard",
    "num_jaccard", "num_first_match", "addr_missing",
    "block_score", "block_rank", "is_source2",
]


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    if inter == 0:
        return 0.0
    return inter / (len(a) + len(b) - inter)


def pair_features(
    s1_name: str, s1_addr: str,
    c_name: str, c_addr: str,
    block_score: float, block_rank: int, is_s2: bool,
    _cache: dict = None,
) -> List[float]:
    if _cache is not None and "s1" in _cache:
        n1toks, a1toks, nums1, comp1 = _cache["s1"]
    else:
        n1toks = set(name_core_tokens(s1_name))
        a1toks = set(addr_tokens(s1_addr))
        nums1 = set(numbers_of(s1_addr))
        comp1 = compress(s1_name)
        if _cache is not None:
            _cache["s1"] = (n1toks, a1toks, nums1, comp1)

    n2toks = set(name_core_tokens(c_name))
    a2toks = set(addr_tokens(c_addr))
    nums2 = set(numbers_of(c_addr))
    comp2 = compress(c_name)

    name_ratio = fuzz.ratio(s1_name, c_name) / 100.0
    name_tsort = fuzz.token_sort_ratio(s1_name, c_name) / 100.0
    name_tset = fuzz.token_set_ratio(s1_name, c_name) / 100.0
    name_part = fuzz.partial_ratio(s1_name, c_name) / 100.0
    name_jac = jaccard(n1toks, n2toks)
    comp_ratio = fuzz.ratio(comp1, comp2) / 100.0
    pref = 0
    for x, y in zip(comp1, comp2):
        if x != y:
            break
        pref += 1
    comp_prefix = pref / max(1, min(len(comp1), len(comp2)))
    l1, l2 = len(s1_name), len(c_name)
    name_len_diff = abs(l1 - l2) / max(1, l1, l2)

    addr_missing = 1.0 if (not c_addr or not s1_addr) else 0.0
    if addr_missing:
        addr_ratio = addr_tset = addr_tsort = addr_jac = 0.0
    else:
        addr_ratio = fuzz.ratio(s1_addr, c_addr) / 100.0
        addr_tset = fuzz.token_set_ratio(s1_addr, c_addr) / 100.0
        addr_tsort = fuzz.token_sort_ratio(s1_addr, c_addr) / 100.0
        addr_jac = jaccard(a1toks, a2toks)

    num_jac = jaccard(nums1, nums2)
    n1f = next(iter(numbers_of(s1_addr)), None)
    n2f = next(iter(numbers_of(c_addr)), None)
    num_first = 1.0 if (n1f is not None and n1f == n2f) else 0.0

    return [
        name_ratio, name_tsort, name_tset, name_part,
        name_jac, comp_ratio, comp_prefix, name_len_diff,
        addr_ratio, addr_tset, addr_tsort, addr_jac,
        num_jac, num_first, addr_missing,
        block_score, float(block_rank), 1.0 if is_s2 else 0.0,
    ]


# ---------------------------------------------------------------------------
# F_0.5 utilities
# ---------------------------------------------------------------------------

def f05(pred: Set[str], truth: Set[str]) -> float:
    if not truth and not pred:
        return 1.0
    if not pred or not truth:
        return 0.0
    tp = len(pred & truth)
    if tp == 0:
        return 0.0
    p = tp / len(pred)
    r = tp / len(truth)
    return 1.25 * p * r / (0.25 * p + r)


def macro_f05(preds: Dict[str, Set[str]], truths: Dict[str, Set[str]]) -> float:
    if not truths:
        return 0.0
    return sum(f05(preds.get(k, set()), v) for k, v in truths.items()) / len(truths)
