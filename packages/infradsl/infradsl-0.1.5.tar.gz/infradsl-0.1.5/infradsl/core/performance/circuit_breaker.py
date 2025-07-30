"""
Circuit Breaker System - Failure detection and automatic recovery patterns

This module provides comprehensive circuit breaker functionality with:
- Multi-state circuit breaker (Closed, Open, Half-Open)
- Failure detection and recovery mechanisms
- Provider-specific circuit breakers
- Intelligent failure thresholds
- Performance monitoring and metrics
"""

import asyncio
import logging
import time
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from collections import deque, defaultdict
import statistics

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class FailureType(Enum):
    """Types of failures that can trigger circuit breaker"""

    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    HTTP_ERROR = "http_error"
    RATE_LIMIT = "rate_limit"
    PROVIDER_ERROR = "provider_error"
    UNKNOWN = "unknown"


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""

    failure_threshold: int = 5  # Number of failures to open circuit
    failure_rate_threshold: float = 0.5  # 50% failure rate to open circuit
    recovery_timeout: float = 60.0  # Time to wait before trying half-open
    success_threshold: int = 3  # Successes needed to close from half-open
    request_volume_threshold: int = 10  # Minimum requests for failure rate calculation
    timeout: float = 30.0  # Request timeout
    max_concurrent_requests: int = 10  # Max concurrent requests in half-open
    enable_metrics: bool = True  # Enable metrics collection
    failure_types: List[FailureType] = field(
        default_factory=lambda: [
            FailureType.TIMEOUT,
            FailureType.CONNECTION_ERROR,
            FailureType.HTTP_ERROR,
            FailureType.PROVIDER_ERROR,
        ]
    )


