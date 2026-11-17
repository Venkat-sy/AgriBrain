# AgriBrain Authentication & Rate Limiting Architecture Specification

**Version:** 1.0  
**Project:** AgriBrain AI Digital Twin API  
**Current State:** No auth, open CORS `[*]`, hardcoded session_id `agribrain_chat`, no rate limiting  
**Target:** Production-ready authentication & rate limiting

---

## 1. JWT Token Structure

### 1.1 Access Token

| Field | Value | Description |
|-------|-------|-------------|
| **Algorithm** | RS256 | Asymmetric signing (private key signs, public key verifies) |
| **Key Size** | 2048-bit RSA | Minimum for RS256 |
| **Expiry** | 15 minutes (900 seconds) | Short-lived for security |
| **Issuer (`iss`)** | `agribrain-api` | Identifies token issuer |
| **Audience (`aud`)** | `agribrain-clients` | Identifies intended recipients |

#### Access Token Claims

```json
{
  "iss": "agribrain-api",
  "aud": "agribrain-clients",
  "iat": 1700000000,
  "exp": 1700000900,
  "sub": "usr_abc123",
  "jti": "acc_tok_xyz789",
  "typ": "access",
  "role": "farmer",
  "permissions": ["simulation:read", "simulation:write", "chat:read", "chat:write"],
  "session_id": "sess_uuid_v4"
}
```

| Claim | Type | Required | Description |
|-------|------|----------|-------------|
| `iss` | string | Yes | Token issuer |
| `aud` | string | Yes | Intended audience |
| `iat` | integer | Yes | Issued at (Unix timestamp) |
| `exp` | integer | Yes | Expiration (Unix timestamp) |
| `sub` | string | Yes | User ID (UUID) |
| `jti` | string | Yes | JWT ID (unique per token) |
| `typ` | string | Yes | Token type: `"access"` |
| `role` | string | Yes | User role: `farmer`, `agronomist`, `admin` |
| `permissions` | array | Yes | Scoped permissions list |
| `session_id` | string | Yes | Active session UUID |

### 1.2 Refresh Token

| Field | Value | Description |
|-------|-------|-------------|
| **Algorithm** | RS256 | Same as access token |
| **Expiry** | 30 days (2,592,000 seconds) | Long-lived, rotated on use |
| **Storage** | HttpOnly Secure cookie + Redis | Never in localStorage |

#### Refresh Token Claims

```json
{
  "iss": "agribrain-api",
  "aud": "agribrain-clients",
  "iat": 1700000000,
  "exp": 1702592000,
  "sub": "usr_abc123",
  "jti": "ref_tok_abc123",
  "typ": "refresh",
  "session_id": "sess_uuid_v4",
  "device_id": "dev_xyz789",
  "token_family": "fam_abc123"
}
```

| Claim | Type | Required | Description |
|-------|------|----------|-------------|
| `typ` | string | Yes | Token type: `"refresh"` |
| `session_id` | string | Yes | Links to active session |
| `device_id` | string | Yes | Client device fingerprint |
| `token_family` | string | Yes | Rotation family ID (detects replay) |

### 1.3 Key Management

```
keys/
├── private_key.pem      # RS256 private key (server only, never committed)
├── public_key.pem       # RS256 public key (distributed to clients)
└── jwks.json            # JWKS endpoint for key rotation
```

- **Rotation**: Every 90 days via JWKS endpoint
- **Algorithm**: RS256 (not HS256) — enables key rotation without invalidating all tokens
- **JWKS Endpoint**: `GET /.well-known/jwks.json`

---

## 2. User Model Extensions

### 2.1 Extended User Model (`backend/models/__init__.py`)

```python
class User(Base):
    """Extended User model with authentication fields."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)  # bcrypt
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default="farmer", nullable=False)  # farmer, agronomist, admin
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
```

### 2.2 Session Model

```python
class UserSession(Base):
    """Server-side session tracking."""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, nullable=False, index=True)  # UUID v4
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    device_id = Column(String(64), nullable=False)  # Client fingerprint
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="sessions")
```

### 2.3 Refresh Token Model (Rotation Tracking)

