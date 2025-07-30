"""
Data models for the import system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
from datetime import datetime


class ImportStatus(Enum):
    """Status of import operations"""

    PENDING = "pending"
    DISCOVERING = "discovering"
    ANALYZING = "analyzing"
    TAGGING = "tagging"         # New: Pillar 1 instant tagging
    CACHING = "caching"         # New: Pillar 1 instant caching  
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ResourceType(Enum):
    """Types of cloud resources that can be imported"""

    VIRTUAL_MACHINE = "virtual_machine"
    DATABASE = "database"
    STORAGE = "storage"
    NETWORK = "network"
    LOAD_BALANCER = "load_balancer"
    SECURITY_GROUP = "security_group"
    UNKNOWN = "unknown"


@dataclass
class ImportConfig:
    """Configuration for import operations"""

    # Provider settings
    provider: str
    region: Optional[str] = None
    project: Optional[str] = None

    # Filtering options
    resource_types: Optional[List[str]] = None
    name_patterns: Optional[List[str]] = None
    tag_filters: Dict[str, str] = field(default_factory=dict)

    # Output options
    output_format: str = "python"
    output_file: Optional[str] = None
    include_dependencies: bool = True
    include_metadata: bool = True

    # Generation options
    generate_comments: bool = True
    optimize_code: bool = True
    group_by_type: bool = False

    # Advanced options
    dry_run: bool = False
    max_resources: Optional[int] = None
    timeout_seconds: int = 300
    
    # Pillar 1: Instant Management Options
    tag_resources: bool = True      # Tag imported resources as InfraDSL-managed
    cache_imported: bool = True     # Cache imported resources for immediate management


@dataclass
class CloudResource:
    """Represents a discovered cloud resource"""

    # Basic identification
    id: str
    name: str
    type: ResourceType
    provider: str

    # Location and organization
    region: Optional[str] = None
    zone: Optional[str] = None
    project: Optional[str] = None

    # Configuration and state
    configuration: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)

    # Relationships
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)

    # Import metadata
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    import_priority: int = 0  # Higher numbers imported first

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value if hasattr(self.type, 'value') else str(self.type),
            "provider": self.provider,
            "region": self.region,
            "zone": self.zone,
            "project": self.project,
            "configuration": self.configuration,
            "metadata": self.metadata,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "dependents": self.dependents,
            "discovered_at": self.discovered_at.isoformat(),
            "import_priority": self.import_priority,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CloudResource":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            type=ResourceType(data["type"]),
            provider=data["provider"],
            region=data.get("region"),
            zone=data.get("zone"),
            project=data.get("project"),
            configuration=data.get("configuration", {}),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", {}),
            dependencies=data.get("dependencies", []),
            dependents=data.get("dependents", []),
            discovered_at=datetime.fromisoformat(
                data.get("discovered_at", datetime.utcnow().isoformat())
            ),
            import_priority=data.get("import_priority", 0),
        )


@dataclass
class DependencyGraph:
    """Represents resource dependencies"""

    resources: Dict[str, CloudResource] = field(default_factory=dict)
    edges: List[Tuple[str, str]] = field(default_factory=list)  # (from_id, to_id)

    def add_resource(self, resource: CloudResource) -> None:
        """Add a resource to the graph"""
        self.resources[resource.id] = resource

    def add_dependency(self, from_id: str, to_id: str) -> None:
        """Add a dependency edge"""
        if (from_id, to_id) not in self.edges:
            self.edges.append((from_id, to_id))

            # Update resource dependency lists
            if from_id in self.resources:
                if to_id not in self.resources[from_id].dependencies:
                    self.resources[from_id].dependencies.append(to_id)

            if to_id in self.resources:
                if from_id not in self.resources[to_id].dependents:
                    self.resources[to_id].dependents.append(from_id)

    def get_creation_order(self) -> List[str]:
        """Get resources in dependency-safe creation order"""
        # Topological sort
        in_degree = {resource_id: 0 for resource_id in self.resources}

        # Calculate in-degrees
        for from_id, to_id in self.edges:
            if to_id in in_degree:
                in_degree[to_id] += 1

        # Start with resources that have no dependencies
        queue = [
            resource_id for resource_id, degree in in_degree.items() if degree == 0
        ]
        result = []

        while queue:
            # Sort by priority for consistent ordering
            queue.sort(key=lambda x: self.resources[x].import_priority, reverse=True)
            current = queue.pop(0)
            result.append(current)

            # Remove edges from current resource
            for from_id, to_id in self.edges:
                if from_id == current and to_id in in_degree:
                    in_degree[to_id] -= 1
                    if in_degree[to_id] == 0:
                        queue.append(to_id)

        return result

    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies"""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            # Visit all dependencies
            for from_id, to_id in self.edges:
                if from_id == node:
                    dfs(to_id, path.copy())

            rec_stack.remove(node)

        for resource_id in self.resources:
            if resource_id not in visited:
                dfs(resource_id, [])

        return cycles


@dataclass
class GeneratedCode:
    """Represents generated InfraDSL code"""

    filename: str
    content: str
    imports: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)

    # Generation metadata
    generated_at: datetime = field(default_factory=datetime.utcnow)
    generator_version: str = "1.0.0"
    source_provider: str = ""
    source_project: Optional[str] = None

    def get_full_content(self) -> str:
        """Get complete file content with header"""
        header = f'''"""
InfraDSL Infrastructure Code
Generated from {self.source_provider} on {self.generated_at.isoformat()}

This file was automatically generated by InfraDSL's "Codify My Cloud" import tool.
Review and modify as needed before applying.
"""

'''
        return header + self.content


@dataclass
class ImportResult:
    """Result of an import operation"""

    status: ImportStatus
    config: ImportConfig

    # Discovery results
    discovered_resources: List[CloudResource] = field(default_factory=list)
    dependency_graph: Optional[DependencyGraph] = None

    # Generation results
    generated_code: Optional[GeneratedCode] = None

    # Statistics and metadata
    total_resources_found: int = 0
    total_resources_imported: int = 0
    total_resources_skipped: int = 0  # Already managed by InfraDSL
    execution_time_seconds: float = 0.0

    # Errors and warnings
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Timestamps
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def add_error(self, error: str) -> None:
        """Add an error message"""
        self.errors.append(error)
        if self.status != ImportStatus.FAILED:
            self.status = ImportStatus.FAILED

    def add_warning(self, warning: str) -> None:
        """Add a warning message"""
        self.warnings.append(warning)

    def complete(self, status: ImportStatus = ImportStatus.COMPLETED) -> None:
        """Mark the import as completed"""
        self.status = status
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.execution_time_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the import results"""
        return {
            "status": self.status.value,
            "provider": self.config.provider,
            "project": self.config.project,
            "total_resources_found": self.total_resources_found,
            "total_resources_imported": self.total_resources_imported,
            "total_resources_skipped": self.total_resources_skipped,
            "execution_time_seconds": self.execution_time_seconds,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "generated_file": (
                self.generated_code.filename if self.generated_code else None
            ),
        }
