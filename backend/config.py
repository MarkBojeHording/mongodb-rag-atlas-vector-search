# RAG WITH ATLAS VECTOR SEARCH/backend/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Hugging Face Configuration ---
# Load Hugging Face access token from environment variable

# --- MongoDB Configuration ---
# MongoDB connection string is now loaded from .env for security
import urllib.parse

raw_mongo_uri = os.getenv("MONGO_URI")  # Set this in your .env file
if raw_mongo_uri:
    # Parse and re-encode the URI to handle special characters
    parsed = urllib.parse.urlparse(raw_mongo_uri)
    # Re-encode username and password if they contain special characters
    if '@' in parsed.netloc:
        auth, host = parsed.netloc.split('@', 1)
        if ':' in auth:
            username, password = auth.split(':', 1)
            # URL encode username and password
            encoded_username = urllib.parse.quote_plus(username)
            encoded_password = urllib.parse.quote_plus(password)
            # Reconstruct the URI
            MONGO_URI = f"{parsed.scheme}://{encoded_username}:{encoded_password}@{host}"
        else:
            MONGO_URI = raw_mongo_uri
    else:
        MONGO_URI = raw_mongo_uri
else:
    MONGO_URI = None
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
