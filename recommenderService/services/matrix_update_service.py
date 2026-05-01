"""
MatrixUpdateService: applies incremental in-memory updates to the co-occurrence matrix
and book embeddings when triggered by Kafka events.

All public methods acquire ml_loader.lock for the full duration of the mutation.
CPU-bound sentence-transformer encoding is done BEFORE acquiring the lock.
"""

import numpy as np
from utils.logger import logger
from services.ml_model_loader import MLModelLoader


class MatrixUpdateService:

    def __init__(self, ml_loader: MLModelLoader, sentence_transformer_model_name: str):
        self.ml_loader = ml_loader
        self._model_name = sentence_transformer_model_name
        self._sentence_model = None  # lazy-loaded on first book event

    def _get_sentence_model(self):
        if self._sentence_model is None:
            from sentence_transformers import SentenceTransformer
            self._sentence_model = SentenceTransformer(self._model_name)
        return self._sentence_model

    # -------------------------------------------------------------------------
    # Co-occurrence matrix updates (review events)
    # -------------------------------------------------------------------------

    def apply_review_create(self, book_id: int, rating: int, other_reviews: list) -> None:
        """
        other_reviews: list of dicts with keys 'bookId' and 'rating'
        """
        with self.ml_loader.lock:
            row_b = self.ml_loader.bookid_to_row_mapping.get(str(book_id))
            if row_b is None:
                logger.warning(f"[MatrixUpdate] CREATE: bookId={book_id} not in mapping, skipping")
                return
            for entry in other_reviews:
                row_a = self.ml_loader.bookid_to_row_mapping.get(str(entry['bookId']))
                if row_a is None:
                    continue
                weight = min(rating, entry['rating']) / 5.0
                self.ml_loader.item_cooccurrence_matrix[row_b, row_a] += weight
                self.ml_loader.item_cooccurrence_matrix[row_a, row_b] += weight
        logger.debug(f"[MatrixUpdate] CREATE applied: bookId={book_id} rating={rating} "
                     f"pairs={len(other_reviews)}")

    def apply_review_delete(self, book_id: int, rating: int, other_reviews: list) -> None:
        with self.ml_loader.lock:
            row_b = self.ml_loader.bookid_to_row_mapping.get(str(book_id))
            if row_b is None:
                logger.warning(f"[MatrixUpdate] DELETE: bookId={book_id} not in mapping, skipping")
                return
            for entry in other_reviews:
                row_a = self.ml_loader.bookid_to_row_mapping.get(str(entry['bookId']))
                if row_a is None:
                    continue
                delta = -min(rating, entry['rating']) / 5.0
                self.ml_loader.item_cooccurrence_matrix[row_b, row_a] += delta
                self.ml_loader.item_cooccurrence_matrix[row_a, row_b] += delta
                # Clamp to zero — floating-point drift must not produce negative weights
                self.ml_loader.item_cooccurrence_matrix[row_b, row_a] = max(
                    0.0, self.ml_loader.item_cooccurrence_matrix[row_b, row_a])
                self.ml_loader.item_cooccurrence_matrix[row_a, row_b] = max(
                    0.0, self.ml_loader.item_cooccurrence_matrix[row_a, row_b])
        logger.debug(f"[MatrixUpdate] DELETE applied: bookId={book_id}")

    def apply_review_update(self, book_id: int, new_rating: int, old_rating: int,
                            other_reviews: list) -> None:
        with self.ml_loader.lock:
            row_b = self.ml_loader.bookid_to_row_mapping.get(str(book_id))
            if row_b is None:
                logger.warning(f"[MatrixUpdate] UPDATE: bookId={book_id} not in mapping, skipping")
                return
            for entry in other_reviews:
                row_a = self.ml_loader.bookid_to_row_mapping.get(str(entry['bookId']))
                if row_a is None:
                    continue
                r_a = entry['rating']
                delta = (min(new_rating, r_a) - min(old_rating, r_a)) / 5.0
                self.ml_loader.item_cooccurrence_matrix[row_b, row_a] += delta
                self.ml_loader.item_cooccurrence_matrix[row_a, row_b] += delta
                self.ml_loader.item_cooccurrence_matrix[row_b, row_a] = max(
                    0.0, self.ml_loader.item_cooccurrence_matrix[row_b, row_a])
                self.ml_loader.item_cooccurrence_matrix[row_a, row_b] = max(
                    0.0, self.ml_loader.item_cooccurrence_matrix[row_a, row_b])
        logger.debug(f"[MatrixUpdate] UPDATE applied: bookId={book_id} "
                     f"old_rating={old_rating} new_rating={new_rating}")

    # -------------------------------------------------------------------------
    # Book embedding updates (book metadata events)
    # -------------------------------------------------------------------------

    @staticmethod
    def _aggregate_metadata(title, author_name, genres, category, description) -> str:
        """Mirrors the aggregation strategy in build_book_embeddings.py."""
        parts = []
        if title:
            parts.append(f"Title: {title}")
        if author_name:
            parts.append(f"Author: {author_name}")
        if genres:
            parts.append(f"Genres: {', '.join(genres)}")
        if category:
            parts.append(f"Category: {category}")
        if description:
            parts.append(f"Description: {description}")
        return "\n".join(parts)

    def apply_book_created(self, book_id: int, title: str, author_name: str,
                           genres: list, category: str, description: str) -> None:
        text = self._aggregate_metadata(title, author_name, genres, category, description)
        # Encoding is CPU-bound — done outside the lock
        new_embedding = self._get_sentence_model().encode(
            [text], normalize_embeddings=True)[0].astype(np.float32)

        with self.ml_loader.lock:
            if str(book_id) in self.ml_loader.bookid_to_row_mapping:
                # Already in model — treat as update (e.g. event replay)
                logger.warning(f"[MatrixUpdate] CREATED but bookId={book_id} already in mapping, "
                               "updating embedding instead")
                row_idx = self.ml_loader.bookid_to_row_mapping[str(book_id)]
                self.ml_loader.book_embeddings[row_idx] = new_embedding
                return

            new_row = len(self.ml_loader.bookid_to_row_mapping)
            self.ml_loader.bookid_to_row_mapping[str(book_id)] = new_row

            # Extend book_embeddings by one row
            self.ml_loader.book_embeddings = np.vstack(
                [self.ml_loader.book_embeddings, new_embedding.reshape(1, -1)]
            )

            # Extend co-occurrence matrix with a zeros row and column
            old_n = self.ml_loader.item_cooccurrence_matrix.shape[0]
            new_col = np.zeros((old_n, 1), dtype=np.float32)
            expanded = np.hstack([self.ml_loader.item_cooccurrence_matrix, new_col])
            new_row_vec = np.zeros((1, old_n + 1), dtype=np.float32)
            self.ml_loader.item_cooccurrence_matrix = np.vstack([expanded, new_row_vec])

        logger.info(f"[MatrixUpdate] New book bookId={book_id} added. "
                    f"Matrix now {self.ml_loader.item_cooccurrence_matrix.shape}")

    def apply_book_updated(self, book_id: int, title: str, author_name: str,
                           genres: list, category: str, description: str) -> None:
        text = self._aggregate_metadata(title, author_name, genres, category, description)
        # Encoding outside the lock
        new_embedding = self._get_sentence_model().encode(
            [text], normalize_embeddings=True)[0].astype(np.float32)

        with self.ml_loader.lock:
            row_idx = self.ml_loader.bookid_to_row_mapping.get(str(book_id))
            if row_idx is None:
                logger.warning(f"[MatrixUpdate] UPDATED: bookId={book_id} not in mapping, skipping")
                return
            self.ml_loader.book_embeddings[row_idx] = new_embedding

        logger.info(f"[MatrixUpdate] Embedding updated for bookId={book_id}")
