"""
Connection Pool Manager - Enterprise connection pooling for InfraDSL providers

This module provides provider-specific connection pooling with health monitoring,
automatic recovery, and performance metrics.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Protocol, Callable, TypeVar, Generic
from contextlib import asynccontextmanager
import weakref

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ConnectionState(Enum):
    """Connection state enumeration"""
    IDLE = "idle"
    ACTIVE = "active"
    FAILED = "failed"
    CLOSED = "closed"


class PoolState(Enum):
    """Pool state enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"


@dataclass
class PoolConfig:
    """Connection pool configuration"""
    min_connections: int = 2
    max_connections: int = 10
    connection_timeout: float = 30.0
    idle_timeout: float = 300.0  # 5 minutes
    max_lifetime: float = 3600.0  # 1 hour
    health_check_interval: float = 60.0  # 1 minute
    retry_attempts: int = 3
    retry_delay: float = 1.0
    enable_metrics: bool = True


@dataclass
class ConnectionMetrics:
    """Connection metrics for monitoring"""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    peak_connections: int = 0
    pool_hits: int = 0
    pool_misses: int = 0
    connection_errors: int = 0
    timeouts: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary"""
        return {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "idle_connections": self.idle_connections,
            "failed_connections": self.failed_connections,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "average_response_time": self.average_response_time,
            "peak_connections": self.peak_connections,
            "pool_hits": self.pool_hits,
            "pool_misses": self.pool_misses,
            "connection_errors": self.connection_errors,
            "timeouts": self.timeouts,
            "success_rate": self.get_success_rate(),
            "pool_efficiency": self.get_pool_efficiency(),
        }
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_pool_efficiency(self) -> float:
        """Calculate pool efficiency (hits vs misses)"""
        total_pool_operations = self.pool_hits + self.pool_misses
        if total_pool_operations == 0:
            return 0.0
        return (self.pool_hits / total_pool_operations) * 100


class ConnectionProtocol(Protocol):
    """Protocol for connections managed by the pool"""
    
    async def connect(self) -> None:
        """Establish connection"""
        ...
    
    async def disconnect(self) -> None:
        """Close connection"""
        ...
    
    async def is_healthy(self) -> bool:
        """Check if connection is healthy"""
        ...
    
    async def reset(self) -> None:
        """Reset connection state"""
        ...


@dataclass
class PooledConnection(Generic[T]):
    """Wrapper for pooled connections"""
    connection: T
    state: ConnectionState
    created_at: datetime
    last_used: datetime
    use_count: int = 0
    health_check_count: int = 0
    last_health_check: Optional[datetime] = None
    
    def is_expired(self, max_lifetime: float) -> bool:
        """Check if connection has exceeded max lifetime"""
        age = (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return age > max_lifetime
    
    def is_idle_expired(self, idle_timeout: float) -> bool:
        """Check if connection has been idle too long"""
        idle_time = (datetime.now(timezone.utc) - self.last_used).total_seconds()
        return idle_time > idle_timeout
    
    def mark_used(self) -> None:
        """Mark connection as used"""
        self.last_used = datetime.now(timezone.utc)
        self.use_count += 1


class ProviderConnectionPool(Generic[T]):
    """Connection pool for a specific provider"""
    
    def __init__(
        self, 
        provider_name: str,
        connection_factory: Callable[[], T],
        config: PoolConfig,
        health_checker: Optional[Callable[[T], bool]] = None
    ):
        self.provider_name = provider_name
        self.connection_factory = connection_factory
        self.config = config
        self.health_checker = health_checker
        
        self._connections: List[PooledConnection[T]] = []
        self._available = asyncio.Queue()
        self._lock = asyncio.Lock()
        self._state = PoolState.HEALTHY
        self._metrics = ConnectionMetrics()
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Start background tasks
        self._start_background_tasks()
    
    async def acquire(self, timeout: Optional[float] = None) -> T:
        """Acquire a connection from the pool"""
        start_time = time.time()
        
        try:
            # Try to get an available connection
            try:
                conn = self._available.get_nowait()
                self._metrics.pool_hits += 1
                return await self._prepare_connection(conn)
            except asyncio.QueueEmpty:
                self._metrics.pool_misses += 1
            
            # Create new connection if under limit
            async with self._lock:
                if len(self._connections) < self.config.max_connections:
                    conn = await self._create_connection()
                    self._connections.append(conn)
                    return await self._prepare_connection(conn)
            
            # Wait for available connection
            timeout = timeout or self.config.connection_timeout
            conn = await asyncio.wait_for(self._available.get(), timeout=timeout)
            return await self._prepare_connection(conn)
            
        except asyncio.TimeoutError:
            self._metrics.timeouts += 1
            raise ConnectionError(f"Connection timeout after {timeout}s")
        except Exception as e:
            self._metrics.connection_errors += 1
            logger.error(f"Error acquiring connection for {self.provider_name}: {e}")
            raise
        finally:
            self._metrics.total_requests += 1
            response_time = time.time() - start_time
            self._update_average_response_time(response_time)
    
    async def release(self, connection: T) -> None:
        """Release a connection back to the pool"""
        try:
            # Find the pooled connection
            pooled_conn = None
            for conn in self._connections:
                if conn.connection is connection:
                    pooled_conn = conn
                    break
            
            if not pooled_conn:
                logger.warning(f"Attempted to release unknown connection for {self.provider_name}")
                return
            
            # Check if connection is still healthy
            if hasattr(connection, 'is_healthy'):
                try:
                    if not await connection.is_healthy():
                        pooled_conn.state = ConnectionState.FAILED
                        await self._remove_connection(pooled_conn)
                        return
                except Exception:
                    pooled_conn.state = ConnectionState.FAILED
                    await self._remove_connection(pooled_conn)
                    return
            
            # Check if connection has expired
            if (pooled_conn.is_expired(self.config.max_lifetime) or 
                pooled_conn.is_idle_expired(self.config.idle_timeout)):
                await self._remove_connection(pooled_conn)
                return
            
            # Return to pool
            pooled_conn.state = ConnectionState.IDLE
            pooled_conn.mark_used()
            self._available.put_nowait(pooled_conn)
            self._metrics.successful_requests += 1
            
        except Exception as e:
            self._metrics.failed_requests += 1
            logger.error(f"Error releasing connection for {self.provider_name}: {e}")
    
    @asynccontextmanager
    async def connection(self, timeout: Optional[float] = None):
        """Context manager for connection acquisition/release"""
        conn = await self.acquire(timeout)
        try:
            yield conn
        finally:
            await self.release(conn)
    
    async def _create_connection(self) -> PooledConnection[T]:
        """Create a new pooled connection"""
        try:
            connection = self.connection_factory()
            if hasattr(connection, 'connect'):
                await connection.connect()
            
            pooled_conn = PooledConnection(
                connection=connection,
                state=ConnectionState.IDLE,
                created_at=datetime.now(timezone.utc),
                last_used=datetime.now(timezone.utc)
            )
            
            self._metrics.total_connections += 1
            self._metrics.peak_connections = max(
                self._metrics.peak_connections, 
                len(self._connections) + 1
            )
            
            logger.debug(f"Created new connection for {self.provider_name}")
            return pooled_conn
            
        except Exception as e:
            self._metrics.connection_errors += 1
            logger.error(f"Failed to create connection for {self.provider_name}: {e}")
            raise
    
    async def _prepare_connection(self, pooled_conn: PooledConnection[T]) -> T:
        """Prepare connection for use"""
        pooled_conn.state = ConnectionState.ACTIVE
        pooled_conn.mark_used()
        
        # Reset connection if needed
        if hasattr(pooled_conn.connection, 'reset'):
            try:
                await pooled_conn.connection.reset()
            except Exception as e:
                logger.warning(f"Failed to reset connection for {self.provider_name}: {e}")
        
        self._metrics.active_connections += 1
        return pooled_conn.connection
    
    async def _remove_connection(self, pooled_conn: PooledConnection[T]) -> None:
        """Remove a connection from the pool"""
        try:
            if hasattr(pooled_conn.connection, 'disconnect'):
                await pooled_conn.connection.disconnect()
        except Exception as e:
            logger.warning(f"Error disconnecting connection for {self.provider_name}: {e}")
        
        async with self._lock:
            if pooled_conn in self._connections:
                self._connections.remove(pooled_conn)
                self._metrics.total_connections -= 1
                if pooled_conn.state == ConnectionState.FAILED:
                    self._metrics.failed_connections += 1
    
    def _start_background_tasks(self) -> None:
        """Start background maintenance tasks"""
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _health_check_loop(self) -> None:
        """Background health check task"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for {self.provider_name}: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup task"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                await self._cleanup_expired_connections()
                await self._ensure_min_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error for {self.provider_name}: {e}")
    
    async def _perform_health_checks(self) -> None:
        """Perform health checks on idle connections"""
        idle_connections = [
            conn for conn in self._connections 
            if conn.state == ConnectionState.IDLE
        ]
        
        for conn in idle_connections:
            try:
                if self.health_checker:
                    is_healthy = await self.health_checker(conn.connection)
                elif hasattr(conn.connection, 'is_healthy'):
                    is_healthy = await conn.connection.is_healthy()
                else:
                    is_healthy = True
                
                conn.health_check_count += 1
                conn.last_health_check = datetime.now(timezone.utc)
                
                if not is_healthy:
                    conn.state = ConnectionState.FAILED
                    await self._remove_connection(conn)
                    
            except Exception as e:
                logger.error(f"Health check failed for {self.provider_name}: {e}")
                conn.state = ConnectionState.FAILED
                await self._remove_connection(conn)
    
    async def _cleanup_expired_connections(self) -> None:
        """Remove expired connections"""
        expired_connections = [
            conn for conn in self._connections
            if (conn.state == ConnectionState.IDLE and 
                (conn.is_expired(self.config.max_lifetime) or 
                 conn.is_idle_expired(self.config.idle_timeout)))
        ]
        
        for conn in expired_connections:
            await self._remove_connection(conn)
    
    async def _ensure_min_connections(self) -> None:
        """Ensure minimum number of connections"""
        if len(self._connections) < self.config.min_connections:
            needed = self.config.min_connections - len(self._connections)
            for _ in range(needed):
                try:
                    conn = await self._create_connection()
                    async with self._lock:
                        self._connections.append(conn)
                        self._available.put_nowait(conn)
                except Exception as e:
                    logger.error(f"Failed to create min connection for {self.provider_name}: {e}")
                    break
    
    def _update_average_response_time(self, response_time: float) -> None:
        """Update average response time using exponential moving average"""
        if self._metrics.average_response_time == 0:
            self._metrics.average_response_time = response_time
        else:
            # Use 0.1 weight for new measurements
            alpha = 0.1
            self._metrics.average_response_time = (
                alpha * response_time + 
                (1 - alpha) * self._metrics.average_response_time
            )
    
    def get_metrics(self) -> ConnectionMetrics:
        """Get current pool metrics"""
        # Update real-time metrics
        self._metrics.active_connections = len([
            conn for conn in self._connections 
            if conn.state == ConnectionState.ACTIVE
        ])
        self._metrics.idle_connections = len([
            conn for conn in self._connections 
            if conn.state == ConnectionState.IDLE
        ])
        
        return self._metrics
    
    def get_state(self) -> PoolState:
        """Get current pool state"""
        healthy_connections = len([
            conn for conn in self._connections
            if conn.state in [ConnectionState.IDLE, ConnectionState.ACTIVE]
        ])
        
        if healthy_connections == 0:
            return PoolState.FAILED
        elif healthy_connections < self.config.min_connections:
            return PoolState.DEGRADED
        elif self._metrics.get_success_rate() < 90:
            return PoolState.DEGRADED
        else:
            return PoolState.HEALTHY
    
    async def close(self) -> None:
        """Close the pool and all connections"""
        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Close all connections
        for conn in self._connections.copy():
            await self._remove_connection(conn)
        
        logger.info(f"Closed connection pool for {self.provider_name}")


