# Model file names
TFIDF_VECTORIZER_FILE = "tfidf_vectorizer.joblib"
TFIDF_MATRIX_FILE = "tfidf_matrix.joblib"
ITEM_COOCCURRENCE_FILE = "item_cooccurrence.npy"
BOOKID_TO_ROW_FILE = "bookid_to_row.json"
POPULAR_BOOKS_FILE = "popular_books.json"
BOOK_EMBEDDINGS_FILE = "book_embeddings.npy"

# Default parameters
DEFAULT_TOP_K = 10
MAX_TOP_K = 50
MIN_SIMILARITY_SCORE = 0.0

# API response constants
SERVICE_NAME = "recommenderService"
SERVICE_VERSION = "1.0.0"
SERVICE_DESCRIPTION = "Hybrid recommendation engine (content-based + collaborative filtering)"
