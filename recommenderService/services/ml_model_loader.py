import os
import json
import threading
from datetime import datetime
from typing import Dict, Optional, List
import joblib
import numpy as np
from utils.logger import logger
from utils import constants


class MLModelLoader:
    """Load and manage ML models in memory"""
    
    def __init__(self, models_dir: str):
        self.models_dir = models_dir
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.item_cooccurrence_matrix = None
        self.bookid_to_row_mapping = None
        self.popular_books_list = None
        self.book_embeddings: Optional[np.ndarray] = None  # shape (n_books, 384)
        self.lock = threading.Lock()

        self.model_metadata = {
            'loaded_at': None,
            'version': None,
            'vectorizer_shape': None,
            'cooccurrence_shape': None,
            'embeddings_shape': None,
        }
    
    def load_all_models(self) -> None:
        """Load all artifacts into memory on service startup"""
        try:
            logger.info(f"Loading ML models from directory: {self.models_dir}")
            
            # Load TF-IDF vectorizer
            vectorizer_path = os.path.join(self.models_dir, constants.TFIDF_VECTORIZER_FILE)
            with open(vectorizer_path, "rb") as f:
                self.tfidf_vectorizer = joblib.load(f)
            logger.info(f"Loaded TF-IDF vectorizer with {len(self.tfidf_vectorizer.vocabulary_)} features")
            
            # Load TF-IDF matrix (dense or sparse)
            tfidf_path = os.path.join(self.models_dir, constants.TFIDF_MATRIX_FILE)
            with open(tfidf_path, "rb") as f:
                self.tfidf_matrix = joblib.load(f)
            logger.info(f"Loaded TF-IDF matrix with shape: {self.tfidf_matrix.shape}")
            self.model_metadata['vectorizer_shape'] = self.tfidf_matrix.shape
            
            # Load item-item co-occurrence matrix (sparse format recommended)
            cooccurrence_path = os.path.join(self.models_dir, constants.ITEM_COOCCURRENCE_FILE)
            self.item_cooccurrence_matrix = np.load(cooccurrence_path, allow_pickle=True)
            logger.info(f"Loaded item co-occurrence matrix with shape: {self.item_cooccurrence_matrix.shape}")
            self.model_metadata['cooccurrence_shape'] = self.item_cooccurrence_matrix.shape
            
            # Load bookId ↔ row index mapping
            bookid_path = os.path.join(self.models_dir, constants.BOOKID_TO_ROW_FILE)
            with open(bookid_path, "r") as f:
                self.bookid_to_row_mapping = json.load(f)
            logger.info(f"Loaded book ID mapping with {len(self.bookid_to_row_mapping)} books")
            
            # Load popular books reference data
            popular_path = os.path.join(self.models_dir, constants.POPULAR_BOOKS_FILE)
            with open(popular_path, "r") as f:
                self.popular_books_list = json.load(f)
            logger.info(f"Loaded {len(self.popular_books_list)} popular books")
            
            # Load pre-computed sentence-transformer book embeddings
            embeddings_path = os.path.join(self.models_dir, constants.BOOK_EMBEDDINGS_FILE)
            self.book_embeddings = np.load(embeddings_path)
            logger.info(f"Loaded book embeddings with shape: {self.book_embeddings.shape}")
            self.model_metadata['embeddings_shape'] = self.book_embeddings.shape

            self.model_metadata['loaded_at'] = datetime.now().isoformat()
            logger.info("All ML models loaded successfully into memory")
            
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def is_ready(self) -> bool:
        """Check if all models are loaded"""
        return all([
            self.tfidf_vectorizer is not None,
            self.tfidf_matrix is not None,
            self.item_cooccurrence_matrix is not None,
            self.bookid_to_row_mapping is not None,
            self.book_embeddings is not None,
        ])

    def flush_to_disk(self) -> None:
        """Persist current in-memory matrices back to the .npy / .json files on disk."""
        with self.lock:
            cooc_path = os.path.join(self.models_dir, constants.ITEM_COOCCURRENCE_FILE)
            np.save(cooc_path, self.item_cooccurrence_matrix.astype(np.float32))

            emb_path = os.path.join(self.models_dir, constants.BOOK_EMBEDDINGS_FILE)
            np.save(emb_path, self.book_embeddings.astype(np.float32))

            mapping_path = os.path.join(self.models_dir, constants.BOOKID_TO_ROW_FILE)
            with open(mapping_path, 'w') as f:
                json.dump(self.bookid_to_row_mapping, f)

        logger.info("MLModelLoader: flushed in-memory matrices to disk")
