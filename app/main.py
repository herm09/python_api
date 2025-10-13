from fastapi import FastAPI

from app.api.routes.books import router as books_router

from app.utils.logger import get_logger, setup_logging

setup_logging()

logger = get_logger(__name__)

logger.info("Démarrage de l'API")
logger.error("Halala une erreur")

app = FastAPI(
    title="bib",
    description="API REST pour une bibliothèque",
    version="1.0.0",
    docs_url="/docs",
)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome",
        "version": "1.0.0",
        "documentation":"/docs"
    }

@app.get("/tests", tags=["Health"])
async def health_check():
    return {
        "status": "Healthy",
        "service": "bib-api",
    }

app.include_router(books_router, prefix="/books", tags=["Books"])