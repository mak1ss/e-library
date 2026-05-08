from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import config as app_config
from config import HOST, PORT, ML_MODELS_DIR, SENTENCE_TRANSFORMER_MODEL
from utils.logger import logger
from services.ml_model_loader import MLModelLoader
from services.content_based_service import ContentBasedRecommender
from services.collaborative_service import CollaborativeRecommender
from services.hybrid_recommender import HybridRecommender
from services.kafka_consumer import start_review_scoring_consumer, stop_review_scoring_consumer
from services.matrix_update_service import MatrixUpdateService
from services.matrix_update_consumer import start_matrix_update_consumer, stop_matrix_update_consumer
from routes import recommendations

# Initialize ML loader as a module-level variable
ml_loader = MLModelLoader(models_dir=ML_MODELS_DIR)
recommender = None
kafka_consumer_task = None
matrix_update_task = None
flush_task = None


async def periodic_flush(loader: MLModelLoader, interval_seconds: int = 1800) -> None:
    """Flush in-memory matrices to disk every interval_seconds."""
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            loader.flush_to_disk()
        except Exception as e:
            logger.error(f"Error during periodic flush: {e}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title="e-library Recommender Service",
    version="1.0.0",
    description="Hybrid recommendation engine (content-based + collaborative filtering)"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize ML models and start Kafka consumer on startup"""
    global ml_loader, recommender, kafka_consumer_task, matrix_update_task, flush_task

    logger.info("=" * 50)
    logger.info("Starting recommenderService...")
    logger.info("=" * 50)

    try:
        # Load ML models
        ml_loader.load_all_models()

        if not ml_loader.is_ready():
            raise RuntimeError("Failed to initialize ML models")

        # Initialize recommendation engines
        content_based = ContentBasedRecommender(ml_loader)
        collaborative = CollaborativeRecommender(ml_loader)
        recommender = HybridRecommender(content_based, collaborative)

        # Set recommender context in routes
        recommendations.set_recommender_context(ml_loader, recommender)

        # Start Kafka consumer for review scoring requests (async background task)
        kafka_consumer_task = asyncio.create_task(start_review_scoring_consumer())
        logger.info("Review scoring consumer started in background")

        # Start incremental matrix update consumer
        matrix_update_svc = MatrixUpdateService(ml_loader, SENTENCE_TRANSFORMER_MODEL)
        matrix_update_task = asyncio.create_task(
            start_matrix_update_consumer(matrix_update_svc)
        )
        logger.info("Matrix update consumer started in background")

        # Periodic flush: persist in-memory matrices to disk every 30 minutes
        flush_task = asyncio.create_task(periodic_flush(ml_loader, interval_seconds=1800))
        logger.info("Periodic flush task started (interval=1800s)")

        logger.info("=" * 50)
        logger.info("recommenderService ready for requests")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Failed to start service: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global kafka_consumer_task, matrix_update_task, flush_task
    logger.info("Shutting down recommenderService")

    # Cancel background tasks
    for task in (matrix_update_task, flush_task):
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    # Stop Kafka consumers gracefully
    try:
        await stop_review_scoring_consumer()
    except Exception as e:
        logger.error(f"Error stopping review scoring consumer: {e}", exc_info=True)

    try:
        await stop_matrix_update_consumer()
    except Exception as e:
        logger.error(f"Error stopping matrix update consumer: {e}", exc_info=True)

    # Final flush before exit
    try:
        ml_loader.flush_to_disk()
        logger.info("Final flush completed on shutdown")
    except Exception as e:
        logger.error(f"Error during shutdown flush: {e}", exc_info=True)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "recommenderService",
        "status": "running",
        "version": "1.0.0"
    }


# Include routers
app.include_router(recommendations.router)


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting FastAPI server on {HOST}:{PORT}")
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )
