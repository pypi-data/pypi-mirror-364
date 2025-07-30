"""
Rate Limiting Engine - Intelligent rate limiting with adaptive backoff strategies

This module provides comprehensive rate limiting capabilities with:
- Per-provider and per-operation rate limiting
- Adaptive backoff strategies
- Token bucket and sliding window algorithms
- Rate limit monitoring and alerting
- Dynamic rate adjustment based on system load
"""

import asyncio
import logging
import time
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Tuple
from collections import deque, defaultdict
import json

logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategy types"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"


class BackoffStrategy(Enum):
    """Backoff strategy types"""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    FIBONACCI = "fibonacci"
    ADAPTIVE = "adaptive"


class RateLimitResult(Enum):
    """Rate limit check result"""
    ALLOWED = "allowed"
    DENIED = "denied"
    THROTTLED = "throttled"


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests_per_second: float = 10.0
    burst_capacity: int = 20
    strategy: RateLimitStrategy = RateLimitStrategy.TOKEN_BUCKET
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    min_backoff: float = 0.1
    max_backoff: float = 60.0
    backoff_multiplier: float = 2.0
    enable_adaptive: bool = True
    window_size: int = 60  # seconds
    enable_circuit_breaker: bool = True
    failure_threshold: float = 0.5  # 50% failure rate
    recovery_timeout: float = 30.0


@dataclass
class RateLimitMetrics:
    """Rate limiting metrics"""
    total_requests: int = 0
    allowed_requests: int = 0
    denied_requests: int = 0
    throttled_requests: int = 0
    current_rate: float = 0.0
    peak_rate: float = 0.0
    average_backoff: float = 0.0
    total_backoff_time: float = 0.0
    circuit_breaker_trips: int = 0
    adaptive_adjustments: int = 0
    last_reset: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "total_requests": self.total_requests,
            "allowed_requests": self.allowed_requests,
            "denied_requests": self.denied_requests,
            "throttled_requests": self.throttled_requests,
            "current_rate": self.current_rate,
            "peak_rate": self.peak_rate,
            "average_backoff": self.average_backoff,
            "total_backoff_time": self.total_backoff_time,
            "circuit_breaker_trips": self.circuit_breaker_trips,
            "adaptive_adjustments": self.adaptive_adjustments,
            "last_reset": self.last_reset.isoformat() if self.last_reset else None,
            "denial_rate": self.get_denial_rate(),
            "throttle_rate": self.get_throttle_rate(),
            "success_rate": self.get_success_rate(),
        }
    
    def get_denial_rate(self) -> float:
        """Calculate denial rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.denied_requests / self.total_requests) * 100
    
    def get_throttle_rate(self) -> float:
        """Calculate throttle rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.throttled_requests / self.total_requests) * 100
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.allowed_requests / self.total_requests) * 100


class TokenBucket:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Consume tokens from the bucket"""
        async with self._lock:
            now = time.time()
            # Add tokens based on elapsed time
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def get_available_tokens(self) -> float:
        """Get current available tokens"""
        now = time.time()
        elapsed = now - self.last_update
        return min(self.capacity, self.tokens + elapsed * self.rate)
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Get time to wait for tokens to be available"""
        available = self.get_available_tokens()
        if available >= tokens:
            return 0.0
        needed = tokens - available
        return needed / self.rate


class SlidingWindow:
    """Sliding window rate limiter implementation"""
    
    def __init__(self, rate: float, window_size: int = 60):
        self.rate = rate  # requests per second
        self.window_size = window_size  # window size in seconds
        self.requests: deque = deque()
        self._lock = asyncio.Lock()
    
    async def is_allowed(self) -> bool:
        """Check if request is allowed"""
        async with self._lock:
            now = time.time()
            # Remove old requests outside the window
            while self.requests and self.requests[0] < now - self.window_size:
                self.requests.popleft()
            
            # Check if we're under the rate limit
            if len(self.requests) < self.rate * self.window_size:
                self.requests.append(now)
                return True
            return False
    
    def get_current_rate(self) -> float:
        """Get current request rate"""
        now = time.time()
        recent_requests = sum(
            1 for req_time in self.requests 
            if req_time > now - 1.0  # Last second
        )
        return recent_requests
    
    def get_window_usage(self) -> float:
        """Get current window usage percentage"""
        max_requests = self.rate * self.window_size
        return (len(self.requests) / max_requests) * 100 if max_requests > 0 else 0


