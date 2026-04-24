import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ML Models directory (shared volume in Docker)
ML_MODELS_DIR = os.getenv("ML_MODELS_DIR", "./models")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Recommendation batch size (default top-K results)
BATCH_SIZE_FOR_RECOMMENDATIONS = 10

# Server port
PORT = int(os.getenv("RECOMMENDER_SERVICE_PORT", 8082))
HOST = "0.0.0.0"

# Enable local fallback to bookService popular_books.json
ENABLE_LOCAL_FALLBACK = True

# Environment
ENV = os.getenv("ENVIRONMENT", "development")

# Kafka Configuration (Event-driven review scoring)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
KAFKA_SCHEMA_REGISTRY_URL = os.getenv("KAFKA_SCHEMA_REGISTRY_URL", "http://localhost:8085")

# Kafka Topics
KAFKA_REVIEW_SCORING_REQUEST_TOPIC = os.getenv("KAFKA_REVIEW_SCORING_REQUEST_TOPIC", "review-scoring-requests")
KAFKA_REVIEW_SCORING_RESULT_TOPIC = os.getenv("KAFKA_REVIEW_SCORING_RESULT_TOPIC", "review-scoring-results")
KAFKA_REVIEW_SCORING_DLQ_TOPIC = os.getenv("KAFKA_REVIEW_SCORING_DLQ_TOPIC", "review-scoring-dlq")

# Kafka Consumer Group
KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "recommender-service-group")

# Batch processing settings (for future optimization)
KAFKA_BATCH_SIZE = int(os.getenv("KAFKA_BATCH_SIZE", "1"))
KAFKA_BATCH_TIMEOUT_MS = int(os.getenv("KAFKA_BATCH_TIMEOUT_MS", "1000"))

# Sentence transformer model for relevance scoring
SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
SENTENCE_TRANSFORMER_MODEL_VERSION = "3.0.0"