class ConnectionPoolManager:
    """
    Global connection pool manager for all providers
    
    Features:
    - Per-provider connection pools
    - Global connection limits
    - Pool health monitoring
    - Performance metrics aggregation
    - Automatic pool creation and cleanup
    """
    
    def __init__(self, global_max_connections: int = 100):
        self.global_max_connections = global_max_connections
        self._pools: Dict[str, ProviderConnectionPool] = {}
        self._pool_configs: Dict[str, PoolConfig] = {}
        self._connection_factories: Dict[str, Callable] = {}
        self._health_checkers: Dict[str, Optional[Callable]] = {}
        self._global_metrics = ConnectionMetrics()
        self._lock = asyncio.Lock()
        
        # Weak references to track pool usage
        self._pool_refs: weakref.WeakSet = weakref.WeakSet()
    
    def register_provider(
        self,
        provider_name: str,
        connection_factory: Callable,
        config: Optional[PoolConfig] = None,
        health_checker: Optional[Callable] = None
    ) -> None:
        """Register a provider with the pool manager"""
        self._connection_factories[provider_name] = connection_factory
        self._pool_configs[provider_name] = config or PoolConfig()
        self._health_checkers[provider_name] = health_checker
        
        logger.info(f"Registered provider {provider_name} with connection pool manager")
    
    async def get_pool(self, provider_name: str) -> ProviderConnectionPool:
        """Get or create a connection pool for a provider"""
        if provider_name not in self._pools:
            async with self._lock:
                # Double-check after acquiring lock
                if provider_name not in self._pools:
                    if provider_name not in self._connection_factories:
                        raise ValueError(f"Provider {provider_name} not registered")
                    
                    pool = ProviderConnectionPool(
                        provider_name=provider_name,
                        connection_factory=self._connection_factories[provider_name],
                        config=self._pool_configs[provider_name],
                        health_checker=self._health_checkers[provider_name]
                    )
                    
                    self._pools[provider_name] = pool
                    self._pool_refs.add(pool)
                    
                    logger.info(f"Created connection pool for provider {provider_name}")
        
        return self._pools[provider_name]
    
    async def get_connection(self, provider_name: str, timeout: Optional[float] = None):
        """Get a connection for a provider (context manager)"""
        pool = await self.get_pool(provider_name)
        return pool.connection(timeout)
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics across all pools"""
        total_metrics = ConnectionMetrics()
        pool_metrics = {}
        
        for provider_name, pool in self._pools.items():
            metrics = pool.get_metrics()
            pool_metrics[provider_name] = metrics.to_dict()
            
            # Aggregate totals
            total_metrics.total_connections += metrics.total_connections
            total_metrics.active_connections += metrics.active_connections
            total_metrics.idle_connections += metrics.idle_connections
            total_metrics.failed_connections += metrics.failed_connections
            total_metrics.total_requests += metrics.total_requests
            total_metrics.successful_requests += metrics.successful_requests
            total_metrics.failed_requests += metrics.failed_requests
            total_metrics.peak_connections = max(
                total_metrics.peak_connections, 
                metrics.peak_connections
            )
            total_metrics.pool_hits += metrics.pool_hits
            total_metrics.pool_misses += metrics.pool_misses
            total_metrics.connection_errors += metrics.connection_errors
            total_metrics.timeouts += metrics.timeouts
        
        # Calculate weighted average response time
        if total_metrics.total_requests > 0:
            total_response_time = sum(
                pool.get_metrics().average_response_time * pool.get_metrics().total_requests
                for pool in self._pools.values()
            )
            total_metrics.average_response_time = total_response_time / total_metrics.total_requests
        
        return {
            "global_metrics": total_metrics.to_dict(),
            "pool_metrics": pool_metrics,
            "active_pools": len(self._pools),
            "global_connection_limit": self.global_max_connections,
            "pool_states": {
                name: pool.get_state().value 
                for name, pool in self._pools.items()
            }
        }
    
    async def close_pool(self, provider_name: str) -> None:
        """Close a specific provider pool"""
        if provider_name in self._pools:
            pool = self._pools[provider_name]
            await pool.close()
            del self._pools[provider_name]
            logger.info(f"Closed connection pool for provider {provider_name}")
    
    async def close_all(self) -> None:
        """Close all connection pools"""
        for provider_name in list(self._pools.keys()):
            await self.close_pool(provider_name)
        
        logger.info("Closed all connection pools")
    
    def get_pool_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all pools"""
        return {
            provider_name: {
                "state": pool.get_state().value,
                "metrics": pool.get_metrics().to_dict(),
                "config": {
                    "min_connections": pool.config.min_connections,
                    "max_connections": pool.config.max_connections,
                    "connection_timeout": pool.config.connection_timeout,
                }
            }
            for provider_name, pool in self._pools.items()
        }


# Global instance
_connection_pool_manager: Optional[ConnectionPoolManager] = None


def get_connection_pool_manager() -> ConnectionPoolManager:
    """Get the global connection pool manager instance"""
    global _connection_pool_manager
    if _connection_pool_manager is None:
        _connection_pool_manager = ConnectionPoolManager()
    return _connection_pool_manager