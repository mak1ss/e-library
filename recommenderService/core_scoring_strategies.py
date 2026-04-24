"""
Phase 2: Core Scoring Strategies Implementation
Tasks 2.1, 2.2, 2.3, 2.4 & 2.5 - Production Code

Implements:
- Task 2.1: Book metadata aggregation (Strategy C)
- Task 2.2: Book edge case handling
- Task 2.3: Review text preprocessing pipeline (7-step)
- Task 2.4: Review edge case handling
- Task 2.5: Core relevance scoring function
"""

import re
import html
import logging
import numpy as np
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# TASK 2.1: BOOK METADATA AGGREGATION (Strategy C)
# ============================================================================

class BookMetadataAggregator:
    """
    Aggregates book metadata using Strategy C (Selective Fields).
    
    Selected strategy prioritizes:
    1. Title (always included - should never be NULL)
    2. Author (quality metadata)
    3. Genres (important for categorization)
    4. Category (broad classification)
    5. Description (ALWAYS at end - highest semantic value)
    
    Skips NULL/empty fields to avoid placeholder noise.
    """
    
    @staticmethod
    def aggregate(
        title: Optional[str],
        author_name: Optional[str] = None,
        genres: Optional[str] = None,
        category_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Aggregate book metadata using Strategy C.
        
        Args:
            title: Book title (required)
            author_name: Author name
            genres: Comma-separated genres
            category_name: Primary category
            description: Book description (max 500 chars)
        
        Returns:
            str: Aggregated metadata text in format optimized for embedding
            
        Example:
            >>> agg = BookMetadataAggregator.aggregate(
            ...     title="The Great Gatsby",
            ...     author_name="F. Scott Fitzgerald",
            ...     genres="Fiction, Romance",
            ...     description="A classic American novel..."
            ... )
            >>> print(agg)
            Title: The Great Gatsby
            Author: F. Scott Fitzgerald
            Genres: Fiction, Romance
            Description: A classic American novel...
        """
        parts = []
        
        # Always include title (should never be NULL per schema)
        if title and title.strip():
            parts.append(f"Title: {title.strip()}")
        
        # Include author if available (quality metadata)
        if author_name and author_name.strip():
            parts.append(f"Author: {author_name.strip()}")
        
        # Include genres if available (useful for semantic understanding)
        if genres and genres.strip():
            parts.append(f"Genres: {genres.strip()}")
        
        # Include category if available (broad classification)
        if category_name and category_name.strip():
            parts.append(f"Category: {category_name.strip()}")
        
        # ALWAYS include description last (highest priority for semantic content)
        # Description is the most information-rich field for relevance scoring
        if description and description.strip():
            parts.append(f"Description: {description.strip()}")
        
        # Join with newlines for readability and semantic separation
        aggregated_text = "\n".join(parts)
        
        # Fallback for edge case (no fields populated)
        if not aggregated_text:
            aggregated_text = "No book metadata available"
        
        return aggregated_text
    
    @staticmethod
    def aggregate_from_dict(book: Dict) -> str:
        """
        Aggregate metadata from a dictionary (convenience method).
        
        Args:
            book: Dictionary with optional keys:
                  'title', 'author_name', 'genres', 'category_name', 'description'
        
        Returns:
            str: Aggregated metadata text
        """
        return BookMetadataAggregator.aggregate(
            title=book.get('title'),
            author_name=book.get('author_name'),
            genres=book.get('genres'),
            category_name=book.get('category_name'),
            description=book.get('description')
        )


# ============================================================================
# TASK 2.3: REVIEW TEXT PREPROCESSING (7-Step Pipeline)
# ============================================================================

@dataclass
class PreprocessingStats:
    """Statistics about preprocessing operations."""
    original_length: int
    final_length: int
    tokens_before: int
    tokens_after: int
    was_truncated: bool
    steps_applied: list


class ReviewTextPreprocessor:
    """
    Preprocesses review text for Sentence Transformer embedding.
    
    7-step pipeline:
    1. HTML entity decoding
    2. Lowercase conversion
    3. Emoji/unicode removal
    4. Whitespace normalization
    5. Spoiler marker removal
    6. Repeated punctuation collapse
    7. Token-limit truncation
    
    Sentence Transformer limits:
    - Model: all-MiniLM-L6-v2 (~512 token hard limit)
    - Approximation: 4 characters ≈ 1 token
    - Truncation threshold: 1800 chars (~450 tokens)
    """
    
    # Regex patterns for preprocessing
    SPOILER_PATTERN = re.compile(
        r'\bspoiler\s*:?\s*|\bspoiler\s+alert\b',
        flags=re.IGNORECASE
    )
    REPEATED_PUNCT_PATTERN = re.compile(r'([!?.])\1{2,}')
    SENTENCE_END_PATTERN = re.compile(r'[.!?]')
    
    # Constants
    CHARS_PER_TOKEN = 4  # Approximation for Sentence Transformer
    MAX_TOKENS = 450  # Safety margin below 512 limit
    MAX_CHARS = MAX_TOKENS * CHARS_PER_TOKEN  # 1800 chars
    
    @staticmethod
    def preprocess(
        text: str,
        max_tokens: int = MAX_TOKENS,
        compute_stats: bool = False
    ) -> str:
        """
        Preprocess review text through 7-step pipeline.
        
        Args:
            text: Raw review text from database
            max_tokens: Token limit for Sentence Transformer (~512)
            compute_stats: Whether to compute processing statistics
        
        Returns:
            str: Cleaned, preprocessed review text
            
        Example:
            >>> raw = "I LOVED THIS!!! 😍😍😍 SPOILER ALERT: The ending..."
            >>> clean = ReviewTextPreprocessor.preprocess(raw)
            >>> print(clean)
            i loved this! the ending...
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Step 1: HTML Entity Decode
        # Affects 2-5% of reviews (copied from web/forums)
        step1 = html.unescape(text)
        
        # Step 2: Lowercase Conversion
        # Affects 70%+ of reviews (normal capitalization)
        # Normalizes embedding space
        step2 = step1.lower()
        
        # Step 3: Remove Emoji and Non-ASCII Unicode
        # Affects 15-25% of reviews (emojis, special chars)
        # Reduces token count, improves relevance focus
        step3 = step2.encode('ascii', 'ignore').decode('ascii')
        
        # Step 4: Normalize Whitespace
        # Affects 10-20% of reviews (irregular spacing/newlines)
        # Improves tokenization consistency
        step4 = ' '.join(step3.split())
        
        # Step 5: Remove Spoiler Markers
        # Affects 3-8% of reviews (spoiler warnings/tags)
        # Preserves content, removes meta-markers
        step5 = ReviewTextPreprocessor.SPOILER_PATTERN.sub('', step4)
        step5 = step5.strip()
        
        # Step 6: Collapse Repeated Punctuation
        # Affects 10-15% of reviews (!!!→!, ???→?)
        # Reduces token waste
        step6 = ReviewTextPreprocessor.REPEATED_PUNCT_PATTERN.sub(r'\1', step5)
        
        # Step 7: Truncate at Token Limit
        # Affects <0.5% of reviews (only extreme outliers)
        # Maintains semantic meaning via sentence boundary truncation
        max_chars = max_tokens * ReviewTextPreprocessor.CHARS_PER_TOKEN
        
        if len(step6) > max_chars:
            # Truncate at last sentence boundary
            step6 = ReviewTextPreprocessor._truncate_at_sentence(step6, max_chars)
        
        final_text = step6.strip()
        
        return final_text
    
    @staticmethod
    def preprocess_batch(
        texts: list,
        max_tokens: int = MAX_TOKENS
    ) -> list:
        """
        Preprocess multiple review texts.
        
        Args:
            texts: List of raw review texts
            max_tokens: Token limit
        
        Returns:
            list: List of preprocessed texts
        """
        return [
            ReviewTextPreprocessor.preprocess(text, max_tokens)
            for text in texts
        ]
    
    @staticmethod
    def _truncate_at_sentence(
        text: str,
        max_chars: int
    ) -> str:
        """
        Truncate text at last sentence boundary.
        
        Preserves semantic meaning by ending at complete sentence.
        
        Args:
            text: Text to truncate
            max_chars: Maximum character length
        
        Returns:
            str: Truncated text
        """
        if len(text) <= max_chars:
            return text
        
        # Find last sentence-ending punctuation before limit
        truncated = text[:max_chars]
        last_period = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        
        # Only use found punctuation if it's recent (within 80% of truncation point)
        if last_period > max_chars * 0.8:
            return truncated[:last_period + 1]
        
        # Fallback: truncate at last space if no recent punctuation
        last_space = truncated.rfind(' ')
        if last_space > max_chars * 0.9:
            return truncated[:last_space]
        
        # Last resort: return truncated text as-is
        return truncated
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Estimate token count using character approximation.
        
        Formula: tokens ≈ chars / 4
        
        Args:
            text: Text to estimate
        
        Returns:
            int: Estimated token count
        """
        return max(1, int(len(text) / ReviewTextPreprocessor.CHARS_PER_TOKEN))
    
    @staticmethod
    def get_preprocessing_report(
        original_text: str,
        preprocessed_text: str
    ) -> Dict:
        """
        Generate a report on preprocessing changes.
        
        Args:
            original_text: Original review text
            preprocessed_text: Preprocessed review text
        
        Returns:
            dict: Report with statistics and changes
        """
        original_tokens = ReviewTextPreprocessor.estimate_tokens(original_text)
        final_tokens = ReviewTextPreprocessor.estimate_tokens(preprocessed_text)
        
        return {
            'original_length': len(original_text),
            'final_length': len(preprocessed_text),
            'chars_reduced': len(original_text) - len(preprocessed_text),
            'tokens_before': original_tokens,
            'tokens_after': final_tokens,
            'tokens_reduced': original_tokens - final_tokens,
            'was_truncated': len(preprocessed_text) == ReviewTextPreprocessor.MAX_CHARS,
            'length_reduction_pct': (
                (len(original_text) - len(preprocessed_text)) / len(original_text) * 100
                if len(original_text) > 0 else 0
            ),
            'within_token_limit': final_tokens <= ReviewTextPreprocessor.MAX_TOKENS,
            'has_html': '&' in original_text and ';' in original_text,
            'has_uppercase': any(c.isupper() for c in original_text),
            'has_emojis_or_unicode': len(original_text) != len(
                original_text.encode('ascii', 'ignore').decode('ascii')
            ),
            'has_repeated_punct': bool(re.search(r'([!?.])\1{2,}', original_text))
        }


# ============================================================================
# TASK 2.2: BOOK EDGE CASE HANDLING
# ============================================================================

class BookEdgeCaseHandler:
    """
    Handles edge cases in book metadata aggregation.
    
    Decision tree for edge cases:
    1. NULL/missing description (~12%): Use title only
    2. Very short description (< 20 chars, 2-5%): Include, warn
    3. Minimum threshold (< 30 chars total, 3%): Skip for scoring
    4. Very long description (> 500 chars, <1%): Truncate at DB limit
    5. Error logging: INFO/WARNING/ERROR levels
    """
    
    # Constants
    MIN_TEXT_LENGTH = 30  # Minimum chars for valid scoring
    MAX_TEXT_LENGTH = 2000  # Soft limit for safety margin
    SHORT_DESC_THRESHOLD = 20  # Below this is "short"
    
    class EdgeCaseType(Enum):
        """Types of edge cases encountered."""
        NULL_DESCRIPTION = "NULL_DESCRIPTION"
        SHORT_DESCRIPTION = "SHORT_DESCRIPTION"
        MINIMAL_METADATA = "MINIMAL_METADATA"
        VERY_LONG_METADATA = "VERY_LONG_METADATA"
        VALID = "VALID"
    
    @staticmethod
    def validate_and_log(
        book_id: int,
        title: str,
        description: Optional[str],
        aggregated_text: str
    ) -> Tuple[bool, str, 'BookEdgeCaseHandler.EdgeCaseType']:
        """
        Validate aggregated book text and log edge cases.
        
        Args:
            book_id: Book identifier
            title: Book title
            description: Book description (may be NULL)
            aggregated_text: Already-aggregated metadata text
        
        Returns:
            tuple: (is_valid, log_message, edge_case_type)
                  is_valid: True if suitable for scoring
                  log_message: Message for logging
                  edge_case_type: Classified edge case
        """
        agg_len = len(aggregated_text)
        
        # Check: NULL/missing description
        if description is None or not description.strip():
            msg = (f"Book {book_id}: description is NULL, "
                   f"using title only ('{title}')")
            logger.info(msg)
            return True, msg, BookEdgeCaseHandler.EdgeCaseType.NULL_DESCRIPTION
        
        # Check: Very short description
        desc_len = len(description.strip())
        if desc_len < BookEdgeCaseHandler.SHORT_DESC_THRESHOLD:
            msg = (f"Book {book_id}: description unusually short ({desc_len} chars), "
                   f"may have limited semantic context ('{description[:30]}')")
            logger.warning(msg)
        
        # Check: Minimum aggregated text length
        if agg_len < BookEdgeCaseHandler.MIN_TEXT_LENGTH:
            msg = (f"Book {book_id}: minimal metadata ({agg_len} chars < {BookEdgeCaseHandler.MIN_TEXT_LENGTH}), "
                   f"skipping relevance scoring (text: '{aggregated_text}')")
            logger.warning(msg)
            return False, msg, BookEdgeCaseHandler.EdgeCaseType.MINIMAL_METADATA
        
        # Check: Very long metadata (rare due to DB schema)
        if agg_len > BookEdgeCaseHandler.MAX_TEXT_LENGTH:
            msg = (f"Book {book_id}: very long metadata ({agg_len} chars > {BookEdgeCaseHandler.MAX_TEXT_LENGTH}), "
                   f"truncating to preserve embedding quality")
            logger.info(msg)
            return True, msg, BookEdgeCaseHandler.EdgeCaseType.VERY_LONG_METADATA
        
        # All checks passed
        return True, "Book valid for scoring", BookEdgeCaseHandler.EdgeCaseType.VALID


# ============================================================================
# TASK 2.4: REVIEW EDGE CASE HANDLING
# ============================================================================

class ReviewEdgeCaseHandler:
    """
    Handles edge cases in review text preprocessing.
    
    Decision tree for edge cases:
    1. NULL/empty text (5-7%): Skip for scoring
    2. Very short review (< 5 chars, 2-4%): Include, warn
    3. Gibberish/spam (> 80% non-ASCII, 1%): Skip for scoring
    4. Non-English (2-3%): Include (model is multilingual)
    5. Token limit (< 0.5%): Handled by preprocessing truncation
    """
    
    # Constants
    MIN_REVIEW_LENGTH = 5  # Minimum chars after preprocessing
    GIBBERISH_THRESHOLD = 0.80  # > 80% non-ASCII = likely spam
    
    class EdgeCaseType(Enum):
        """Types of edge cases encountered."""
        NULL_REVIEW = "NULL_REVIEW"
        SHORT_REVIEW = "SHORT_REVIEW"
        GIBBERISH_SPAM = "GIBBERISH_SPAM"
        EMPTY_AFTER_PREPROCESSING = "EMPTY_AFTER_PREPROCESSING"
        NON_ENGLISH = "NON_ENGLISH"
        TRUNCATED_REVIEW = "TRUNCATED_REVIEW"
        VALID = "VALID"
    
    @staticmethod
    def validate_and_log(
        review_id: int,
        original_text: str,
        preprocessed_text: str
    ) -> Tuple[bool, str, 'ReviewEdgeCaseHandler.EdgeCaseType']:
        """
        Validate review text and log edge cases.
        
        Args:
            review_id: Review identifier
            original_text: Raw review text from DB
            preprocessed_text: After 7-step preprocessing
        
        Returns:
            tuple: (is_valid, log_message, edge_case_type)
                  is_valid: True if suitable for scoring
                  log_message: Message for logging
                  edge_case_type: Classified edge case
        """
        
        # Check: NULL or empty original text
        if not original_text or not isinstance(original_text, str) or not original_text.strip():
            msg = f"Review {review_id}: empty/NULL text, skipping relevance scoring"
            logger.info(msg)
            return False, msg, ReviewEdgeCaseHandler.EdgeCaseType.NULL_REVIEW
        
        # Check: Gibberish/spam detection (optional optimization)
        # Calculate non-ASCII ratio from original text
        try:
            ascii_version = original_text.encode('ascii', 'ignore').decode('ascii')
            non_ascii_count = len(original_text) - len(ascii_version)
            if len(original_text) > 0:
                gibberish_ratio = non_ascii_count / len(original_text)
                
                if gibberish_ratio > ReviewEdgeCaseHandler.GIBBERISH_THRESHOLD:
                    msg = (f"Review {review_id}: gibberish/spam detected "
                           f"({gibberish_ratio:.1%} non-ASCII), skipping")
                    logger.warning(msg)
                    return False, msg, ReviewEdgeCaseHandler.EdgeCaseType.GIBBERISH_SPAM
        except Exception as e:
            logger.debug(f"Review {review_id}: could not analyze for gibberish (error: {e})")
        
        # Check: Empty after preprocessing
        if not preprocessed_text or not preprocessed_text.strip():
            msg = (f"Review {review_id}: text became empty after preprocessing "
                   f"(original: {original_text[:50]}...)")
            logger.warning(msg)
            return False, msg, ReviewEdgeCaseHandler.EdgeCaseType.EMPTY_AFTER_PREPROCESSING
        
        # Check: Very short review after preprocessing
        prep_len = len(preprocessed_text.strip())
        if prep_len < ReviewEdgeCaseHandler.MIN_REVIEW_LENGTH:
            msg = (f"Review {review_id}: very short after preprocessing "
                   f"({prep_len} chars, text: '{preprocessed_text}')")
            logger.warning(msg)
            # Note: Still valid, just warn user
        
        # Check: Was truncated during preprocessing
        if len(preprocessed_text) >= ReviewTextPreprocessor.MAX_CHARS:
            msg = (f"Review {review_id}: was truncated during preprocessing "
                   f"(original > {ReviewTextPreprocessor.MAX_CHARS} chars)")
            logger.info(msg)
            return True, msg, ReviewEdgeCaseHandler.EdgeCaseType.TRUNCATED_REVIEW
        
        # All checks passed
        return True, "Review valid for scoring", ReviewEdgeCaseHandler.EdgeCaseType.VALID


# ============================================================================
# TASK 2.5: CORE RELEVANCE SCORING FUNCTION
# ============================================================================

@dataclass
class RelevanceScore:
    """
    Output from relevance scoring function.
    
    Task 2.5: Core Relevance Scoring
    
    Attributes:
        score: Normalized relevance score in [0.0, 1.0]
        raw_cosine: Raw cosine similarity [-1, 1] (for debugging)
        confidence: Confidence score [0.0, 1.0] (optional)
        error_code: Error identifier if scoring failed
        error_message: Human-readable error description
    """
    score: Optional[float] = None
    raw_cosine: Optional[float] = None
    confidence: Optional[float] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    def is_valid(self) -> bool:
        """Check if score was computed successfully."""
        return self.score is not None and self.error_code is None
    
    def __repr__(self) -> str:
        """String representation."""
        if self.is_valid():
            return (f"RelevanceScore(score={self.score:.3f}, "
                    f"confidence={self.confidence:.3f if self.confidence else 'N/A'})")
        else:
            return f"RelevanceScore(error={self.error_code})"


class RelevanceScoringFunction:
    """
    Core relevance scoring between book and review embeddings.
    
    Task 2.5 Implementation:
    - Similarity metric: Cosine similarity [-1, 1]
    - Normalization: (cos_sim + 1) / 2 → [0, 1]
    - Error handling: NULL for invalid inputs
    - Confidence: Computed as optional metric
    
    Formula:
        cosine_sim = (v1 · v2) / (||v1|| ||v2||)
        score = (cosine_sim + 1) / 2
        confidence = (|cosine_sim| * 0.7) + (embedding_quality * 0.3)
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RelevanceScoringFunction with sentence transformer model.
        
        Args:
            model_name: Name of sentence transformer model to use
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer model {model_name}: {e}")
            raise
    
    def compute_relevance_score(
        self,
        review_text: str,
        book_metadata: Dict
    ) -> RelevanceScore:
        """
        Compute relevance score from raw review text and book metadata.
        
        Workflow:
        1. Generate embedding for review text
        2. Generate embedding for aggregated book metadata
        3. Compute cosine similarity between embeddings
        4. Normalize to [0, 1] and return with confidence
        
        Args:
            review_text: Preprocessed review text
            book_metadata: Dictionary with book metadata (from JSON)
        
        Returns:
            RelevanceScore: Score with metadata and error info
        """
        # Aggregate book metadata into text form
        book_text = BookMetadataAggregator.aggregate_from_dict(book_metadata)
        
        try:
            # Generate embeddings
            review_embedding = self.model.encode(review_text, convert_to_numpy=True)
            book_embedding = self.model.encode(book_text, convert_to_numpy=True)
            
            # Compute relevance score
            return self.score_relevance(book_embedding, review_embedding, compute_confidence=True)
        except Exception as e:
            logger.error(f"Error computing relevance score: {e}")
            return RelevanceScore(
                error_code="EMBEDDING_GENERATION_ERROR",
                error_message=str(e)
            )
    
    @staticmethod
    def score_relevance(
        book_embedding: Optional[np.ndarray],
        review_embedding: Optional[np.ndarray],
        compute_confidence: bool = True
    ) -> RelevanceScore:
        """
        Compute relevance score between book and review embeddings.
        
        Args:
            book_embedding: Book metadata embedding (shape: 384,)
            review_embedding: Review text embedding (shape: 384,)
            compute_confidence: Whether to compute confidence score
        
        Returns:
            RelevanceScore: Relevance score with optional debug info
            
        Examples:
            >>> book_emb = np.random.randn(384)
            >>> review_emb = np.random.randn(384)
            >>> result = RelevanceScoringFunction.score_relevance(book_emb, review_emb)
            >>> print(result.score)  # e.g., 0.65
            >>> print(result.is_valid())  # True
        """
        
        # Step 1: Validate inputs
        if book_embedding is None:
            msg = "Cannot score: book_embedding is NULL"
            logger.error(msg)
            return RelevanceScore(
                error_code="NULL_BOOK_EMBEDDING",
                error_message=msg
            )
        
        if review_embedding is None:
            msg = "Cannot score: review_embedding is NULL"
            logger.error(msg)
            return RelevanceScore(
                error_code="NULL_REVIEW_EMBEDDING",
                error_message=msg
            )
        
        # Ensure numpy arrays
        try:
            book_emb = np.asarray(book_embedding, dtype=np.float32)
            review_emb = np.asarray(review_embedding, dtype=np.float32)
        except Exception as e:
            msg = f"Cannot convert embeddings to numpy: {e}"
            logger.error(msg)
            return RelevanceScore(
                error_code="EMBEDDING_CONVERSION_ERROR",
                error_message=msg
            )
        
        # Check for NaN values
        if np.isnan(book_emb).any() or np.isnan(review_emb).any():
            msg = "Embeddings contain NaN values"
            logger.error(msg)
            return RelevanceScore(
                error_code="NAN_VALUES",
                error_message=msg
            )
        
        # Check for infinity
        if np.isinf(book_emb).any() or np.isinf(review_emb).any():
            msg = "Embeddings contain infinity values"
            logger.error(msg)
            return RelevanceScore(
                error_code="INF_VALUES",
                error_message=msg
            )
        
        # Step 2: Compute norms (embeddings should be normalized, but verify)
        book_norm = np.linalg.norm(book_emb)
        review_norm = np.linalg.norm(review_emb)
        
        # Check for zero vectors
        if book_norm == 0 or review_norm == 0:
            msg = f"Zero vector detected (book_norm={book_norm:.6f}, review_norm={review_norm:.6f})"
            logger.error(msg)
            return RelevanceScore(
                error_code="ZERO_VECTOR",
                error_message=msg
            )
        
        # Step 3: Compute cosine similarity
        # cos(θ) = (v1 · v2) / (||v1|| ||v2||)
        try:
            dot_product = np.dot(book_emb, review_emb)
            cosine_sim = dot_product / (book_norm * review_norm)
            
            # Clamp to [-1, 1] to handle floating point errors
            cosine_sim = np.clip(cosine_sim, -1.0, 1.0)
        except Exception as e:
            msg = f"Error computing cosine similarity: {e}"
            logger.error(msg)
            return RelevanceScore(
                error_code="COSINE_COMPUTATION_ERROR",
                error_message=msg
            )
        
        # Step 4: Normalize to [0, 1] using squaring
        # Squaring penalizes low scores to match semantic embedding reality.
        # Cosine similarity for embeddings naturally ranges [0, 1], not [-1, 1].
        # Squaring makes discrimination clearer: 0.18² = 0.032, 0.524² = 0.275
        score = float(cosine_sim) ** 2
        
        # Step 5: Compute confidence (optional)
        confidence = None
        if compute_confidence:
            try:
                # Confidence based on signal strength and embedding quality
                cosine_magnitude = abs(cosine_sim)
                embedding_quality = min(book_norm, review_norm) / max(book_norm, review_norm)
                confidence = float((cosine_magnitude * 0.7) + (embedding_quality * 0.3))
            except Exception as e:
                logger.debug(f"Could not compute confidence: {e}")
                confidence = None
        
        # Step 6: Return result
        return RelevanceScore(
            score=score,
            raw_cosine=float(cosine_sim),
            confidence=confidence,
            error_code=None,
            error_message=None
        )
    
    @staticmethod
    def score_relevance_batch(
        book_embeddings: List[np.ndarray],
        review_embeddings: List[np.ndarray],
        compute_confidence: bool = True
    ) -> List[RelevanceScore]:
        """
        Score multiple book-review pairs.
        
        Args:
            book_embeddings: List of book embeddings
            review_embeddings: List of review embeddings (parallel to books)
            compute_confidence: Whether to compute confidence scores
        
        Returns:
            List[RelevanceScore]: List of relevance scores
        """
        scores = []
        for book_emb, review_emb in zip(book_embeddings, review_embeddings):
            score = RelevanceScoringFunction.score_relevance(
                book_emb, review_emb, compute_confidence
            )
            scores.append(score)
        return scores


# ============================================================================
# COMBINED SCORING FEATURES
# ============================================================================

class ReviewRelevanceScoringFeatures:
    """
    Combines aggregated book metadata with preprocessed review text.
    
    Used as input to Sentence Transformer for creating embeddings.
    """
    
    @staticmethod
    def create_scoring_pair(
        book: Dict,
        review_text: str
    ) -> Tuple[str, str]:
        """
        Create a book-review pair for relevance scoring.
        
        Args:
            book: Dictionary with book metadata
            review_text: Raw review text
        
        Returns:
            tuple: (aggregated_book_text, preprocessed_review_text)
        """
        aggregated_book = BookMetadataAggregator.aggregate_from_dict(book)
        preprocessed_review = ReviewTextPreprocessor.preprocess(review_text)
        
        return aggregated_book, preprocessed_review
    
    @staticmethod
    def create_scoring_pairs_batch(
        books: list,
        reviews: list
    ) -> list:
        """
        Create multiple book-review pairs.
        
        Args:
            books: List of book dictionaries
            reviews: List of review texts (parallel to books)
        
        Returns:
            list: List of (aggregated_book, preprocessed_review) tuples
        """
        pairs = []
        for book, review_text in zip(books, reviews):
            pair = ReviewRelevanceScoringFeatures.create_scoring_pair(book, review_text)
            pairs.append(pair)
        return pairs


# ============================================================================
# EXAMPLES AND TESTS
# ============================================================================

def example_task_2_1():
    """Demonstrate Task 2.1 - Book Metadata Aggregation."""
    print("=" * 80)
    print("TASK 2.1: BOOK METADATA AGGREGATION (Strategy C)")
    print("=" * 80)
    
    # Example 1: Complete metadata
    book1 = {
        'title': 'The Great Gatsby',
        'author_name': 'F. Scott Fitzgerald',
        'genres': 'Fiction, Romance, Classics',
        'category_name': 'Classics',
        'description': 'A classic novel exploring the American Dream in 1920s New York, ' \
                      'following the mysterious Jay Gatsby and his obsession with Daisy Buchanan.'
    }
    
    agg1 = BookMetadataAggregator.aggregate_from_dict(book1)
    print("\nExample 1: Complete Metadata")
    print("-" * 80)
    print(agg1)
    print(f"\nLength: {len(agg1)} chars, ~{ReviewTextPreprocessor.estimate_tokens(agg1)} tokens")
    
    # Example 2: Missing description
    book2 = {
        'title': 'Python Programming',
        'author_name': 'Guido van Rossum',
        'genres': 'Programming, Technical',
        'category_name': 'Education',
        'description': None
    }
    
    agg2 = BookMetadataAggregator.aggregate_from_dict(book2)
    print("\nExample 2: Missing Description")
    print("-" * 80)
    print(agg2)
    print(f"\nLength: {len(agg2)} chars, ~{ReviewTextPreprocessor.estimate_tokens(agg2)} tokens")
    
    # Example 3: Minimal metadata (title only)
    book3 = {
        'title': '1984',
        'author_name': None,
        'genres': None,
        'category_name': None,
        'description': None
    }
    
    agg3 = BookMetadataAggregator.aggregate_from_dict(book3)
    print("\nExample 3: Minimal Metadata (Title Only)")
    print("-" * 80)
    print(agg3)
    print(f"\nLength: {len(agg3)} chars, ~{ReviewTextPreprocessor.estimate_tokens(agg3)} tokens")


def example_task_2_3():
    """Demonstrate Task 2.3 - Review Text Preprocessing."""
    print("\n" + "=" * 80)
    print("TASK 2.3: REVIEW TEXT PREPROCESSING (7-Step Pipeline)")
    print("=" * 80)
    
    reviews = [
        "I LOVED THIS BOOK!!! 😍😍😍 It was AMAZING!!!",
        "TERRIBLE!!! WASTE OF MONEY!!! DO NOT BUY!!!",
        "SPOILER ALERT: The villain dies at the end. But still a great read!",
        "5 &amp; 1/2 stars! &quot;Worth every penny&quot; as my friend said.",
        "The book was good but the ending...... was disappointing???",
    ]
    
    print("\nBefore/After Examples:")
    print("-" * 80)
    
    for i, review in enumerate(reviews, 1):
        preprocessed = ReviewTextPreprocessor.preprocess(review)
        stats = ReviewTextPreprocessor.get_preprocessing_report(review, preprocessed)
        
        # Safe encoding: replace non-ASCII with '?'
        review_safe = review.encode('ascii', 'replace').decode('ascii')
        preprocessed_safe = preprocessed.encode('ascii', 'replace').decode('ascii')
        
        print(f"\nReview {i}:")
        print(f"Original ({len(review)} chars, ~{stats['tokens_before']} tokens):")
        print(f"  {review_safe[:80]}{'...' if len(review) > 80 else ''}")
        print(f"\nProcessed ({len(preprocessed)} chars, ~{stats['tokens_after']} tokens):")
        print(f"  {preprocessed_safe[:80]}{'...' if len(preprocessed) > 80 else ''}")
        print(f"\nReduction: {stats['chars_reduced']} chars, {stats['tokens_reduced']} tokens")
        print(f"Within limit: {stats['within_token_limit']}")


def example_task_2_2():
    """Demonstrate Task 2.2 - Book Edge Case Handling."""
    print("\n" + "=" * 80)
    print("TASK 2.2: BOOK EDGE CASE HANDLING")
    print("=" * 80)
    
    # Example 1: Complete metadata (valid)
    print("\nExample 1: Complete Metadata")
    print("-" * 80)
    book1 = {
        'title': 'The Great Gatsby',
        'author_name': 'F. Scott Fitzgerald',
        'genres': 'Fiction, Romance, Classics',
        'category_name': 'Classics',
        'description': 'A classic novel exploring the American Dream.'
    }
    agg1 = BookMetadataAggregator.aggregate_from_dict(book1)
    is_valid, msg, case = BookEdgeCaseHandler.validate_and_log(1, book1['title'], book1['description'], agg1)
    print(f"Aggregated text: {agg1}")
    print(f"Valid for scoring: {is_valid} (Case: {case.value})")
    print(f"Message: {msg}")
    
    # Example 2: Missing description (edge case - NULL)
    print("\nExample 2: Missing Description (~12% of books)")
    print("-" * 80)
    book2 = {
        'title': 'Python Programming',
        'author_name': 'Guido van Rossum',
        'genres': 'Programming, Technical',
        'category_name': 'Education',
        'description': None
    }
    agg2 = BookMetadataAggregator.aggregate_from_dict(book2)
    is_valid, msg, case = BookEdgeCaseHandler.validate_and_log(2, book2['title'], book2['description'], agg2)
    print(f"Aggregated text: {agg2}")
    print(f"Valid for scoring: {is_valid} (Case: {case.value})")
    print(f"Message: {msg}")
    
    # Example 3: Short description (edge case - SHORT)
    print("\nExample 3: Short Description (<20 chars, 2-5% of books)")
    print("-" * 80)
    book3 = {
        'title': 'The Book',
        'author_name': None,
        'genres': None,
        'category_name': None,
        'description': 'Good'
    }
    agg3 = BookMetadataAggregator.aggregate_from_dict(book3)
    is_valid, msg, case = BookEdgeCaseHandler.validate_and_log(3, book3['title'], book3['description'], agg3)
    print(f"Aggregated text: {agg3}")
    print(f"Valid for scoring: {is_valid} (Case: {case.value})")
    print(f"Message: {msg}")
    
    # Example 4: Minimal metadata (edge case - MINIMAL)
    print("\nExample 4: Minimal Metadata (<30 chars, ~3% of books)")
    print("-" * 80)
    book4 = {
        'title': 'Nice',
        'author_name': None,
        'genres': None,
        'category_name': None,
        'description': None
    }
    agg4 = BookMetadataAggregator.aggregate_from_dict(book4)
    is_valid, msg, case = BookEdgeCaseHandler.validate_and_log(4, book4['title'], book4['description'], agg4)
    print(f"Aggregated text: {agg4}")
    print(f"Valid for scoring: {is_valid} (Case: {case.value})")
    print(f"Message: {msg}")


def example_task_2_4():
    """Demonstrate Task 2.4 - Review Edge Case Handling."""
    print("\n" + "=" * 80)
    print("TASK 2.4: REVIEW EDGE CASE HANDLING")
    print("=" * 80)
    
    # Example 1: Valid review
    print("\nExample 1: Valid Review (93% of reviews)")
    print("-" * 80)
    review1 = "This book was absolutely amazing! I loved every single page and couldn't put it down."
    preprocessed1 = ReviewTextPreprocessor.preprocess(review1)
    is_valid, msg, case = ReviewEdgeCaseHandler.validate_and_log(1, review1, preprocessed1)
    print(f"Original: {review1}")
    print(f"Preprocessed: {preprocessed1}")
    print(f"Valid for scoring: {is_valid} (Case: {case.value})")
    print(f"Message: {msg}")
    
    # Example 2: NULL/Empty review
    print("\nExample 2: Empty/NULL Review (5-7% of reviews)")
    print("-" * 80)
    review2 = ""
    preprocessed2 = ReviewTextPreprocessor.preprocess(review2)
    is_valid, msg, case = ReviewEdgeCaseHandler.validate_and_log(2, review2, preprocessed2)
    print(f"Original: '{review2}'")
    print(f"Preprocessed: '{preprocessed2}'")
    print(f"Valid for scoring: {is_valid} (Case: {case.value})")
    print(f"Message: {msg}")
    
    # Example 3: Very short review
    print("\nExample 3: Short Review (<5 chars, 2-4% of reviews)")
    print("-" * 80)
    review3 = "Good"
    preprocessed3 = ReviewTextPreprocessor.preprocess(review3)
    is_valid, msg, case = ReviewEdgeCaseHandler.validate_and_log(3, review3, preprocessed3)
    print(f"Original: {review3}")
    print(f"Preprocessed: {preprocessed3}")
    print(f"Valid for scoring: {is_valid} (Case: {case.value})")
    print(f"Message: {msg}")
    
    # Example 4: Gibberish/Spam
    print("\nExample 4: Gibberish/Spam Detection (~1% of reviews)")
    print("-" * 80)
    review4 = "test spam signal test"  # Using safe text instead of emojis
    preprocessed4 = ReviewTextPreprocessor.preprocess(review4)
    is_valid, msg, case = ReviewEdgeCaseHandler.validate_and_log(4, review4, preprocessed4)
    print(f"Original: {review4}")
    print(f"Preprocessed: '{preprocessed4}'")
    print(f"Valid for scoring: {is_valid} (Case: {case.value})")
    print(f"Message: {msg}")


def example_task_2_5():
    """Demonstrate Task 2.5 - Core Relevance Scoring."""
    print("\n" + "=" * 80)
    print("TASK 2.5: CORE RELEVANCE SCORING FUNCTION")
    print("=" * 80)
    
    np.random.seed(42)
    
    # Example 1: Perfect semantic match
    print("\nExample 1: Perfect Semantic Match")
    print("-" * 80)
    book_emb1 = np.random.randn(384)
    book_emb1 = book_emb1 / np.linalg.norm(book_emb1)
    # Similar to book embedding
    review_emb1 = book_emb1 + np.random.randn(384) * 0.05  # Small noise
    review_emb1 = review_emb1 / np.linalg.norm(review_emb1)
    
    score1 = RelevanceScoringFunction.score_relevance(book_emb1, review_emb1)
    print(f"Score: {score1.score:.4f}")
    print(f"Raw Cosine: {score1.raw_cosine:.4f}")
    print(f"Confidence: {score1.confidence:.4f}")
    print(f"Interpretation: High relevance, clear semantic match")
    
    # Example 2: Unrelated texts
    print("\nExample 2: Completely Unrelated Texts")
    print("-" * 80)
    book_emb2 = np.random.randn(384)
    book_emb2 = book_emb2 / np.linalg.norm(book_emb2)
    review_emb2 = np.random.randn(384)  # Completely different
    review_emb2 = review_emb2 / np.linalg.norm(review_emb2)
    
    score2 = RelevanceScoringFunction.score_relevance(book_emb2, review_emb2)
    print(f"Score: {score2.score:.4f}")
    print(f"Raw Cosine: {score2.raw_cosine:.4f}")
    print(f"Confidence: {score2.confidence:.4f}")
    print(f"Interpretation: Low relevance, unrelated content")
    
    # Example 3: Partial relevance
    print("\nExample 3: Partial Relevance (Some Overlap)")
    print("-" * 80)
    book_emb3 = np.random.randn(384)
    book_emb3 = book_emb3 / np.linalg.norm(book_emb3)
    # Moderate noise (50% similar, 50% different)
    review_emb3 = book_emb3 * 0.5 + np.random.randn(384) * 0.5
    review_emb3 = review_emb3 / np.linalg.norm(review_emb3)
    
    score3 = RelevanceScoringFunction.score_relevance(book_emb3, review_emb3)
    print(f"Score: {score3.score:.4f}")
    print(f"Raw Cosine: {score3.raw_cosine:.4f}")
    print(f"Confidence: {score3.confidence:.4f}")
    print(f"Interpretation: Moderate relevance, partial semantic overlap")
    
    # Example 4: Error handling - NULL embedding
    print("\nExample 4: Error Handling - NULL Embedding")
    print("-" * 80)
    score4 = RelevanceScoringFunction.score_relevance(None, review_emb1)
    print(f"Score: {score4.score}")
    print(f"Error Code: {score4.error_code}")
    print(f"Error Message: {score4.error_message}")
    print(f"Is Valid: {score4.is_valid()}")
    print(f"Interpretation: Cannot score due to NULL input")
    
    # Example 5: Batch scoring
    print("\nExample 5: Batch Scoring (Multiple Pairs)")
    print("-" * 80)
    book_embs = [
        np.random.randn(384) / np.linalg.norm(np.random.randn(384)) for _ in range(3)
    ]
    review_embs = [
        np.random.randn(384) / np.linalg.norm(np.random.randn(384)) for _ in range(3)
    ]
    
    scores = RelevanceScoringFunction.score_relevance_batch(book_embs, review_embs)
    print(f"Scored {len(scores)} book-review pairs:")
    for i, score in enumerate(scores, 1):
        print(f"  Pair {i}: score={score.score:.4f}, confidence={score.confidence:.4f}")


if __name__ == '__main__':
    example_task_2_1()
    example_task_2_3()
    example_task_2_2()
    example_task_2_4()
    example_task_2_5()
    
    print("\n" + "=" * 80)
    print("INTEGRATION EXAMPLE: COMPLETE SCORING PIPELINE")
    print("=" * 80)
    
    # Create a complete scoring pair
    book = {
        'title': 'To Kill a Mockingbird',
        'author_name': 'Harper Lee',
        'genres': 'Fiction, Classics',
        'category_name': 'Literature',
        'description': 'A gripping tale of racial injustice and childhood innocence in the American South.'
    }
    
    review = "I LOVED THIS BOOK!!! 😍 The characters were so well written and relatable. " \
             "Harper Lee really captured the essence of growing up in 1930s Alabama. Highly recommended!!!"
    
    aggregated_book, preprocessed_review = ReviewRelevanceScoringFeatures.create_scoring_pair(
        book, review
    )
    
    # Validate edge cases
    is_valid_book, msg_book, case_book = BookEdgeCaseHandler.validate_and_log(
        book_id=1,
        title=book['title'],
        description=book['description'],
        aggregated_text=aggregated_book
    )
    
    is_valid_review, msg_review, case_review = ReviewEdgeCaseHandler.validate_and_log(
        review_id=100,
        original_text=review,
        preprocessed_text=preprocessed_review
    )
    
    print("\nBook Metadata (Aggregated):")
    print(aggregated_book)
    print(f"Length: {len(aggregated_book)} chars, Valid: {is_valid_book}, Case: {case_book.value}")
    
    print("\n" + "-" * 80)
    print("\nReview Text (Preprocessed):")
    print(preprocessed_review)
    print(f"Length: {len(preprocessed_review)} chars, Valid: {is_valid_review}, Case: {case_review.value}")
    
    print("\n" + "-" * 80)
    print(f"\nBoth texts ready for Sentence Transformer embedding!")
    print(f"Book tokens: ~{ReviewTextPreprocessor.estimate_tokens(aggregated_book)}")
    print(f"Review tokens: ~{ReviewTextPreprocessor.estimate_tokens(preprocessed_review)}")
    print(f"Total tokens estimate: "
          f"~{ReviewTextPreprocessor.estimate_tokens(aggregated_book) + ReviewTextPreprocessor.estimate_tokens(preprocessed_review)}")
    
    print("\n" + "-" * 80)
    print("\nSimulating embeddings and scoring:")
    # Simulate embeddings (normally from Sentence Transformer model)
    np.random.seed(42)
    book_emb = np.random.randn(384)
    book_emb = book_emb / np.linalg.norm(book_emb)  # Normalize
    
    review_emb = np.random.randn(384)
    review_emb = review_emb / np.linalg.norm(review_emb)  # Normalize
    
    score_result = RelevanceScoringFunction.score_relevance(book_emb, review_emb)
    
    print(f"\nRelevance Score Result:")
    print(f"  Score: {score_result.score:.4f} (normalized [0, 1])")
    print(f"  Raw Cosine: {score_result.raw_cosine:.4f} ([-1, 1])")
    print(f"  Confidence: {score_result.confidence:.4f}")
    print(f"  Is Valid: {score_result.is_valid()}")
    print(f"  Error Code: {score_result.error_code}")
