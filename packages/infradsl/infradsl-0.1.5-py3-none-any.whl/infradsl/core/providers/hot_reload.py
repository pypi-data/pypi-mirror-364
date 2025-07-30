"""
Hot-Reloading System for InfraDSL Providers

This module implements runtime provider reloading without service restart,
with safe provider swapping and rollback mechanisms.
"""

import asyncio
import importlib
import importlib.util
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable, Any, Type
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from infradsl.core.interfaces.provider import ProviderInterface
from .registry import EnhancedProviderRegistry, ProviderInfo, get_enhanced_registry

logger = logging.getLogger(__name__)


class ReloadStatus(Enum):
    """Provider reload status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ReloadEvent:
    """Provider reload event"""
    provider_name: str
    old_version: Optional[str]
    new_version: str
    status: ReloadStatus
    timestamp: datetime
    error: Optional[str] = None
    rollback_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "provider_name": self.provider_name,
            "old_version": self.old_version,
            "new_version": self.new_version,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "rollback_reason": self.rollback_reason,
            "metadata": self.metadata,
        }


class ProviderWatcher(FileSystemEventHandler):
    """File system watcher for provider changes"""
    
    def __init__(self, hot_reload_manager: "HotReloadManager"):
        self.hot_reload_manager = hot_reload_manager
        self.debounce_delay = 1.0  # seconds
        self.pending_reloads: Dict[str, asyncio.Task] = {}
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        
        # Only handle Python files
        if file_path.suffix != ".py":
            return
        
        # Find which provider this file belongs to
        provider_name = self._get_provider_name(file_path)
        if not provider_name:
            return
        
        # Debounce rapid file changes
        if provider_name in self.pending_reloads:
            self.pending_reloads[provider_name].cancel()
        
        self.pending_reloads[provider_name] = asyncio.create_task(
            self._debounced_reload(provider_name, file_path)
        )
    
    async def _debounced_reload(self, provider_name: str, file_path: Path):
        """Debounced reload with delay"""
        await asyncio.sleep(self.debounce_delay)
        
        try:
            await self.hot_reload_manager.reload_provider(provider_name)
        except Exception as e:
            logger.error(f"Failed to reload provider {provider_name}: {e}")
        finally:
            # Clean up
            if provider_name in self.pending_reloads:
                del self.pending_reloads[provider_name]
    
    def _get_provider_name(self, file_path: Path) -> Optional[str]:
        """Get provider name from file path"""
        # This is a simplified version - in practice, you'd have a more
        # sophisticated mapping from file paths to provider names
        
        # Look for provider.py files
        if file_path.name == "provider.py":
            return file_path.parent.name
        
        # Look for files in provider directories
        for part in file_path.parts:
            if part.startswith("provider_"):
                return part.replace("provider_", "")
        
        return None


class HotReloadManager:
    """
    Hot-reloading manager for InfraDSL providers
    
    Features:
    - Runtime provider reloading without service restart
    - Safe provider swapping with rollback
    - Provider health monitoring
    - Automatic failover mechanisms
    - Lifecycle management
    """
    
    def __init__(
        self,
        registry: Optional[EnhancedProviderRegistry] = None,
        watch_directories: Optional[List[Path]] = None,
        enable_auto_reload: bool = True,
        health_check_interval: float = 30.0,
        max_reload_attempts: int = 3,
    ):
        self.registry = registry or get_enhanced_registry()
        self.watch_directories = watch_directories or []
        self.enable_auto_reload = enable_auto_reload
        self.health_check_interval = health_check_interval
        self.max_reload_attempts = max_reload_attempts
        
        # State tracking
        self.reload_history: List[ReloadEvent] = []
        self.active_providers: Dict[str, ProviderInfo] = {}
        self.provider_backups: Dict[str, ProviderInfo] = {}
        self.reload_locks: Dict[str, asyncio.Lock] = {}
        
        # File system watching
        self.observer: Optional[Observer] = None
        self.watcher: Optional[ProviderWatcher] = None
        
        # Health monitoring
        self.health_check_task: Optional[asyncio.Task] = None
        self.provider_health: Dict[str, Dict[str, Any]] = {}
        
        # Event handlers
        self.reload_handlers: List[Callable[[ReloadEvent], None]] = []
        self.health_handlers: List[Callable[[str, Dict[str, Any]], None]] = []
    
    async def start(self):
        """Start the hot-reload manager"""
        logger.info("Starting hot-reload manager")
        
        # Initialize active providers
        self._initialize_active_providers()
        
        # Start file system watching
        if self.enable_auto_reload:
            self._start_file_watching()
        
        # Start health monitoring
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("Hot-reload manager started")
    
    async def stop(self):
        """Stop the hot-reload manager"""
        logger.info("Stopping hot-reload manager")
        
        # Stop file watching
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        # Stop health monitoring
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Hot-reload manager stopped")
    
    async def reload_provider(
        self,
        provider_name: str,
        version: Optional[str] = None,
        force: bool = False
    ) -> ReloadEvent:
        """Reload a specific provider"""
        # Get reload lock for this provider
        if provider_name not in self.reload_locks:
            self.reload_locks[provider_name] = asyncio.Lock()
        
        async with self.reload_locks[provider_name]:
            return await self._do_reload_provider(provider_name, version, force)
    
    async def _do_reload_provider(
        self,
        provider_name: str,
        version: Optional[str] = None,
        force: bool = False
    ) -> ReloadEvent:
        """Internal provider reload implementation"""
        old_version = None
        
        # Get current provider info
        if provider_name in self.active_providers:
            old_version = self.active_providers[provider_name].version
        
        # Create reload event
        reload_event = ReloadEvent(
            provider_name=provider_name,
            old_version=old_version,
            new_version=version or "unknown",
            status=ReloadStatus.PENDING,
            timestamp=datetime.now(timezone.utc),
        )
        
        try:
            # Update status
            reload_event.status = ReloadStatus.IN_PROGRESS
            self._notify_reload_handlers(reload_event)
            
            # Backup current provider if exists
            if provider_name in self.active_providers:
                self.provider_backups[provider_name] = self.active_providers[provider_name]
            
            # Reload the provider module
            new_provider_info = await self._reload_provider_module(provider_name, version)
            
            if not new_provider_info:
                raise ValueError(f"Failed to load provider {provider_name}")
            
            # Update version in event
            reload_event.new_version = new_provider_info.version
            
            # Health check new provider
            if not force:
                health_ok = await self._health_check_provider(provider_name, new_provider_info)
                if not health_ok:
                    raise ValueError(f"Health check failed for {provider_name}")
            
            # Activate new provider
            self.active_providers[provider_name] = new_provider_info
            
            # Register with registry
            self.registry.register_versioned(new_provider_info, activate=True)
            
            # Success
            reload_event.status = ReloadStatus.SUCCESS
            logger.info(f"Successfully reloaded provider {provider_name} v{new_provider_info.version}")
            
        except Exception as e:
            # Reload failed - attempt rollback
            reload_event.status = ReloadStatus.FAILED
            reload_event.error = str(e)
            
            logger.error(f"Failed to reload provider {provider_name}: {e}")
            
            # Attempt rollback
            if provider_name in self.provider_backups:
                try:
                    await self._rollback_provider(provider_name)
                    reload_event.status = ReloadStatus.ROLLED_BACK
                    reload_event.rollback_reason = f"Reload failed: {e}"
                except Exception as rollback_error:
                    logger.error(f"Rollback failed for {provider_name}: {rollback_error}")
                    reload_event.rollback_reason = f"Rollback failed: {rollback_error}"
        
        # Record event
        self.reload_history.append(reload_event)
        self._notify_reload_handlers(reload_event)
        
        return reload_event
    
    async def _reload_provider_module(
        self,
        provider_name: str,
        version: Optional[str] = None
    ) -> Optional[ProviderInfo]:
        """Reload a provider module from disk"""
        try:
            # Find provider directory
            provider_dir = self._find_provider_directory(provider_name)
            if not provider_dir:
                logger.error(f"Provider directory not found for {provider_name}")
                return None
            
            # Load provider module
            module_path = provider_dir / "provider.py"
            if not module_path.exists():
                logger.error(f"Provider module not found: {module_path}")
                return None
            
            # Load module spec
            spec = importlib.util.spec_from_file_location(
                f"provider_{provider_name}",
                module_path
            )
            
            if not spec or not spec.loader:
                logger.error(f"Failed to load module spec for {provider_name}")
                return None
            
            # Create module
            module = importlib.util.module_from_spec(spec)
            
            # Execute module
            spec.loader.exec_module(module)
            
            # Find provider class
            provider_class = self._find_provider_class(module)
            if not provider_class:
                logger.error(f"Provider class not found in {module_path}")
                return None
            
            # Get metadata
            if not hasattr(provider_class, "METADATA"):
                logger.error(f"Provider class missing METADATA in {module_path}")
                return None
            
            metadata = provider_class.METADATA
            
            # Create provider info
            provider_info = ProviderInfo(
                metadata=metadata,
                provider_class=provider_class,
                version=version or metadata.version,
                published_at=datetime.now(timezone.utc),
            )
            
            return provider_info
            
        except Exception as e:
            logger.error(f"Failed to reload provider module {provider_name}: {e}")
            return None
    
    def _find_provider_directory(self, provider_name: str) -> Optional[Path]:
        """Find the directory containing a provider"""
        for watch_dir in self.watch_directories:
            provider_dir = watch_dir / provider_name
            if provider_dir.exists() and provider_dir.is_dir():
                return provider_dir
        
        # Check registry base path
        registry_path = self.registry.base_path / provider_name
        if registry_path.exists() and registry_path.is_dir():
            # Find latest version
            versions = [d for d in registry_path.iterdir() if d.is_dir()]
            if versions:
                # Sort by version and get latest
                latest = max(versions, key=lambda p: p.name)
                return latest
        
        return None
    
    def _find_provider_class(self, module) -> Optional[Type[ProviderInterface]]:
        """Find the provider class in a module"""
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            if (isinstance(attr, type) and
                issubclass(attr, ProviderInterface) and
                attr != ProviderInterface):
                return attr
        
        return None
    
    async def _rollback_provider(self, provider_name: str):
        """Rollback to previous provider version"""
        if provider_name not in self.provider_backups:
            raise ValueError(f"No backup available for provider {provider_name}")
        
        backup = self.provider_backups[provider_name]
        
        # Restore active provider
        self.active_providers[provider_name] = backup
        
        # Re-register with registry
        self.registry.register_versioned(backup, activate=True)
        
        logger.info(f"Rolled back provider {provider_name} to v{backup.version}")
    
    async def _health_check_provider(
        self,
        provider_name: str,
        provider_info: ProviderInfo
    ) -> bool:
        """Health check a provider"""
        try:
            # Create provider instance for testing
            from infradsl.core.interfaces.provider import ProviderConfig, ProviderType
            
            # Create minimal config for testing
            test_config = ProviderConfig(
                type=ProviderType.CUSTOM,
                credentials={}
            )
            
            # Try to instantiate the provider
            provider_instance = provider_info.provider_class(test_config)
            
            # Run basic health checks
            if hasattr(provider_instance, 'health_check'):
                health_result = await provider_instance.health_check()
                return health_result
            
            # If no health check method, assume healthy if instantiation succeeded
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for {provider_name}: {e}")
            return False
    
    async def _health_check_loop(self):
        """Background health checking loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._check_all_provider_health()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
    
    async def _check_all_provider_health(self):
        """Check health of all active providers"""
        for provider_name, provider_info in self.active_providers.items():
            try:
                health_status = {
                    "provider_name": provider_name,
                    "version": provider_info.version,
                    "timestamp": datetime.now(timezone.utc),
                    "healthy": True,
                    "details": {},
                }
                
                # Run health check
                healthy = await self._health_check_provider(provider_name, provider_info)
                health_status["healthy"] = healthy
                
                if not healthy:
                    health_status["details"]["error"] = "Health check failed"
                    
                    # Consider automatic failover or reload
                    if self.enable_auto_reload:
                        logger.warning(f"Provider {provider_name} unhealthy, considering reload")
                
                # Update health status
                self.provider_health[provider_name] = health_status
                
                # Notify handlers
                self._notify_health_handlers(provider_name, health_status)
                
            except Exception as e:
                logger.error(f"Health check error for {provider_name}: {e}")
    
    def _initialize_active_providers(self):
        """Initialize active providers from registry"""
        for provider_name, version in self.registry._active_versions.items():
            provider_info = self.registry.get_provider_info(provider_name, version)
            if provider_info:
                self.active_providers[provider_name] = provider_info
    
    def _start_file_watching(self):
        """Start file system watching"""
        if not self.watch_directories:
            return
        
        self.observer = Observer()
        self.watcher = ProviderWatcher(self)
        
        for watch_dir in self.watch_directories:
            if watch_dir.exists():
                self.observer.schedule(
                    self.watcher,
                    str(watch_dir),
                    recursive=True
                )
                logger.info(f"Watching directory: {watch_dir}")
        
        self.observer.start()
    
    def add_reload_handler(self, handler: Callable[[ReloadEvent], None]):
        """Add a reload event handler"""
        self.reload_handlers.append(handler)
    
    def add_health_handler(self, handler: Callable[[str, Dict[str, Any]], None]):
        """Add a health check handler"""
        self.health_handlers.append(handler)
    
    def _notify_reload_handlers(self, event: ReloadEvent):
        """Notify reload event handlers"""
        for handler in self.reload_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in reload handler: {e}")
    
    def _notify_health_handlers(self, provider_name: str, health_status: Dict[str, Any]):
        """Notify health event handlers"""
        for handler in self.health_handlers:
            try:
                handler(provider_name, health_status)
            except Exception as e:
                logger.error(f"Error in health handler: {e}")
    
    def get_reload_history(self, provider_name: Optional[str] = None) -> List[ReloadEvent]:
        """Get reload history"""
        if provider_name:
            return [event for event in self.reload_history if event.provider_name == provider_name]
        return self.reload_history.copy()
    
    def get_provider_health(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Get provider health status"""
        if provider_name:
            return self.provider_health.get(provider_name, {})
        return self.provider_health.copy()


# Global hot-reload manager instance
_hot_reload_manager = None


def get_hot_reload_manager() -> HotReloadManager:
    """Get the global hot-reload manager instance"""
    global _hot_reload_manager
    if _hot_reload_manager is None:
        _hot_reload_manager = HotReloadManager()
    return _hot_reload_manager