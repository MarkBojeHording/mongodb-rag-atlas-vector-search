# RAG WITH ATLAS VECTOR SEARCH/backend/config.py
import os
from dotenv import load_dotenv
import urllib.parse

# Load environment variables from .env file
load_dotenv()

def encode_mongo_uri_safely(raw_uri):
    """Safely encode MongoDB URI with comprehensive error handling"""
    if not raw_uri:
        return None

    try:
        # Check if it's already a MongoDB URI
        if not (raw_uri.startswith('mongodb://') or raw_uri.startswith('mongodb+srv://')):
            print(f"[WARNING] URI doesn't look like MongoDB: {raw_uri[:50]}...")
            return raw_uri

        # Split the URI into components
        if '://' not in raw_uri:
            print(f"[ERROR] Invalid URI format: {raw_uri[:50]}...")
            return raw_uri

        scheme, rest = raw_uri.split('://', 1)

        # Handle URIs without authentication
        if '@' not in rest:
            print("[INFO] No authentication found in URI")
            return raw_uri

        # Split authentication and host parts
        auth_part, host_part = rest.split('@', 1)

        # Handle URIs without password
        if ':' not in auth_part:
            print("[INFO] No password found in URI")
            return raw_uri

        # Split username and password
        username, password = auth_part.split(':', 1)

        # URL encode with aggressive encoding (no safe characters)
        encoded_username = urllib.parse.quote_plus(username, safe='')
        encoded_password = urllib.parse.quote_plus(password, safe='')

        # Reconstruct the URI
        encoded_uri = f"{scheme}://{encoded_username}:{encoded_password}@{host_part}"

        print(f"[SUCCESS] URI encoded successfully")
        print(f"[DEBUG] Original username: {username}")
        print(f"[DEBUG] Encoded username: {encoded_username}")
        print(f"[DEBUG] Original password length: {len(password)}")
        print(f"[DEBUG] Encoded password length: {len(encoded_password)}")
        print(f"[DEBUG] Final URI preview: {encoded_uri[:50]}...")

        return encoded_uri

    except Exception as e:
        print(f"[ERROR] Failed to encode MongoDB URI: {e}")
        print(f"[ERROR] Raw URI: {raw_uri[:50]}...")
        return raw_uri

# --- MongoDB Configuration ---
# MongoDB connection string is now loaded from .env for security
raw_mongo_uri = os.getenv("MONGO_URI")  # Set this in your .env file
print(f"[DEBUG] Raw MongoDB URI: {raw_mongo_uri[:20]}..." if raw_mongo_uri else "[DEBUG] No MongoDB URI found")

# Encode the URI safely
MONGO_URI = encode_mongo_uri_safely(raw_mongo_uri)

if not MONGO_URI:
    print("[ERROR] MONGO_URI is not set or could not be processed")

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
