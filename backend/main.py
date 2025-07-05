# RAG WITH ATLAS VECTOR SEARCH/backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_chain import answer_question # Import your RAG function
from db_utils import ingest_documents_to_mongodb # For initial ingestion
import logging
import sys
import datetime
from config import MONGO_URI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MongoDB Investor RAG API",
    description="API for Retrieval Augmented Generation using MongoDB Investor Relations documents.",
    version="0.1.0"
)

# Configure CORS to allow your frontend to access the API
# IMPORTANT: In production, change "http://localhost:3000" and "http://localhost:5173"
# to the actual domain where your frontend will be hosted!
origins = [
    "http://localhost:3000",  # Default for Create React App
    "http://localhost:5173",  # Default for Vite React app
    # Add your deployed frontend URL here when ready, e.g., "https://your-frontend-app.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"], # Allows all headers
)

class QueryRequest(BaseModel):
    query: str

print(f"[DEBUG] Python version: {sys.version}")
print(f"[DEBUG] MONGO_URI: {MONGO_URI}")

@app.get("/")
async def read_root():
    """Root endpoint to check if the API is running."""
    logger.info("Root endpoint accessed.")
    return {"message": "RAG API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    try:
        # Test MongoDB connection
        from db_utils import get_mongo_collection
        collection = get_mongo_collection()
        collection.find_one()  # Simple query to test connection

        return {
            "status": "healthy",
            "mongodb": "connected",
            "timestamp": str(datetime.datetime.now())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": str(datetime.datetime.now())
        }

@app.post("/ask")
async def ask_rag(request: QueryRequest):
    """
    Endpoint to ask a question to the RAG system and get an answer with sources.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Received query: '{request.query}'")
    try:
        response = answer_question(request.query)
        return response
    except Exception as e:
        logger.exception("Error processing RAG query in API.") # Logs full traceback
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.post("/api/chat")
async def chat_endpoint(request: QueryRequest):
    """
    Chat endpoint that returns answer and sources in the format expected by the frontend.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Received chat query: '{request.query}'")
    try:
        response = answer_question(request.query)

        # Format response for frontend
        return {
            "answer": response.get("answer", "I couldn't find a specific answer to your question."),
            "sources": response.get("sources", [])
        }
    except Exception as e:
        logger.exception("Error processing chat query in API.")
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {e}")

@app.post("/ingest_documents")
async def ingest_documents_endpoint():
    """
    Endpoint to trigger the ingestion of the specified PDF document into MongoDB.
    This should typically be run once or on demand, not continuously.
    """
    logger.info("Received request to ingest documents via API.")
    try:
        # In a production app, you would add authentication/authorization to this endpoint
        # to prevent unauthorized document ingestion.
        ingest_documents_to_mongodb()
        logger.info("Document ingestion process initiated successfully via API.")
        return {"message": "Document ingestion initiated. Check backend logs for progress."}
    except Exception as e:
        logger.exception("Error during document ingestion via API.")
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {e}")

# You can add more endpoints here, e.g., for document upload, system status, etc.
