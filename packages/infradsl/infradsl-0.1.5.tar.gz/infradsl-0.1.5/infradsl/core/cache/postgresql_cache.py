"""
PostgreSQL-backed cache manager for InfraDSL

This module provides a persistent cache implementation using PostgreSQL
for storing API responses, resource discovery results, and plan caches.
"""

import asyncio
import json
import time
import logging
import os
from typing import Any, Dict, Optional
from datetime import datetime, timezone

import asyncpg

from .cache_manager import CacheConfig, CacheType, CacheEntry
from ..performance.postgresql import PostgreSQLConfig, PostgreSQLConnectionPool

logger = logging.getLogger(__name__)


class PostgreSQLCacheManager:
    """PostgreSQL-backed cache manager for persistent caching"""

    def __init__(
        self, config: Optional[CacheConfig] = None, db_url: Optional[str] = None
    ):
        self.config = config or CacheConfig()
        self.db_url = db_url or os.getenv(
            "INFRADSL_DATABASE_URL",
            "postgresql://infradsl:infradsl@localhost:5432/infradsl",
        )
        self._pool: Optional[asyncpg.Pool] = None
        self.statistics = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
        }
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._initialized = False

    async def initialize(self):
        """Initialize PostgreSQL connection pool and create tables"""
        if self._initialized:
            return

        try:
            # Create connection pool
            self._pool = await asyncpg.create_pool(
                self.db_url, min_size=2, max_size=10, command_timeout=30
            )

            # Create cache table if it doesn't exist
            await self._create_tables()

            # Start cleanup task
            self._start_cleanup_task()

            self._initialized = True
            logger.info("PostgreSQL cache manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL cache manager: {e}")
            raise

    async def _create_tables(self):
        """Create cache tables if they don't exist"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS infradsl_cache (
            cache_key TEXT PRIMARY KEY,
            cache_type TEXT NOT NULL,
            value_data JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            ttl_seconds INTEGER NOT NULL,
            access_count INTEGER DEFAULT 0,
            last_access TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_cache_type ON infradsl_cache(cache_type);
        CREATE INDEX IF NOT EXISTS idx_created_at ON infradsl_cache(created_at);
        CREATE INDEX IF NOT EXISTS idx_last_access ON infradsl_cache(last_access);
        """

        async with self._pool.acquire() as conn:
            await conn.execute(create_table_sql)

    def _start_cleanup_task(self):
        """Start the background cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        """Background task to clean up expired cache entries"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup: {e}")

    async def _cleanup_expired(self):
        """Remove expired cache entries"""
        if not self._pool:
            return

        try:
            cleanup_sql = """
            DELETE FROM infradsl_cache
            WHERE created_at + (ttl_seconds || ' seconds')::interval < NOW()
            """

            async with self._pool.acquire() as conn:
                result = await conn.execute(cleanup_sql)
                deleted_count = (
                    int(result.split()[-1])
                    if result.startswith("DELETE")
                    else 0
                )
                if deleted_count > 0:
                    self.statistics["evictions"] += deleted_count
                    logger.debug(
                        f"Cleaned up {deleted_count} expired cache entries"
                    )

        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")

    def _generate_cache_key(
        self, cache_type: CacheType, *args, **kwargs
    ) -> str:
        """Generate a cache key from arguments"""
        import hashlib

        key_data = {"type": cache_type.value, "args": args, "kwargs": kwargs}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get(
        self, cache_type: CacheType, *args, **kwargs
    ) -> Optional[Any]:
        """Get value from cache"""
        if not self.config.enable_cache:
            return None
            
        # Ensure we're initialized
        if not self._initialized:
            await self.initialize()
            
        if not self._pool:
            return None

        cache_key = self._generate_cache_key(cache_type, *args, **kwargs)

        try:
            async with self._pool.acquire() as conn:
                # Get cache entry and check if it's expired
                query = """
                SELECT value_data, created_at, ttl_seconds, access_count
                FROM infradsl_cache
                WHERE cache_key = $1
                AND created_at + (ttl_seconds || ' seconds')::interval > NOW()
                """

                row = await conn.fetchrow(query, cache_key)

                if row is None:
                    self.statistics["misses"] += 1
                    return None

                # Update access count and last access time
                await conn.execute(
                    "UPDATE infradsl_cache SET access_count = access_count + 1, last_access = NOW() WHERE cache_key = $1",
                    cache_key,
                )

                self.statistics["hits"] += 1
                return row["value_data"]

        except Exception as e:
            logger.error(f"Error getting cache entry {cache_key}: {e}")
            self.statistics["misses"] += 1
            return None

    async def set(
        self, cache_type: CacheType, value: Any, *args, **kwargs
    ) -> None:
        """Set value in cache"""
        if not self.config.enable_cache:
            return
            
        # Ensure we're initialized
        if not self._initialized:
            await self.initialize()
            
        if not self._pool:
            return

        cache_key = self._generate_cache_key(cache_type, *args, **kwargs)
        ttl = self.config.get_ttl(cache_type)

        try:
            async with self._pool.acquire() as conn:
                # Insert or update cache entry
                query = """
                INSERT INTO infradsl_cache (cache_key, cache_type, value_data, ttl_seconds)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (cache_key)
                DO UPDATE SET
                    value_data = EXCLUDED.value_data,
                    created_at = NOW(),
                    ttl_seconds = EXCLUDED.ttl_seconds,
                    access_count = 0,
                    last_access = NOW()
                """

                await conn.execute(
                    query,
                    cache_key,
                    cache_type.value,
                    json.dumps(value, default=str),
                    ttl,
                )

        except Exception as e:
            logger.error(f"Error setting cache entry {cache_key}: {e}")

    async def append_to_list(self, list_key: str, item: Any) -> None:
        """Append an item to a list cache entry (for discovery cache)"""
        if not self._pool:
            logger.warning("PostgreSQL pool not available for list append")
            return

        try:
            async with self._pool.acquire() as conn:
                # Check if list exists in the main cache table
                existing = await conn.fetchval(
                    "SELECT value_data FROM infradsl_cache WHERE cache_key = $1",
                    list_key
                )
                
                if existing:
                    # Parse existing list and append
                    current_list = json.loads(existing) if isinstance(existing, str) else existing
                    if not isinstance(current_list, list):
                        current_list = [current_list]
                    current_list.append(item)
                else:
                    # Create new list
                    current_list = [item]
                
                # Update cache with new list using the main cache table structure
                await conn.execute(
                    """
                    INSERT INTO infradsl_cache (cache_key, cache_type, value_data, ttl_seconds)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (cache_key) DO UPDATE SET
                        value_data = EXCLUDED.value_data,
                        created_at = NOW(),
                        access_count = 0,
                        last_access = NOW()
                    """,
                    list_key,
                    "discovery",  # Default type for discovery lists
                    json.dumps(current_list),
                    3600  # 1 hour TTL
                )
                
                logger.debug(f"Appended item to list cache {list_key}")

        except Exception as e:
            logger.error(f"Error appending to list cache {list_key}: {e}")

    async def invalidate(self, cache_type: CacheType, *args, **kwargs) -> None:
        """Invalidate specific cache entry"""
        if not self._pool:
            return

        cache_key = self._generate_cache_key(cache_type, *args, **kwargs)

        try:
            async with self._pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM infradsl_cache WHERE cache_key = $1", cache_key
                )
                if result.startswith("DELETE") and int(result.split()[-1]) > 0:
                    self.statistics["invalidations"] += 1

        except Exception as e:
            logger.error(f"Error invalidating cache entry {cache_key}: {e}")

    async def clear(self, cache_type: Optional[CacheType] = None) -> None:
        """Clear cache entries"""
        if not self._pool:
            return

        try:
            async with self._pool.acquire() as conn:
                if cache_type:
                    result = await conn.execute(
                        "DELETE FROM infradsl_cache WHERE cache_type = $1",
                        cache_type.value,
                    )
                else:
                    result = await conn.execute("DELETE FROM infradsl_cache")

                deleted_count = (
                    int(result.split()[-1])
                    if result.startswith("DELETE")
                    else 0
                )
                self.statistics["invalidations"] += deleted_count
                logger.info(f"Cleared {deleted_count} cache entries")

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics (async version)"""
        stats = self.statistics.copy()

        if self._pool:
            try:
                async with self._pool.acquire() as conn:
                    # Get database stats
                    db_stats = await conn.fetchrow(
                        """
                        SELECT
                            COUNT(*) as total_entries,
                            COUNT(DISTINCT cache_type) as cache_types,
                            SUM(access_count) as total_accesses,
                            AVG(access_count) as avg_accesses_per_entry
                        FROM infradsl_cache
                    """
                    )

                    if db_stats:
                        stats.update(
                            {
                                "total_entries": db_stats["total_entries"],
                                "cache_types": db_stats["cache_types"],
                                "total_accesses": db_stats["total_accesses"]
                                or 0,
                                "avg_accesses_per_entry": float(
                                    db_stats["avg_accesses_per_entry"] or 0
                                ),
                            }
                        )

                        # Calculate hit rate
                        total_requests = stats["hits"] + stats["misses"]
                        stats["hit_rate"] = (
                            (stats["hits"] / total_requests * 100)
                            if total_requests > 0
                            else 0
                        )

            except Exception as e:
                logger.error(f"Error getting database statistics: {e}")

        return stats

    def get_statistics_sync(self) -> Dict[str, Any]:
        """Get cache statistics (sync version for CLI compatibility)"""
        try:
            # Handle different event loop scenarios
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an event loop, we need a new thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.get_statistics())
                        return future.result()
                else:
                    return loop.run_until_complete(self.get_statistics())
            except RuntimeError:
                # No event loop exists, create a new one
                return asyncio.run(self.get_statistics())
        except Exception as e:
            logger.error(f"Error getting statistics synchronously: {e}")
            # Return basic stats from memory
            total_requests = self.statistics["hits"] + self.statistics["misses"]
            hit_rate = (
                (self.statistics["hits"] / total_requests * 100)
                if total_requests > 0
                else 0
            )

            return {
                **self.statistics,
                "total_entries": 0,
                "cache_types": 0,
                "total_accesses": 0,
                "avg_accesses_per_entry": 0.0,
                "hit_rate": hit_rate,
            }

    async def shutdown(self):
        """Shutdown cache manager"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        if self._pool:
            await self._pool.close()

        self._initialized = False
        logger.info("PostgreSQL cache manager shutdown complete")


# Global PostgreSQL cache manager instance
_postgresql_cache_manager: Optional[PostgreSQLCacheManager] = None


async def get_postgresql_cache_manager() -> PostgreSQLCacheManager:
    """Get the global PostgreSQL cache manager instance"""
    global _postgresql_cache_manager

    if _postgresql_cache_manager is None:
        _postgresql_cache_manager = PostgreSQLCacheManager()
        await _postgresql_cache_manager.initialize()

    return _postgresql_cache_manager


def is_postgresql_cache_enabled() -> bool:
    """Check if PostgreSQL cache is enabled via environment variables"""
    return (
        os.getenv("INFRADSL_CACHE_ENABLED", "false").lower() == "true"
        and os.getenv("INFRADSL_CACHE_BACKEND", "memory").lower()
        == "postgresql"
    )