@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeouts: int = 0
    circuit_opens: int = 0
    circuit_closes: int = 0
    half_open_attempts: int = 0
    current_state: CircuitBreakerState = CircuitBreakerState.CLOSED
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    current_failure_count: int = 0
    current_success_count: int = 0
    average_response_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "timeouts": self.timeouts,
            "circuit_opens": self.circuit_opens,
            "circuit_closes": self.circuit_closes,
            "half_open_attempts": self.half_open_attempts,
            "current_state": self.current_state.value,
            "last_failure_time": (
                self.last_failure_time.isoformat() if self.last_failure_time else None
            ),
            "last_success_time": (
                self.last_success_time.isoformat() if self.last_success_time else None
            ),
            "current_failure_count": self.current_failure_count,
            "current_success_count": self.current_success_count,
            "average_response_time": self.average_response_time,
            "failure_rate": self.get_failure_rate(),
            "success_rate": self.get_success_rate(),
        }

    def get_failure_rate(self) -> float:
        """Calculate failure rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100

    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100


class FailureDetector:
    """Intelligent failure detection with adaptive thresholds"""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_history: deque = deque(maxlen=100)
        self.response_times: deque = deque(maxlen=100)
        self.failure_types: defaultdict = defaultdict(int)
        self.baseline_response_time: Optional[float] = None

    def record_success(self, response_time: float) -> None:
        """Record a successful request"""
        now = time.time()
        self.failure_history.append((now, False, response_time))
        self.response_times.append(response_time)

        # Update baseline response time
        if len(self.response_times) >= 10:
            self.baseline_response_time = statistics.median(
                list(self.response_times)[-10:]
            )

    def record_failure(
        self, failure_type: FailureType, response_time: Optional[float] = None
    ) -> None:
        """Record a failed request"""
        now = time.time()
        self.failure_history.append((now, True, response_time))
        self.failure_types[failure_type] += 1

        if response_time:
            self.response_times.append(response_time)

    def should_open_circuit(self) -> bool:
        """Determine if circuit should be opened"""
        if len(self.failure_history) < self.config.request_volume_threshold:
            return False

        # Count recent failures
        now = time.time()
        recent_window = 60.0  # Last 60 seconds
        recent_failures = [
            _
            for timestamp, failed, _ in self.failure_history
            if now - timestamp <= recent_window and failed
        ]

        recent_total = [
            _
            for timestamp, _, _ in self.failure_history
            if now - timestamp <= recent_window
        ]

        # Check failure count threshold
        if len(recent_failures) >= self.config.failure_threshold:
            logger.warning(
                f"Circuit breaker: failure count threshold exceeded ({len(recent_failures)}/{self.config.failure_threshold})"
            )
            return True

        # Check failure rate threshold
        if len(recent_total) >= self.config.request_volume_threshold:
            failure_rate = len(recent_failures) / len(recent_total)
            if failure_rate >= self.config.failure_rate_threshold:
                logger.warning(
                    f"Circuit breaker: failure rate threshold exceeded ({failure_rate:.2%}/{self.config.failure_rate_threshold:.2%})"
                )
                return True

        # Check response time degradation
        if self.baseline_response_time and len(self.response_times) >= 5:
            recent_avg = statistics.mean(list(self.response_times)[-5:])
            if recent_avg > self.baseline_response_time * 3:  # 3x slower than baseline
                logger.warning(
                    f"Circuit breaker: response time degradation detected ({recent_avg:.2f}s vs {self.baseline_response_time:.2f}s baseline)"
                )
                return True

        return False

    def get_failure_summary(self) -> Dict[str, int]:
        """Get summary of failure types"""
        return dict(self.failure_types)


class CircuitBreakerException(Exception):
    """Exception raised when circuit breaker is open"""

    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class CircuitBreaker:
    """
    Circuit breaker implementation with intelligent failure detection

    The circuit breaker has three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing, requests are blocked and fail fast
    - HALF_OPEN: Testing recovery, limited requests allowed
    """

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self._state = CircuitBreakerState.CLOSED
        self._failure_detector = FailureDetector(config)
        self._metrics = CircuitBreakerMetrics()
        self._last_failure_time = 0.0
        self._half_open_requests = 0
        self._lock = asyncio.Lock()

        # State-specific counters
        self._consecutive_failures = 0
        self._consecutive_successes = 0

        # Callbacks
        self._state_change_callbacks: List[Callable] = []

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        return self._state

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)"""
        return self._state == CircuitBreakerState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing)"""
        return self._state == CircuitBreakerState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing)"""
        return self._state == CircuitBreakerState.HALF_OPEN

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            await self._update_state()

            if self._state == CircuitBreakerState.OPEN:
                retry_after = self.config.recovery_timeout - (
                    time.time() - self._last_failure_time
                )
                raise CircuitBreakerException(
                    f"Circuit breaker '{self.name}' is OPEN",
                    retry_after=max(0, retry_after),
                )

            if self._state == CircuitBreakerState.HALF_OPEN:
                if self._half_open_requests >= self.config.max_concurrent_requests:
                    raise CircuitBreakerException(
                        f"Circuit breaker '{self.name}' is HALF_OPEN with max concurrent requests"
                    )
                self._half_open_requests += 1

        # Execute the function
        start_time = time.time()
        try:
            # Apply timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs), timeout=self.config.timeout
            )

            response_time = time.time() - start_time
            await self._record_success(response_time)
            return result

        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            await self._record_failure(FailureType.TIMEOUT, response_time)
            raise
        except ConnectionError as e:
            response_time = time.time() - start_time
            await self._record_failure(FailureType.CONNECTION_ERROR, response_time)
            raise
        except Exception as e:
            response_time = time.time() - start_time
            failure_type = self._classify_exception(e)
            await self._record_failure(failure_type, response_time)
            raise
        finally:
            async with self._lock:
                if self._state == CircuitBreakerState.HALF_OPEN:
                    self._half_open_requests -= 1

    async def _record_success(self, response_time: float) -> None:
        """Record successful request"""
        async with self._lock:
            self._metrics.total_requests += 1
            self._metrics.successful_requests += 1
            self._metrics.last_success_time = datetime.now(timezone.utc)
            self._metrics.current_success_count += 1
            self._consecutive_failures = 0
            self._consecutive_successes += 1

            # Update average response time
            self._update_average_response_time(response_time)

            # Record in failure detector
            self._failure_detector.record_success(response_time)

            # Check if we should close the circuit from half-open
            if (
                self._state == CircuitBreakerState.HALF_OPEN
                and self._consecutive_successes >= self.config.success_threshold
            ):
                await self._close_circuit()

    async def _record_failure(
        self, failure_type: FailureType, response_time: Optional[float] = None
    ) -> None:
        """Record failed request"""
        async with self._lock:
            self._metrics.total_requests += 1
            self._metrics.failed_requests += 1
            self._metrics.last_failure_time = datetime.now(timezone.utc)
            self._metrics.current_failure_count += 1
            self._consecutive_successes = 0
            self._consecutive_failures += 1
            self._last_failure_time = time.time()

            if failure_type == FailureType.TIMEOUT:
                self._metrics.timeouts += 1

            if response_time:
                self._update_average_response_time(response_time)

            # Record in failure detector
            self._failure_detector.record_failure(failure_type, response_time)

            # Check if we should open the circuit
            if self._state == CircuitBreakerState.CLOSED:
                if self._failure_detector.should_open_circuit():
                    await self._open_circuit()
            elif self._state == CircuitBreakerState.HALF_OPEN:
                # Any failure in half-open state opens the circuit
                await self._open_circuit()

    async def _update_state(self) -> None:
        """Update circuit breaker state based on conditions"""
        if self._state == CircuitBreakerState.OPEN:
            # Check if we should transition to half-open
            time_since_failure = time.time() - self._last_failure_time
            if time_since_failure >= self.config.recovery_timeout:
                await self._half_open_circuit()

    async def _open_circuit(self) -> None:
        """Open the circuit breaker"""
        if self._state != CircuitBreakerState.OPEN:
            old_state = self._state
            self._state = CircuitBreakerState.OPEN
            self._metrics.circuit_opens += 1
            self._metrics.current_state = CircuitBreakerState.OPEN
            self._consecutive_successes = 0

            logger.warning(
                f"Circuit breaker '{self.name}' opened (was {old_state.value})"
            )
            await self._notify_state_change(old_state, CircuitBreakerState.OPEN)

    async def _close_circuit(self) -> None:
        """Close the circuit breaker"""
        if self._state != CircuitBreakerState.CLOSED:
            old_state = self._state
            self._state = CircuitBreakerState.CLOSED
            self._metrics.circuit_closes += 1
            self._metrics.current_state = CircuitBreakerState.CLOSED
            self._consecutive_failures = 0
            self._metrics.current_failure_count = 0

            logger.info(f"Circuit breaker '{self.name}' closed (was {old_state.value})")
            await self._notify_state_change(old_state, CircuitBreakerState.CLOSED)

    async def _half_open_circuit(self) -> None:
        """Transition circuit breaker to half-open state"""
        if self._state != CircuitBreakerState.HALF_OPEN:
            old_state = self._state
            self._state = CircuitBreakerState.HALF_OPEN
            self._metrics.half_open_attempts += 1
            self._metrics.current_state = CircuitBreakerState.HALF_OPEN
            self._consecutive_successes = 0
            self._half_open_requests = 0

            logger.info(
                f"Circuit breaker '{self.name}' half-opened (was {old_state.value})"
            )
            await self._notify_state_change(old_state, CircuitBreakerState.HALF_OPEN)

    def _classify_exception(self, exception: Exception) -> FailureType:
        """Classify exception into failure type"""
        if isinstance(exception, asyncio.TimeoutError):
            return FailureType.TIMEOUT
        elif isinstance(exception, ConnectionError):
            return FailureType.CONNECTION_ERROR
        elif hasattr(exception, "response") and hasattr(
            exception.response, "status_code"
        ):
            # HTTP-like error
            status_code = exception.response.status_code
            if status_code == 429:
                return FailureType.RATE_LIMIT
            elif 500 <= status_code < 600:
                return FailureType.HTTP_ERROR

        return FailureType.PROVIDER_ERROR

    def _update_average_response_time(self, response_time: float) -> None:
        """Update average response time using exponential moving average"""
        if self._metrics.average_response_time == 0:
            self._metrics.average_response_time = response_time
        else:
            # Use 0.1 weight for new measurements
            alpha = 0.1
            self._metrics.average_response_time = (
                alpha * response_time
                + (1 - alpha) * self._metrics.average_response_time
            )

    def add_state_change_callback(
        self, callback: Callable[[CircuitBreakerState, CircuitBreakerState], None]
    ) -> None:
        """Add callback for state changes"""
        self._state_change_callbacks.append(callback)

    async def _notify_state_change(
        self, old_state: CircuitBreakerState, new_state: CircuitBreakerState
    ) -> None:
        """Notify callbacks of state change"""
        for callback in self._state_change_callbacks:
            try:
                await callback(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in circuit breaker state change callback: {e}")

    def get_metrics(self) -> CircuitBreakerMetrics:
        """Get current circuit breaker metrics"""
        return self._metrics

    def reset(self) -> None:
        """Reset circuit breaker to closed state"""
        self._state = CircuitBreakerState.CLOSED
        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._metrics.current_failure_count = 0
        self._metrics.current_success_count = 0
        logger.info(f"Circuit breaker '{self.name}' reset to CLOSED state")


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers for different providers/operations

    Features:
    - Per-provider circuit breakers
    - Global circuit breaker policies
    - Centralized monitoring and metrics
    - Automatic circuit breaker creation
    """

    def __init__(self, default_config: Optional[CircuitBreakerConfig] = None):
        self.default_config = default_config or CircuitBreakerConfig()
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._configs: Dict[str, CircuitBreakerConfig] = {}
        self._lock = asyncio.Lock()

        # Global monitoring
        self._alert_callbacks: List[Callable] = []

    def register_circuit_breaker(
        self, name: str, config: Optional[CircuitBreakerConfig] = None
    ) -> None:
        """Register a circuit breaker with specific configuration"""
        circuit_config = config or self.default_config
        self._configs[name] = circuit_config

        logger.info(f"Registered circuit breaker configuration for: {name}")

    async def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create a circuit breaker"""
        if name not in self._circuit_breakers:
            async with self._lock:
                # Double-check after acquiring lock
                if name not in self._circuit_breakers:
                    config = self._configs.get(name, self.default_config)
                    circuit_breaker = CircuitBreaker(name, config)

                    # Add state change callback for alerts
                    circuit_breaker.add_state_change_callback(
                        lambda old, new: self._handle_state_change(name, old, new)
                    )

                    self._circuit_breakers[name] = circuit_breaker
                    logger.info(f"Created circuit breaker: {name}")

        return self._circuit_breakers[name]

    async def call_with_circuit_breaker(
        self, name: str, func: Callable[..., T], *args, **kwargs
    ) -> T:
        """Execute function with circuit breaker protection"""
        circuit_breaker = await self.get_circuit_breaker(name)
        return await circuit_breaker.call(func, *args, **kwargs)

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all circuit breakers"""
        return {
            name: cb.get_metrics().to_dict()
            for name, cb in self._circuit_breakers.items()
        }

    def get_global_status(self) -> Dict[str, Any]:
        """Get global circuit breaker status"""
        total_breakers = len(self._circuit_breakers)
        open_breakers = len(
            [cb for cb in self._circuit_breakers.values() if cb.is_open]
        )
        half_open_breakers = len(
            [cb for cb in self._circuit_breakers.values() if cb.is_half_open]
        )

        return {
            "total_circuit_breakers": total_breakers,
            "open_circuit_breakers": open_breakers,
            "half_open_circuit_breakers": half_open_breakers,
            "healthy_circuit_breakers": total_breakers
            - open_breakers
            - half_open_breakers,
            "circuit_breaker_status": {
                name: cb.state.value for name, cb in self._circuit_breakers.items()
            },
        }

    def add_alert_callback(
        self,
        callback: Callable[[str, str, CircuitBreakerState, CircuitBreakerState], None],
    ) -> None:
        """Add callback for circuit breaker alerts"""
        self._alert_callbacks.append(callback)

    async def _handle_state_change(
        self, name: str, old_state: CircuitBreakerState, new_state: CircuitBreakerState
    ) -> None:
        """Handle circuit breaker state changes"""
        # Send alerts
        for callback in self._alert_callbacks:
            try:
                await callback(
                    name,
                    f"Circuit breaker '{name}' changed from {old_state.value} to {new_state.value}",
                    old_state,
                    new_state,
                )
            except Exception as e:
                logger.error(f"Error in circuit breaker alert callback: {e}")

    async def reset_all(self) -> None:
        """Reset all circuit breakers"""
        for cb in self._circuit_breakers.values():
            cb.reset()
        logger.info("Reset all circuit breakers")

    async def reset_circuit_breaker(self, name: str) -> None:
        """Reset specific circuit breaker"""
        if name in self._circuit_breakers:
            self._circuit_breakers[name].reset()
            logger.info(f"Reset circuit breaker: {name}")


# Global instance
_circuit_breaker_manager: Optional[CircuitBreakerManager] = None


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """Get the global circuit breaker manager instance"""
    global _circuit_breaker_manager
    if _circuit_breaker_manager is None:
        _circuit_breaker_manager = CircuitBreakerManager()
    return _circuit_breaker_manager


def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Get a circuit breaker by name (sync version for convenience)"""
    manager = get_circuit_breaker_manager()
    # Note: This creates an async context that needs to be handled by the caller
    return asyncio.create_task(manager.get_circuit_breaker(name))
