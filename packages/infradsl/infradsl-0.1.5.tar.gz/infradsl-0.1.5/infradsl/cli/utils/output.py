"""
Output formatting and console utilities
"""

import json
import yaml
from enum import Enum
from typing import Any, Dict, List, Optional
from rich.console import Console as RichConsole
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich.markup import escape


class OutputFormat(Enum):
    """Output format options"""

    TABLE = "table"
    JSON = "json"
    YAML = "yaml"


class Console:
    """Enhanced console with rich formatting and multiple output formats"""

    def __init__(
        self,
        format: OutputFormat = OutputFormat.TABLE,
        no_color: bool = False,
        verbosity: int = 1,
    ):
        self.format = format
        self.verbosity = verbosity
        self._rich_console = RichConsole(
            force_terminal=not no_color, no_color=no_color, stderr=True
        )

    def print(self, message: str, **kwargs) -> None:
        """Print a message to stdout"""
        if self.verbosity > 0:
            print(message, **kwargs)

    def error(self, message: str) -> None:
        """Print an error message to stderr"""
        self._rich_console.print(f"[red]✗[/red] {message}", style="red")

    def success(self, message: str) -> None:
        """Print a success message"""
        if self.verbosity > 0:
            self._rich_console.print(f"[green]✓[/green] {message}", style="green")

    def warning(self, message: str) -> None:
        """Print a warning message"""
        if self.verbosity > 0:
            self._rich_console.print(f"[yellow]⚠[/yellow] {message}", style="yellow")

    def info(self, message: str) -> None:
        """Print an info message"""
        if self.verbosity > 0:
            self._rich_console.print(f"[blue]ℹ[/blue] {message}", style="blue")

    def debug(self, message: str) -> None:
        """Print a debug message"""
        if self.verbosity >= 2:
            self._rich_console.print(f"[dim]DEBUG: {message}[/dim]", style="dim")

    def output(self, data: Any, title: Optional[str] = None) -> None:
        """Output data in the specified format"""
        if self.format == OutputFormat.JSON:
            self._output_json(data)
        elif self.format == OutputFormat.YAML:
            self._output_yaml(data)
        else:
            self._output_table(data, title)

    def _output_json(self, data: Any) -> None:
        """Output data as JSON"""
        print(json.dumps(data, indent=2, default=str))

    def _output_yaml(self, data: Any) -> None:
        """Output data as YAML"""
        print(yaml.dump(data, default_flow_style=False))

    def _output_table(self, data: Any, title: Optional[str] = None) -> None:
        """Output data as a formatted table"""
        if isinstance(data, dict):
            self._output_dict_table(data, title)
        elif isinstance(data, list):
            self._output_list_table(data, title)
        else:
            self.print(str(data))

    def _output_dict_table(
        self, data: Dict[str, Any], title: Optional[str] = None
    ) -> None:
        """Output dictionary as a two-column table"""
        table = Table(title=title)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        for key, value in data.items():
            table.add_row(str(key), str(value))

        self._rich_console.print(table)

    def _output_list_table(self, data: List[Any], title: Optional[str] = None) -> None:
        """Output list as a table"""
        if not data:
            self.info("No data to display")
            return

        # If list contains dictionaries, create a table with columns
        if isinstance(data[0], dict):
            table = Table(title=title)

            # Add columns from the first item
            for key in data[0].keys():
                table.add_column(str(key).title(), style="cyan")

            # Add rows
            for item in data:
                row = [str(item.get(key, "")) for key in data[0].keys()]
                table.add_row(*row)

            self._rich_console.print(table)
        else:
            # Simple list
            table = Table(title=title)
            table.add_column("Item", style="white")

            for item in data:
                table.add_row(str(item))

            self._rich_console.print(table)

    def panel(
        self, content: str, title: Optional[str] = None, style: str = "white"
    ) -> None:
        """Display content in a panel"""
        if self.verbosity > 0:
            panel = Panel(content, title=title, style=style)
            self._rich_console.print(panel)

    def progress(self, description: str = "Working..."):
        """Create a progress context manager"""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self._rich_console,
            transient=True,
        )
        progress.add_task(description, total=None)
        return progress

    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask for user confirmation"""
        if self.verbosity == 0:
            return default

        suffix = " [Y/n]" if default else " [y/N]"

        try:
            response = input(f"{message}{suffix}: ").strip().lower()
            if not response:
                return default
            return response in ("y", "yes")
        except (EOFError, KeyboardInterrupt):
            return False

    def input(self, message: str, default: Optional[str] = None) -> str:
        """Get input from user"""
        if default:
            prompt = f"{message} [{default}]: "
        else:
            prompt = f"{message}: "

        try:
            response = input(prompt).strip()
            return response if response else (default or "")
        except (EOFError, KeyboardInterrupt):
            return default or ""

    def status(self, message: str):
        """Create a status context manager"""
        return self._rich_console.status(message)

    def print_table(self, headers: List[str], rows: List[List[str]], title: Optional[str] = None) -> None:
        """Print a table with headers and rows"""
        if not rows:
            self.info("No data to display")
            return

        table = Table(title=title)
        
        # Add columns
        for header in headers:
            table.add_column(header, style="cyan")
        
        # Add rows
        for row in rows:
            table.add_row(*[str(cell) for cell in row])
        
        self._rich_console.print(table)


def format_duration(seconds: float) -> str:
    """Format a duration in seconds to human readable format"""
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds / 60:.1f}m"
    else:
        return f"{seconds / 3600:.1f}h"


def format_size(bytes: int) -> str:
    """Format bytes to human readable size"""
    size = float(bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f}{unit}"
        size /= 1024.0
    return f"{size:.1f}PB"


def format_cost(amount: float, currency: str = "USD") -> str:
    """Format cost amount"""
    if currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"
