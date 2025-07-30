"""
Enterprise Performance & Scalability Module for InfraDSL

This module provides enterprise-grade performance optimizations including:
- Connection pool management
- Rate limiting with adaptive backoff
- Circuit breaker patterns
- Redis clustering support
- PostgreSQL integration
- Performance monitoring and metrics
"""

from .pools import (
    ConnectionPoolManager,
    ProviderConnectionPool,
    ConnectionMetrics,
    PoolConfig,
    get_connection_pool_manager,
)
from .rate_limiting import (
    RateLimitingEngine,
    RateLimitConfig,
    RateLimitStrategy,
    BackoffStrategy,
    get_rate_limiting_engine,
)
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerConfig,
    FailureDetector,
    CircuitBreakerManager,
    get_circuit_breaker_manager,
)
from .redis_cluster import (
    RedisClusterClient,
    ClusterConfig,
    RedisNode,
    NodeRole,
    NodeState,
    initialize_redis_cluster,
    get_redis_cluster_client,
)
from .postgresql import (
    PostgreSQLConnectionPool,
    PostgreSQLConfig,
    StateManager,
    ResourceState,
    initialize_postgresql,
    get_postgresql_pool,
    get_state_manager,
)

__all__ = [
    # Connection Pools
    "ConnectionPoolManager",
    "ProviderConnectionPool", 
    "ConnectionMetrics",
    "PoolConfig",
    "get_connection_pool_manager",
    # Rate Limiting
    "RateLimitingEngine",
    "RateLimitConfig",
    "RateLimitStrategy",
    "BackoffStrategy", 
    "get_rate_limiting_engine",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerState",
    "CircuitBreakerConfig",
    "FailureDetector",
    "CircuitBreakerManager",
    "get_circuit_breaker_manager",
    # Redis Clustering
    "RedisClusterClient",
    "ClusterConfig",
    "RedisNode",
    "NodeRole",
    "NodeState",
    "initialize_redis_cluster",
    "get_redis_cluster_client",
    # PostgreSQL Integration
    "PostgreSQLConnectionPool",
    "PostgreSQLConfig",
    "StateManager",
    "ResourceState",
    "initialize_postgresql",
    "get_postgresql_pool",
    "get_state_manager",
]