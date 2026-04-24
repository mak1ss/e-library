#!/usr/bin/env python3
"""
Task 2.7: Offline Evaluation Script for Review Relevance Scoring System

Purpose:
  Validate review relevance scoring model quality on ground truth dataset
  before integrating with live system.

Usage:
  python offline_evaluation.py \\
    --dataset phase1_datasets/ground_truth_evaluation_set.csv \\
    --model all-MiniLM-L6-v2 \\
    --output_dir evaluation_results/ \\
    --sample_size 10000 \\
    --score_threshold 0.6

Output:
  - evaluation_report.html (interactive report)
  - evaluation_metrics.json (machine-readable results)
  - evaluation_log.txt (detailed processing log)
  - flagged_outliers.csv (anomalous scores)

Status: Phase 2, Task 2.7 - COMPLETE
"""

import argparse
import csv
import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import math
from collections import defaultdict
import statistics

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics import (
    precision_score, recall_score, f1_score, accuracy_score,
    confusion_matrix, roc_auc_score, roc_curve
)

# ============================================================================
# Configuration & Data Classes
# ============================================================================

@dataclass
class EvaluationConfig:
    """Configuration for offline evaluation"""
    dataset_path: Path
    model_name: str
    output_dir: Path
    sample_size: int
    score_threshold: float
    quick_test: bool = False
    log_level: str = "INFO"

    def __post_init__(self):
        """Validate configuration"""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")
        self.output_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class ScoringRecord:
    """Single book-review pair scoring result"""
    book_id: int
    review_id: str
    book_text: str  # Aggregated metadata (Task 2.1)
    review_text: str  # Raw text
    review_text_preprocessed: str  # After Task 2.3 pipeline
    book_embedding: np.ndarray
    review_embedding: np.ndarray
    raw_cosine_similarity: float
    relevance_score: float  # Normalized [0.0, 1.0]
    confidence: float  # [0.0, 1.0]
    ground_truth_label: str  # "RELEVANT" | "IRRELEVANT"
    processing_time_ms: float
    review_length: int
    book_length: int


@dataclass
class EvaluationMetrics:
    """Complete evaluation results"""
    # Distribution metrics
    mean_score: float
    median_score: float
    std_dev: float
    min_score: float
    max_score: float
    score_histogram: Dict[str, int]  # "0.0-0.1": count, ...
    
    # Quality metrics at threshold
    threshold: float
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    
    # Confusion matrix
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int
    
    # Performance metrics
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    total_runtime_sec: float
    throughput_per_sec: float
    
    # Correlation metrics
    correlation_score_to_label: float
    
    # Edge cases
    null_score_count: int
    short_review_count: int
    long_review_count: int
    poor_metadata_count: int
    
    # Pass/fail
    passes_criteria: bool
    failure_reasons: List[str]


# ============================================================================
# Core Scoring Functions (from Tasks 2.1-2.5)
# ============================================================================

class BookMetadataAggregator:
    """Task 2.1: Aggregate book metadata using Strategy C"""
    
    @staticmethod
    def aggregate_from_dict(book_data: Dict[str, Any]) -> str:
        """
        Aggregate book metadata (Strategy C: Selective Fields with Priority)
        
        Order: Title → Author → Genres → Category → Description
        Skip NULL fields entirely
        
        Args:
            book_data: dict with keys: title, author, genres, category, description
        
        Returns:
            Aggregated text (max ~500 chars)
        """
        parts = []
        
        # Always include title
        if book_data.get('title'):
            parts.append(f"Title: {book_data['title']}")
        
        # Author (high signal)
        if book_data.get('author'):
            parts.append(f"Author: {book_data['author']}")
        
        # Genres (categorical signal)
        if book_data.get('genres'):
            genres = book_data['genres']
            if isinstance(genres, list):
                genres = ', '.join(genres)
            if genres:
                parts.append(f"Genres: {genres}")
        
        # Category (categorical signal)
        if book_data.get('category'):
            parts.append(f"Category: {book_data['category']}")
        
        # Description (most semantic-rich, prioritize)
        if book_data.get('description'):
            parts.append(f"Description: {book_data['description']}")
        
        return '\n'.join(parts)


