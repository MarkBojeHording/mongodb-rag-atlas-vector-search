#!/usr/bin/env python3
"""
Test script to verify MongoDB Atlas connection and diagnose SSL issues.
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import logging
import urllib.parse

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def encode_mongo_uri(uri):
    """Encode MongoDB URI to handle special characters in username/password."""
    if not uri:
        return uri

    try:
        if 'mongodb+srv://' in uri:
            scheme, rest = uri.split('://', 1)
            if '@' in rest:
                auth_part, host_part = rest.split('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                    # URL encode username and password
                    encoded_username = urllib.parse.quote_plus(username)
                    encoded_password = urllib.parse.quote_plus(password)
                    # Reconstruct the URI
                    return f"{scheme}://{encoded_username}:{encoded_password}@{host_part}"
        return uri
    except Exception as e:
        logger.error(f"Error encoding MongoDB URI: {e}")
        return uri

def test_mongodb_connection():
    """Test MongoDB Atlas connection with different configurations."""
    raw_mongo_uri = os.getenv("MONGO_URI")

    if not raw_mongo_uri:
        logger.error("MONGO_URI not found in environment variables")
        return False

    # Encode the URI to handle special characters
    mongo_uri = encode_mongo_uri(raw_mongo_uri)
    logger.info(f"MongoDB URI: {mongo_uri[:50]}...")  # Show first 50 chars for security

    # Test different connection configurations
    configs = [
        {
            "name": "Default with TLS",
            "config": {
                "serverSelectionTimeoutMS": 30000,
                "connectTimeoutMS": 30000,
                "socketTimeoutMS": 30000,
                "tls": True,
                "tlsAllowInvalidCertificates": False,
                "tlsAllowInvalidHostnames": False,
                "retryWrites": True,
                "w": "majority"
            }
        },
        {
            "name": "Relaxed SSL",
            "config": {
                "serverSelectionTimeoutMS": 30000,
                "connectTimeoutMS": 30000,
                "socketTimeoutMS": 30000,
                "tls": True,
                "tlsAllowInvalidCertificates": True,
                "tlsAllowInvalidHostnames": True,
                "retryWrites": True,
                "w": "majority"
            }
        }
    ]

    for config in configs:
        logger.info(f"\nTesting configuration: {config['name']}")
        try:
            client = MongoClient(mongo_uri, **config['config'])

            # Test connection
            client.admin.command('ping')
            logger.info(f"✅ {config['name']}: Connection successful!")

            # Test database access
            db = client["rag_db"]
            collection = db["test"]
            count = collection.count_documents({})
            logger.info(f"✅ {config['name']}: Database access successful! Document count: {count}")

            client.close()
            return True

        except Exception as e:
            logger.error(f"❌ {config['name']}: Connection failed - {e}")
            continue

    return False

if __name__ == "__main__":
    logger.info("Testing MongoDB Atlas connection...")
    success = test_mongodb_connection()

    if success:
        logger.info("✅ Connection test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ All connection attempts failed!")
        sys.exit(1)
