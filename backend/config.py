# RAG WITH ATLAS VECTOR SEARCH/backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Hugging Face Configuration ---
# Load Hugging Face access token from environment variable

# --- MongoDB Configuration ---
# MongoDB connection string is now loaded from .env for security
MONGO_URI = os.getenv("MONGO_URI")  # Set this in your .env file
DB_NAME = "rag_db"
COLLECTION_NAME = "test"
VECTOR_SEARCH_INDEX_NAME = "vector_index"

# --- LLM Configuration ---
# Using Hugging Face's Mistral model
HF_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"

# PDF URL for initial ingestion
INVESTOR_PDF_URL = "https://investors.mongodb.com/node/12236/pdf"

# Chunking parameters
CHUNK_SIZE = 400
CHUNK_OVERLAP = 20