```python
class RefreshToken(Base):
    """Refresh token family tracking for rotation & replay detection."""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("user_sessions.session_id"), nullable=False)
    token_family = Column(String(36), nullable=False, index=True)  # Rotation family
    device_id = Column(String(64), nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked_at = Column(DateTime, nullable=True)
    replaced_by = Column(String(64), nullable=True)  # Hash of new token

    user = relationship("User", back_populates="refresh_tokens")
```

### 2.4 Password Hashing

- **Algorithm**: bcrypt (via `passlib[bcrypt]`)
- **Cost Factor**: 12 (adjustable via config)
- **Salt**: Auto-generated per hash

---

## 3. Login/Register Endpoints

### 3.1 Schemas (`backend/schemas/auth.py`)

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field("farmer", pattern="^(farmer|agronomist)$")

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    device_id: str = Field(..., min_length=1, max_length=64)
    remember_me: bool = False  # Extends refresh token to 30 days vs 7 days

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str  # Only in body for first login; subsequent via cookie
    token_type: str = "bearer"
    expires_in: int  # Access token TTL in seconds
    user: "UserResponse"

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RefreshRequest(BaseModel):
    refresh_token: Optional[str] = None  # From cookie if not in body

class LogoutRequest(BaseModel):
    revoke_all_sessions: bool = False
```

### 3.2 Endpoints (`backend/api/auth.py`)

| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| POST | `/api/v1/auth/register` | Register new user | 5/min/IP |
| POST | `/api/v1/auth/login` | Login, issue tokens | 10/min/IP |
| POST | `/api/v1/auth/refresh` | Rotate refresh token, issue new access | 30/min/user |
| POST | `/api/v1/auth/logout` | Revoke session/token family | 20/min/user |
| POST | `/api/v1/auth/logout-all` | Revoke all user sessions | 5/min/user |
| GET | `/api/v1/auth/me` | Get current user profile | 60/min/user |
| POST | `/api/v1/auth/forgot-password` | Request password reset email | 3/hour/IP |
| POST | `/api/v1/auth/reset-password` | Reset password with token | 5/hour/IP |
| GET | `/.well-known/jwks.json` | Public key set for token verification | 100/min/IP |

### 3.3 Validation Rules

**Password Policy:**
- Minimum 8 characters
- At least 1 uppercase, 1 lowercase, 1 digit, 1 special char (`!@#$%^&*`)
- Reject common passwords (check against `haveibeenpwned` top 10k)
- bcrypt cost: 12

**Email:**
- Valid RFC 5322 format
- Domain MX record check (optional, configurable)
- Normalize to lowercase

**Device ID:**
- Client-generated UUID v4 (stored in localStorage/IndexedDB)
- Sent with every auth request
- Used for session binding & anomaly detection

---

## 4. Auth Middleware (FastAPI Dependency Injection)

### 4.1 Core Dependencies (`backend/core/auth.py`)

```python
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from backend.core.config import settings
from backend.core.database import get_db
from backend.models import User, UserSession
from backend.services.token_service import TokenService
from typing import Optional

security = HTTPBearer(auto_error=False)
token_service = TokenService()

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Validate access token and return current user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = token_service.verify_access_token(credentials.credentials)
        user_id = payload.get("sub")
        session_id = payload.get("session_id")
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    # Validate session exists and not revoked
    session = db.query(UserSession).filter(
        UserSession.session_id == session_id,
        UserSession.user_id == user_id,
        UserSession.is_revoked == False,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    if not session:
        raise HTTPException(status_code=401, detail="Session expired or revoked")
    
    # Update last activity
    session.last_activity = datetime.utcnow()
    db.commit()
    
    return user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Optional auth - returns user if valid token, None otherwise."""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

def require_role(*allowed_roles: str):
    """Dependency factory for role-based access control."""
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker

def require_permission(*permissions: str):
    """Dependency factory for permission-based access control."""
    async def permission_checker(user: User = Depends(get_current_user)) -> User:
        user_perms = get_role_permissions(user.role)
        if not all(p in user_perms for p in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required permissions: {', '.join(permissions)}"
            )
        return user
    return permission_checker
```

