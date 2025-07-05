#!/usr/bin/env python3
"""
Test script to verify MongoDB Atlas connection and diagnose SSL issues.
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mongodb_connection():
    """Test MongoDB Atlas connection with different configurations."""
    mongo_uri = os.getenv("MONGO_URI")

    if not mongo_uri:
        logger.error("MONGO_URI not found in environment variables")
        return False

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
