"""
Change Executor - applies planned changes with dependency resolution
"""

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, Dict, List
from argparse import Namespace

from ....core.nexus.engine import NexusEngine
from ....core.nexus.lifecycle import LifecycleManager
from ....core.services.dependency_resolver import DependencyResolver
from ....core.hooks.lifecycle_hooks import trigger_lifecycle_event, LifecycleEvent
from .cache_manager import CacheManager

if TYPE_CHECKING:
    from ...utils.output import Console

logger = logging.getLogger(__name__)


class ChangeExecutor:
    """Executes planned changes with proper dependency resolution"""

    def __init__(self):
        self.cache_manager = CacheManager()

    def apply_changes_with_dependencies(
        self,
        changes: Dict[str, List[Any]],
        engine: NexusEngine,
        lifecycle_manager: LifecycleManager,
        console: "Console",
        args: Namespace,
    ) -> int:
        """Apply the planned changes with dependency resolution"""
        console.info("\nApplying changes...")

        start_time = time.time()
        applied_count = 0
        failed_count = 0

        # Collect all resources that need to be created or updated
        resources_to_process = []
        resources_to_process.extend(changes.get("create", []))
        resources_to_process.extend(changes.get("update", []))
        resources_to_process.extend(changes.get("replace", []))

        if resources_to_process:
            # Use dependency resolver to determine correct order
            try:
                resolver = DependencyResolver()
                resolver.add_resources(resources_to_process)

                # Get creation order based on dependencies
                ordered_resources = resolver.resolve_creation_order()

                console.info(f"Creating {len(ordered_resources)} resources...")

                # Apply resources in dependency order
                for resource in ordered_resources:
                    action = self._get_action_for_resource(resource, changes)

                    try:
                        with console.status(f"{action.title()}ing {resource.name}..."):
                            result = self._apply_resource(
                                resource, action, engine, lifecycle_manager
                            )

                        if result:
                            console.success(f"{action.title()}d {resource.name}")
                            applied_count += 1
                        else:
                            console.error(f"Failed to {action} {resource.name}")
                            failed_count += 1

                    except Exception as e:
                        console.error(f"Error {action}ing {resource.name}: {e}")
                        if console.verbosity >= 2:
                            import traceback
                            console.error(traceback.format_exc())
                        failed_count += 1

            except ValueError as e:
                # Dependency resolution failed (likely circular dependency)
                console.error(f"Dependency resolution failed: {e}")
                return 1

        # Handle deletions separately (in reverse dependency order)
        if changes.get("delete"):
            console.info(f"\nDeleting {len(changes['delete'])} resources...")

            try:
                resolver = DependencyResolver()
                resolver.add_resources(changes["delete"])

                # Get destruction order (reverse of creation order)
                ordered_resources = resolver.resolve_destruction_order()

                for resource in ordered_resources:
                    try:
                        with console.status(f"Deleting {resource.name}..."):
                            result = self._apply_resource(
                                resource, "delete", engine, lifecycle_manager
                            )

                        if result:
                            console.success(f"Deleted {resource.name}")
                            applied_count += 1
                        else:
                            console.error(f"Failed to delete {resource.name}")
                            failed_count += 1

                    except Exception as e:
                        console.error(f"Error deleting {resource.name}: {e}")
                        if console.verbosity >= 2:
                            import traceback
                            console.error(traceback.format_exc())
                        failed_count += 1

            except ValueError as e:
                # Dependency resolution failed
                console.error(f"Dependency resolution failed for deletions: {e}")
                return 1

        # Summary
        duration = time.time() - start_time
        console.info(f"\nApply completed in {duration:.1f}s")
        console.info(f"Resources: {applied_count} applied, {failed_count} failed")

        if failed_count > 0:
            console.error(f"Apply completed with {failed_count} errors")
            return 1
        else:
            console.success("Apply completed successfully")
            return 0

    def _get_action_for_resource(
        self, resource: Any, changes: Dict[str, List[Any]]
    ) -> str:
        """Get the action type for a resource"""
        if resource in changes.get("create", []):
            return "create"
        elif resource in changes.get("update", []):
            return "update"
        elif resource in changes.get("replace", []):
            return "replace"
        else:
            return "create"  # Default fallback

    def _apply_resource(
        self,
        resource: Any,
        action: str,
        engine: NexusEngine,
        lifecycle_manager: LifecycleManager,
    ) -> bool:
        """Apply a single resource change"""
        try:
            if action == "create":
                # Register resource with engine first
                engine.register_resource(resource)

                # Debug: Check if provider is attached
                logger.debug(
                    f"Resource {resource.name} provider: {type(resource._provider).__name__ if resource._provider else 'None'}"
                )

                # Use the resource's create method directly
                resource.create()

                # Trigger after_create lifecycle hook
                try:
                    asyncio.run(
                        trigger_lifecycle_event(LifecycleEvent.AFTER_CREATE, resource)
                    )
                except Exception as hook_error:
                    import traceback
                    traceback.print_exc()
                    logger.debug(f"Lifecycle hook error: {hook_error}")

                # Add created resource to cache
                self.cache_manager.update_cache_after_create(resource)

                return True

            elif action == "update":
                # Use the resource's reconcile method
                current_state = resource._get_current_state()
                if current_state is not None:
                    resource._reconcile(current_state)

                    # Trigger after_update lifecycle hook
                    try:
                        asyncio.run(
                            trigger_lifecycle_event(
                                LifecycleEvent.AFTER_UPDATE, resource
                            )
                        )
                    except Exception as hook_error:
                        logger.debug(f"Lifecycle hook error: {hook_error}")

                    # Update cache after successful update
                    self.cache_manager.update_cache_after_update(resource)

                    return True
                return False

            elif action == "replace":
                # Delete then create - for clean disk configuration

                # First destroy the existing resource
                if resource.status.cloud_id:
                    print(
                        f"[DEBUG] Destroying existing resource with cloud_id: {resource.status.cloud_id}"
                    )
                    resource.destroy()

                    # Trigger after_destroy lifecycle hook
                    try:
                        asyncio.run(
                            trigger_lifecycle_event(
                                LifecycleEvent.AFTER_DESTROY, resource
                            )
                        )
                    except Exception as hook_error:
                        logger.debug(f"Lifecycle hook error: {hook_error}")

                    # Remove from cache after destroy
                    self.cache_manager.remove_from_cache(resource)
                else:
                    resource.create()

                # Trigger after_create lifecycle hook for replaced resource
                try:
                    asyncio.run(
                        trigger_lifecycle_event(LifecycleEvent.AFTER_CREATE, resource)
                    )
                except Exception as hook_error:
                    logger.debug(f"Lifecycle hook error: {hook_error}")

                # Add replaced resource to cache
                self.cache_manager.update_cache_after_create(resource)

                return True

            elif action == "delete":
                resource.destroy()

                # Trigger after_destroy lifecycle hook
                try:
                    asyncio.run(
                        trigger_lifecycle_event(LifecycleEvent.AFTER_DESTROY, resource)
                    )
                except Exception as hook_error:
                    logger.debug(f"Lifecycle hook error: {hook_error}")

                # Remove from cache after successful deletion
                self.cache_manager.remove_from_cache(resource)

                return True

            return False

        except Exception as e:
            # Log the error but don't re-raise to allow other resources to be processed
            logger.error(f"Failed to {action} resource {resource.name}: {e}")
            logger.debug(f"Exception details: {e}", exc_info=True)
            return False