class ReviewTextPreprocessor:
    """Task 2.3: Preprocess review text (7-step pipeline)"""
    
    @staticmethod
    def preprocess(text: str) -> str:
        """
        Preprocess review text using 7-step pipeline
        
        Steps:
        1. HTML decode (&amp; → &, etc.)
        2. Lowercase
        3. Remove emojis/unicode
        4. Normalize whitespace
        5. Remove spoiler markers
        6. Collapse repeated punctuation
        7. Truncate at 1800 chars or 450 tokens
        
        Args:
            text: Raw review text
        
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Step 1: HTML decode
        import html
        text = html.unescape(text)
        
        # Step 2: Lowercase
        text = text.lower()
        
        # Step 3: Remove emojis/unicode (keep ASCII + common punctuation)
        text = ''.join(
            c if ord(c) < 128 or c in '\n\t' else ''
            for c in text
        )
        
        # Step 4: Normalize whitespace
        text = ' '.join(text.split())
        
        # Step 5: Remove spoiler markers
        spoiler_patterns = [
            'spoiler alert:', 'spoiler:', 'spoilers:',
            'trigger warning:', 'content warning:'
        ]
        for pattern in spoiler_patterns:
            text = text.replace(pattern, '')
        
        # Step 6: Collapse repeated punctuation
        while '!!' in text:
            text = text.replace('!!', '!')
        while '??' in text:
            text = text.replace('??', '?')
        while '..' in text:
            text = text.replace('..', '.')
        
        # Step 7: Truncate at sentence boundary (~450 tokens = ~1800 chars)
        max_chars = 1800
        if len(text) > max_chars:
            # Find last sentence boundary
            text = text[:max_chars]
            last_period = max(
                text.rfind('.'),
                text.rfind('!'),
                text.rfind('?')
            )
            if last_period > max_chars - 200:  # If near end
                text = text[:last_period + 1]
        
        return text


class RelevanceScoringFunction:
    """Task 2.5: Core relevance scoring function"""
    
    @staticmethod
    def score_relevance(
        book_embedding: np.ndarray,
        review_embedding: np.ndarray,
        text_quality: float = 0.5
    ) -> Tuple[float, float, float]:
        """
        Compute relevance score from embeddings via cosine similarity
        
        Args:
            book_embedding: Sentence transformer embedding for book
            review_embedding: Sentence transformer embedding for review
            text_quality: Quality score [0, 1] for confidence computation
        
        Returns:
            Tuple of (relevance_score, raw_cosine_similarity, confidence)
            - relevance_score: [0.0, 1.0] normalized
            - raw_cosine_similarity: [-1.0, 1.0] before normalization
            - confidence: [0.0, 1.0] confidence in score
        """
        # Input validation
        if book_embedding is None or review_embedding is None:
            return None, None, None
        
        if len(book_embedding) == 0 or len(review_embedding) == 0:
            return None, None, None
        
        # Compute cosine similarity
        norm_book = np.linalg.norm(book_embedding)
        norm_review = np.linalg.norm(review_embedding)
        
        if norm_book == 0 or norm_review == 0:
            return None, None, None
        
        raw_cosine = np.dot(book_embedding, review_embedding) / (norm_book * norm_review)
        raw_cosine = float(np.clip(raw_cosine, -1.0, 1.0))
        
        # Normalize to [0, 1]
        relevance_score = (raw_cosine + 1.0) / 2.0
        
        # Confidence: high when |cosine_sim| is high (strong signal)
        confidence = (abs(raw_cosine) * 0.7) + (text_quality * 0.3)
        confidence = float(np.clip(confidence, 0.0, 1.0))
        
        return relevance_score, raw_cosine, confidence


# ============================================================================
# Dataset Loading
# ============================================================================

class GroundTruthDataset:
    """Load and manage ground truth evaluation dataset"""
    
    def __init__(self, csv_path: Path, sample_size: int = 10000):
        """
        Load ground truth dataset from CSV
        
        Expected columns:
        - book_id: int
        - review_id: string (UUID)
        - book_text: string (aggregated metadata)
        - review_text: string (raw review)
        - review_rating: float (1-5)
        - relevance_label: string ("RELEVANT" | "IRRELEVANT")
        
        Args:
            csv_path: Path to ground_truth_evaluation_set.csv
            sample_size: Max records to load (10000 for full, 100 for quick test)
        """
        self.csv_path = csv_path
        self.records = []
        self._load(sample_size)
    
    def _load(self, max_records: int):
        """Load dataset from CSV"""
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= max_records:
                    break
                
                self.records.append({
                    'book_id': int(row['book_id']),
                    'review_id': row['review_id'],
                    'book_text': row.get('book_text', ''),
                    'review_text': row.get('review_text', ''),
                    'review_rating': float(row.get('review_rating', 3.0)),
                    'relevance_label': row['relevance_label'],  # Ground truth
                })
    
    def __len__(self) -> int:
        return len(self.records)
    
    def __iter__(self):
        return iter(self.records)


# ============================================================================
# Evaluation Engine
# ============================================================================

class OfflineEvaluationEngine:
    """Main evaluation orchestrator"""
    
    def __init__(self, config: EvaluationConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.model: Optional[SentenceTransformer] = None
        self.scoring_records: List[ScoringRecord] = []
        self.metrics: Optional[EvaluationMetrics] = None
    
    def run(self) -> EvaluationMetrics:
        """Execute full evaluation pipeline"""
        start_time = time.time()
        self.logger.info(f"Starting evaluation: {self.config.sample_size} samples")
        
        try:
            # Step 1: Load model
            self._load_model()
            
            # Step 2: Load dataset
            dataset = self._load_dataset()
            
            # Step 3: Score all samples
            self._score_all_samples(dataset)
            
            # Step 4: Compute metrics
            self.metrics = self._compute_metrics()
            
            # Step 5: Generate report
            self._generate_report()
            
            total_time = time.time() - start_time
            self.logger.info(f"Evaluation complete in {total_time:.1f}s")
            
            return self.metrics
        
        except Exception as e:
            self.logger.error(f"Evaluation failed: {e}", exc_info=True)
            raise
    
    def _load_model(self):
        """Load sentence transformer model"""
        self.logger.info(f"Loading model: {self.config.model_name}")
        try:
            self.model = SentenceTransformer(self.config.model_name)
            self.logger.info(f"Model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_dataset(self) -> GroundTruthDataset:
        """Load ground truth dataset"""
        self.logger.info(f"Loading dataset: {self.config.dataset_path}")
        dataset = GroundTruthDataset(
            self.config.dataset_path,
            sample_size=self.config.sample_size
        )
        self.logger.info(f"Loaded {len(dataset)} samples")
        return dataset
    
    def _score_all_samples(self, dataset: GroundTruthDataset):
        """Score all book-review pairs and measure latency"""
        start_time = time.time()
        latencies = []
        
        for i, record in enumerate(dataset):
            sample_start = time.time()
            
            try:
                # Preprocess review
                review_preprocessed = ReviewTextPreprocessor.preprocess(
                    record['review_text']
                )
                
                # Generate embeddings
                book_embedding = self.model.encode(record['book_text'])
                review_embedding = self.model.encode(review_preprocessed)
                
                # Score relevance
                score, raw_cos, confidence = RelevanceScoringFunction.score_relevance(
                    book_embedding,
                    review_embedding,
                    text_quality=0.5
                )
                
                # Record result
                latency_ms = (time.time() - sample_start) * 1000
                latencies.append(latency_ms)
                
                self.scoring_records.append(ScoringRecord(
                    book_id=record['book_id'],
                    review_id=record['review_id'],
                    book_text=record['book_text'],
                    review_text=record['review_text'],
                    review_text_preprocessed=review_preprocessed,
                    book_embedding=book_embedding,
                    review_embedding=review_embedding,
                    raw_cosine_similarity=raw_cos if raw_cos is not None else float('nan'),
                    relevance_score=score if score is not None else float('nan'),
                    confidence=confidence if confidence is not None else float('nan'),
                    ground_truth_label=record['relevance_label'],
                    processing_time_ms=latency_ms,
                    review_length=len(record['review_text'].split()),
                    book_length=len(record['book_text'].split()),
                ))
            
            except Exception as e:
                self.logger.error(f"Failed to score sample {i}: {e}")
                continue
            
            if (i + 1) % 100 == 0:
                self.logger.info(f"Scored {i + 1}/{len(dataset)} samples")
        
        total_time = time.time() - start_time
        self.logger.info(f"Scoring complete: {total_time:.1f}s for {len(self.scoring_records)} samples")
        self.logger.info(f"Average latency: {np.mean(latencies):.1f}ms")
    
    def _compute_metrics(self) -> EvaluationMetrics:
        """Compute all evaluation metrics"""
        self.logger.info("Computing evaluation metrics...")
        
        # Extract data
        scores = [r.relevance_score for r in self.scoring_records]
        labels = [1 if r.ground_truth_label == "RELEVANT" else 0 
                  for r in self.scoring_records]
        latencies = [r.processing_time_ms for r in self.scoring_records]
        
        # Remove NaN scores for metrics
        valid_mask = np.array([not math.isnan(s) for s in scores])
        valid_scores = np.array(scores)[valid_mask]
        valid_labels = np.array(labels)[valid_mask]
        
        # Distribution metrics
        mean_score = float(np.mean(valid_scores))
        median_score = float(np.median(valid_scores))
        std_dev = float(np.std(valid_scores))
        min_score = float(np.min(valid_scores))
        max_score = float(np.max(valid_scores))
        
        # Score histogram
        histogram = defaultdict(int)
        for score in valid_scores:
            bin_idx = int(score * 10)  # 0.0-0.1, 0.1-0.2, ...
            bin_idx = min(bin_idx, 9)  # Cap at 0.9-1.0
            histogram[f"{bin_idx * 0.1:.1f}-{(bin_idx + 1) * 0.1:.1f}"] += 1
        
        # Compute binary predictions at threshold
        predictions = np.array([1 if s >= self.config.score_threshold else 0 
                               for s in valid_scores])
        
        # Quality metrics
        cm = confusion_matrix(valid_labels, predictions)
        tn, fp, fn, tp = cm.ravel()
        
        accuracy = accuracy_score(valid_labels, predictions)
        precision = precision_score(valid_labels, predictions, zero_division=0)
        recall = recall_score(valid_labels, predictions, zero_division=0)
        f1 = f1_score(valid_labels, predictions, zero_division=0)
        roc_auc = roc_auc_score(valid_labels, valid_scores)
        
        # Latency percentiles
        p50 = float(np.percentile(latencies, 50))
        p95 = float(np.percentile(latencies, 95))
        p99 = float(np.percentile(latencies, 99))
        
        # Throughput
        total_time = sum(latencies) / 1000  # ms to seconds
        throughput = len(self.scoring_records) / total_time if total_time > 0 else 0
        
        # Correlation with label
        try:
            correlation = float(np.corrcoef(valid_scores, valid_labels)[0, 1])
        except:
            correlation = 0.0
        
        # Edge cases
        null_count = sum(1 for s in scores if math.isnan(s))
        short_count = sum(1 for r in self.scoring_records if r.review_length < 5)
        long_count = sum(1 for r in self.scoring_records if r.review_length > 300)
        poor_metadata = sum(1 for r in self.scoring_records if r.book_length < 5)
        
        # Pass/fail criteria
        failure_reasons = []
        passes = True
        
        if accuracy < 0.70:
            failure_reasons.append(f"Accuracy {accuracy:.2%} < 0.70")
            passes = False
        if precision < 0.65:
            failure_reasons.append(f"Precision {precision:.2%} < 0.65")
            passes = False
        if recall < 0.65:
            failure_reasons.append(f"Recall {recall:.2%} < 0.65")
            passes = False
        if p95 > 500:
            failure_reasons.append(f"P95 latency {p95:.0f}ms > 500ms")
            passes = False
        if null_count / len(scores) > 0.01:
            failure_reasons.append(f"NULL scores {null_count / len(scores):.1%} > 1%")
            passes = False
        
        metrics = EvaluationMetrics(
            mean_score=mean_score,
            median_score=median_score,
            std_dev=std_dev,
            min_score=min_score,
            max_score=max_score,
            score_histogram=dict(sorted(histogram.items())),
            threshold=self.config.score_threshold,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1=f1,
            roc_auc=roc_auc,
            true_positives=int(tp),
            true_negatives=int(tn),
            false_positives=int(fp),
            false_negatives=int(fn),
            p50_latency_ms=p50,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            total_runtime_sec=total_time,
            throughput_per_sec=throughput,
            correlation_score_to_label=correlation,
            null_score_count=null_count,
            short_review_count=short_count,
            long_review_count=long_count,
            poor_metadata_count=poor_metadata,
            passes_criteria=passes,
            failure_reasons=failure_reasons,
        )
        
        # Log results
        self._log_metrics(metrics)
        return metrics
    
    def _log_metrics(self, metrics: EvaluationMetrics):
        """Log metrics to logger"""
        self.logger.info("=" * 70)
        self.logger.info("EVALUATION RESULTS")
        self.logger.info("=" * 70)
        self.logger.info(f"Samples evaluated: {len(self.scoring_records)}")
        self.logger.info(f"Threshold: {metrics.threshold}")
        self.logger.info("")
        self.logger.info("DISTRIBUTION:")
        self.logger.info(f"  Mean score: {metrics.mean_score:.3f}")
        self.logger.info(f"  Median score: {metrics.median_score:.3f}")
        self.logger.info(f"  Std dev: {metrics.std_dev:.3f}")
        self.logger.info(f"  Range: [{metrics.min_score:.3f}, {metrics.max_score:.3f}]")
        self.logger.info("")
        self.logger.info("QUALITY METRICS:")
        self.logger.info(f"  Accuracy: {metrics.accuracy:.1%}")
        self.logger.info(f"  Precision: {metrics.precision:.1%}")
        self.logger.info(f"  Recall: {metrics.recall:.1%}")
        self.logger.info(f"  F1 Score: {metrics.f1:.3f}")
        self.logger.info(f"  ROC-AUC: {metrics.roc_auc:.3f}")
        self.logger.info("")
        self.logger.info("CONFUSION MATRIX:")
        self.logger.info(f"  TP: {metrics.true_positives}, FP: {metrics.false_positives}")
        self.logger.info(f"  FN: {metrics.false_negatives}, TN: {metrics.true_negatives}")
        self.logger.info("")
        self.logger.info("LATENCY:")
        self.logger.info(f"  P50: {metrics.p50_latency_ms:.1f}ms")
        self.logger.info(f"  P95: {metrics.p95_latency_ms:.1f}ms")
        self.logger.info(f"  P99: {metrics.p99_latency_ms:.1f}ms")
        self.logger.info(f"  Total runtime: {metrics.total_runtime_sec:.1f}s")
        self.logger.info(f"  Throughput: {metrics.throughput_per_sec:.1f} samples/sec")
        self.logger.info("")
        self.logger.info("EDGE CASES:")
        self.logger.info(f"  NULL scores: {metrics.null_score_count}")
        self.logger.info(f"  Short reviews (<5 words): {metrics.short_review_count}")
        self.logger.info(f"  Long reviews (>300 words): {metrics.long_review_count}")
        self.logger.info(f"  Poor metadata (<5 words): {metrics.poor_metadata_count}")
        self.logger.info("")
        
        if metrics.passes_criteria:
            self.logger.info("✅ PASS: All success criteria met!")
        else:
            self.logger.info("❌ FAIL: Some criteria not met:")
            for reason in metrics.failure_reasons:
                self.logger.info(f"   - {reason}")
        self.logger.info("=" * 70)
    
    def _generate_report(self):
        """Generate evaluation reports"""
        # JSON report
        self._write_json_report()
        
        # HTML report
        self._write_html_report()
        
        # Flagged outliers CSV
        self._write_outliers_csv()
        
        self.logger.info(f"Reports written to: {self.config.output_dir}")
    
    def _write_json_report(self):
        """Write machine-readable JSON report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'config': {
                'dataset': str(self.config.dataset_path),
                'model': self.config.model_name,
                'sample_size': self.config.sample_size,
                'threshold': self.config.score_threshold,
            },
            'metrics': asdict(self.metrics),
        }
        
        output_file = self.config.output_dir / 'evaluation_metrics.json'
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"JSON report: {output_file}")
    
    def _write_html_report(self):
        """Write interactive HTML report"""
        # Build histogram HTML
        histogram_html = "<tr>"
        for bin_label in sorted(self.metrics.score_histogram.keys()):
            count = self.metrics.score_histogram[bin_label]
            width = (count / max(self.metrics.score_histogram.values())) * 200
            histogram_html += f"""
            <td style="text-align: center; padding: 5px;">
                <div style="height: {width}px; background: #4CAF50; margin: 5px;"></div>
                <small>{bin_label}</small><br/>
                <small>{count}</small>
            </td>"""
        histogram_html += "</tr>"
        
        # Determine status color
        status_color = "#4CAF50" if self.metrics.passes_criteria else "#f44336"
        status_text = "✅ PASS" if self.metrics.passes_criteria else "❌ FAIL"
        
        # Failure reasons HTML
        failure_html = ""
        if self.metrics.failure_reasons:
            failure_html = "<ul>"
            for reason in self.metrics.failure_reasons:
                failure_html += f"<li>{reason}</li>"
            failure_html += "</ul>"
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Review Relevance Evaluation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #2196F3; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .status {{ background: {status_color}; color: white; padding: 15px; border-radius: 4px; font-size: 18px; font-weight: bold; width: fit-content; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #2196F3; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .metric-value {{ font-weight: bold; color: #2196F3; }}
        .good {{ color: #4CAF50; }}
        .bad {{ color: #f44336; }}
        .histogram {{ display: flex; align-items: flex-end; height: 250px; justify-content: space-around; }}
        .bar {{ flex: 1; margin: 0 5px; background: #2196F3; border-radius: 4px 4px 0 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Review Relevance Scoring System - Offline Evaluation Report</h1>
        
        <div class="status">{status_text}</div>
        
        <h2>📋 Evaluation Configuration</h2>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Dataset</td><td>{self.config.dataset_path}</td></tr>
            <tr><td>Model</td><td>{self.config.model_name}</td></tr>
            <tr><td>Samples Evaluated</td><td>{len(self.scoring_records)}</td></tr>
            <tr><td>Score Threshold</td><td><span class="metric-value">{self.metrics.threshold}</span></td></tr>
            <tr><td>Timestamp</td><td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
        </table>
        
        <h2>📊 Score Distribution</h2>
        <table>
            <tr>
                <th>Metric</th><th>Value</th>
            </tr>
            <tr><td>Mean Score</td><td><span class="metric-value">{self.metrics.mean_score:.4f}</span></td></tr>
            <tr><td>Median Score</td><td><span class="metric-value">{self.metrics.median_score:.4f}</span></td></tr>
            <tr><td>Standard Deviation</td><td>{self.metrics.std_dev:.4f}</td></tr>
            <tr><td>Min Score</td><td>{self.metrics.min_score:.4f}</td></tr>
            <tr><td>Max Score</td><td>{self.metrics.max_score:.4f}</td></tr>
        </table>
        
        <h3>Score Histogram (0.0 - 1.0)</h3>
        <table>
            {histogram_html}
        </table>
        
        <h2>✅ Quality Metrics (at threshold {self.metrics.threshold})</h2>
        <table>
            <tr>
                <th>Metric</th><th>Value</th><th>Status</th>
            </tr>
            <tr>
                <td>Accuracy</td>
                <td><span class="metric-value">{self.metrics.accuracy:.1%}</span></td>
                <td><span class="{'good' if self.metrics.accuracy >= 0.70 else 'bad'}">
                    {'✅' if self.metrics.accuracy >= 0.70 else '❌'} {'Pass' if self.metrics.accuracy >= 0.70 else 'Fail'} (target: ≥ 0.70)</span>
                </td>
            </tr>
            <tr>
                <td>Precision</td>
                <td><span class="metric-value">{self.metrics.precision:.1%}</span></td>
                <td><span class="{'good' if self.metrics.precision >= 0.65 else 'bad'}">
                    {'✅' if self.metrics.precision >= 0.65 else '❌'} {'Pass' if self.metrics.precision >= 0.65 else 'Fail'} (target: ≥ 0.65)</span>
                </td>
            </tr>
            <tr>
                <td>Recall</td>
                <td><span class="metric-value">{self.metrics.recall:.1%}</span></td>
                <td><span class="{'good' if self.metrics.recall >= 0.65 else 'bad'}">
                    {'✅' if self.metrics.recall >= 0.65 else '❌'} {'Pass' if self.metrics.recall >= 0.65 else 'Fail'} (target: ≥ 0.65)</span>
                </td>
            </tr>
            <tr>
                <td>F1 Score</td>
                <td><span class="metric-value">{self.metrics.f1:.4f}</span></td>
                <td></td>
            </tr>
            <tr>
                <td>ROC-AUC</td>
                <td><span class="metric-value">{self.metrics.roc_auc:.4f}</span></td>
                <td></td>
            </tr>
        </table>
        
        <h2>🎯 Confusion Matrix (at threshold {self.metrics.threshold})</h2>
        <table>
            <tr><th></th><th>Predicted Relevant</th><th>Predicted Irrelevant</th></tr>
            <tr><td><strong>Actually Relevant</strong></td><td style="background: #c8e6c9;">{self.metrics.true_positives}</td><td style="background: #ffcdd2;">{self.metrics.false_negatives}</td></tr>
            <tr><td><strong>Actually Irrelevant</strong></td><td style="background: #ffcdd2;">{self.metrics.false_positives}</td><td style="background: #c8e6c9;">{self.metrics.true_negatives}</td></tr>
        </table>
        
        <h2>⚡ Performance / Latency</h2>
        <table>
            <tr>
                <th>Metric</th><th>Value</th><th>Status</th>
            </tr>
            <tr>
                <td>P50 Latency</td>
                <td><span class="metric-value">{self.metrics.p50_latency_ms:.1f} ms</span></td>
                <td></td>
            </tr>
            <tr>
                <td>P95 Latency</td>
                <td><span class="metric-value">{self.metrics.p95_latency_ms:.1f} ms</span></td>
                <td><span class="{'good' if self.metrics.p95_latency_ms < 500 else 'bad'}">
                    {'✅' if self.metrics.p95_latency_ms < 500 else '❌'} {'Pass' if self.metrics.p95_latency_ms < 500 else 'Fail'} (target: &lt; 500ms)</span>
                </td>
            </tr>
            <tr>
                <td>P99 Latency</td>
                <td><span class="metric-value">{self.metrics.p99_latency_ms:.1f} ms</span></td>
                <td></td>
            </tr>
            <tr>
                <td>Total Runtime</td>
                <td><span class="metric-value">{self.metrics.total_runtime_sec:.1f} sec</span></td>
                <td></td>
            </tr>
            <tr>
                <td>Throughput</td>
                <td><span class="metric-value">{self.metrics.throughput_per_sec:.1f} samples/sec</span></td>
                <td></td>
            </tr>
        </table>
        
        <h2>🔗 Correlation & Edge Cases</h2>
        <table>
            <tr>
                <th>Metric</th><th>Value</th>
            </tr>
            <tr>
                <td>Score-to-Label Correlation</td>
                <td><span class="metric-value">{self.metrics.correlation_score_to_label:.4f}</span></td>
            </tr>
            <tr>
                <td>NULL/NaN Scores</td>
                <td>{self.metrics.null_score_count} ({self.metrics.null_score_count / len(self.scoring_records):.1%})</td>
            </tr>
            <tr>
                <td>Short Reviews (&lt;5 words)</td>
                <td>{self.metrics.short_review_count}</td>
            </tr>
            <tr>
                <td>Long Reviews (&gt;300 words)</td>
                <td>{self.metrics.long_review_count}</td>
            </tr>
            <tr>
                <td>Poor Book Metadata (&lt;5 words)</td>
                <td>{self.metrics.poor_metadata_count}</td>
            </tr>
        </table>
        
        <h2>📝 Summary</h2>
        {failure_html}
        
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        output_file = self.config.output_dir / 'evaluation_report.html'
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report: {output_file}")
    
    def _write_outliers_csv(self):
        """Identify and write flagged outliers"""
        outliers = []
        
        for record in self.scoring_records:
            is_outlier = False
            reasons = []
            
            # High rating but low predicted score
            if record.book_embedding is not None:
                label = record.ground_truth_label
                score = record.relevance_score
                
                if label == "RELEVANT" and score < 0.4:
                    is_outlier = True
                    reasons.append(f"Low score for relevant review")
                elif label == "IRRELEVANT" and score > 0.7:
                    is_outlier = True
                    reasons.append(f"High score for irrelevant review")
            
            if is_outlier:
                outliers.append({
                    'review_id': record.review_id,
                    'book_id': record.book_id,
                    'predicted_score': record.relevance_score,
                    'ground_truth': record.ground_truth_label,
                    'confidence': record.confidence,
                    'review_length': record.review_length,
                    'reasons': '; '.join(reasons),
                })
        
        output_file = self.config.output_dir / 'flagged_outliers.csv'
        if outliers:
            keys = outliers[0].keys()
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(outliers)
            self.logger.info(f"Outliers CSV: {output_file} ({len(outliers)} outliers)")
        else:
            self.logger.info(f"No outliers found")


# ============================================================================
# CLI & Main
# ============================================================================

def setup_logging(log_dir: Path, level_name: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("OfflineEvaluation")
    logger.setLevel(getattr(logging, level_name))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level_name))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_dir / 'evaluation_log.txt')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Offline evaluation of review relevance scoring system',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full evaluation (10,000 samples):
  python offline_evaluation.py --sample_size 10000
  
  # Quick test (100 samples):
  python offline_evaluation.py --sample_size 100 --quick_test
  
  # Medium test (1,000 samples):
  python offline_evaluation.py --sample_size 1000
        """
    )
    
    parser.add_argument(
        '--dataset',
        type=Path,
        default=Path('phase1_datasets/ground_truth_evaluation_set.csv'),
        help='Path to ground truth dataset CSV'
    )
    
    parser.add_argument(
        '--model',
        default='all-MiniLM-L6-v2',
        help='Sentence transformer model name'
    )
    
    parser.add_argument(
        '--output_dir',
        type=Path,
        default=Path('evaluation_results'),
        help='Output directory for reports'
    )
    
    parser.add_argument(
        '--sample_size',
        type=int,
        default=100,
        help='Number of samples to evaluate (100, 1000, or 10000)'
    )
    
    parser.add_argument(
        '--score_threshold',
        type=float,
        default=0.6,
        help='Score threshold for binary classification'
    )
    
    parser.add_argument(
        '--quick_test',
        action='store_true',
        help='Run quick test (100 samples)'
    )
    
    parser.add_argument(
        '--log_level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.output_dir, args.log_level)
    
    # Create config
    config = EvaluationConfig(
        dataset_path=args.dataset,
        model_name=args.model,
        output_dir=args.output_dir,
        sample_size=args.sample_size if not args.quick_test else 100,
        score_threshold=args.score_threshold,
        quick_test=args.quick_test,
        log_level=args.log_level,
    )
    
    # Run evaluation
    try:
        engine = OfflineEvaluationEngine(config, logger)
        metrics = engine.run()
        
        # Exit code based on pass/fail
        sys.exit(0 if metrics.passes_criteria else 1)
    
    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == '__main__':
    main()
