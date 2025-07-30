"""
Simple PostgreSQL cache for CLI operations

This avoids async/event loop issues by using sync database operations
"""

import os
import json
import time
import hashlib
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 not available, falling back to memory cache")


class SimplePostgreSQLCache:
    """Simple sync PostgreSQL cache for CLI operations"""
    
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.getenv(
            "INFRADSL_DATABASE_URL",
            "postgresql://infradsl:infradsl@localhost:5432/infradsl"
        )
        self._connection = None
        self._ensure_table()
    
    def _get_connection(self):
        """Get database connection"""
        if not PSYCOPG2_AVAILABLE:
            return None
            
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(self.db_url)
                self._connection.autocommit = True
            except Exception as e:
                logger.error(f"Failed to connect to PostgreSQL: {e}")
                return None
        return self._connection
    
    def _ensure_table(self):
        """Ensure cache table exists"""
        conn = self._get_connection()
        if not conn:
            return
            
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS infradsl_resource_cache (
                        cache_key TEXT PRIMARY KEY,
                        provider TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        resource_id TEXT NOT NULL,
                        state_data JSONB NOT NULL,
                        fingerprint TEXT NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        last_seen TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        ttl_seconds INTEGER NOT NULL DEFAULT 300
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_resource_cache_provider 
                    ON infradsl_resource_cache(provider);
                    
                    CREATE INDEX IF NOT EXISTS idx_resource_cache_fingerprint 
                    ON infradsl_resource_cache(fingerprint);
                    
                    CREATE INDEX IF NOT EXISTS idx_resource_cache_last_seen 
                    ON infradsl_resource_cache(last_seen);
                """)
        except Exception as e:
            logger.error(f"Failed to create cache table: {e}")
    
    def _generate_fingerprint(self, provider: str, resource_type: str, resource_name: str, 
                            project: str = "", environment: str = "", region: str = "") -> str:
        """Generate deterministic fingerprint for resource"""
        components = {
            "provider": provider,
            "resource_type": resource_type,
            "resource_name": resource_name,
            "project": project,
            "environment": environment,
            "region": region
        }
        fingerprint_str = json.dumps(components, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
    
    def cache_resource_state(self, provider: str, resource_type: str, resource_id: str,
                           resource_name: str, state_data: Dict[str, Any],
                           project: str = "", environment: str = "", region: str = "",
                           ttl_seconds: int = 3600) -> None:
        """Cache resource state"""
        conn = self._get_connection()
        if not conn:
            return
            
        fingerprint = self._generate_fingerprint(
            provider, resource_type, resource_name, project, environment, region
        )
        cache_key = f"{provider}:{resource_type}:{resource_id}"
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO infradsl_resource_cache 
                    (cache_key, provider, resource_type, resource_id, state_data, 
                     fingerprint, ttl_seconds)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (cache_key) 
                    DO UPDATE SET
                        state_data = EXCLUDED.state_data,
                        last_seen = NOW(),
                        ttl_seconds = EXCLUDED.ttl_seconds
                """, (cache_key, provider, resource_type, resource_id, 
                     json.dumps(state_data), fingerprint, ttl_seconds))
                
            logger.debug(f"Cached resource state: {fingerprint}")
        except Exception as e:
            logger.error(f"Failed to cache resource state: {e}")
    
    def get_resource_by_fingerprint(self, provider: str, resource_type: str, 
                                  resource_name: str, project: str = "", 
                                  environment: str = "", region: str = "") -> Optional[Dict[str, Any]]:
        """Get cached resource by fingerprint"""
        conn = self._get_connection()
        if not conn:
            return None
            
        fingerprint = self._generate_fingerprint(
            provider, resource_type, resource_name, project, environment, region
        )
        
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT state_data, created_at, last_seen
                    FROM infradsl_resource_cache
                    WHERE fingerprint = %s
                    AND last_seen + (ttl_seconds || ' seconds')::interval > NOW()
                    ORDER BY last_seen DESC
                    LIMIT 1
                """, (fingerprint,))
                
                row = cur.fetchone()
                if row:
                    logger.debug(f"Cache HIT for fingerprint: {fingerprint}")
                    return dict(row['state_data'])
                else:
                    logger.debug(f"Cache MISS for fingerprint: {fingerprint}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get cached resource: {e}")
            return None
    
    def invalidate_resource(self, provider: str, resource_type: str, resource_id: str) -> None:
        """Invalidate cached resource"""
        conn = self._get_connection()
        if not conn:
            return
            
        cache_key = f"{provider}:{resource_type}:{resource_id}"
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM infradsl_resource_cache 
                    WHERE cache_key = %s
                """, (cache_key,))
                
                rows_deleted = cur.rowcount
                
            if rows_deleted > 0:
                logger.debug(f"Invalidated cache for: {cache_key} ({rows_deleted} row(s) deleted)")
            else:
                logger.warning(f"No cache entry found for: {cache_key}")
        except Exception as e:
            logger.error(f"Failed to invalidate cache for {cache_key}: {e}")
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries"""
        conn = self._get_connection()
        if not conn:
            return 0
            
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM infradsl_resource_cache
                    WHERE last_seen + (ttl_seconds || ' seconds')::interval < NOW()
                """)
                return cur.rowcount
        except Exception as e:
            logger.error(f"Failed to cleanup expired cache: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        conn = self._get_connection()
        if not conn:
            return {"total_entries": 0, "providers": []}
            
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_entries,
                        COUNT(DISTINCT provider) as provider_count,
                        COUNT(DISTINCT resource_type) as resource_type_count,
                        MIN(created_at) as oldest_entry,
                        MAX(last_seen) as newest_entry
                    FROM infradsl_resource_cache
                    WHERE last_seen + (ttl_seconds || ' seconds')::interval > NOW()
                """)
                
                stats = dict(cur.fetchone())
                
                # Get breakdown by provider
                cur.execute("""
                    SELECT provider, COUNT(*) as count
                    FROM infradsl_resource_cache
                    WHERE last_seen + (ttl_seconds || ' seconds')::interval > NOW()
                    GROUP BY provider
                """)
                
                stats['providers'] = {row['provider']: row['count'] for row in cur.fetchall()}
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"total_entries": 0, "providers": []}
    
    def close(self):
        """Close database connection"""
        if self._connection and not self._connection.closed:
            self._connection.close()


# Global instance
_simple_cache: Optional[SimplePostgreSQLCache] = None


def get_simple_cache() -> SimplePostgreSQLCache:
    """Get global simple cache instance"""
    global _simple_cache
    if _simple_cache is None:
        _simple_cache = SimplePostgreSQLCache()
    return _simple_cache