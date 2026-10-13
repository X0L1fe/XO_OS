#!/usr/bin/env python3
"""
Track exactly when session_mock is called and what queries happen in each.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection


def test_call_tracking():
    """Track session calls and queries precisely."""
    print("=== Tracking Session Calls and Queries ===")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    # Track all session mock calls
    session_call_count = 0
    session_details = []  # List of dicts, one per session call

    def session_mock(*args, **kwargs):
        nonlocal session_call_count
        session_call_count += 1
        current_session_index = session_call_count - 1  # 0-based

        print(f"\n{'='*60}")
        print(f"SESSION MOCK CALL #{session_call_count} STARTING")
        print(f"{'='*60}")

        # Initialize tracking for this session
        session_details.append({
            'call_number': session_call_count,
            'queries': []
        })

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        query_count = 0

        def query_side_effect(*query_args):
            nonlocal query_count
            query_count += 1
            query_type = query_args[0].__name__ if hasattr(query_args[0], '__name__') else str(query_args[0])

            # Track this query
            session_details[current_session_index]['queries'].append({
                'query_number': query_count,
                'type': query_type,
                'args': query_args
            })

            print(f"  Query #{query_count}: {query_type}")
            if len(query_args) > 1:
                print(f"    Args: {query_args[1:]}")

            # Handle the query based on type and session context
            if query_args[0] is User:
                print(f"    -> Processing User query")
                user_mock = Mock()
                user_mock.id = user_id
                user_mock.selected_calendar_id = target_calendar_id  # Match target for relevance check

                # Proper mock chaining: query.filter().first()
                query_mock = Mock()
                filter_mock = Mock()
                query_mock.filter.return_value = filter_mock
                filter_mock.first.return_value = user_mock
                return query_mock

            elif query_args[0] is GoogleCalendarConnection:
                print(f"    -> Processing GoogleCalendarConnection query")
                print(f"    ==> Current session: #{session_call_count}")
                print(f"    ==> Query number in this session: {query_count}")

                # We need to determine what kind of connection query this is
                # based on the session number and query number within that session

                current_session_num = session_call_count
                current_query_num = query_count

                print(f"    ==> Session {current_session_num}, Query {current_query_num}")

                # SESSION 1: Relevance check (should ONLY have User query)
                if current_session_num == 1:
                    print(f"    !! Unexpected GoogleCalendarConnection query in relevance check session!")
                    # Return empty mock to avoid breaking the flow
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

                # SESSION 2: Connection check (should have 2 GoogleCalendarConnection queries)
                elif current_session_num == 2:
                    if current_query_num == 1:
                        print(f"    -> This is source connection check (1st GCC query in session 2)")
                        query_mock = Mock()
                        filter_mock = Mock()
                        query_mock.filter.return_value = filter_mock
                        filter_mock.first.return_value = Mock()  # Return a mock connection
                        return query_mock
                    elif current_query_num == 2:
                        print(f"    -> This is target connection check (2nd GCC query in session 2)")
                        query_mock = Mock()
                        filter_mock = Mock()
                        query_mock.filter.return_value = filter_mock
                        filter_mock.first.return_value = Mock()  # Return a mock connection
                        return query_mock
                    else:
                        print(f"    -> Unexpected GCC query #{current_query_num} in session 2")
                        query_mock = Mock()
                        filter_mock = Mock()
                        query_mock.filter.return_value = filter_mock
                        filter_mock.first.return_value = None
                        return query_mock

                # SESSION 3: Get lessons (should get connections again, then lessons)
                elif current_session_num == 3:
                    if current_query_num == 1:
                        print(f"    -> Getting source connection again (1st GCC query in session 3)")
                        query_mock = Mock()
                        filter_mock = Mock()
                        query_mock.filter.return_value = filter_mock
                        filter_mock.first.return_value = Mock()
                        return query_mock
                    elif current_query_num == 2:
                        print(f"    -> Getting target connection again (2nd GCC query in session 3)")
                        query_mock = Mock()
                        filter_mock = Mock()
                        query_mock.filter.return_value = filter_mock
                        filter_mock.first.return_value = Mock()
                        return query_mock
                    elif current_query_num >= 3:
                        print(f"    -> Building lessons query (query #{current_query_num} in session 3)")
                        query_mock = Mock()
                        join_mock = Mock()
                        filter1_mock = Mock()
                        filter2_mock = Mock()

                        query_mock.join.return_value = join_mock
                        join_mock.filter.return_value = filter1_mock
                        filter1_mock.filter.return_value = filter2_mock
                        filter2_mock.all.return_value = []  # Default to empty

                        return query_mock
                    else:
                        print(f"    -> Unexpected query #{current_query_num} in session 3")
                        query_mock = Mock()
                        filter_mock = Mock()
                        query_mock.filter.return_value = filter_mock
                        filter_mock.first.return_value = None
                        return query_mock

                else:
                    # Any other session - return safe defaults
                    print(f"    -> Safe default for GCC query in session {current_session_num}")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

            elif query_args[0] is Lesson:
                print(f"    -> Processing Lesson query")
                print(f"    ==> Session: {session_call_count}, Query: {query_count}")
                query_mock = Mock()
                join_mock = Mock()
                filter1_mock = Mock()
                filter2_mock = Mock()

                query_mock.join.return_value = join_mock
                join_mock.filter.return_value = filter1_mock
                filter1_mock.filter.return_value = filter2_mock

                # Different behavior based on session
                if session_call_count == 3:
                    # Session 3: getting lessons list
                    filter2_mock.all.return_value = []  # Default empty
                elif session_call_count >= 4:
                    # Session 4+: processing individual lessons
                    filter2_mock.all.return_value = []  # Will be overridden in specific tests
                else:
                    filter2_mock.all.return_value = []

                return query_mock

            else:
                print(f"    -> Processing other query type")
                # Safe default for any other query type
                query_mock = Mock()
                filter_mock = Mock()
                query_mock.filter.return_value = filter_mock
                query_mock.all.return_value = []
                query_mock.first.return_value = None
                query_mock.with_for_update.return_value = query_mock
                return query_mock

        mock_session.query.side_effect = query_side_effect
        return mock_session

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = session_mock

        print("Calling switch_calendar_for_user...")
        try:
            result = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, source_calendar_id, target_calendar_id
            )
            print(f"\n{'='*60}")
            print(f"FINAL RESULT: {result}")
            print(f"{'='*60}")

            print(f"\nTotal session mock calls: {session_call_count}")
            print(f"Session details:")
            for i, session in enumerate(session_details):
                print(f"  Session #{session['call_number']} had {len(session['queries'])} queries:")
                for j, query in enumerate(session['queries']):
                    print(f"    Query #{query['query_number']}: {query['type']}")

        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_call_tracking()