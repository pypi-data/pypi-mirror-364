"""
InfraDSL Import CLI Commands

This module provides CLI commands for importing existing cloud infrastructure
into well-organized, dependency-aware InfraDSL code.
"""

import asyncio
import click
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.progress import Progress, TaskID, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from ...core.import.resource_discovery import ResourceDiscoveryEngine, ProgressReporter, discover_and_import
from ...core.import.dependency_graph import DependencyGraph, CircularDependencyError
from ...core.import.file_organizer import FileOrganizer, OrganizationStrategy
from ...core.import.code_generator import CodeGenerator

logger = logging.getLogger(__name__)
console = Console()


@click.group(name="import")
def import_group():
    """Import existing cloud infrastructure into InfraDSL"""
    pass


@import_group.command()
@click.argument("providers", nargs=-1, required=True)
@click.option("--regions", "-r", help="Comma-separated regions (e.g., us-east-1,us-west-2)")
@click.option("--organization", "-o", 
              type=click.Choice(["service", "environment", "layer", "hybrid"], case_sensitive=False),
              default="service", help="File organization strategy")
@click.option("--output", "-O", default="infrastructure", help="Output directory")
@click.option("--filter", "-f", multiple=True, help="Filter resources (e.g., Environment=production)")
@click.option("--dry-run", is_flag=True, help="Preview what would be imported without making changes")
@click.option("--no-tag", is_flag=True, help="Skip tagging resources (useful for testing)")
@click.option("--max-workers", default=10, help="Maximum parallel workers")
@click.option("--batch-size", default=50, help="Batch size for operations")
@click.option("--verify", is_flag=True, help="Verify import completeness after generation")
async def discover(providers, regions, organization, output, filter, dry_run, no_tag, max_workers, batch_size, verify):
    """
    Discover and import cloud infrastructure from specified providers.
    
    Examples:
        infra import discover aws gcp --regions us-east-1,us-central1
        infra import discover digitalocean --organization environment
        infra import discover aws --filter Environment=production --dry-run
    """
    console.print(Panel.fit(
        "[bold cyan]InfraDSL Superior Import System[/bold cyan]\n"
        "Transform your cloud infrastructure into manageable code",
        border_style="cyan"
    ))
    
    try:
        # Parse regions
        region_dict = {}
        if regions:
            for provider in providers:
                region_dict[provider] = regions.split(",")
        
        # Parse filters
        filters = {}
        for filter_str in filter:
            if "=" in filter_str:
                key, value = filter_str.split("=", 1)
                filters[key] = value
        
        console.print(f"🌍 [bold]Providers:[/bold] {', '.join(providers)}")
        console.print(f"📍 [bold]Regions:[/bold] {region_dict or 'default'}")
        console.print(f"📁 [bold]Organization:[/bold] {organization}")
        console.print(f"📂 [bold]Output:[/bold] {output}")
        if filters:
            console.print(f"🔍 [bold]Filters:[/bold] {filters}")
        if dry_run:
            console.print("🔍 [bold yellow]DRY RUN MODE[/bold yellow] - No changes will be made")
        console.print()
        
        # Phase 1: Resource Discovery
        console.print("🔍 [bold]Phase 1: Resource Discovery & Analysis[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            discovery_task = progress.add_task("Discovering resources...", total=100)
            
            # Discover resources
            dependency_graph = await discover_and_import(
                providers=list(providers),
                regions=region_dict,
                filters=filters,
                auto_tag=not no_tag and not dry_run,
                max_workers=max_workers
            )
            
            progress.update(discovery_task, completed=100)
        
        # Display discovery results
        total_resources = len(dependency_graph.nodes)
        stats = dependency_graph.get_statistics()
        
        console.print(f"✅ [bold green]Discovery Complete![/bold green]")
        console.print(f"   📊 {total_resources} resources discovered")
        console.print(f"   🔗 {stats['total_dependencies']} dependencies found")
        console.print(f"   ⚡ {stats['average_dependencies_per_resource']:.1f} avg dependencies per resource")
        
        if stats['circular_dependencies'] > 0:
            console.print(f"   ⚠️  [bold yellow]{stats['circular_dependencies']} circular dependencies detected[/bold yellow]")
        
        console.print()
        
        # Phase 2: File Organization
        console.print("📁 [bold]Phase 2: Intelligent File Organization[/bold]")
        
        # Get organization strategy
        strategy_map = {
            "service": OrganizationStrategy.SERVICE,
            "environment": OrganizationStrategy.ENVIRONMENT, 
            "layer": OrganizationStrategy.LAYER,
            "hybrid": OrganizationStrategy.HYBRID
        }
        
        organizer = FileOrganizer(strategy=strategy_map[organization])
        file_groups = organizer.organize(dependency_graph, output)
        
        # Display organization results
        org_stats = organizer.get_statistics(file_groups)
        console.print(f"✅ [bold green]Organization Complete![/bold green]")
        console.print(f"   📄 {org_stats['total_files']} files will be created")
        console.print(f"   📊 {org_stats['average_resources_per_file']:.1f} avg resources per file")
        console.print(f"   📂 Largest file: {Path(org_stats['largest_file']).name}")
        console.print()
        
        # Phase 3: Code Generation
        console.print("⚡ [bold]Phase 3: Clean Code Generation[/bold]")
        
        if not dry_run:
            generator = CodeGenerator()
            creation_order = organizer.get_creation_order(file_groups)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
            ) as progress:
                gen_task = progress.add_task("Generating code...", total=len(creation_order))
                
                # Generate code files
                generated_files = []
                for i, file_path in enumerate(creation_order):
                    file_group = file_groups[file_path]
                    
                    # Generate code
                    code = generator.generate_file(file_group, dependency_graph, file_groups)
                    formatted_code = generator.format_code(code)
                    
                    # Create directory if needed
                    output_path = Path(file_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write file
                    with open(output_path, "w") as f:
                        f.write(formatted_code)
                    
                    generated_files.append(file_path)
                    progress.update(gen_task, advance=1, description=f"Generated {output_path.name}")
            
            console.print(f"✅ [bold green]Code Generation Complete![/bold green]")
            console.print(f"   📝 {len(generated_files)} files generated")
            console.print(f"   📂 Output directory: {output}")
        else:
            console.print("🔍 [bold yellow]DRY RUN:[/bold yellow] Code generation skipped")
            
            # Show what would be generated
            table = Table(title="Files that would be generated")
            table.add_column("File Path", style="cyan")
            table.add_column("Resources", justify="right", style="green")
            table.add_column("Description", style="dim")
            
            for file_path, file_group in file_groups.items():
                table.add_row(
                    file_path,
                    str(len(file_group.resources)),
                    file_group.description
                )
            
            console.print(table)
        
        # Phase 4: Verification (if requested)
        if verify and not dry_run:
            console.print()
            console.print("🔍 [bold]Phase 4: Import Verification[/bold]")
            # TODO: Implement verification logic
            console.print("✅ [bold green]Verification Complete![/bold green] (placeholder)")
        
        # Summary
        console.print()
        console.print(Panel.fit(
            f"[bold green]🎉 Import Complete![/bold green]\n\n"
            f"📊 {total_resources} resources imported\n"
            f"📁 {len(file_groups)} files {'would be ' if dry_run else ''}created\n" 
            f"⚡ Organized using {organization} strategy\n"
            f"📂 Output: {output}/",
            border_style="green"
        ))
        
        if not dry_run:
            console.print("\n[bold cyan]Next steps:[/bold cyan]")
            console.print("1. Review the generated code")
            console.print("2. Run [bold]infra preview[/bold] to verify the infrastructure")
            console.print("3. Make any necessary adjustments")
            console.print("4. Use [bold]infra apply[/bold] to manage your infrastructure")
        
    except CircularDependencyError as e:
        console.print(f"❌ [bold red]Circular Dependency Error:[/bold red] {e}")
        raise click.ClickException("Import failed due to circular dependencies")
    
    except Exception as e:
        logger.exception("Import failed")
        console.print(f"❌ [bold red]Import Failed:[/bold red] {e}")
        raise click.ClickException(f"Import failed: {e}")


@import_group.command()
@click.argument("providers", nargs=-1, required=True)
@click.option("--regions", "-r", help="Comma-separated regions")
@click.option("--filter", "-f", multiple=True, help="Filter resources")
@click.option("--format", "output_format", type=click.Choice(["table", "json", "yaml"]), 
              default="table", help="Output format")
@click.option("--save", help="Save results to file")
async def list(providers, regions, filter, output_format, save):
    """
    List discoverable resources without importing them.
    
    Examples:
        infra import list aws --regions us-east-1
        infra import list gcp digitalocean --format json
    """
    console.print("🔍 [bold]Discovering Resources (read-only)[/bold]")
    
    try:
        # Parse regions and filters
        region_dict = {}
        if regions:
            for provider in providers:
                region_dict[provider] = regions.split(",")
        
        filters = {}
        for filter_str in filter:
            if "=" in filter_str:
                key, value = filter_str.split("=", 1)
                filters[key] = value
        
        # Discover without tagging
        dependency_graph = await discover_and_import(
            providers=list(providers),
            regions=region_dict,
            filters=filters,
            auto_tag=False,
            max_workers=5
        )
        
        resources = list(dependency_graph.nodes.values())
        
        if output_format == "table":
            table = Table(title="Discovered Resources")
            table.add_column("Provider", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Name", style="bold")
            table.add_column("Region", style="dim")
            table.add_column("ID", style="dim", max_width=20)
            
            for resource in resources:
                table.add_row(
                    resource.provider,
                    resource.type,
                    resource.name,
                    resource.region,
                    resource.id[:18] + "..." if len(resource.id) > 20 else resource.id
                )
            
            console.print(table)
            
        elif output_format == "json":
            resource_data = []
            for resource in resources:
                resource_data.append({
                    "id": resource.id,
                    "name": resource.name,
                    "type": resource.type,
                    "provider": resource.provider,
                    "region": resource.region,
                    "attributes": resource.attributes,
                    "tags": resource.tags
                })
            
            output = json.dumps(resource_data, indent=2)
            if save:
                Path(save).write_text(output)
                console.print(f"✅ Results saved to {save}")
            else:
                console.print(output)
        
        console.print(f"\n📊 Found {len(resources)} resources across {len(providers)} providers")
        
    except Exception as e:
        logger.exception("Resource listing failed")
        console.print(f"❌ [bold red]Listing Failed:[/bold red] {e}")
        raise click.ClickException(f"Listing failed: {e}")


@import_group.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--organization", "-o",
              type=click.Choice(["service", "environment", "layer", "hybrid"], case_sensitive=False),
              default="service", help="File organization strategy")
@click.option("--output", "-O", default="infrastructure", help="Output directory")
def from_file(input_file, organization, output):
    """
    Import resources from a JSON file (useful for testing or offline processing).
    
    Examples:
        infra import from-file resources.json --organization environment
    """
    console.print(f"📁 [bold]Importing from file:[/bold] {input_file}")
    
    try:
        # Load resource data
        with open(input_file, 'r') as f:
            resource_data = json.load(f)
        
        # TODO: Implement file-based import
        console.print(f"✅ Would import {len(resource_data)} resources")
        console.print("🚧 [bold yellow]File-based import not yet implemented[/bold yellow]")
        
    except Exception as e:
        console.print(f"❌ [bold red]Import Failed:[/bold red] {e}")
        raise click.ClickException(f"Import failed: {e}")


# Export the command group
__all__ = ["import_group"]