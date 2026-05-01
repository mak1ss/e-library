#!/usr/bin/env python3
"""
Offline build script: generate sentence-transformer embeddings for all books.

Reads a CSV of book metadata, aggregates each book's text using the same
BookMetadataAggregator strategy as the Kafka review-scoring pipeline, then
encodes every book with all-MiniLM-L6-v2 and writes two artefacts:

  book_embeddings.npy   — float32 array, shape (n_books, 384)
  bookid_to_row.json    — {"<book_id>": <row_index>, ...}

Both files are written to --models_dir alongside the existing TF-IDF and
co-occurrence artefacts so MLModelLoader can load them at service startup.

Usage:
  python build_book_embeddings.py \\
    --books_csv data/books.csv \\
    --models_dir data/ml_models \\
    --model all-MiniLM-L6-v2 \\
    --batch_size 64

Expected CSV columns (extra columns are ignored):
  book_id, title, author, genres, category, description
"""

import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# ============================================================================
# Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("BuildBookEmbeddings")


# ============================================================================
# CSV loading
# ============================================================================

def load_books_csv(csv_path: Path) -> List[Tuple[int, Dict]]:
    """Load books from CSV. Returns list of (book_id, book_dict) tuples."""
    books: List[Tuple[int, Dict]] = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                book_id = int(row["book_id"])
            except (KeyError, ValueError) as exc:
                logger.warning(f"Skipping row with invalid book_id: {exc}")
                continue
            books.append((
                book_id,
                {
                    "title": row.get("title", ""),
                    "author": row.get("author", ""),
                    "genres": row.get("genres", ""),
                    "category": row.get("category", ""),
                    "description": row.get("description", ""),
                },
            ))
    return books


# ============================================================================
# Build
# ============================================================================

def _aggregate_book_metadata(book: Dict) -> str:
    """Aggregate book fields into a single string for embedding.

    Field priority: Title > Author > Genres > Category > Description.
    Matches the Strategy C aggregation used in offline_evaluation.py.
    """
    parts = []
    if book.get("title"):
        parts.append(f"Title: {book['title']}")
    if book.get("author"):
        parts.append(f"Author: {book['author']}")
    if book.get("genres"):
        genres = book["genres"]
        if isinstance(genres, list):
            genres = ", ".join(genres)
        if genres:
            parts.append(f"Genres: {genres}")
    if book.get("category"):
        parts.append(f"Category: {book['category']}")
    if book.get("description"):
        parts.append(f"Description: {book['description']}")
    return "\n".join(parts)


def build_embeddings(
    books_csv: Path,
    models_dir: Path,
    model_name: str,
    batch_size: int,
) -> None:
    models_dir.mkdir(parents=True, exist_ok=True)

    from sentence_transformers import SentenceTransformer

    logger.info(f"Loading books from: {books_csv}")
    books = load_books_csv(books_csv)
    if not books:
        logger.error("No books loaded - check CSV path and column names")
        sys.exit(1)
    logger.info(f"Loaded {len(books)} books")

    # Build ordered lists so the row index is deterministic
    book_ids: List[int] = [b[0] for b in books]
    texts: List[str] = [_aggregate_book_metadata(b[1]) for b in books]

    logger.info(f"Loading sentence transformer: {model_name}")
    model = SentenceTransformer(model_name)

    logger.info(f"Encoding {len(texts)} books in batches of {batch_size}...")
    start = time.time()
    embeddings: np.ndarray = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,   # unit vectors → dot product == cosine similarity
    )
    elapsed = time.time() - start
    logger.info(
        f"Encoded {len(texts)} books in {elapsed:.1f}s "
        f"({elapsed / len(texts) * 1000:.1f} ms/book) — shape: {embeddings.shape}"
    )

    # Save embeddings
    from utils import constants
    embeddings_path = models_dir / constants.BOOK_EMBEDDINGS_FILE
    np.save(embeddings_path, embeddings.astype(np.float32))
    logger.info(f"Saved embeddings: {embeddings_path}")

    # Save (or overwrite) bookid_to_row mapping
    bookid_to_row: Dict[str, int] = {str(bid): idx for idx, bid in enumerate(book_ids)}
    mapping_path = models_dir / constants.BOOKID_TO_ROW_FILE
    with open(mapping_path, "w") as f:
        json.dump(bookid_to_row, f, indent=2)
    logger.info(f"Saved bookid_to_row mapping: {mapping_path}  ({len(bookid_to_row)} books)")

    logger.info("Done.")


# ============================================================================
# Entry point
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-compute sentence-transformer embeddings for all books",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_book_embeddings.py --books_csv data/books.csv --models_dir data/ml_models
  python build_book_embeddings.py --books_csv data/books.csv --models_dir data/ml_models --batch_size 32
        """,
    )
    parser.add_argument(
        "--books_csv", type=Path, required=True,
        help="CSV with columns: book_id, title, author, genres, category, description",
    )
    parser.add_argument(
        "--models_dir", type=Path, default=Path("../data/ml_models"),
        help="Directory to write book_embeddings.npy and bookid_to_row.json",
    )
    parser.add_argument(
        "--model", default="all-MiniLM-L6-v2",
        help="Sentence transformer model name (default: all-MiniLM-L6-v2)",
    )
    parser.add_argument(
        "--batch_size", type=int, default=64,
        help="Encoding batch size (default: 64)",
    )

    args = parser.parse_args()

    if not args.books_csv.exists():
        logger.error(f"CSV not found: {args.books_csv}")
        sys.exit(1)

    build_embeddings(
        books_csv=args.books_csv,
        models_dir=args.models_dir,
        model_name=args.model,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
