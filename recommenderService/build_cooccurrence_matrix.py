#!/usr/bin/env python3
"""
Offline build script: generate rating-weighted item-item co-occurrence matrix.

Each (book_i, book_j) co-occurrence is weighted by min(r_i, r_j) / 5.0 so
mutually-liked pairs accumulate high scores while mixed-sentiment pairs
contribute near zero.

Usage:
  python build_cooccurrence_matrix.py \\
    --reviews_json data/seeding/reviews.json \\
    --models_dir   data/ml_models \\
    [--books_csv   data/books.csv]  \\
    [--min_rating  1]

Expected reviews JSON format (list of objects):
  [{"userId": "...", "bookId": 1, "rating": 3}, ...]

Writes:
  <models_dir>/item_cooccurrence.npy   — float32 array, shape (n_books, n_books)
  <models_dir>/bookid_to_row.json      — {"<book_id>": <row_index>, ...}
"""

import argparse
import csv
import json
import logging
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("BuildCooccurrenceMatrix")


def load_reviews(reviews_path: Path, min_rating: int) -> List[Tuple[str, int, int]]:
    """Return list of (user_id, book_id, rating) after applying min_rating filter."""
    with open(reviews_path, encoding="utf-8") as f:
        raw = json.load(f)

    reviews = []
    skipped = 0
    for item in raw:
        try:
            user_id = str(item["userId"])
            book_id = int(item["bookId"])
            rating = int(item["rating"])
        except (KeyError, ValueError) as exc:
            logger.warning(f"Skipping malformed record: {exc} — {item}")
            skipped += 1
            continue

        if rating < min_rating:
            skipped += 1
            continue

        reviews.append((user_id, book_id, rating))

    logger.info(f"Loaded {len(reviews)} reviews ({skipped} skipped by filter or malform)")
    return reviews


def load_book_order_from_csv(books_csv: Path) -> List[int]:
    """Return ordered list of book_ids from CSV (keeps TF-IDF/embeddings artefacts in sync)."""
    ids: List[int] = []
    with open(books_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ids.append(int(row["book_id"]))
            except (KeyError, ValueError) as exc:
                logger.warning(f"Skipping CSV row with invalid book_id: {exc}")
    logger.info(f"Loaded {len(ids)} book IDs from {books_csv}")
    return ids


def build_matrix(
    reviews: List[Tuple[str, int, int]],
    bookid_to_row: Dict[str, int],
    n_books: int,
) -> np.ndarray:
    """Build the weighted co-occurrence matrix from (user, book, rating) triples."""
    matrix = np.zeros((n_books, n_books), dtype=np.float32)

    # Group by user
    user_reviews: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
    for user_id, book_id, rating in reviews:
        row = bookid_to_row.get(str(book_id))
        if row is None:
            continue
        user_reviews[user_id].append((row, rating))

    total_pairs = 0
    for user_id, items in user_reviews.items():
        for (row_i, r_i), (row_j, r_j) in combinations(items, 2):
            weight = min(r_i, r_j) / 5.0
            matrix[row_i][row_j] += weight
            matrix[row_j][row_i] += weight
            total_pairs += 1

    logger.info(f"Processed {total_pairs} user-book pairs across {len(user_reviews)} users")
    return matrix


def log_matrix_stats(matrix: np.ndarray, row_to_bookid: Dict[int, int]) -> None:
    """Log sparsity and top-5 highest-weighted pairs."""
    n = matrix.shape[0]
    total_cells = n * n
    nonzero = int(np.count_nonzero(matrix))
    sparsity = 1.0 - nonzero / total_cells
    logger.info(f"Matrix shape: {matrix.shape}  non-zero: {nonzero}  sparsity: {sparsity:.4f}")

    # Top-5 pairs (upper triangle only to avoid duplicates)
    upper = np.triu(matrix, k=1)
    flat = upper.flatten()
    top5_flat = np.argsort(flat)[-5:][::-1]
    logger.info("Top-5 highest-weighted book pairs:")
    for idx in top5_flat:
        i, j = divmod(int(idx), n)
        bid_i = row_to_bookid.get(i, f"row{i}")
        bid_j = row_to_bookid.get(j, f"row{j}")
        logger.info(f"  book {bid_i} ↔ book {bid_j}: {matrix[i][j]:.3f}")


def build(
    reviews_json: Path,
    models_dir: Path,
    books_csv: Path | None,
    min_rating: int,
) -> None:
    models_dir.mkdir(parents=True, exist_ok=True)

    from utils import constants

    reviews = load_reviews(reviews_json, min_rating)
    if not reviews:
        logger.error("No reviews loaded — check path and min_rating setting")
        sys.exit(1)

    # Determine book ordering
    if books_csv and books_csv.exists():
        ordered_ids = load_book_order_from_csv(books_csv)
        # Include any book_ids from reviews not in the CSV
        review_ids = {bid for _, bid, _ in reviews}
        extra = sorted(bid for bid in review_ids if bid not in set(ordered_ids))
        if extra:
            logger.warning(f"{len(extra)} book IDs in reviews not found in CSV — appending: {extra[:10]}")
            ordered_ids.extend(extra)
    else:
        ordered_ids = sorted({bid for _, bid, _ in reviews})
        logger.info(f"No books_csv provided — derived {len(ordered_ids)} unique book IDs from reviews")

    bookid_to_row: Dict[str, int] = {str(bid): idx for idx, bid in enumerate(ordered_ids)}
    row_to_bookid: Dict[int, int] = {idx: bid for bid, idx in ((int(k), v) for k, v in bookid_to_row.items())}
    n_books = len(ordered_ids)

    logger.info(f"Building {n_books}×{n_books} co-occurrence matrix (min_rating={min_rating})")
    matrix = build_matrix(reviews, bookid_to_row, n_books)
    log_matrix_stats(matrix, row_to_bookid)

    cooc_path = models_dir / constants.ITEM_COOCCURRENCE_FILE
    np.save(cooc_path, matrix.astype(np.float32))
    logger.info(f"Saved co-occurrence matrix: {cooc_path}")

    mapping_path = models_dir / constants.BOOKID_TO_ROW_FILE
    with open(mapping_path, "w") as f:
        json.dump(bookid_to_row, f, indent=2)
    logger.info(f"Saved bookid_to_row mapping: {mapping_path}  ({len(bookid_to_row)} books)")

    logger.info("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build rating-weighted item-item co-occurrence matrix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_cooccurrence_matrix.py --reviews_json data/seeding/reviews.json --models_dir data/ml_models
  python build_cooccurrence_matrix.py --reviews_json data/seeding/reviews.json --models_dir data/ml_models --min_rating 3
        """,
    )
    parser.add_argument("--reviews_json", type=Path, required=True,
                        help="JSON file: list of {userId, bookId, rating}")
    parser.add_argument("--models_dir", type=Path, default=Path("../data/ml_models"),
                        help="Directory to write artefacts (default: ../data/ml_models)")
    parser.add_argument("--books_csv", type=Path, default=None,
                        help="CSV with book_id column — used to keep row ordering in sync with other artefacts")
    parser.add_argument("--min_rating", type=int, default=1, choices=range(1, 6),
                        help="Ignore reviews below this rating (1=keep all, 3=positive only; default: 1)")

    args = parser.parse_args()

    if not args.reviews_json.exists():
        logger.error(f"Reviews file not found: {args.reviews_json}")
        sys.exit(1)

    build(
        reviews_json=args.reviews_json,
        models_dir=args.models_dir,
        books_csv=args.books_csv,
        min_rating=args.min_rating,
    )


if __name__ == "__main__":
    main()