### 4.2 Role & Permission Matrix

| Role | Permissions |
|------|-------------|
| `farmer` | `simulation:read`, `simulation:write`, `chat:read`, `chat:write`, `spatial:read`, `profile:read`, `profile:write` |
| `agronomist` | All farmer + `simulation:admin`, `crop:read`, `crop:write`, `district:read` |
| `admin` | All permissions + `user:read`, `user:write`, `user:delete`, `system:config` |

### 4.3 Usage in Routers

```python
# Public endpoints - no auth
router.post("/simulation/run", ...)

# Protected - any authenticated user
router.post("/chat", dependencies=[Depends(get_current_user)])

# Role-protected
router.get("/admin/users", dependencies=[Depends(require_role("admin"))])

# Permission-protected
router.delete("/crops/{id}", dependencies=[Depends(require_permission("crop:write"))])
```

---

## 5. CORS Policy for Production

### 5.1 Configuration (`backend/core/config.py` additions)

```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    # CORS - Production Configuration
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "https://agribrain.app",
            "https://www.agribrain.app",
            "https://app.agribrain.app",
            "http://localhost:3000",  # Dev only
            "http://localhost:5173",  # Vite dev
        ],
        description="Allowed CORS origins (no wildcards in production)"
    )
    ALLOWED_ORIGINS_REGEX: Optional[str] = Field(
        default=r"^https://(.+\.)?agribrain\.app$",
        description="Regex for dynamic subdomains"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = [
        "Authorization",
        "Content-Type",
        "X-Device-ID",
        "X-Request-ID",
        "Accept",
        "Origin",
    ]
    CORS_EXPOSE_HEADERS: List[str] = ["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
    CORS_MAX_AGE: int = 86400  # 24 hours preflight cache
```

### 5.2 Middleware Setup (`backend/main.py`)

```python
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=settings.ALLOWED_ORIGINS_REGEX,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=settings.CORS_EXPOSE_HEADERS,
    max_age=settings.CORS_MAX_AGE,
)
```

### 5.3 Production Rules

| Rule | Value |
|------|-------|
| No wildcard origins | `allow_origins=["*"]` forbidden in prod |
| Credentials required | `allow_credentials=True` for cookies |
| Preflight caching | 24 hours (`max_age=86400`) |
| Origin validation | Exact match + regex for subdomains |
| Vary header | Automatic via Starlette |

---

## 6. Rate Limiting Strategy

### 6.1 Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│   Client    │────▶│  Rate Limit      │────▶│   Redis     │
│  Request    │     │  Middleware      │     │  (Upstash)  │
└─────────────┘     └──────────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────────┐
                    │  Key Builder     │
                    │  (tier + scope)  │
                    └──────────────────┘
