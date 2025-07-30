"""
File-based state storage implementation

Provides persistent storage for resource state using JSON files.
Suitable for single-user environments and development workflows.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from ..interfaces.state_storage import StateStorage


class FileStorage(StateStorage):
    """
    File-based storage backend for resource state.

    Stores state in JSON files with atomic writes and backup support.
    Provides persistence across process restarts.
    """

    def __init__(self, state_dir: Optional[str] = None):
        """
        Initialize file storage.

        Args:
            state_dir: Directory for state files (default: ~/.infradsl/state)
        """
        if state_dir is None:
            home_dir = Path.home()
            state_dir = str(home_dir / ".infradsl" / "state")

        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / "resources.json"

        # Create directory if it doesn't exist
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Initialize empty state file if it doesn't exist
        if not self.state_file.exists():
            self._write_state({})

    def _read_state(self) -> Dict[str, Dict[str, Any]]:
        """
        Read state from file.

        Returns:
            Dictionary of all resource states
        """
        try:
            with open(self.state_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_state(self, state: Dict[str, Dict[str, Any]]) -> None:
        """
        Write state to file atomically.

        Args:
            state: Complete state dictionary to write
        """
        # Write to temporary file first
        temp_file = self.state_file.with_suffix(".tmp")

        try:
            with open(temp_file, "w") as f:
                json.dump(state, f, indent=2, sort_keys=True)

            # Atomic move to final location
            temp_file.replace(self.state_file)

        except Exception as e:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise e

    def _backup_state(self) -> None:
        """Create a backup of the current state file."""
        if self.state_file.exists():
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = self.state_dir / f"resources_backup_{timestamp}.json"

            # Keep only last 5 backups
            existing_backups = sorted(
                self.state_dir.glob("resources_backup_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            # Remove old backups (keep 4, as we're about to create the 5th)
            for backup in existing_backups[4:]:
                backup.unlink()

            # Create new backup
            import shutil

            shutil.copy2(self.state_file, backup_file)

    def get(self, resource_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve state for a specific resource.

        Args:
            resource_name: Name of the resource

        Returns:
            Resource state dictionary or None if not found
        """
        state = self._read_state()
        return state.get(resource_name)

    def set(self, resource_name: str, state: Dict[str, Any]) -> None:
        """
        Store state for a specific resource.

        Args:
            resource_name: Name of the resource
            state: Resource state dictionary
        """
        current_state = self._read_state()
        current_state[resource_name] = state.copy()
        self._write_state(current_state)

    def delete(self, resource_name: str) -> bool:
        """
        Delete state for a specific resource.

        Args:
            resource_name: Name of the resource

        Returns:
            True if resource was deleted, False if not found
        """
        current_state = self._read_state()
        if resource_name in current_state:
            del current_state[resource_name]
            self._write_state(current_state)
            return True
        return False

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """
        List all stored resource states.

        Returns:
            Dictionary mapping resource names to their states
        """
        return self._read_state()

    def clear(self) -> None:
        """Clear all stored states."""
        self._backup_state()
        self._write_state({})

    def exists(self, resource_name: str) -> bool:
        """
        Check if state exists for a resource.

        Args:
            resource_name: Name of the resource

        Returns:
            True if state exists, False otherwise
        """
        state = self._read_state()
        return resource_name in state

    def get_state_file_path(self) -> str:
        """
        Get the path to the state file.

        Returns:
            Absolute path to the state file
        """
        return str(self.state_file.absolute())

    def get_state_dir_path(self) -> str:
        """
        Get the path to the state directory.

        Returns:
            Absolute path to the state directory
        """
        return str(self.state_dir.absolute())
