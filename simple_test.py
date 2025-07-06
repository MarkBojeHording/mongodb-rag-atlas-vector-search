#!/usr/bin/env python3
"""
Simple test to isolate MongoDB connection issue
"""
import os
import urllib.parse
from pymongo import MongoClient

def test_direct_connection():
    """Test MongoDB connection directly without config.py"""

    # Get raw URI from environment
    raw_uri = os.getenv("MONGO_URI")
    print(f"Raw URI length: {len(raw_uri) if raw_uri else 0}")

    if not raw_uri:
        print("No MONGO_URI found")
        return False

    try:
        # Try direct connection first
        print("Testing direct connection...")
        client = MongoClient(raw_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✓ Direct connection successful")
        return True
    except Exception as e:
        print(f"✗ Direct connection failed: {e}")

        # Try with manual encoding
        try:
            print("Testing with manual encoding...")
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
                        print("✓ Encoded connection successful")
                        return True
        except Exception as e2:
            print(f"✗ Encoded connection failed: {e2}")

    return False

if __name__ == "__main__":
    test_direct_connection()