```

### 6.2 Rate Limit Tiers

| Tier | Scope | Limit | Window | Key Prefix | Use Case |
|------|-------|-------|--------|------------|----------|
| **Auth Strict** | IP | 5 | 1 min | `rl:auth:ip:{ip}` | Register, login, password reset |
| **Auth User** | User ID | 10 | 1 min | `rl:auth:user:{uid}` | Refresh, logout |
| **API Standard** | User ID | 60 | 1 min | `rl:api:user:{uid}` | Simulation, chat, spatial |
| **API Burst** | User ID | 20 | 10 sec | `rl:burst:user:{uid}` | Burst protection |
| **Anonymous** | IP | 20 | 1 min | `rl:anon:ip:{ip}` | Unauthenticated endpoints |
| **Admin** | User ID | 300 | 1 min | `rl:admin:user:{uid}` | Admin panel |
| **WebSocket** | User ID | 50 | 1 min | `rl:ws:user:{uid}` | Chat connections |

### 6.3 Key Prefix Convention

```
rl:{tier}:{scope}:{identifier}
```

Examples:
- `rl:auth:ip:192.168.1.100`
- `rl:api:user:123`
- `rl:burst:user:123`
- `rl:anon:ip:203.0.113.45`

### 6.4 Implementation (`backend/core/rate_limit.py`)

```python
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.redis_client import get_redis_client
from backend.core.config import settings
import time
import hashlib

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window rate limiter with Redis backend."""
    
    TIER_CONFIG = {
        "/api/v1/auth/register": ("auth", "ip", 5, 60),
        "/api/v1/auth/login": ("auth", "ip", 10, 60),
        "/api/v1/auth/forgot-password": ("auth", "ip", 3, 3600),
        "/api/v1/auth/reset-password": ("auth", "ip", 5, 3600),
        "/api/v1/auth/refresh": ("auth", "user", 30, 60),
        "/api/v1/auth/logout": ("auth", "user", 20, 60),
        "/api/v1/auth/logout-all": ("auth", "user", 5, 60),
    }
    
    DEFAULT_TIER = ("api", "user", 60, 60)
    ANON_TIER = ("anon", "ip", 20, 60)
    
    async def dispatch(self, request: Request, call_next):
        # Skip for health checks, static, JWKS
        if request.url.path in ["/", "/health", "/.well-known/jwks.json"]:
            return await call_next(request)
        
        # Determine tier
        tier_name, scope, limit, window = self._get_tier(request)
        
        # Build identifier
        identifier = self._get_identifier(request, scope)
        key = f"rl:{tier_name}:{scope}:{identifier}"
        
        # Check rate limit
        allowed, remaining, reset = await self._check_limit(key, limit, window)
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(reset - int(time.time())),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset),
                }
            )
        
        return response
    
    def _get_tier(self, request: Request) -> tuple:
        path = request.url.path
        method = request.method
        
        # Exact path match
        if path in self.TIER_CONFIG:
            return self.TIER_CONFIG[path]
        
        # Pattern match for API routes
        if path.startswith("/api/v1/"):
            # Check for user auth
            if hasattr(request.state, "user_id") and request.state.user_id:
                return self.DEFAULT_TIER
            return self.ANON_TIER
        
        return self.ANON_TIER
    
    def _get_identifier(self, request: Request, scope: str) -> str:
        if scope == "ip":
            # Handle proxy headers
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                ip = forwarded.split(",")[0].strip()
            else:
                ip = request.client.host if request.client else "unknown"
            return hashlib.sha256(ip.encode()).hexdigest()[:16]
        
        elif scope == "user":
            return str(getattr(request.state, "user_id", "anonymous"))
        
        return "unknown"
    
    async def _check_limit(self, key: str, limit: int, window: int) -> tuple:
        """Sliding window algorithm using Redis sorted sets."""
        redis = get_redis_client()
        now = time.time()
        window_start = now - window
        
        # Remove expired entries
        redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current = redis.zcard(key)
        
        if current >= limit:
            # Get oldest entry for reset time
            oldest = redis.zrange(key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1]) + window if oldest else int(now) + window
            return False, 0, reset_time
        
        # Add current request
        redis.zadd(key, {f"{now}:{uuid.uuid4().hex[:8]}": now})
        redis.expire(key, window + 1)
        
        return True, limit - current - 1, int(now) + window
```

### 6.5 Redis Key TTL Management

| Key Pattern | TTL | Cleanup |
|-------------|-----|---------|
| `rl:*:*:*` | window + 60s | Auto-expire |
| `session:*` | 24h (configurable) | Auto-expire |
| `refresh_token:*` | 30d | Manual on revoke |
| `auth:lockout:{ip}` | 15 min | Auto-expire |

---

## 7. Session Management

### 7.1 Session Lifecycle

```
┌─────────────┐     Login      ┌─────────────┐     Activity      ┌─────────────┐
│  Anonymous  │───────────────▶│   Active    │──────────────────▶│   Active    │
│  (no sess)  │                │  (24h TTL)  │  (refreshes TTL)  │  (extended) │
└─────────────┘                └─────────────┘                   └─────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌──────────┐    ┌────────────┐   ┌────────────┐
              │ Logout   │    │  Expired   │   │  Revoked   │
              │ (revoke) │    │  (24h idle)│   │ (security) │
              └──────────┘    └────────────┘   └────────────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     ▼
                            ┌─────────────┐
                            │  Deleted    │
                            │  (cleanup)  │
                            └─────────────┘
```

### 7.2 Session ID Generation

```python
import uuid
import secrets

def generate_session_id() -> str:
    """Generate cryptographically secure session ID."""
    return str(uuid.uuid4())

def generate_device_id() -> str:
    """Generate or validate client device ID."""
    # Client should generate UUID v4 and persist in localStorage
    # Server validates format
    return str(uuid.uuid4())
```

### 7.3 Storage (Redis + Database)

**Redis (Hot Data - Fast Access):**
```
Key: session:{session_id}
Value: JSON {
    "user_id": 123,
    "device_id": "dev_abc",
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "created_at": "2026-11-16T10:00:00Z",
    "last_activity": "2026-11-16T10:30:00Z",
    "is_revoked": false
}
TTL: 86400 (24 hours, sliding on activity)
```

**Database (Persistent - Audit Trail):**
- `UserSession` table (see Section 2.2)
- Used for: admin views, security audit, compliance

### 7.4 Session Service (`backend/services/session_service.py`)

```python
from backend.core.redis_client import get_redis_client
from backend.core.config import settings
from backend.models import UserSession
from sqlalchemy.orm import Session
import json
from datetime import datetime, timedelta

SESSION_TTL = 86400  # 24 hours
EXTENDED_TTL = 604800  # 7 days for "remember me"

class SessionService:
    def __init__(self):
        self.redis = get_redis_client()
    
    def create_session(
        self, 
        db: Session, 
        user_id: int, 
        device_id: str, 
        ip: str, 
        user_agent: str,
        remember_me: bool = False
    ) -> UserSession:
        session_id = generate_session_id()
        ttl = EXTENDED_TTL if remember_me else SESSION_TTL
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        # DB record
        session = UserSession(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            ip_address=ip,
            user_agent=user_agent,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        
        # Redis cache
        self._cache_session(session_id, {
            "user_id": user_id,
            "device_id": device_id,
            "ip": ip,
            "user_agent": user_agent,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "is_revoked": False
        }, ttl)
        
        return session
    
    def _cache_session(self, session_id: str, data: dict, ttl: int):
        key = f"session:{session_id}"
        self.redis.setex(key, ttl, json.dumps(data))
    
    def get_session(self, session_id: str) -> Optional[dict]:
        key = f"session:{session_id}"
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    def update_activity(self, session_id: str, ttl: int = None) -> bool:
        """Sliding expiration on activity."""
        key = f"session:{session_id}"
        data = self.redis.get(key)
        if not data:
            return False
        
        session_data = json.loads(data)
        session_data["last_activity"] = datetime.utcnow().isoformat()
        ttl = ttl or SESSION_TTL
        self.redis.setex(key, ttl, json.dumps(session_data))
        return True
    
    def revoke_session(self, session_id: str, db: Session = None) -> bool:
        # Redis
        self.redis.delete(f"session:{session_id}")
        
        # DB
        if db:
            session = db.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            if session:
                session.is_revoked = True
                db.commit()
        return True
    
    def revoke_all_user_sessions(self, user_id: int, db: Session, exclude_session: str = None):
        query = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_revoked == False
        )
        if exclude_session:
            query = query.filter(UserSession.session_id != exclude_session)
        
        sessions = query.all()
        for session in sessions:
            session.is_revoked = True
            self.redis.delete(f"session:{session.session_id}")
        db.commit()
        return len(sessions)
    
    def cleanup_expired_sessions(self, db: Session) -> int:
        """Periodic cleanup job - run via cron."""
        expired = db.query(UserSession).filter(
            UserSession.expires_at < datetime.utcnow(),
            UserSession.is_revoked == False
        ).all()
        
        count = 0
        for session in expired:
            session.is_revoked = True
            self.redis.delete(f"session:{session.session_id}")
            count += 1
        
        db.commit()
        return count
```

### 7.5 Cleanup Strategy

| Method | Schedule | Scope |
|--------|----------|-------|
| Redis TTL | Automatic | Expired keys auto-evicted |
| DB Cleanup | Daily cron (03:00 UTC) | Sessions past `expires_at` |
| Revoked Cleanup | Weekly | Hard delete revoked > 30 days |
| Orphan Cleanup | Weekly | Sessions without valid user |

---

## 8. Migration Plan: Hardcoded `session_id` → Authenticated Sessions

### 8.1 Current State Analysis

**Problematic Code Locations:**
1. `backend/api/chat.py` - In-memory `chat_sessions` dict + `get_or_create_session()`
2. `backend/core/redis_client.py` - `chat_session:{session_id}` keys
3. Frontend - Sends hardcoded `session_id: "agribrain_chat"`

### 8.2 Migration Phases

#### Phase 1: Backward Compatibility (Week 1)
**Goal**: Support both old and new session handling

```python
# backend/api/chat.py - Updated get_or_create_session
def get_or_create_session(session_id: str = None, user_id: int = None) -> str:
    # New: authenticated session
    if user_id and session_id:
        # Validate session belongs to user
        session = session_service.get_session(session_id)
        if session and session.get("user_id") == user_id:
            session_service.update_activity(session_id)
            return session_id
    
    # Legacy: anonymous session_id from client
    if session_id and session_id != "agribrain_chat":
        # Migrate legacy session to new format
        session_service.create_anonymous_session(session_id)
        return session_id
    
    # New anonymous session
    new_session_id = generate_session_id()
    session_service.create_anonymous_session(new_session_id)
    return new_session_id
```

**Changes:**
- Add `user_id` parameter to chat endpoints (optional)
- Accept `Authorization` header for authenticated users
- Keep `session_id` in request body for backward compatibility
- Map legacy `agribrain_chat` → new anonymous session

#### Phase 2: Frontend Migration (Week 2)
**Goal**: Update frontend to use auth tokens

```javascript
// Frontend auth service
class AuthService {
  async login(email, password) {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password, device_id: getDeviceId() }),
      credentials: 'include'  // For refresh cookie
    });
    const { access_token, user } = await res.json();
    localStorage.setItem('access_token', access_token);
    return user;
  }
  
  getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
  
  async chat(message, context) {
    return fetch('/api/v1/chat/troubleshoot', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.getAuthHeaders(),
        'X-Device-ID': getDeviceId()
      },
      body: JSON.stringify({ message, context })
    });
  }
}
```

#### Phase 3: Deprecate Legacy (Week 3)
**Goal**: Remove hardcoded session handling

**Removals:**
- `chat_sessions` in-memory dict in `chat.py`
- `get_or_create_session()` legacy logic
- `agribrain_chat` special case
- Anonymous session fallback for authenticated endpoints

**Additions:**
- Require `Authorization` header for all `/api/v1/chat/*` endpoints
- Return `401` for missing/invalid tokens
- Session ID now comes from JWT `session_id` claim

### 8.3 Database Migration (Alembic)

```bash
# Generate migration
alembic revision --autogenerate -m "Add auth tables: users, sessions, refresh_tokens"

# Migration file: backend/alembic/versions/xxx_add_auth_tables.py
```

```python
# Alembic migration
def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(100), nullable=True),
        sa.Column("role", sa.String(20), default="farmer", nullable=False),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_verified", sa.Boolean, default=False, nullable=False),
        sa.Column("last_login", sa.DateTime, nullable=True),
        sa.Column("failed_login_attempts", sa.Integer, default=0, nullable=False),
        sa.Column("locked_until", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column("updated_at", sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    )
    
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("session_id", sa.String(36), unique=True, nullable=False, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("device_id", sa.String(64), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column("last_activity", sa.DateTime, default=datetime.utcnow, nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime, nullable=False, index=True),
        sa.Column("is_revoked", sa.Boolean, default=False, nullable=False),
    )
    
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("user_sessions.session_id"), nullable=False),
        sa.Column("token_family", sa.String(36), nullable=False, index=True),
        sa.Column("device_id", sa.String(64), nullable=False),
        sa.Column("issued_at", sa.DateTime, default=datetime.utcnow, nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=False, index=True),
        sa.Column("revoked_at", sa.DateTime, nullable=True),
        sa.Column("replaced_by", sa.String(64), nullable=True),
    )
    
    # Index for cleanup queries
    op.create_index("ix_user_sessions_user_expires", "user_sessions", ["user_id", "expires_at"])
    op.create_index("ix_refresh_tokens_family", "refresh_tokens", ["token_family"])

def downgrade():
    op.drop_table("refresh_tokens")
    op.drop_table("user_sessions")
    op.drop_table("users")
```

### 8.4 Environment Variables (`.env.production`)

```env
# JWT Keys (generate with: openssl genrsa -out private_key.pem 2048)
JWT_PRIVATE_KEY_PATH=/app/keys/private_key.pem
JWT_PUBLIC_KEY_PATH=/app/keys/public_key.pem
JWT_ALGORITHM=RS256
JWT_ACCESS_TTL=900
JWT_REFRESH_TTL=2592000
JWT_ISSUER=agribrain-api
JWT_AUDIENCE=agribrain-clients

# Password Hashing
BCRYPT_ROUNDS=12

# CORS
ALLOWED_ORIGINS=["https://agribrain.app","https://www.agribrain.app"]
ALLOWED_ORIGINS_REGEX="^https://(.+\.)?agribrain\.app$"

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REDIS_URL=${UPSTASH_REDIS_REST_URL}
RATE_LIMIT_REDIS_TOKEN=${UPSTASH_REDIS_REST_TOKEN}

# Session
SESSION_TTL=86400
SESSION_EXTENDED_TTL=604800
SESSION_CLEANUP_CRON="0 3 * * *"

# Security
SECURE_COOKIES=true
COOKIE_DOMAIN=.agribrain.app
```

### 8.5 Rollout Checklist

| Step | Description | Verification |
|------|-------------|--------------|
| 1 | Generate RSA key pair | `openssl rsa -in private_key.pem -pubout -out public_key.pem` |
| 2 | Add auth tables via Alembic | `alembic upgrade head` |
| 3 | Deploy auth endpoints | Test register/login/refresh |
| 4 | Add rate limit middleware | Verify headers on responses |
| 5 | Update CORS config | Test from production domain |
| 6 | Deploy session service | Verify Redis + DB sync |
| 7 | Frontend auth integration | E2E login → chat flow |
| 8 | Enable auth on chat endpoints | Verify 401 without token |
| 9 | Deprecate legacy session code | Remove `chat_sessions` dict |
| 10 | Load test | 1000 concurrent users |
| 11 | Security audit | Penetration test auth flows |
| 12 | Monitor | Dashboards for 401/429 rates |

### 8.6 Rollback Plan

If critical issues arise:
1. **Feature flag**: `AUTH_ENABLED=false` bypasses all auth middleware
2. **Database**: `alembic downgrade -1` removes auth tables
3. **Frontend**: Revert to hardcoded `session_id` in single commit
4. **Redis**: Flush `session:*` and `rl:*` keys

---

## Appendix: File Structure Summary

```
backend/
├── core/
│   ├── auth.py              # Auth dependencies, token service
│   ├── config.py            # Settings with CORS, JWT, rate limit config
│   ├── rate_limit.py        # Rate limiting middleware
│   ├── redis_client.py      # Redis session/rate limit client
│   └── security.py          # Password hashing, token utilities
├── models/
│   └── __init__.py          # User, UserSession, RefreshToken models
├── schemas/
│   └── auth.py              # Pydantic schemas for auth endpoints
├── services/
│   ├── token_service.py     # JWT create/verify/refresh
│   ├── session_service.py   # Session CRUD, cleanup
│   └── auth_service.py      # Login, register, password reset logic
├── api/
│   └── auth.py              # Auth endpoints (register, login, refresh, logout)
├── main.py                  # Updated with CORS, rate limit, auth middleware
└── alembic/
    └── versions/
        └── xxx_add_auth_tables.py
```

---

## Appendix: Dependencies to Add

```txt
# requirements.txt additions
python-jose[cryptography]==3.3.0      # JWT handling
passlib[bcrypt]==1.7.4                # Password hashing
slowapi==0.1.9                        # Alternative rate limiter (optional)
python-multipart==0.0.6               # Already present for forms
```

---

**End of Specification**  
*Generated for AgriBrain AI Digital Twin API v3.0+*