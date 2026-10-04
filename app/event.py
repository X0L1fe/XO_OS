from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any

# We'll use a simple in-memory dictionary to track active connections
# In a production app, you would use a proper message queue like Redis Pub/Sub
active_connections: dict[int, list[asyncio.Queue]] = {}


async def event_publisher(user_id: int) -> AsyncGenerator[str, None]:
    """
    Publish events for a specific user.
    """
    # Create a queue for this connection
    queue: asyncio.Queue = asyncio.Queue()

    # Add the queue to the user's connections
    if user_id not in active_connections:
        active_connections[user_id] = []
    active_connections[user_id].append(queue)

    try:
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'user_id': user_id})}\n\n"

        # Wait for events to be published
        while True:
            # Wait for an event with a timeout for heartbeat
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(event)}\n\n"
                queue.task_done()
            except asyncio.TimeoutError:
                # Send heartbeat
                yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now(timezone.utc).isoformat()})}\n\n"
    finally:
        # Remove the queue when the connection closes
        if user_id in active_connections:
            if queue in active_connections[user_id]:
                active_connections[user_id].remove(queue)
            if not active_connections[user_id]:
                del active_connections[user_id]


def publish_focus_updated(user_id: int):
    """
    Publish a focus session updated event to all connections for a user.
    """
    if user_id in active_connections:
        event = {
            "type": "xo-os:focus-updated",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        # Put the event in all queues for this user
        for queue in active_connections[user_id]:
            # Use put_nowait to avoid blocking, and handle queue full errors
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # If queue is full, we just skip this event
                pass


def publish_gamification_updated(user_id: int):
    """
    Publish a gamification updated event to all connections for a user.
    """
    if user_id in active_connections:
        event = {
            "type": "xo-os:gamification-updated",
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        # Put the event in all queues for this user
        for queue in active_connections[user_id]:
            # Use put_nowait to avoid blocking, and handle queue full errors
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                # If queue is full, we just skip this event
                pass
