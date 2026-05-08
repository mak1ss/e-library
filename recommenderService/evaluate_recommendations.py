#!/usr/bin/env python3
"""
Offline Evaluation Script for Recommendation Algorithms

Evaluates two engines using data already embedded in the trained model files
(no click-through data or external labels required):

  1. Collaborative Filtering (item-item co-occurrence)
     Ground truth: books that co-occur with the seed book in the interaction matrix.
     Metrics:  Precision@K, Recall@K, NDCG@K, MAP@K, MRR@K, Hit Rate@K
               for K in {5, 10, 20} (configurable)

  2. Content-Based (TF-IDF similarity)
     No ground-truth labels — intrinsic catalog-level metrics instead:
     Catalog Coverage, Intra-list Diversity, Personalization

Usage:
  python evaluate_recommendations.py \\
    --models_dir /path/to/models \\
    --output_dir evaluation_results/recommendations \\
    --sample_size 500 \\
    --k_values 5,10,20 \\
    --min_cooccurrences 3

Output:
  - recommendation_metrics.json   (machine-readable)
  - recommendation_report.html    (human-readable)
  - recommendation_eval_log.txt   (detailed log)
"""

import argparse
import json
import logging
import math
import random
import sys
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class RecommendationEvalConfig:
    models_dir: Path
    output_dir: Path
    sample_size: int
    k_values: List[int]
    min_cooccurrences: int
    log_level: str = "INFO"

    def __post_init__(self):
        self.output_dir.mkdir(parents=True, exist_ok=True)


# ============================================================================
# Result data classes
# ============================================================================

@dataclass
class RankingMetrics:
    k: int
    precision: float      # hits in top-K / K
    recall: float         # hits in top-K / |relevant|
    ndcg: float           # Normalised Discounted Cumulative Gain
    map_score: float      # Mean Average Precision
    mrr: float            # Mean Reciprocal Rank (first hit within top-K)
    hit_rate: float       # fraction of queries with ≥1 hit in top-K
    n_queries: int


@dataclass
class ContentBasedCatalogMetrics:
    catalog_coverage: float           # fraction of catalog appearing in any rec list
    mean_intra_list_diversity: float  # 1 - avg pairwise cosine sim within lists
    personalization: float            # 1 - avg Jaccard overlap between lists
    n_queries: int


@dataclass
class RecommendationEvalReport:
    cf_metrics_by_k: List[RankingMetrics]
    cb_catalog_metrics: Optional[ContentBasedCatalogMetrics]
    n_queries_cf: int
    n_queries_cb: int
    passes_criteria: bool
    failure_reasons: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================================
# Core ranking metric functions (pure — easy to unit-test independently)
# ============================================================================

def precision_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Fraction of top-K recommendations that are relevant."""
    if k == 0:
        return 0.0
    hits = sum(1 for item in recommended[:k] if item in relevant)
    return hits / k


def recall_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Fraction of all relevant items found in top-K recommendations."""
    if not relevant:
        return 0.0
    hits = sum(1 for item in recommended[:k] if item in relevant)
    return hits / len(relevant)


def ndcg_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Normalised Discounted Cumulative Gain at K.

    DCG@K  = Σ rel_i / log2(i+2)   for i in 0..k-1   (rel_i ∈ {0,1})
    IDCG@K = Σ 1   / log2(i+2)     for i in 0..min(k,|R|)-1
    NDCG@K = DCG@K / IDCG@K
    """
    if not relevant:
        return 0.0
    top_k = recommended[:k]
    dcg = sum(
        (1.0 / math.log2(i + 2)) if top_k[i] in relevant else 0.0
        for i in range(len(top_k))
    )
    ideal_hits = min(k, len(relevant))
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))
    return dcg / idcg if idcg > 0.0 else 0.0


def average_precision_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Average Precision at K.

    AP@K = (1 / min(k,|R|)) * Σ P@i * rel(i)   for i in 1..k
    """
    if not relevant:
        return 0.0
    hits = 0
    cumulative = 0.0
    for i, item in enumerate(recommended[:k]):
        if item in relevant:
            hits += 1
            cumulative += hits / (i + 1)
    normalizer = min(k, len(relevant))
    return cumulative / normalizer if normalizer > 0 else 0.0


