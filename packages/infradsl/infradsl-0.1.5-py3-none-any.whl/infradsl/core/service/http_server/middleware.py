"""
HTTP Server Middleware - Authentication, rate limiting, and CORS middleware
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Rate limiting storage
rate_limit_storage: Dict[str, List[float]] = {}

# Security dependency
security = HTTPBearer()


class MiddlewareManager:
    """Manager for HTTP middleware components"""
    
    def __init__(
        self,
        auth_enabled: bool = True,
        rate_limit_enabled: bool = True,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
    ):
        self.auth_enabled = auth_enabled
        self.rate_limit_enabled = rate_limit_enabled
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
    
    def setup_middleware(self, app: FastAPI):
        """Setup all middleware for the FastAPI app"""
        self._setup_cors_middleware(app)
        if self.rate_limit_enabled:
            self._setup_rate_limiting_middleware(app)
    
    def _setup_cors_middleware(self, app: FastAPI):
        """Setup CORS middleware"""
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure based on environment
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def _setup_rate_limiting_middleware(self, app: FastAPI):
        """Setup rate limiting middleware"""
        @app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next):
            client_ip = request.client.host if request.client else "unknown"
            now = datetime.now(timezone.utc).timestamp()

            # Clean old entries
            if client_ip in rate_limit_storage:
                rate_limit_storage[client_ip] = [
                    ts
                    for ts in rate_limit_storage[client_ip]
                    if now - ts < self.rate_limit_window
                ]

            # Check rate limit
            if client_ip not in rate_limit_storage:
                rate_limit_storage[client_ip] = []

            if (
                len(rate_limit_storage[client_ip])
                >= self.rate_limit_requests
            ):
                return HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )

            rate_limit_storage[client_ip].append(now)
            response = await call_next(request)
            return response
    
    def get_auth_dependency(self):
        """Get auth dependency based on auth_enabled setting"""
        if not self.auth_enabled:
            # Return a dependency that always returns success
            def no_auth():
                return {"authenticated": True}
            return no_auth
        else:
            # Return the actual auth verification
            return self._verify_auth_token
    
    async def _verify_auth_token(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Verify authentication token"""
        # TODO: Implement actual token verification
        # For now, accept any bearer token that matches a pattern
        if credentials.credentials == "test-token":
            return {"authenticated": True, "user": "test-user"}

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )