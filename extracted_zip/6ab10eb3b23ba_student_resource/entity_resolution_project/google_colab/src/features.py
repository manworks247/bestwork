"""
Feature Engineering Module for Business Entity Resolution.
Computes string, token, phonetic, and numeric similarity features between S1 and candidate records.
"""

from typing import Dict, List, Optional, Tuple, Set
import rapidfuzz.fuzz as fuzz
from src.preprocessor import (
    clean_name_tokens,
    clean_addr_tokens,
    extract_numbers,
    normalize_text,
    get_compressed_name,
)

FEATURE_NAMES = [
    'name_fuzz_ratio',
    'name_token_sort_ratio',
    'name_token_set_ratio',
    'name_jaccard',
    'name_len_diff',
    'addr_fuzz_ratio',
    'addr_token_sort_ratio',
    'addr_token_set_ratio',
    'addr_jaccard',
    'number_overlap',
    'number_match_exact',
    'addr_missing',
    'combined_token_set',
    'blocking_score',
    'is_source2',
]


def compute_jaccard(set1: set, set2: set) -> float:
    """Compute Jaccard index between two sets."""
    if not set1 or not set2:
        return 0.0
    inter = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return inter / union if union > 0 else 0.0


class PreparedRecord:
    """Caches normalized text and token sets for fast pairwise comparison."""

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


def extract_prepared_features(
    s1: PreparedRecord,
    cand: PreparedRecord,
    blocking_score: float = 0.0,
    cand_id: str = "",
) -> List[float]:
    """
    Extract pairwise feature vector between pre-cached Source 1 and candidate records.
    """
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

        num_overlap = (
            len(s1.numbers.intersection(cand.numbers)) / max(len(s1.numbers), 1)
            if s1.numbers
            else 0.0
        )
        if s1.numbers and cand.numbers:
            num_match_exact = 1.0 if s1.numbers.intersection(cand.numbers) else 0.0
        else:
            num_match_exact = 0.5
    else:
        ar = 0.0
        atsr = 0.0
        atsetr = 0.0
        a_jaccard = 0.0
        num_overlap = 0.0
        num_match_exact = 0.5

    # 3. Combined features
    comb_set_ratio = fuzz.token_set_ratio(s1.combined, cand.combined) / 100.0
    is_s2 = 1.0 if cand_id.startswith('S2-') else 0.0

    return [
        nr,
        ntsr,
        ntsetr,
        n_jaccard,
        n_len_diff,
        ar,
        atsr,
        atsetr,
        a_jaccard,
        num_overlap,
        num_match_exact,
        addr_missing,
        comb_set_ratio,
        blocking_score,
        is_s2,
    ]


def extract_pair_features(
    s1_name: str,
    s1_addr: str,
    cand_name: str,
    cand_addr: str,
    blocking_score: float = 0.0,
    cand_id: str = "",
) -> List[float]:
    """Convenience wrapper for non-cached pair feature extraction."""
    s1 = PreparedRecord(s1_name, s1_addr)
    cand = PreparedRecord(cand_name, cand_addr)
    return extract_prepared_features(s1, cand, blocking_score, cand_id)
