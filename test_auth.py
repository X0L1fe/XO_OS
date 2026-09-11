#!/usr/bin/env python3
"""Test script to debug authentication issues"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from auth.service import get_password_hash, create_user, authenticate_user
from auth.schemas import UserCreate
from database.db import Database
from database.models import User

def test_password_hash():
    """Test password hashing directly"""
    print("=== Testing password hashing ===")
    test_passwords = [
        "test1234",  # 8 chars
        "a",         # 1 char
        "ab",        # 2 chars
        "abc123!",    # 8 chars with special
        "x" * 72,    # exactly 72 chars (bcrypt limit)
        "x" * 73,    # 73 chars (should fail)
    ]

    for pwd in test_passwords:
        print(f"\nTesting password: {repr(pwd)} (length: {len(pwd)})")
        try:
            hashed = get_password_hash(pwd)
            print(f"  Success: hash generated (length: {len(hashed)})")
            # Verify it
            verified = pwd_context.verify(pwd, hashed)
            print(f"  Verify: {verified}")
        except Exception as e:
            print(f"  Error: {e}")

def test_user_creation():
    """Test creating a user in the database"""
    print("\n=== Testing user creation ===")
    db = Database()
    session = db.session()
    try:
        # Clean up any existing test user
        session.query(User).filter(User.email == "test@example.com").delete()
        session.commit()

        # Create test user
        user_data = UserCreate(
            email="test@example.com",
            name="Test User",
            password="test1234"
        )

        print(f"Creating user with: {user_data}")
        created_user = create_user(session, user_data)
        print(f"Created user: {created_user.email}")
        print(f"Password hash: {created_user.password_hash}")

        # Test authentication
        authenticated = authenticate_user(session, "test@example.com", "test1234")
        print(f"Authenticated with correct password: {authenticated is not None}")

        authenticated_wrong = authenticate_user(session, "test@example.com", "wrong")
        print(f"Authenticated with wrong password: {authenticated_wrong is not None}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    # Import pwd_context for verification
    from passlib.context import CryptContext
    global pwd_context
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    test_password_hash()
    test_user_creation()