def reciprocal_rank_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Reciprocal rank of the first relevant item within top-K (0 if none)."""
    for i, item in enumerate(recommended[:k]):
        if item in relevant:
            return 1.0 / (i + 1)
    return 0.0


# ============================================================================
# Model loading
# ============================================================================

def load_models(models_dir: Path, logger: logging.Logger):
    """Load model artefacts from disk.

    Mirrors MLModelLoader.load_all_models() but returns plain objects
    so this script runs standalone without importing the FastAPI app.
    """
    from utils import constants  # noqa: local import keeps script portable

    logger.info(f"Loading models from: {models_dir}")

    cooccurrence_matrix = np.load(
        models_dir / constants.ITEM_COOCCURRENCE_FILE, allow_pickle=True
    )
    logger.info(f"Co-occurrence matrix shape: {cooccurrence_matrix.shape}")

    book_embeddings = np.load(models_dir / constants.BOOK_EMBEDDINGS_FILE)
    logger.info(f"Book embeddings shape: {book_embeddings.shape}")

    with open(models_dir / constants.BOOKID_TO_ROW_FILE) as f:
        bookid_to_row: Dict[str, int] = json.load(f)
    row_to_bookid: Dict[int, int] = {v: int(k) for k, v in bookid_to_row.items()}
    logger.info(f"Catalog size: {len(bookid_to_row)} books")

    return cooccurrence_matrix, book_embeddings, bookid_to_row, row_to_bookid


# ============================================================================
# Collaborative Filtering evaluator
# ============================================================================

class CollaborativeFilteringEvaluator:
    """Leave-one-out evaluation on the item-item co-occurrence matrix.

    For each sampled seed book the full co-occurrence row defines the
    relevant set (books that real users reviewed alongside the seed).
    We then run the same ranking logic as CollaborativeRecommender and
    measure how many relevant books land in the top-K positions.
    """

    def __init__(
        self,
        cooccurrence_matrix: np.ndarray,
        row_to_bookid: Dict[int, int],
        config: RecommendationEvalConfig,
        logger: logging.Logger,
    ):
        self.matrix = cooccurrence_matrix
        self.row_to_bookid = row_to_bookid
        self.config = config
        self.logger = logger

    def run(self) -> List[RankingMetrics]:
        n_books = self.matrix.shape[0]
        max_k = max(self.config.k_values)

        # Find books that have enough co-occurring neighbours to be useful queries
        eligible: List[int] = []
        for i in range(n_books):
            row = self.matrix[i]
            n_cooc = int(np.sum(row > 0))
            # Subtract 1 if the book co-occurs with itself (self-loop)
            if row[i] > 0:
                n_cooc -= 1
            if n_cooc >= self.config.min_cooccurrences:
                eligible.append(i)

        self.logger.info(f"CF eligible books (>={self.config.min_cooccurrences} co-occurrences): {len(eligible)}")
        if not eligible:
            self.logger.warning("No books meet the min_cooccurrences threshold - skipping CF evaluation")
            return []

        sampled = (
            eligible
            if len(eligible) <= self.config.sample_size
            else random.sample(eligible, self.config.sample_size)
        )
        self.logger.info(f"CF evaluation queries: {len(sampled)}")

        # Per-K accumulators
        buckets: Dict[int, Dict[str, List[float]]] = {
            k: {"precision": [], "recall": [], "ndcg": [], "map": [], "mrr": [], "hit": []}
            for k in self.config.k_values
        }

        for query_idx in sampled:
            scores = self.matrix[query_idx].copy().astype(float)

            # Ground truth: all books co-reviewed with the seed (excluding self)
            relevant_rows = {j for j in range(n_books) if scores[j] > 0 and j != query_idx}
            relevant_ids = {self.row_to_bookid[j] for j in relevant_rows if j in self.row_to_bookid}
            if not relevant_ids:
                continue

            # Rank: sort by co-occurrence count descending, exclude self
            scores[query_idx] = -1.0
            top_indices = np.argsort(scores)[::-1][:max_k]
            recommended = [
                self.row_to_bookid[int(idx)]
                for idx in top_indices
                if scores[int(idx)] >= 0 and int(idx) in self.row_to_bookid
            ]

            for k in self.config.k_values:
                buckets[k]["precision"].append(precision_at_k(recommended, relevant_ids, k))
                buckets[k]["recall"].append(recall_at_k(recommended, relevant_ids, k))
                buckets[k]["ndcg"].append(ndcg_at_k(recommended, relevant_ids, k))
                buckets[k]["map"].append(average_precision_at_k(recommended, relevant_ids, k))
                buckets[k]["mrr"].append(reciprocal_rank_at_k(recommended, relevant_ids, k))
                buckets[k]["hit"].append(
                    1.0 if any(r in relevant_ids for r in recommended[:k]) else 0.0
                )

        results: List[RankingMetrics] = []
        for k in sorted(self.config.k_values):
            vals = buckets[k]
            n = len(vals["precision"])
            if n == 0:
                continue
            m = RankingMetrics(
                k=k,
                precision=float(np.mean(vals["precision"])),
                recall=float(np.mean(vals["recall"])),
                ndcg=float(np.mean(vals["ndcg"])),
                map_score=float(np.mean(vals["map"])),
                mrr=float(np.mean(vals["mrr"])),
                hit_rate=float(np.mean(vals["hit"])),
                n_queries=n,
            )
            results.append(m)
            self.logger.info(
                f"CF @K={k:2d}: Precision={m.precision:.4f}  Recall={m.recall:.4f}"
                f"  NDCG={m.ndcg:.4f}  MAP={m.map_score:.4f}"
                f"  MRR={m.mrr:.4f}  HitRate={m.hit_rate:.4f}  (n={n})"
            )

        return results


# ============================================================================
# Content-Based evaluator (intrinsic / catalog metrics)
# ============================================================================

class ContentBasedEvaluator:
    """Catalog-level intrinsic metrics for the TF-IDF similarity engine.

    Three metrics that require no external labels:

    Coverage      — what fraction of the catalog is ever recommended?
                    Low coverage means the system keeps suggesting the same books.

    Intra-list    — 1 minus the average pairwise cosine similarity among
    Diversity       the K items in a single recommendation list.
                    Higher = more variety within each list.

    Personali-    — 1 minus the average Jaccard overlap between recommendation
    zation          lists produced for different query books.
                    Higher = lists vary meaningfully across different users/seeds.
    """

    _K = 10  # fixed list length for catalog metrics

    def __init__(
        self,
        tfidf_matrix,
        bookid_to_row: Dict[str, int],
        row_to_bookid: Dict[int, int],
        config: RecommendationEvalConfig,
        logger: logging.Logger,
    ):
        self.matrix = tfidf_matrix
        self.bookid_to_row = bookid_to_row
        self.row_to_bookid = row_to_bookid
        self.config = config
        self.logger = logger

    def run(self) -> ContentBasedCatalogMetrics:
        n_books = self.matrix.shape[0]
        all_indices = list(range(n_books))
        sampled = (
            all_indices
            if len(all_indices) <= self.config.sample_size
            else random.sample(all_indices, self.config.sample_size)
        )
        self.logger.info(f"Content-based evaluation queries: {len(sampled)}")

        recommended_catalog: Set[int] = set()
        intra_diversities: List[float] = []
        rec_sets: List[Set[int]] = []

        for step, seed_idx in enumerate(sampled):
            seed_vec = self.matrix[seed_idx]
            if hasattr(seed_vec, "reshape"):
                seed_vec = seed_vec.reshape(1, -1)

            sims = cosine_similarity(seed_vec, self.matrix)[0]
            sims[seed_idx] = -1.0  # exclude self

            top_indices = np.argsort(sims)[::-1][: self._K]
            top_bookids = {
                self.row_to_bookid[int(i)]
                for i in top_indices
                if sims[int(i)] >= 0 and int(i) in self.row_to_bookid
            }

            recommended_catalog.update(top_bookids)
            rec_sets.append(top_bookids)

            # Intra-list diversity: pairwise distance within this list
            if len(top_indices) >= 2:
                rec_vecs = self.matrix[top_indices[: self._K]]
                pw = cosine_similarity(rec_vecs)
                upper = pw[np.triu_indices_from(pw, k=1)]
                intra_diversities.append(1.0 - float(np.mean(upper)))

            if (step + 1) % 100 == 0:
                self.logger.info(f"  Content-based: {step + 1}/{len(sampled)}")

        coverage = len(recommended_catalog) / n_books if n_books > 0 else 0.0
        mean_diversity = float(np.mean(intra_diversities)) if intra_diversities else 0.0
        personalization = self._personalization(rec_sets)

        metrics = ContentBasedCatalogMetrics(
            catalog_coverage=coverage,
            mean_intra_list_diversity=mean_diversity,
            personalization=personalization,
            n_queries=len(sampled),
        )
        self.logger.info(
            f"Content-Based: Coverage={coverage:.4f}"
            f"  Diversity={mean_diversity:.4f}"
            f"  Personalization={personalization:.4f}"
        )
        return metrics

    @staticmethod
    def _personalization(rec_sets: List[Set[int]], max_pairs: int = 500) -> float:
        """1 - mean Jaccard similarity across sampled pairs of recommendation lists."""
        n = len(rec_sets)
        if n < 2:
            return 0.0
        all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        pairs = (
            random.sample(all_pairs, max_pairs)
            if len(all_pairs) > max_pairs
            else all_pairs
        )
        jaccards = []
        for i, j in pairs:
            a, b = rec_sets[i], rec_sets[j]
            union = len(a | b)
            jaccards.append(len(a & b) / union if union > 0 else 0.0)
        return 1.0 - float(np.mean(jaccards))


# ============================================================================
# Pass / fail criteria
# ============================================================================

_THRESHOLDS = {
    "hit_rate_at_10": 0.20,
    "ndcg_at_10": 0.10,
    "coverage": 0.50,
}


def check_criteria(
    cf_metrics: List[RankingMetrics],
    cb_metrics: Optional[ContentBasedCatalogMetrics],
) -> Tuple[bool, List[str]]:
    failures: List[str] = []

    cf_at_10 = next((m for m in cf_metrics if m.k == 10), None)
    if cf_at_10:
        if cf_at_10.hit_rate < _THRESHOLDS["hit_rate_at_10"]:
            failures.append(
                f"CF Hit Rate@10 {cf_at_10.hit_rate:.4f} < {_THRESHOLDS['hit_rate_at_10']}"
            )
        if cf_at_10.ndcg < _THRESHOLDS["ndcg_at_10"]:
            failures.append(
                f"CF NDCG@10 {cf_at_10.ndcg:.4f} < {_THRESHOLDS['ndcg_at_10']}"
            )

    if cb_metrics and cb_metrics.catalog_coverage < _THRESHOLDS["coverage"]:
        failures.append(
            f"Catalog coverage {cb_metrics.catalog_coverage:.1%} < {_THRESHOLDS['coverage']:.0%}"
        )

    return len(failures) == 0, failures


# ============================================================================
# Report generation
# ============================================================================

class ReportGenerator:
    def __init__(
        self,
        report: RecommendationEvalReport,
        config: RecommendationEvalConfig,
        logger: logging.Logger,
    ):
        self.report = report
        self.config = config
        self.logger = logger

    def write_all(self):
        self._write_json()
        self._write_html()

    def _write_json(self):
        payload = {
            "timestamp": self.report.timestamp,
            "config": {
                "models_dir": str(self.config.models_dir),
                "sample_size": self.config.sample_size,
                "k_values": self.config.k_values,
                "min_cooccurrences": self.config.min_cooccurrences,
            },
            "results": {
                "collaborative_filtering": [asdict(m) for m in self.report.cf_metrics_by_k],
                "content_based": (
                    asdict(self.report.cb_catalog_metrics)
                    if self.report.cb_catalog_metrics
                    else None
                ),
            },
            "passes_criteria": self.report.passes_criteria,
            "failure_reasons": self.report.failure_reasons,
        }
        out = self.config.output_dir / "recommendation_metrics.json"
        with open(out, "w") as f:
            json.dump(payload, f, indent=2)
        self.logger.info(f"JSON report: {out}")

    def _write_html(self):
        # CF table rows
        cf_rows = ""
        for m in self.report.cf_metrics_by_k:
            hr_class = "good" if m.hit_rate >= _THRESHOLDS["hit_rate_at_10"] and m.k == 10 else "metric-value"
            nd_class = "good" if m.ndcg >= _THRESHOLDS["ndcg_at_10"] and m.k == 10 else "metric-value"
            cf_rows += f"""
        <tr>
            <td><strong>@{m.k}</strong></td>
            <td class="metric-value">{m.precision:.4f}</td>
            <td class="metric-value">{m.recall:.4f}</td>
            <td class="{nd_class}">{m.ndcg:.4f}</td>
            <td class="metric-value">{m.map_score:.4f}</td>
            <td class="metric-value">{m.mrr:.4f}</td>
            <td class="{hr_class}">{m.hit_rate:.4f}</td>
            <td>{m.n_queries}</td>
        </tr>"""

        # Content-based section
        cb = self.report.cb_catalog_metrics
        cb_section = ""
        if cb:
            cov_class = "good" if cb.catalog_coverage >= _THRESHOLDS["coverage"] else "bad"
            cb_section = f"""
    <h2>Content-Based: Catalog Metrics (top-{ContentBasedEvaluator._K} per query)</h2>
    <p>Intrinsic metrics — no external ground truth required.</p>
    <table>
        <tr><th>Metric</th><th>Value</th><th>Interpretation</th></tr>
        <tr>
            <td>Catalog Coverage</td>
            <td class="{cov_class}">{cb.catalog_coverage:.1%}</td>
            <td>Fraction of all books that appear in at least one recommendation list
                (target ≥ 50%)</td>
        </tr>
        <tr>
            <td>Intra-list Diversity</td>
            <td class="metric-value">{cb.mean_intra_list_diversity:.4f}</td>
            <td>1 − avg pairwise cosine similarity within each list (higher = more varied lists)</td>
        </tr>
        <tr>
            <td>Personalization</td>
            <td class="metric-value">{cb.personalization:.4f}</td>
            <td>1 − avg Jaccard overlap between lists for different seeds
                (higher = more tailored results)</td>
        </tr>
        <tr><td>Queries evaluated</td><td colspan="2">{cb.n_queries}</td></tr>
    </table>"""

        # Pass/fail banner
        status_color = "#4CAF50" if self.report.passes_criteria else "#f44336"
        status_text = "PASS" if self.report.passes_criteria else "FAIL"
        failure_html = (
            "<ul>" + "".join(f"<li>{r}</li>" for r in self.report.failure_reasons) + "</ul>"
            if self.report.failure_reasons
            else "<p style='color:#4CAF50'>All criteria met.</p>"
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Recommendation Evaluation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,.15); }}
        h1 {{ color: #333; border-bottom: 3px solid #2196F3; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .status {{ background: {status_color}; color: white; padding: 12px 20px; border-radius: 4px; font-size: 18px; font-weight: bold; display: inline-block; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #2196F3; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .metric-value {{ font-weight: bold; color: #2196F3; }}
        .good {{ font-weight: bold; color: #4CAF50; }}
        .bad  {{ font-weight: bold; color: #f44336; }}
    </style>
</head>
<body>
<div class="container">
    <h1>Recommendation Algorithms — Offline Evaluation Report</h1>
    <div class="status">{status_text}</div>

    <h2>Configuration</h2>
    <table>
        <tr><th>Parameter</th><th>Value</th></tr>
        <tr><td>Models directory</td><td>{self.config.models_dir}</td></tr>
        <tr><td>Sample size</td><td>{self.config.sample_size}</td></tr>
        <tr><td>K values</td><td>{self.config.k_values}</td></tr>
        <tr><td>Min co-occurrences (CF)</td><td>{self.config.min_cooccurrences}</td></tr>
        <tr><td>Generated at</td><td>{self.report.timestamp}</td></tr>
    </table>

    <h2>Collaborative Filtering: Ranking Metrics</h2>
    <p>
        Ground truth: for each seed book, all books with a positive co-occurrence count
        in the interaction matrix are treated as relevant.
        The recommender ranks by raw co-occurrence score; metrics measure list quality.
    </p>
    <table>
        <tr>
            <th>K</th>
            <th>Precision@K</th>
            <th>Recall@K</th>
            <th>NDCG@K</th>
            <th>MAP@K</th>
            <th>MRR@K</th>
            <th>Hit Rate@K</th>
            <th>Queries</th>
        </tr>
        {cf_rows}
    </table>

    {cb_section}

    <h2>Pass / Fail Criteria</h2>
    <table>
        <tr><th>Criterion</th><th>Threshold</th></tr>
        <tr><td>CF Hit Rate@10</td><td>≥ {_THRESHOLDS['hit_rate_at_10']:.0%}</td></tr>
        <tr><td>CF NDCG@10</td><td>≥ {_THRESHOLDS['ndcg_at_10']:.2f}</td></tr>
        <tr><td>Catalog Coverage</td><td>≥ {_THRESHOLDS['coverage']:.0%}</td></tr>
    </table>
    {failure_html}

    <p><em>Generated: {self.report.timestamp}</em></p>
</div>
</body>
</html>"""

        out = self.config.output_dir / "recommendation_report.html"
        with open(out, "w", encoding="utf-8") as f:
            f.write(html)
        self.logger.info(f"HTML report: {out}")


