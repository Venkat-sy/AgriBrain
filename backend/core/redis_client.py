"""
Upstash Redis client configuration for session management.
"""
import os
from upstash_redis import Redis
from backend.core.config import settings

# Initialize Redis client from environment variables
redis_client = None

if settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN:
    redis_client = Redis(
        url=settings.UPSTASH_REDIS_REST_URL,
        token=settings.UPSTASH_REDIS_REST_TOKEN
    )


def get_redis_client() -> Redis:
    """Get the Redis client instance."""
    if redis_client is None:
        raise RuntimeError(
            "Redis client not initialized. "
            "Check UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN environment variables."
        )
    return redis_client


SESSION_TTL = 86400  # 24 hours in seconds


def get_session(session_id: str) -> list:
    """
    Fetch and JSON-decode the chat history from Redis.
    Returns an empty list if no session exists.
    """
    client = get_redis_client()
    try:
        data = client.get(f"chat_session:{session_id}")
        if data:
            import json
            return json.loads(data)
    except Exception:
        pass
    return []


def save_session(session_id: str, chat_history: list) -> bool:
    """
    JSON-encode the chat history and save it to Redis using setex
    with an 86400-second (24-hour) expiration.
    """
    client = get_redis_client()
    try:
        import json
        client.setex(
            f"chat_session:{session_id}",
            SESSION_TTL,
            json.dumps(chat_history)
        )
        return True
    except Exception:
        return False


def delete_session(session_id: str) -> bool:
    """Delete a session from Redis."""
    client = get_redis_client()
    try:
        client.delete(f"chat_session:{session_id}")
        return True
    except Exception:
        return False