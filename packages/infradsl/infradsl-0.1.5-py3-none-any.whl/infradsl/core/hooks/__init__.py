"""
InfraDSL Lifecycle Hooks

Rails-like lifecycle hooks for InfraDSL resources.
"""

from .lifecycle_hooks import (
    hooks,
    LifecycleEvent,
    HookContext,
    LifecycleHooks,
    before_create,
    after_create,
    before_update,
    after_update,
    before_destroy,
    after_destroy,
    on_drift,
    on_error,
    configure_notifications,
    trigger_lifecycle_event
)

__all__ = [
    "hooks",
    "LifecycleEvent", 
    "HookContext",
    "LifecycleHooks",
    "before_create",
    "after_create",
    "before_update", 
    "after_update",
    "before_destroy",
    "after_destroy",
    "on_drift",
    "on_error",
    "configure_notifications",
    "trigger_lifecycle_event"
]