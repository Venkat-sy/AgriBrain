"""
Rate limiting middleware for AgriBrain.
Uses Upstash Redis for distributed rate limiting with fallback to in-memory.
"""
import time
import asyncio
from typing import Optional
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from backend.core.config import get_settings

settings = get_settings()


class RateLimiter:
    """Rate limiter with Redis backend and in-memory fallback."""
    
    def __init__(self):
        self.settings = get_settings()
        self._local_cache = {}
        self._lock = asyncio.Lock()
        self._redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis client if configured."""
        if self.settings.UPSTASH_REDIS_REST_URL and self.settings.UPSTASH_REDIS_REST_TOKEN:
            try:
                import httpx
                self._redis_client = httpx.AsyncClient(
                    base_url=self.settings.UPSTASH_REDIS_REST_URL,
                    headers={"Authorization": f"Bearer {self.settings.UPSTASH_REDIS_REST_TOKEN}"},
                    timeout=5.0
                )
            except Exception:
                self._redis_client = None
    
    async def _get_redis(self, key: str) -> Optional[int]:
        """Get value from Redis."""
        if not self._redis_client:
            return None
        try:
            response = await self._redis_client.get(f"/get/{key}")
            if response.status_code == 200:
                data = response.json()
                if data.get("result"):
                    return int(data["result"])
        except Exception:
            pass
        return None
    
    async def _set_redis(self, key: str, value: int, expire: int) -> bool:
        """Set value in Redis with expiration."""
        if not self._redis_client:
            return False
        try:
            response = await self._redis_client.post(
                f"/set/{key}/{value}",
                params={"EX": expire}
            )
            return response.status_code == 200
        except Exception:
            return False
    
    async def _increment_redis(self, key: str, expire: int) -> Optional[int]:
        """Increment counter in Redis."""
        if not self._redis_client:
            return None
        try:
            response = await self._redis_client.post(
                f"/incr/{key}",
                params={"EX": expire}
            )
            if response.status_code == 200:
                data = response.json()
                return int(data.get("result", 0))
        except Exception:
            pass
        return None
    
    async def check_rate_limit(
        self,
        identifier: str,
        limit: int,
        window_seconds: int = 60,
        endpoint: str = "default"
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit.
        Returns (allowed, headers_dict).
        """
        if not self.settings.RATE_LIMIT_ENABLED:
            return True, {}
        
        key = f"ratelimit:{endpoint}:{identifier}"
        current_time = int(time.time())
        window_start = current_time - window_seconds
        
        # Try Redis first
        if self._redis_client:
            try:
                count = await self._increment_redis(key, window_seconds)
                if count is not None:
                    remaining = max(0, limit - count)
                    reset_time = current_time + window_seconds
                    allowed = count <= limit
                    headers = {
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": str(remaining),
                        "X-RateLimit-Reset": str(reset_time),
                    }
                    return allowed, headers
            except Exception:
                pass  # Fall back to local
        
        # In-memory fallback
        async with self._lock:
            if key not in self._local_cache:
                self._local_cache[key] = {"count": 0, "window_start": current_time}
            
            entry = self._local_cache[key]
            
            # Reset window if expired
            if current_time - entry["window_start"] >= window_seconds:
                entry["count"] = 0
                entry["window_start"] = current_time
            
            entry["count"] += 1
            remaining = max(0, limit - entry["count"])
            reset_time = entry["window_start"] + window_seconds
            allowed = entry["count"] <= limit
            
            # Cleanup old entries periodically
            if len(self._local_cache) > 10000:
                self._cleanup_cache(current_time)
            
            headers = {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
            }
            return allowed, headers
    
    def _cleanup_cache(self, current_time: int):
        """Remove expired entries from local cache."""
        expired_keys = [
            k for k, v in self._local_cache.items()
            if current_time - v["window_start"] >= 300  # 5 minutes
        ]
        for k in expired_keys:
            del self._local_cache[k]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    def __init__(self, app, rate_limiter: RateLimiter = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.settings = get_settings()
        
        # Endpoint-specific limits (requests per minute)
        self.endpoint_limits = {
            "/api/v1/auth/login": 10,
            "/api/v1/auth/register": 5,
            "/api/v1/auth/refresh": 20,
            "/api/v1/simulation/run": 30,
            "/api/v1/chat/troubleshoot": 20,
            "/api/v1/chat/troubleshoot-vision": 10,
            "/api/v1/crop/recommend": 30,
            "/api/v1/spatial/lookup": 30,
            "/api/v1/spatial/autocomplete": 30,
        }
        self.default_limit = self.settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        self.burst_limit = self.settings.RATE_LIMIT_BURST
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/", "/health"]:
            return await call_next(request)
        
        # Get client identifier (IP + user if authenticated)
        client_ip = request.client.host if request.client else "unknown"
        identifier = client_ip
        
        # Try to get user ID from auth header for per-user limits
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            try:
                from backend.api.auth import decode_token
                token = auth_header.split(" ")[1]
                payload = decode_token(token)
                if payload and payload.get("type") == "access":
                    identifier = f"user:{payload.get('sub', client_ip)}"
            except Exception:
                pass
        
        # Determine limit for this endpoint
        endpoint = request.url.path
        limit = self.endpoint_limits.get(endpoint, self.default_limit)
        
        # Apply burst allowance for authenticated users
        if identifier.startswith("user:"):
            limit += self.burst_limit
        
        # Check rate limit
        allowed, headers = await self.rate_limiter.check_rate_limit(
            identifier=identifier,
            limit=limit,
            window_seconds=60,
            endpoint=endpoint
        )
        
        if not allowed:
            return Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers=headers
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        for key, value in headers.items():
            response.headers[key] = value
        
        return response


# Global rate limiter instance
rate_limiter = RateLimiter()