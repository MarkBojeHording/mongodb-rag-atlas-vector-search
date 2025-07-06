#!/usr/bin/env python3
"""
Test script to debug MongoDB URI encoding issues
"""
import os
import urllib.parse

def test_uri_encoding():
    """Test URI encoding with various scenarios"""

    # Get the raw URI from environment
    raw_uri = os.getenv("MONGO_URI")
    print(f"Raw URI from environment: {raw_uri[:50]}..." if raw_uri else "No URI found")

    if not raw_uri:
        return

    try:
        # Test 1: Basic parsing
        print("\n=== Test 1: Basic URI Parsing ===")
        if '://' in raw_uri:
            scheme, rest = raw_uri.split('://', 1)
            print(f"Scheme: {scheme}")
            print(f"Rest: {rest[:50]}...")
        else:
            print("No scheme found")
            return

        # Test 2: Authentication parsing
        print("\n=== Test 2: Authentication Parsing ===")
        if '@' in rest:
            auth_part, host_part = rest.split('@', 1)
            print(f"Auth part: {auth_part}")
            print(f"Host part: {host_part[:50]}...")
        else:
            print("No authentication found")
            return

        # Test 3: Username/Password parsing
        print("\n=== Test 3: Username/Password Parsing ===")
        if ':' in auth_part:
            username, password = auth_part.split(':', 1)
            print(f"Username: {username}")
            print(f"Password length: {len(password)}")
            print(f"Password preview: {password[:10]}...")
        else:
            print("No password found")
            return

        # Test 4: URL encoding
        print("\n=== Test 4: URL Encoding ===")
        encoded_username = urllib.parse.quote_plus(username, safe='')
        encoded_password = urllib.parse.quote_plus(password, safe='')
        print(f"Encoded username: {encoded_username}")
        print(f"Encoded password: {encoded_password}")

        # Test 5: Reconstruct URI
        print("\n=== Test 5: Reconstruct URI ===")
        encoded_uri = f"{scheme}://{encoded_username}:{encoded_password}@{host_part}"
        print(f"Encoded URI: {encoded_uri[:50]}...")

        # Test 6: Validate URI format
        print("\n=== Test 6: URI Validation ===")
        if encoded_uri.startswith('mongodb+srv://') or encoded_uri.startswith('mongodb://'):
            print("✓ URI format looks correct")
        else:
            print("✗ URI format looks incorrect")

        # Test 7: Check for problematic characters
        print("\n=== Test 7: Character Analysis ===")
        problematic_chars = ['@', ':', '/', '?', '#', '[', ']']
        for char in problematic_chars:
            if char in username:
                print(f"⚠️  Username contains '{char}'")
            if char in password:
                print(f"⚠️  Password contains '{char}'")

    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_uri_encoding()