class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on system performance"""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.base_rate = config.requests_per_second
        self.current_rate = config.requests_per_second
        self.success_history: deque = deque(maxlen=100)
        self.response_times: deque = deque(maxlen=100)
        self.last_adjustment = time.time()
        self.adjustment_interval = 10.0  # Adjust every 10 seconds
        
    def record_request(self, success: bool, response_time: float) -> None:
        """Record request outcome and response time"""
        self.success_history.append(success)
        self.response_times.append(response_time)
    
    def should_adjust(self) -> bool:
        """Check if rate should be adjusted"""
        now = time.time()
        return (now - self.last_adjustment) >= self.adjustment_interval
    
    def calculate_adjustment(self) -> float:
        """Calculate rate adjustment based on recent performance"""
        if len(self.success_history) < 10:
            return self.current_rate
        
        # Calculate success rate
        success_rate = sum(self.success_history) / len(self.success_history)
        
        # Calculate average response time
        avg_response_time = sum(self.response_times) / len(self.response_times)
        
        # Adjustment factors
        adjustment_factor = 1.0
        
        # If success rate is high and response times are low, increase rate
        if success_rate > 0.95 and avg_response_time < 1.0:
            adjustment_factor = 1.1
        # If success rate is low or response times are high, decrease rate
        elif success_rate < 0.8 or avg_response_time > 5.0:
            adjustment_factor = 0.8
        # If performance is degrading, be more conservative
        elif success_rate < 0.9 and avg_response_time > 2.0:
            adjustment_factor = 0.9
        
        new_rate = self.current_rate * adjustment_factor
        
        # Ensure rate stays within bounds (50% to 200% of base rate)
        min_rate = self.base_rate * 0.5
        max_rate = self.base_rate * 2.0
        new_rate = max(min_rate, min(max_rate, new_rate))
        
        self.last_adjustment = time.time()
        return new_rate
    
    def adjust_rate(self) -> float:
        """Adjust rate and return new rate"""
        if self.should_adjust():
            old_rate = self.current_rate
            self.current_rate = self.calculate_adjustment()
            
            if abs(self.current_rate - old_rate) > 0.1:
                logger.info(
                    f"Adaptive rate limiter adjusted rate from {old_rate:.2f} "
                    f"to {self.current_rate:.2f} req/s"
                )
            
        return self.current_rate


class BackoffCalculator:
    """Calculates backoff delays using various strategies"""
    
    @staticmethod
    def calculate_backoff(
        strategy: BackoffStrategy,
        attempt: int,
        base_delay: float,
        max_delay: float,
        multiplier: float = 2.0
    ) -> float:
        """Calculate backoff delay"""
        
        if strategy == BackoffStrategy.LINEAR:
            delay = base_delay * attempt
        elif strategy == BackoffStrategy.EXPONENTIAL:
            delay = base_delay * (multiplier ** (attempt - 1))
        elif strategy == BackoffStrategy.FIBONACCI:
            delay = base_delay * BackoffCalculator._fibonacci(attempt)
        elif strategy == BackoffStrategy.ADAPTIVE:
            # Adaptive backoff considers system load
            load_factor = 1.0  # Could be calculated from system metrics
            delay = base_delay * (multiplier ** (attempt - 1)) * load_factor
        else:
            delay = base_delay
        
        # Add jitter to prevent thundering herd
        jitter = delay * 0.1 * (0.5 + 0.5 * time.time() % 1)
        delay += jitter
        
        return min(delay, max_delay)
    
    @staticmethod
    def _fibonacci(n: int) -> int:
        """Calculate nth Fibonacci number"""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        return b


class ProviderRateLimiter:
    """Rate limiter for a specific provider"""
    
    def __init__(self, provider_name: str, config: RateLimitConfig):
        self.provider_name = provider_name
        self.config = config
        self.metrics = RateLimitMetrics()
        
        # Initialize rate limiter based on strategy
        if config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            self.limiter = TokenBucket(config.requests_per_second, config.burst_capacity)
        elif config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            self.limiter = SlidingWindow(config.requests_per_second, config.window_size)
        else:
            # Default to token bucket
            self.limiter = TokenBucket(config.requests_per_second, config.burst_capacity)
        
        # Adaptive rate limiting
        self.adaptive = AdaptiveRateLimiter(config) if config.enable_adaptive else None
        
        # Backoff tracking
        self.backoff_attempts: Dict[str, int] = defaultdict(int)
        self.backoff_until: Dict[str, float] = defaultdict(float)
        
        # Circuit breaker state
        self.circuit_open = False
        self.circuit_failures = 0
        self.circuit_last_failure = 0.0
        
        self._lock = asyncio.Lock()
    
    async def check_rate_limit(self, operation: str = "default") -> Tuple[RateLimitResult, float]:
        """Check if request is allowed and return wait time if not"""
        async with self._lock:
            now = time.time()
            self.metrics.total_requests += 1
            
            # Check circuit breaker
            if self._is_circuit_open(now):
                self.metrics.denied_requests += 1
                wait_time = self.config.recovery_timeout
                return RateLimitResult.DENIED, wait_time
            
            # Check if operation is in backoff
            if operation in self.backoff_until and now < self.backoff_until[operation]:
                self.metrics.throttled_requests += 1
                wait_time = self.backoff_until[operation] - now
                return RateLimitResult.THROTTLED, wait_time
            
            # Adjust rate if adaptive
            if self.adaptive:
                new_rate = self.adaptive.adjust_rate()
                if isinstance(self.limiter, TokenBucket):
                    self.limiter.rate = new_rate
                elif isinstance(self.limiter, SlidingWindow):
                    self.limiter.rate = new_rate
            
            # Check rate limit
            if isinstance(self.limiter, TokenBucket):
                allowed = await self.limiter.consume()
                wait_time = self.limiter.get_wait_time() if not allowed else 0.0
            elif isinstance(self.limiter, SlidingWindow):
                allowed = await self.limiter.is_allowed()
                wait_time = 1.0 / self.config.requests_per_second if not allowed else 0.0
            else:
                allowed = True
                wait_time = 0.0
            
            if allowed:
                self.metrics.allowed_requests += 1
                # Reset backoff on success
                if operation in self.backoff_attempts:
                    del self.backoff_attempts[operation]
                    del self.backoff_until[operation]
                return RateLimitResult.ALLOWED, 0.0
            else:
                self.metrics.denied_requests += 1
                # Calculate backoff
                self.backoff_attempts[operation] += 1
                backoff_delay = BackoffCalculator.calculate_backoff(
                    self.config.backoff_strategy,
                    self.backoff_attempts[operation],
                    self.config.min_backoff,
                    self.config.max_backoff,
                    self.config.backoff_multiplier
                )
                self.backoff_until[operation] = now + backoff_delay
                self.metrics.total_backoff_time += backoff_delay
                
                return RateLimitResult.DENIED, wait_time
    
    def record_request_outcome(self, success: bool, response_time: float, operation: str = "default") -> None:
        """Record the outcome of a request for adaptive adjustment"""
        if self.adaptive:
            self.adaptive.record_request(success, response_time)
        
        # Update circuit breaker
        if not success:
            self.circuit_failures += 1
            self.circuit_last_failure = time.time()
        else:
            # Reset circuit breaker on success
            if self.circuit_failures > 0:
                self.circuit_failures = max(0, self.circuit_failures - 1)
        
        # Update current rate for metrics
        if isinstance(self.limiter, SlidingWindow):
            self.metrics.current_rate = self.limiter.get_current_rate()
            self.metrics.peak_rate = max(self.metrics.peak_rate, self.metrics.current_rate)
    
    def _is_circuit_open(self, now: float) -> bool:
        """Check if circuit breaker is open"""
        if not self.config.enable_circuit_breaker:
            return False
        
        # Check if circuit should be opened
        if (self.circuit_failures >= self.config.failure_threshold * 10 and 
            now - self.circuit_last_failure < self.config.recovery_timeout):
            if not self.circuit_open:
                self.circuit_open = True
                self.metrics.circuit_breaker_trips += 1
                logger.warning(f"Circuit breaker opened for {self.provider_name}")
            return True
        
        # Check if circuit should be closed
        if self.circuit_open and now - self.circuit_last_failure > self.config.recovery_timeout:
            self.circuit_open = False
            self.circuit_failures = 0
            logger.info(f"Circuit breaker closed for {self.provider_name}")
        
        return self.circuit_open
    
    def get_metrics(self) -> RateLimitMetrics:
        """Get current rate limiting metrics"""
        return self.metrics
    
    def reset_metrics(self) -> None:
        """Reset rate limiting metrics"""
        self.metrics = RateLimitMetrics()
        self.metrics.last_reset = datetime.now(timezone.utc)


class RateLimitingEngine:
    """
    Central rate limiting engine for all providers and operations
    
    Features:
    - Per-provider rate limiting
    - Per-operation rate limiting within providers
    - Global rate limiting across all providers
    - Adaptive rate adjustment
    - Circuit breaker integration
    - Comprehensive metrics and monitoring
    """
    
    def __init__(self, global_config: Optional[RateLimitConfig] = None):
        self.global_config = global_config or RateLimitConfig()
        self._provider_limiters: Dict[str, ProviderRateLimiter] = {}
        self._provider_configs: Dict[str, RateLimitConfig] = {}
        self._global_limiter = ProviderRateLimiter("global", self.global_config)
        self._lock = asyncio.Lock()
        
        # Monitoring
        self._alert_callbacks: List[Callable] = []
        self._monitoring_task: Optional[asyncio.Task] = None
        self._start_monitoring()
    
    def register_provider(
        self, 
        provider_name: str, 
        config: Optional[RateLimitConfig] = None
    ) -> None:
        """Register a provider with specific rate limiting configuration"""
        provider_config = config or self.global_config
        self._provider_configs[provider_name] = provider_config
        
        logger.info(f"Registered provider {provider_name} with rate limiting engine")
    
    async def check_rate_limit(
        self, 
        provider_name: str, 
        operation: str = "default"
    ) -> Tuple[RateLimitResult, float]:
        """Check rate limit for a provider operation"""
        
        # Check global rate limit first
        global_result, global_wait = await self._global_limiter.check_rate_limit("global")
        if global_result != RateLimitResult.ALLOWED:
            return global_result, global_wait
        
        # Get or create provider limiter
        limiter = await self._get_provider_limiter(provider_name)
        
        # Check provider-specific rate limit
        return await limiter.check_rate_limit(operation)
    
    async def record_request_outcome(
        self, 
        provider_name: str, 
        success: bool, 
        response_time: float,
        operation: str = "default"
    ) -> None:
        """Record request outcome for adaptive rate limiting"""
        
        # Record for global limiter
        self._global_limiter.record_request_outcome(success, response_time, "global")
        
        # Record for provider limiter
        limiter = await self._get_provider_limiter(provider_name)
        limiter.record_request_outcome(success, response_time, operation)
    
    async def _get_provider_limiter(self, provider_name: str) -> ProviderRateLimiter:
        """Get or create provider rate limiter"""
        if provider_name not in self._provider_limiters:
            async with self._lock:
                # Double-check after acquiring lock
                if provider_name not in self._provider_limiters:
                    config = self._provider_configs.get(provider_name, self.global_config)
                    limiter = ProviderRateLimiter(provider_name, config)
                    self._provider_limiters[provider_name] = limiter
                    
                    logger.info(f"Created rate limiter for provider {provider_name}")
        
        return self._provider_limiters[provider_name]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive rate limiting metrics"""
        metrics = {
            "global_metrics": self._global_limiter.get_metrics().to_dict(),
            "provider_metrics": {},
            "total_providers": len(self._provider_limiters),
            "active_circuit_breakers": 0,
        }
        
        for provider_name, limiter in self._provider_limiters.items():
            provider_metrics = limiter.get_metrics().to_dict()
            metrics["provider_metrics"][provider_name] = provider_metrics
            
            if limiter.circuit_open:
                metrics["active_circuit_breakers"] += 1
        
        return metrics
    
    def add_alert_callback(self, callback: Callable[[str, Dict], None]) -> None:
        """Add callback for rate limiting alerts"""
        self._alert_callbacks.append(callback)
    
    def _start_monitoring(self) -> None:
        """Start background monitoring task"""
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._check_alerts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Rate limiting monitoring error: {e}")
    
    async def _check_alerts(self) -> None:
        """Check for rate limiting alerts"""
        for provider_name, limiter in self._provider_limiters.items():
            metrics = limiter.get_metrics()
            
            # High denial rate alert
            if metrics.get_denial_rate() > 50:
                await self._send_alert(
                    "high_denial_rate",
                    {
                        "provider": provider_name,
                        "denial_rate": metrics.get_denial_rate(),
                        "message": f"High denial rate for {provider_name}: {metrics.get_denial_rate():.1f}%"
                    }
                )
            
            # Circuit breaker alert
            if limiter.circuit_open:
                await self._send_alert(
                    "circuit_breaker_open",
                    {
                        "provider": provider_name,
                        "message": f"Circuit breaker open for {provider_name}"
                    }
                )
    
    async def _send_alert(self, alert_type: str, data: Dict) -> None:
        """Send alert to registered callbacks"""
        for callback in self._alert_callbacks:
            try:
                callback(alert_type, data)
            except Exception as e:
                logger.error(f"Error sending rate limiting alert: {e}")
    
    async def close(self) -> None:
        """Close the rate limiting engine"""
        if self._monitoring_task:
            self._monitoring_task.cancel()
        
        logger.info("Closed rate limiting engine")


# Global instance
_rate_limiting_engine: Optional[RateLimitingEngine] = None


def get_rate_limiting_engine() -> RateLimitingEngine:
    """Get the global rate limiting engine instance"""
    global _rate_limiting_engine
    if _rate_limiting_engine is None:
        _rate_limiting_engine = RateLimitingEngine()
    return _rate_limiting_engine