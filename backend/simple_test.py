#!/usr/bin/env python3
"""
Simple test script to diagnose MongoDB Atlas SSL connection issues.
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import ssl
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
                    # URL encode username and password with aggressive encoding
                    encoded_username = urllib.parse.quote_plus(username, safe='')
                    encoded_password = urllib.parse.quote_plus(password, safe='')
                    # Reconstruct the URI
                    return f"{scheme}://{encoded_username}:{encoded_password}@{host_part}"
        return uri
    except Exception as e:
        logger.error(f"Error encoding MongoDB URI: {e}")
        return uri

def test_basic_connection():
    """Test basic MongoDB connection without complex SSL settings."""
    raw_mongo_uri = os.getenv("MONGO_URI")

    if not raw_mongo_uri:
        logger.error("MONGO_URI not found in environment variables")
        return False

    # Encode the URI to handle special characters
    mongo_uri = encode_mongo_uri(raw_mongo_uri)
    logger.info(f"MongoDB URI: {mongo_uri[:50]}...")

    # Test 1: Basic connection with minimal settings
    try:
        logger.info("Test 1: Basic connection with minimal settings")
        client = MongoClient(mongo_uri)
        client.admin.command('ping')
        logger.info("✅ Basic connection successful!")
        client.close()
        return True
    except Exception as e:
        logger.error(f"❌ Basic connection failed: {e}")

    # Test 2: Connection with explicit SSL context
    try:
        logger.info("Test 2: Connection with explicit SSL context")
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        client = MongoClient(
            mongo_uri,
            tls=True,
            tlsInsecure=True,
            serverSelectionTimeoutMS=10000
        )
        client.admin.command('ping')
        logger.info("✅ SSL context connection successful!")
        client.close()
        return True
    except Exception as e:
        logger.error(f"❌ SSL context connection failed: {e}")

    # Test 3: Connection with older SSL settings
    try:
        logger.info("Test 3: Connection with older SSL settings")
        client = MongoClient(
            mongo_uri,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE,
            serverSelectionTimeoutMS=10000
        )
        client.admin.command('ping')
        logger.info("✅ Older SSL settings connection successful!")
        client.close()
        return True
    except Exception as e:
        logger.error(f"❌ Older SSL settings connection failed: {e}")

    return False

if __name__ == "__main__":
    logger.info("Testing basic MongoDB Atlas connection...")
    success = test_basic_connection()

    if success:
        logger.info("✅ Connection test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ All connection attempts failed!")
        sys.exit(1)
