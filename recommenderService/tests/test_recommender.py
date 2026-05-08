"""
Unit tests for recommender service.

Covers the pure ranking-metric functions in evaluate_recommendations.py
using small synthetic cases where expected values can be verified by hand.
No real model files or external dependencies required.
"""
import math
import sys
from pathlib import Path

import numpy as np
import pytest

# Make the parent directory importable so we can reach evaluate_recommendations
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluate_recommendations import (
    average_precision_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank_at_k,
)


# ============================================================================
# precision_at_k
# ============================================================================

class TestPrecisionAtK:
    def test_all_relevant(self):
        assert precision_at_k([1, 2, 3], {1, 2, 3}, k=3) == pytest.approx(1.0)

    def test_none_relevant(self):
        assert precision_at_k([1, 2, 3], {4, 5, 6}, k=3) == pytest.approx(0.0)

    def test_half_relevant(self):
        # 2 hits out of 4 → 0.5
        assert precision_at_k([1, 2, 3, 4], {1, 3}, k=4) == pytest.approx(0.5)

    def test_k_larger_than_list(self):
        # Only 2 items available, k=5 — precision = 1/5
        assert precision_at_k([1, 2], {1}, k=5) == pytest.approx(1 / 5)

    def test_k_zero_returns_zero(self):
        assert precision_at_k([1, 2], {1}, k=0) == pytest.approx(0.0)

    def test_truncates_to_k(self):
        # Item 3 is relevant but falls outside top-2
        assert precision_at_k([1, 2, 3], {3}, k=2) == pytest.approx(0.0)


# ============================================================================
# recall_at_k
# ============================================================================

class TestRecallAtK:
    def test_all_found(self):
        assert recall_at_k([1, 2, 3], {1, 2, 3}, k=3) == pytest.approx(1.0)

    def test_none_found(self):
        assert recall_at_k([1, 2, 3], {4, 5}, k=3) == pytest.approx(0.0)

    def test_partial(self):
        # 1 of 3 relevant items found in top-2
        assert recall_at_k([1, 99, 99], {1, 2, 3}, k=2) == pytest.approx(1 / 3)

    def test_empty_relevant_returns_zero(self):
        assert recall_at_k([1, 2, 3], set(), k=3) == pytest.approx(0.0)

    def test_k_limits_scope(self):
        # Item 2 is relevant but ranked 3rd, k=2 should miss it
        assert recall_at_k([1, 9, 2], {2}, k=2) == pytest.approx(0.0)
        assert recall_at_k([1, 9, 2], {2}, k=3) == pytest.approx(1.0)


# ============================================================================
# ndcg_at_k
# ============================================================================

class TestNdcgAtK:
    def test_perfect_ranking(self):
        # All relevant items at the top → NDCG = 1.0
        assert ndcg_at_k([1, 2, 3], {1, 2, 3}, k=3) == pytest.approx(1.0)

    def test_no_hits(self):
        assert ndcg_at_k([1, 2, 3], {4, 5, 6}, k=3) == pytest.approx(0.0)

    def test_empty_relevant(self):
        assert ndcg_at_k([1, 2, 3], set(), k=3) == pytest.approx(0.0)

    def test_single_hit_at_position_1(self):
        # DCG = 1/log2(2) = 1, IDCG = 1 → NDCG = 1.0
        assert ndcg_at_k([1, 99, 99], {1}, k=3) == pytest.approx(1.0)

    def test_single_hit_at_position_2(self):
        # DCG = 1/log2(3), IDCG = 1/log2(2) = 1
        expected = (1.0 / math.log2(3)) / 1.0
        assert ndcg_at_k([99, 1, 99], {1}, k=3) == pytest.approx(expected)

    def test_two_relevant_reversed_order(self):
        # Ideal: [1,2,...] → IDCG = 1/log2(2) + 1/log2(3)
        # Actual: [2,1,...] → same DCG value = IDCG → NDCG = 1.0
        assert ndcg_at_k([2, 1, 99], {1, 2}, k=3) == pytest.approx(1.0)

    def test_relevant_below_k_cutoff(self):
        # Relevant item at position 4, k=3 → not counted
        assert ndcg_at_k([99, 99, 99, 1], {1}, k=3) == pytest.approx(0.0)


# ============================================================================
# average_precision_at_k
# ============================================================================

class TestAveragePrecisionAtK:
    def test_perfect(self):
        # All 3 relevant items at positions 1,2,3
        # AP = (1/1 + 2/2 + 3/3) / 3 = 1.0
        assert average_precision_at_k([1, 2, 3], {1, 2, 3}, k=3) == pytest.approx(1.0)

    def test_no_hits(self):
        assert average_precision_at_k([1, 2, 3], {4, 5}, k=3) == pytest.approx(0.0)

    def test_empty_relevant(self):
        assert average_precision_at_k([1, 2], set(), k=3) == pytest.approx(0.0)

    def test_single_hit_at_position_2(self):
        # Hit at position 2: precision@2 = 1/2, normalizer = min(3,1)=1
        # AP = (1/2) / 1 = 0.5
        assert average_precision_at_k([99, 1, 99], {1}, k=3) == pytest.approx(0.5)

    def test_two_hits_spread(self):
        # Hits at positions 1 and 3: (1/1 + 2/3) / min(3,2) = (1 + 0.666...) / 2
        expected = (1.0 + 2.0 / 3.0) / 2.0
        assert average_precision_at_k([1, 99, 2], {1, 2}, k=3) == pytest.approx(expected)


# ============================================================================
# reciprocal_rank_at_k
# ============================================================================

class TestReciprocalRankAtK:
    def test_first_position(self):
        assert reciprocal_rank_at_k([1, 2, 3], {1}, k=3) == pytest.approx(1.0)

    def test_second_position(self):
        assert reciprocal_rank_at_k([99, 1, 3], {1}, k=3) == pytest.approx(0.5)

    def test_third_position(self):
        assert reciprocal_rank_at_k([99, 99, 1], {1}, k=3) == pytest.approx(1 / 3)

    def test_no_hit_returns_zero(self):
        assert reciprocal_rank_at_k([1, 2, 3], {4}, k=3) == pytest.approx(0.0)

    def test_k_cutoff_excludes_hit(self):
        # Relevant item is at rank 4, k=3 → should return 0
        assert reciprocal_rank_at_k([99, 99, 99, 1], {1}, k=3) == pytest.approx(0.0)

    def test_returns_first_hit_only(self):
        # Items 2 and 3 are both relevant; first hit is at rank 2
        assert reciprocal_rank_at_k([99, 2, 3], {2, 3}, k=3) == pytest.approx(0.5)
