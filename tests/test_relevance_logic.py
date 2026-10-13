#!/usr/bin/env python3
"""
Test the relevance check logic directly.
"""
import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.db import Database
from app.database.models import User


def test_relevance_logic():
    """Test the relevance check logic directly."""
    print("=== Testing Relevance Check Logic ===")

    db = Database()
    user_id = 1
    target_calendar_id = "target_calendar_id"

    # Test 1: Exact match (should NOT trigger early return)
    print("\n--- Test 1: Exact match ---")
    user_mock1 = Mock()
    user_mock1.id = user_id
    user_mock1.selected_calendar_id = target_calendar_id
    relevance_check1 = user_mock1.selected_calendar_id != target_calendar_id
    print(f"user.selected_calendar_id: '{user_mock1.selected_calendar_id}'")
    print(f"target_calendar_id: '{target_calendar_id}'")
    print(f"selected_calendar_id != target_calendar_id: {relevance_check1}")
    print(f"Should return early (True means return 0): {relevance_check1}")

    # Test 2: No match (should trigger early return)
    print("\n--- Test 2: No match ---")
    user_mock2 = Mock()
    user_mock2.id = user_id
    user_mock2.selected_calendar_id = "different_calendar_id"
    relevance_check2 = user_mock2.selected_calendar_id != target_calendar_id
    print(f"user.selected_calendar_id: '{user_mock2.selected_calendar_id}'")
    print(f"target_calendar_id: '{target_calendar_id}'")
    print(f"selected_calendar_id != target_calendar_id: {relevance_check2}")
    print(f"Should return early (True means return 0): {relevance_check2}")

    # Test 3: None value
    print("\n--- Test 3: None value ---")
    user_mock3 = Mock()
    user_mock3.id = user_id
    user_mock3.selected_calendar_id = None
    relevance_check3 = user_mock3.selected_calendar_id != target_calendar_id
    print(f"user.selected_calendar_id: {user_mock3.selected_calendar_id}")
    print(f"target_calendar_id: '{target_calendar_id}'")
    print(f"selected_calendar_id != target_calendar_id: {relevance_check3}")
    print(f"Should return early (True means return 0): {relevance_check3}")

    # Test 4: Empty string
    print("\n--- Test 4: Empty string ---")
    user_mock4 = Mock()
    user_mock4.id = user_id
    user_mock4.selected_calendar_id = ""
    relevance_check4 = user_mock4.selected_calendar_id != target_calendar_id
    print(f"user.selected_calendar_id: '{user_mock4.selected_calendar_id}'")
    print(f"target_calendar_id: '{target_calendar_id}'")
    print(f"selected_calendar_id != target_calendar_id: {relevance_check4}")
    print(f"Should return early (True means return 0): {relevance_check4}")


if __name__ == "__main__":
    test_relevance_logic()