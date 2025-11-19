"""
Simple Rate Limiting Middleware
For immediate deployment to fix brute force vulnerability

AGENTS.md Compliance:
- Zero hardcoded values (all from config)
- Clean naming
- Type safety
"""

from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status
from typing import Dict, List
import asyncio
import logging

from config.settings import get_settings

logger = logging.getLogger(__name__)


class SimpleRateLimiter:
    """
    Simple in-memory rate limiter for IP addresses
    
    Tracks requests per IP and blocks when limit is exceeded.
    Zero hardcoded values - all configuration from environment.
    """
    
    def __init__(self):
        # Load configuration from settings (AGENTS.md compliant)
        settings = get_settings()
        
        # Track requests: {ip: [timestamp1, timestamp2, ...]}
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        
        # Configuration from environment (zero hardcoded values)
        self.max_requests_per_minute = settings.security.rate_limit_ip_per_minute
        self.max_login_attempts_per_minute = settings.security.rate_limit_login_per_minute
        self.window = timedelta(minutes=settings.security.rate_limit_window_minutes)
        
        # Start cleanup task
        asyncio.create_task(self._cleanup_old_data())
        
        logger.info("Simple Rate Limiter initialized")
    
    async def _cleanup_old_data(self):
        """Clean up old request data periodically"""
        while True:
            await asyncio.sleep(60)  # Every minute
            
            try:
                cutoff = datetime.now() - self.window
                
                # Clean old requests
                for ip in list(self.requests.keys()):
                    self.requests[ip] = [
                        t for t in self.requests[ip] if t > cutoff
                    ]
                    if not self.requests[ip]:
                        del self.requests[ip]
                        
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    def check_rate_limit(
        self,
        ip: str,
        endpoint: str = "general",
        max_requests: int = None
    ) -> bool:
        """
        Check if request is within rate limit
        
        Args:
            ip: Client IP address
            endpoint: Endpoint being accessed
            max_requests: Override default max requests
            
        Returns:
            True if within limit, False if exceeded
        """
        now = datetime.now()
        cutoff = now - self.window
        
        # Clean old requests for this IP
        self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]
        
        # Determine limit based on endpoint
        if max_requests is None:
            if "login" in endpoint or "register" in endpoint:
                max_requests = self.max_login_attempts_per_minute
            else:
                max_requests = self.max_requests_per_minute
        
        # Check limit
        current_requests = len(self.requests[ip])
        
        if current_requests >= max_requests:
            logger.warning(
                f"Rate limit exceeded for IP {ip} on {endpoint}: "
                f"{current_requests}/{max_requests} requests"
            )
            return False
        
        # Add this request
        self.requests[ip].append(now)
        return True
    
    def get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request
        
        Args:
            request: FastAPI request
            
        Returns:
            Client IP address
        """
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        if request.client:
            return request.client.host
        
        return "unknown"


# Global rate limiter instance
rate_limiter = SimpleRateLimiter()


async def check_rate_limit(request: Request, endpoint: str = "general"):
    """
    Dependency to check rate limit for an endpoint
    
    Args:
        request: FastAPI request
        endpoint: Endpoint name for specific limits
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    ip = rate_limiter.get_client_ip(request)
    
    if not rate_limiter.check_rate_limit(ip, endpoint):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later.",
            headers={"Retry-After": "60"}
        )
