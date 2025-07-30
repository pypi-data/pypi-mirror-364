"""
Base command class for all CLI commands
"""

from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..utils.output import Console
    from ..utils.config import CLIConfig


class BaseCommand(ABC):
    """Base class for all CLI commands"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Command description"""
        pass
    
    @abstractmethod
    def register(self, subparsers) -> None:
        """Register command arguments"""
        pass
    
    @abstractmethod
    def execute(self, args: Namespace, config: "CLIConfig", console: "Console") -> int:
        """Execute the command"""
        pass
    
    def add_common_arguments(self, parser: ArgumentParser) -> None:
        """Add common arguments to command parser"""
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes"
        )
        parser.add_argument(
            "--yes", "-y",
            action="store_true",
            help="Assume yes to all prompts"
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=300,
            help="Timeout in seconds (default: 300)"
        )