# RAG WITH ATLAS VECTOR SEARCH/backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_chain import answer_question # Import your RAG function
from db_utils import ingest_documents_to_mongodb # For initial ingestion
import logging
import sys
import datetime
import os
import urllib.parse
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MongoDB Investor RAG API",
    description="API for Retrieval Augmented Generation using MongoDB Investor Relations documents.",
    version="0.1.0"
)

# Configure CORS to allow your frontend to access the API
origins = [
    "http://localhost:3000",  # Default for Create React App
    "http://localhost:5173",  # Default for Vite React app
    "https://*.netlify.app",  # Allow all Netlify domains
    "https://*.onrender.com", # Allow all Render domains
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

# Load MongoDB URI directly to avoid config.py import issues
raw_mongo_uri = os.getenv("MONGO_URI")
if raw_mongo_uri:
    try:
        # Encode the URI safely
        if 'mongodb+srv://' in raw_mongo_uri:
            scheme, rest = raw_mongo_uri.split('://', 1)
            if '@' in rest:
                auth_part, host_part = rest.split('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                    encoded_username = urllib.parse.quote_plus(username, safe='')
                    encoded_password = urllib.parse.quote_plus(password, safe='')
                    MONGO_URI = f"{scheme}://{encoded_username}:{encoded_password}@{host_part}"
                else:
                    MONGO_URI = raw_mongo_uri
            else:
                MONGO_URI = raw_mongo_uri
        else:
            MONGO_URI = raw_mongo_uri
    except Exception as e:
        print(f"Error encoding MongoDB URI: {e}")
        MONGO_URI = raw_mongo_uri
else:
    MONGO_URI = None

print(f"[DEBUG] MONGO_URI: {MONGO_URI[:50] if MONGO_URI else 'None'}...")

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
    except ValueError as e:
        if "Port contains non-digit characters" in str(e):
            # This is the specific error we're dealing with
            logger.error(f"MongoDB URI encoding error: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "issue": "MongoDB URI encoding problem - special characters in username/password need URL encoding",
                "timestamp": str(datetime.datetime.now())
            }
        else:
            logger.error(f"ValueError in health check: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
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

@app.get("/debug")
async def debug_info():
    """Debug endpoint to show MongoDB URI information"""
    raw_uri = os.getenv("MONGO_URI")

    if not raw_uri:
        return {"error": "MONGO_URI not found in environment"}

    # Show basic info without exposing sensitive data
    info = {
        "uri_length": len(raw_uri),
        "uri_preview": raw_uri[:20] + "..." if len(raw_uri) > 20 else raw_uri,
        "starts_with_mongodb": raw_uri.startswith('mongodb'),
        "contains_at": '@' in raw_uri,
        "contains_colon": ':' in raw_uri,
        "special_chars": []
    }

    # Check for problematic characters
    problematic_chars = ['@', ':', '/', '?', '#', '[', ']', '%', '+', '=', '&']
    for char in problematic_chars:
        if char in raw_uri:
            info["special_chars"].append(char)

    return info

@app.get("/test-connection")
async def test_connection():
    """Test MongoDB connection directly without config.py"""
    raw_uri = os.getenv("MONGO_URI")
    if not raw_uri:
        return {"error": "MONGO_URI not found"}

    results = {
        "raw_uri_length": len(raw_uri),
        "raw_uri_preview": raw_uri[:30] + "..." if len(raw_uri) > 30 else raw_uri,
        "tests": {}
    }

    # Test 1: Direct connection
    try:
        client = MongoClient(raw_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        results["tests"]["direct"] = "success"
        client.close()
    except Exception as e:
        results["tests"]["direct"] = f"failed: {str(e)}"

    # Test 2: Manual encoding
    try:
        if 'mongodb+srv://' in raw_uri:
            scheme, rest = raw_uri.split('://', 1)
            if '@' in rest:
                auth_part, host_part = rest.split('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                    encoded_username = urllib.parse.quote_plus(username, safe='')
                    encoded_password = urllib.parse.quote_plus(password, safe='')
                    encoded_uri = f"{scheme}://{encoded_username}:{encoded_password}@{host_part}"

                    client = MongoClient(encoded_uri, serverSelectionTimeoutMS=5000)
                    client.admin.command('ping')
                    results["tests"]["encoded"] = "success"
                    results["encoded_uri_preview"] = encoded_uri[:30] + "..."
                    client.close()
                else:
                    results["tests"]["encoded"] = "no password found"
            else:
                results["tests"]["encoded"] = "no authentication found"
        else:
            results["tests"]["encoded"] = "not mongodb+srv URI"
    except Exception as e:
        results["tests"]["encoded"] = f"failed: {str(e)}"

    return results

# You can add more endpoints here, e.g., for document upload, system status, etc.
