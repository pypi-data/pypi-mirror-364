"""
Cache management CLI commands
"""

import asyncio
import json
from argparse import Namespace
from typing import TYPE_CHECKING

from .base import BaseCommand
from ..utils.errors import CommandError
from ...core.cache import (
    get_cache_manager,
    get_provider_cache_manager,
    CacheConfig,
    CacheType,
    configure_cache,
)

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class CacheCommand(BaseCommand):
    """Manage InfraDSL cache"""

    @property
    def name(self) -> str:
        return "cache"

    @property
    def description(self) -> str:
        return "Manage InfraDSL cache"

    def register(self, subparsers) -> None:
        """Register cache command and subcommands"""
        parser = subparsers.add_parser(
            self.name,
            help=self.description,
            description="Manage InfraDSL intelligent caching layer",
        )

        cache_subparsers = parser.add_subparsers(dest="cache_action", help="Cache actions")

        # Cache status
        status_parser = cache_subparsers.add_parser(
            "status",
            help="Show cache status and statistics"
        )

        # Cache clear
        clear_parser = cache_subparsers.add_parser(
            "clear",
            help="Clear cache entries"
        )
        clear_parser.add_argument(
            "--type",
            choices=[t.value for t in CacheType],
            help="Clear specific cache type only"
        )
        clear_parser.add_argument(
            "--provider",
            help="Clear cache for specific provider only"
        )

        # Cache config
        config_parser = cache_subparsers.add_parser(
            "config",
            help="Configure cache settings"
        )
        config_parser.add_argument(
            "--show",
            action="store_true",
            help="Show current cache configuration"
        )
        config_parser.add_argument(
            "--ttl",
            type=int,
            metavar="SECONDS",
            help="Set default TTL for cache entries"
        )
        config_parser.add_argument(
            "--max-size",
            type=int,
            metavar="SIZE",
            help="Set maximum cache size"
        )
        config_parser.add_argument(
            "--disable",
            action="store_true",
            help="Disable caching"
        )
        config_parser.add_argument(
            "--enable",
            action="store_true",
            help="Enable caching"
        )

        # Cache stats
        stats_parser = cache_subparsers.add_parser(
            "stats",
            help="Show detailed cache statistics"
        )
        stats_parser.add_argument(
            "--json",
            action="store_true",
            help="Output statistics in JSON format"
        )

    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute cache command"""
        try:
            if not hasattr(args, 'cache_action') or args.cache_action is None:
                console.error("No cache action specified. Use --help for available actions.")
                return 1

            if args.cache_action == "status":
                return self._show_status(console)
            elif args.cache_action == "clear":
                return self._clear_cache(args, console)
            elif args.cache_action == "config":
                return self._manage_config(args, console)
            elif args.cache_action == "stats":
                return self._show_stats(args, console)
            else:
                console.error(f"Unknown cache action: {args.cache_action}")
                return 1

        except Exception as e:
            console.error(f"Cache command failed: {str(e)}")
            return 1

    def _show_status(self, console: "Console") -> int:
        """Show cache status"""
        cache_manager = get_cache_manager()
        
        # Get statistics (handle both sync and async cache managers)
        if hasattr(cache_manager, 'get_statistics_sync'):
            # PostgreSQL cache manager
            stats = cache_manager.get_statistics_sync()
            cache_type = "PostgreSQL"
        else:
            # In-memory cache manager
            stats = cache_manager.get_statistics()
            cache_type = "Memory"
        
        console.print(f"🗄️  InfraDSL Cache Status ({cache_type})\n")
        console.print(f"Cache Status: {'✅ Enabled' if cache_manager.config.enable_cache else '❌ Disabled'}")
        console.print(f"Total Entries: {stats.get('total_entries', 0)}")
        console.print(f"Hit Rate: {stats.get('hit_rate', 0):.1f}%")
        console.print(f"Cache Hits: {stats.get('hits', 0)}")
        console.print(f"Cache Misses: {stats.get('misses', 0)}")
        console.print(f"Evictions: {stats.get('evictions', 0)}")
        console.print(f"Invalidations: {stats.get('invalidations', 0)}")
        
        # Show additional PostgreSQL stats if available
        if 'cache_types' in stats:
            console.print(f"Cache Types: {stats['cache_types']}")
            console.print(f"Total Accesses: {stats['total_accesses']}")
            console.print(f"Avg Accesses per Entry: {stats['avg_accesses_per_entry']:.1f}")
        
        # Show entries by type
        entries_by_type = stats.get('entries_by_type', {})
        if entries_by_type:
            console.print("\nEntries by Type:")
            for cache_type, count in entries_by_type.items():
                console.print(f"  {cache_type}: {count}")
        
        return 0

    def _clear_cache(self, args: Namespace, console: "Console") -> int:
        """Clear cache entries"""
        cache_manager = get_cache_manager()
        provider_cache_manager = get_provider_cache_manager()
        
        # Run async cache clearing with proper event loop handling
        def run_async_operation(coro):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an event loop, we need a new thread
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, coro)
                        return future.result()
                else:
                    return loop.run_until_complete(coro)
            except RuntimeError:
                # No event loop exists, create a new one
                return asyncio.run(coro)
        
        if args.type:
            # Clear specific cache type
            cache_type = CacheType(args.type)
            if hasattr(cache_manager, 'invalidate_type'):
                run_async_operation(cache_manager.invalidate_type(cache_type))
            else:
                # For PostgreSQL cache manager that doesn't have invalidate_type
                run_async_operation(cache_manager.clear(cache_type))
            console.print(f"✅ Cleared {args.type} cache")
        elif args.provider:
            # Clear specific provider cache
            run_async_operation(provider_cache_manager.invalidate_provider_cache(args.provider))
            console.print(f"✅ Cleared cache for provider: {args.provider}")
        else:
            # Clear all cache
            run_async_operation(cache_manager.clear())
            console.print("✅ Cleared all cache")
        
        return 0

    def _manage_config(self, args: Namespace, console: "Console") -> int:
        """Manage cache configuration"""
        if args.show:
            return self._show_config(console)
        
        cache_manager = get_cache_manager()
        config = cache_manager.config
        
        # Update configuration
        if args.ttl is not None:
            # Update TTL for all cache types
            for cache_type in CacheType:
                config.ttl_config[cache_type] = args.ttl
            console.print(f"✅ Set default TTL to {args.ttl} seconds")
        
        if args.max_size is not None:
            # Update max size for all cache types
            for cache_type in CacheType:
                config.max_size_config[cache_type] = args.max_size
            console.print(f"✅ Set max cache size to {args.max_size}")
        
        if args.disable:
            config.enable_cache = False
            console.print("✅ Disabled caching")
        
        if args.enable:
            config.enable_cache = True
            console.print("✅ Enabled caching")
        
        return 0

    def _show_config(self, console: "Console") -> int:
        """Show current cache configuration"""
        cache_manager = get_cache_manager()
        config = cache_manager.config
        
        console.print("🔧 Cache Configuration\n")
        console.print(f"Enabled: {config.enable_cache}")
        console.print(f"Compression: {config.enable_compression}")
        console.print(f"Statistics: {config.enable_statistics}")
        console.print(f"Cleanup Interval: {config.cleanup_interval}s")
        
        console.print("\nTTL Configuration:")
        for cache_type, ttl in config.ttl_config.items():
            console.print(f"  {cache_type.value}: {ttl}s")
        
        console.print("\nMax Size Configuration:")
        for cache_type, max_size in config.max_size_config.items():
            console.print(f"  {cache_type.value}: {max_size}")
        
        return 0

    def _show_stats(self, args: Namespace, console: "Console") -> int:
        """Show detailed cache statistics"""
        cache_manager = get_cache_manager()
        
        # Get statistics (handle both sync and async cache managers)
        if hasattr(cache_manager, 'get_statistics_sync'):
            # PostgreSQL cache manager
            stats = cache_manager.get_statistics_sync()
        else:
            # In-memory cache manager
            stats = cache_manager.get_statistics()
        
        if args.json:
            console.print(json.dumps(stats, indent=2))
        else:
            console.print("📊 Detailed Cache Statistics\n")
            
            # Performance metrics
            console.print("Performance Metrics:")
            console.print(f"  Hit Rate: {stats.get('hit_rate', '0%')}")
            console.print(f"  Total Hits: {stats.get('hits', 0)}")
            console.print(f"  Total Misses: {stats.get('misses', 0)}")
            
            # Cache management
            console.print("\nCache Management:")
            console.print(f"  Total Entries: {stats.get('total_entries', 0)}")
            console.print(f"  Evictions: {stats.get('evictions', 0)}")
            console.print(f"  Invalidations: {stats.get('invalidations', 0)}")
            
            # Entries by type
            entries_by_type = stats.get('entries_by_type', {})
            if entries_by_type:
                console.print("\nEntries by Type:")
                for cache_type, count in entries_by_type.items():
                    console.print(f"  {cache_type}: {count}")
        
        return 0