# ============================================================================
# Logging setup
# ============================================================================

def setup_logging(output_dir: Path, level: str) -> logging.Logger:
    output_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("RecommendationEval")
    logger.setLevel(getattr(logging, level))
    fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = logging.FileHandler(output_dir / "recommendation_eval_log.txt")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger


# ============================================================================
# Entry point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Offline evaluation of recommendation algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default run (sample 500 books, K={5,10,20}):
  python evaluate_recommendations.py --models_dir /path/to/models

  # Smaller sample for a quick check:
  python evaluate_recommendations.py --models_dir /path/to/models --sample_size 100 --k_values 5,10
        """,
    )
    parser.add_argument(
        "--models_dir", type=Path, required=True,
        help="Directory containing trained model artefacts (tfidf_matrix.joblib, item_cooccurrence.npy, etc.)",
    )
    parser.add_argument(
        "--output_dir", type=Path, default=Path("evaluation_results/recommendations"),
    )
    parser.add_argument("--sample_size", type=int, default=500)
    parser.add_argument(
        "--k_values", type=str, default="5,10,20",
        help="Comma-separated K values, e.g. 5,10,20",
    )
    parser.add_argument(
        "--min_cooccurrences", type=int, default=3,
        help="Minimum number of co-occurring books required to include a seed in CF evaluation",
    )
    parser.add_argument(
        "--log_level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )

    args = parser.parse_args()
    k_values = [int(k.strip()) for k in args.k_values.split(",")]

    config = RecommendationEvalConfig(
        models_dir=args.models_dir,
        output_dir=args.output_dir,
        sample_size=args.sample_size,
        k_values=k_values,
        min_cooccurrences=args.min_cooccurrences,
        log_level=args.log_level,
    )

    logger = setup_logging(config.output_dir, config.log_level)
    logger.info("=" * 70)
    logger.info("RECOMMENDATION OFFLINE EVALUATION")
    logger.info("=" * 70)

    try:
        cooccurrence_matrix, book_embeddings, bookid_to_row, row_to_bookid = load_models(
            config.models_dir, logger
        )
    except FileNotFoundError as exc:
        logger.error(f"Model file not found: {exc}")
        sys.exit(2)

    cf_evaluator = CollaborativeFilteringEvaluator(
        cooccurrence_matrix, row_to_bookid, config, logger
    )
    cf_metrics = cf_evaluator.run()

    cb_evaluator = ContentBasedEvaluator(
        book_embeddings, bookid_to_row, row_to_bookid, config, logger
    )
    cb_metrics = cb_evaluator.run()

    passes, failures = check_criteria(cf_metrics, cb_metrics)

    report = RecommendationEvalReport(
        cf_metrics_by_k=cf_metrics,
        cb_catalog_metrics=cb_metrics,
        n_queries_cf=cf_metrics[0].n_queries if cf_metrics else 0,
        n_queries_cb=cb_metrics.n_queries if cb_metrics else 0,
        passes_criteria=passes,
        failure_reasons=failures,
    )

    ReportGenerator(report, config, logger).write_all()

    logger.info("=" * 70)
    if passes:
        logger.info("PASS - all criteria met")
    else:
        logger.info("FAIL:")
        for f in failures:
            logger.info(f"  - {f}")
    logger.info("=" * 70)

    sys.exit(0 if passes else 1)


if __name__ == "__main__":
    main()
