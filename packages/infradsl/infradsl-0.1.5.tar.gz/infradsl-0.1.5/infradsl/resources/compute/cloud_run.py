from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import os
import subprocess

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec, ResourceState


class IngressType(Enum):
    """Cloud Run ingress types"""
    ALL = "all"                    # Allow all traffic
    INTERNAL = "internal"          # VPC traffic only
    INTERNAL_LOAD_BALANCER = "internal-and-cloud-load-balancing"  # Internal + LB


class ExecutionEnvironment(Enum):
    """Cloud Run execution environments"""
    FIRST_GEN = "gen1"   # First generation
    SECOND_GEN = "gen2"  # Second generation (recommended)


class ConcurrencyType(Enum):
    """Request concurrency types"""
    SINGLE = "single"         # One request per container
    MULTI = "multi"          # Multiple requests per container


@dataclass
class ContainerSpec:
    """Container configuration"""
    image: str
    port: int = 8080
    cpu: str = "1000m"        # 1 vCPU
    memory: str = "512Mi"     # 512 MB
    max_concurrency: int = 1000
    timeout: int = 300        # 5 minutes
    
    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)
    secret_env_vars: Dict[str, str] = field(default_factory=dict)  # Secret Manager refs
    
    # Startup and liveness probes
    startup_probe_path: Optional[str] = None
    liveness_probe_path: Optional[str] = None


@dataclass
class TrafficSpec:
    """Traffic allocation specification"""
    percent: int = 100
    revision: Optional[str] = None
    tag: Optional[str] = None


@dataclass
class CloudRunSpec(ResourceSpec):
    """Specification for a Cloud Run service"""
    
    # Core configuration
    region: str = "us-central1"
    
    # Container configuration
    container: ContainerSpec = field(default_factory=lambda: ContainerSpec("hello-world"))
    
    # Service configuration
    ingress: IngressType = IngressType.ALL
    execution_environment: ExecutionEnvironment = ExecutionEnvironment.SECOND_GEN
    
    # Scaling
    min_instances: int = 0
    max_instances: int = 100
    
    # Security
    allow_unauthenticated: bool = True
    service_account: Optional[str] = None
    
    # VPC configuration
    vpc_connector: Optional[str] = None
    vpc_egress: str = "private-ranges-only"  # private-ranges-only, all-traffic
    
    # Traffic management
    traffic_allocations: List[TrafficSpec] = field(default_factory=lambda: [TrafficSpec()])
    
    # Custom domains
    custom_domains: List[str] = field(default_factory=list)
    
    # Labels and annotations
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    
    # Build configuration (for local builds)
    dockerfile_path: Optional[str] = None
    build_context: str = "."
    build_args: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class CloudRun(BaseResource):
    """
    GCP Cloud Run serverless container platform with Rails-like conventions.
    
    Examples:
        # Deploy from existing image
        api_service = (CloudRun("api-service")
                      .region("us-central1")
                      .image("gcr.io/my-project/api:latest")
                      .port(8080)
                      .memory("1Gi")
                      .env("DATABASE_URL", "postgres://...")
                      .public())
        
        # Deploy from Dockerfile
        web_app = (CloudRun("web-app")
                  .region("us-west1")
                  .dockerfile("./Dockerfile")
                  .port(3000)
                  .cpu("2000m")
                  .memory("2Gi")
                  .min_instances(1)
                  .max_instances(50)
                  .production())
        
        # Deploy from GitHub Container Registry
        worker = (CloudRun("worker-service")
                 .region("us-east1")
                 .image("ghcr.io/myorg/worker:v1.2.3")
                 .memory("512Mi")
                 .env_from_secret("API_KEY", "worker-secrets", "api-key")
                 .private()
                 .vpc_connector("my-vpc-connector"))
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: CloudRunSpec = self._create_spec()
        # Store resource type in annotations for cache fingerprinting
        self.metadata.annotations["resource_type"] = "CloudRun"
        
        # CloudRun is GCP-specific, so automatically attach GCP provider
        self._auto_attach_gcp_provider()
        
        # Set smart defaults based on name patterns
        name_lower = name.lower()
        
        # Scaling defaults based on service type (no port defaults for Cloud Run)
        if any(keyword in name_lower for keyword in ["api", "service", "worker"]):
            self.spec.min_instances = 0  # Scale to zero for services
        elif "web" in name_lower or "app" in name_lower:
            self.spec.min_instances = 1  # Keep warm for web apps
            
        # Production overrides (checked separately)
        if any(keyword in name_lower for keyword in ["prod", "production"]):
            self.spec.min_instances = 2  # Production should stay warm
            self.spec.execution_environment = ExecutionEnvironment.SECOND_GEN
            
    def _create_spec(self) -> CloudRunSpec:
        return CloudRunSpec()
        
    def _auto_attach_gcp_provider(self) -> None:
        """Automatically attach GCP provider since CloudRun is GCP-specific"""
        try:
            from ...providers.gcp import GCPComputeProvider
            from ...core.interfaces.provider import ProviderConfig, ProviderType
            
            # Create a default GCP provider config
            config = ProviderConfig(
                type=ProviderType.GCP,
                project=os.environ.get('GOOGLE_CLOUD_PROJECT', 'default-project')
            )
            
            # Create and attach the provider
            provider = GCPComputeProvider(config)
            self._provider = provider
            
        except Exception as e:
            # If we can't auto-attach, that's ok - user can still attach manually
            pass
        
    def _validate_spec(self) -> None:
        """Validate service specification"""
        if not self.spec.container.image and not self.spec.dockerfile_path:
            raise ValueError("Must specify either container image or Dockerfile path")
            
        if self.spec.min_instances > self.spec.max_instances:
            raise ValueError("Min instances cannot be greater than max instances")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "name": self.metadata.name,
            "location": self.spec.region,
            "template": self._build_template_spec(),
            "traffic": self._build_traffic_spec(),
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
        }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            # Handle string provider like "GoogleCloud"
            provider_str = str(self._provider).lower()
            if "google" in provider_str or "gcp" in provider_str:
                provider_type_str = "gcp"
            else:
                provider_type_str = provider_str

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config

    def _build_template_spec(self) -> Dict[str, Any]:
        """Build Cloud Run template specification"""
        template = {
            "metadata": {
                "annotations": {
                    **self.spec.annotations,
                    "autoscaling.knative.dev/minScale": str(self.spec.min_instances),
                    "autoscaling.knative.dev/maxScale": str(self.spec.max_instances),
                    "run.googleapis.com/execution-environment": self.spec.execution_environment.value
                }
            },
            "spec": {
                "containerConcurrency": self.spec.container.max_concurrency,
                "timeoutSeconds": self.spec.container.timeout,
                "containers": [self._build_container_spec()]
            }
        }
        
        # Service account
        if self.spec.service_account:
            template["spec"]["serviceAccountName"] = self.spec.service_account
            
        # VPC connector
        if self.spec.vpc_connector:
            template["metadata"]["annotations"]["run.googleapis.com/vpc-access-connector"] = self.spec.vpc_connector
            template["metadata"]["annotations"]["run.googleapis.com/vpc-access-egress"] = self.spec.vpc_egress
            
        return template
        
    def _build_container_spec(self) -> Dict[str, Any]:
        """Build container specification"""
        container = {
            "image": self.spec.container.image,
            "ports": [{"containerPort": self.spec.container.port}],
            "resources": {
                "limits": {
                    "cpu": self.spec.container.cpu,
                    "memory": self.spec.container.memory
                }
            }
        }
        
        # Environment variables
        if self.spec.container.env_vars or self.spec.container.secret_env_vars:
            env = []
            
            # Regular environment variables
            for key, value in self.spec.container.env_vars.items():
                env.append({"name": key, "value": value})
                
            # Secret environment variables
            for key, secret_ref in self.spec.container.secret_env_vars.items():
                env.append({
                    "name": key,
                    "valueFrom": {
                        "secretKeyRef": {
                            "name": secret_ref.split(":")[0],
                            "key": secret_ref.split(":")[1] if ":" in secret_ref else key.lower()
                        }
                    }
                })
                
            container["env"] = env
            
        # Health checks
        if self.spec.container.startup_probe_path:
            container["startupProbe"] = {
                "httpGet": {
                    "path": self.spec.container.startup_probe_path,
                    "port": self.spec.container.port
                }
            }
            
        if self.spec.container.liveness_probe_path:
            container["livenessProbe"] = {
                "httpGet": {
                    "path": self.spec.container.liveness_probe_path,
                    "port": self.spec.container.port
                }
            }
            
        return container
        
    def _build_traffic_spec(self) -> List[Dict[str, Any]]:
        """Build traffic allocation specification"""
        traffic = []
        for allocation in self.spec.traffic_allocations:
            traffic_spec = {"percent": allocation.percent}
            
            if allocation.revision:
                traffic_spec["revisionName"] = allocation.revision
            else:
                traffic_spec["latestRevision"] = True
                
            if allocation.tag:
                traffic_spec["tag"] = allocation.tag
                
            traffic.append(traffic_spec)
            
        return traffic

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP Cloud Run configuration"""
        config = {
            "resource_type": "cloud_run_service"
        }
        
        # Ingress configuration
        if self.spec.ingress != IngressType.ALL:
            config["ingress"] = self.spec.ingress.value
            
        # IAM policy for public access
        if self.spec.allow_unauthenticated:
            config["members"] = ["allUsers"]
            
        return config
        
    def _build_image_if_needed(self) -> str:
        """Build container image from Dockerfile if specified, using smart hash comparison"""
        if not self.spec.dockerfile_path:
            return self.spec.container.image
            
        # Build image using Cloud Build or local Docker
        dockerfile_path = os.path.expanduser(self.spec.dockerfile_path)
        if not os.path.exists(dockerfile_path):
            raise FileNotFoundError(f"Dockerfile not found: {dockerfile_path}")
            
        # Use the image name if already set (e.g., by artifact_registry())
        if self.spec.container.image and "pkg.dev" in self.spec.container.image:
            image_name = self.spec.container.image
        else:
            # Generate image name using gcr.io
            project_id = self._get_project_id()
            image_name = f"gcr.io/{project_id}/{self.name}:latest"
        
        # Check if we need to rebuild using content hash
        current_hash = self._compute_build_hash(dockerfile_path)
        if self._should_skip_build(image_name, current_hash):
            print(f"Skipping build for {image_name} - no changes detected")
            return image_name
            
        print(f"Building {image_name} - changes detected or first build")
        
        # Update the image tag with the content hash for better tracking
        base_image = image_name.rsplit(':', 1)[0] if ':' in image_name else image_name
        hashed_image_name = f"{base_image}:{current_hash[:8]}"
        
        # Build with Cloud Build (preferred) or Docker
        if self._should_use_cloud_build():
            self._build_with_cloud_build(hashed_image_name, dockerfile_path)
        else:
            self._build_with_docker(hashed_image_name, dockerfile_path)
            
        # Also tag as latest
        self._tag_as_latest(hashed_image_name, image_name)
            
        return image_name
        
    def _get_project_id(self) -> str:
        """Get GCP project ID"""
        # Try to get from provider or environment
        if hasattr(self._provider, 'project_id'):
            return self._provider.project_id
        return os.environ.get('GOOGLE_CLOUD_PROJECT', 'my-project')
        
    def _should_use_cloud_build(self) -> bool:
        """Determine whether to use Cloud Build or local Docker"""
        return os.environ.get('USE_CLOUD_BUILD', '').lower() == 'true'
        
    def _compute_build_hash(self, dockerfile_path: str) -> str:
        """Compute hash of all build inputs to detect changes"""
        import hashlib
        import glob
        
        hasher = hashlib.sha256()
        build_context = os.path.expanduser(self.spec.build_context)
        
        # Hash Dockerfile content
        with open(dockerfile_path, 'rb') as f:
            hasher.update(f.read())
            
        # Hash build args
        for key, value in sorted(self.spec.build_args.items()):
            hasher.update(f"{key}={value}".encode())
            
        # Hash all files in build context (excluding common ignore patterns)
        ignore_patterns = {'.git', '__pycache__', '*.pyc', '.DS_Store', 'node_modules', '.env'}
        
        def should_ignore(file_path):
            basename = os.path.basename(file_path)
            return any(
                basename.startswith('.git') or
                basename == pattern.replace('*', '') or
                file_path.endswith(pattern.replace('*', ''))
                for pattern in ignore_patterns
            )
        
        # Collect and sort all files for consistent hashing
        files_to_hash = []
        for root, dirs, files in os.walk(build_context):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not should_ignore(file_path):
                    rel_path = os.path.relpath(file_path, build_context)
                    files_to_hash.append(rel_path)
        
        # Hash files in sorted order
        for rel_path in sorted(files_to_hash):
            full_path = os.path.join(build_context, rel_path)
            try:
                with open(full_path, 'rb') as f:
                    # Hash relative path first, then content
                    hasher.update(rel_path.encode())
                    hasher.update(f.read())
            except (IOError, OSError):
                # Skip files that can't be read
                continue
                
        return hasher.hexdigest()
        
    def _should_skip_build(self, image_name: str, current_hash: str) -> bool:
        """Check if we can skip building by comparing with existing image hash"""
        try:
            # Check if image exists with this hash tag
            base_image = image_name.rsplit(':', 1)[0] if ':' in image_name else image_name
            hashed_image_name = f"{base_image}:{current_hash[:8]}"
            
            # Try to check if the image exists in the registry
            if "pkg.dev" in image_name:
                # For Artifact Registry, use gcloud to check
                result = subprocess.run([
                    "gcloud", "container", "images", "describe", hashed_image_name,
                    "--quiet", "--format=value(name)"
                ], capture_output=True, text=True)
                return result.returncode == 0
            else:
                # For other registries, use docker manifest inspect
                result = subprocess.run([
                    "docker", "manifest", "inspect", hashed_image_name
                ], capture_output=True, text=True)
                return result.returncode == 0
        except Exception:
            # If we can't check, err on the side of building
            return False
            
    def _tag_as_latest(self, source_image: str, target_image: str):
        """Tag the hashed image as the latest version"""
        try:
            if "pkg.dev" in source_image:
                # Use gcloud to tag for Artifact Registry
                subprocess.run([
                    "gcloud", "container", "images", "add-tag", source_image, target_image,
                    "--quiet"
                ], check=False)  # Don't fail if tagging fails
            else:
                # Use docker tag for other registries
                subprocess.run([
                    "docker", "tag", source_image, target_image
                ], check=False)
                subprocess.run([
                    "docker", "push", target_image
                ], check=False)
        except Exception as e:
            print(f"Warning: Failed to tag image as latest: {e}")
        
    def _build_with_cloud_build(self, image_name: str, dockerfile_path: str):
        """Build image using Google Cloud Build"""
        build_config = {
            "steps": [
                {
                    "name": "gcr.io/cloud-builders/docker",
                    "args": [
                        "build",
                        "-t", image_name,
                        "-f", dockerfile_path,
                        *[f"--build-arg={k}={v}" for k, v in self.spec.build_args.items()],
                        self.spec.build_context
                    ]
                }
            ],
            "images": [image_name]
        }
        
        # This would be implemented by the provider
        print(f"Building {image_name} with Cloud Build...")
        
    def _build_with_docker(self, image_name: str, dockerfile_path: str):
        """Build image using local Docker"""
        build_cmd = [
            "docker", "build",
            "-t", image_name,
            "-f", dockerfile_path
        ]
        
        # Add build args
        for key, value in self.spec.build_args.items():
            build_cmd.extend(["--build-arg", f"{key}={value}"])
            
        build_cmd.append(self.spec.build_context)
        
        print(f"Building {image_name} with local Docker...")
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Docker build failed: {result.stderr}")
            
        print(f"Successfully built {image_name}")
        
        # Authenticate to Artifact Registry if needed
        if "pkg.dev" in image_name:
            # Extract region from image name
            parts = image_name.split("-docker.pkg.dev")
            if len(parts) > 0:
                region = parts[0].split("/")[-1] if "/" in parts[0] else parts[0]
                auth_cmd = ["gcloud", "auth", "configure-docker", f"{region}-docker.pkg.dev", "--quiet"]
                auth_result = subprocess.run(auth_cmd, capture_output=True, text=True)
                if auth_result.returncode != 0:
                    print(f"Warning: Failed to configure Docker auth: {auth_result.stderr}")
        
        # Push to registry
        push_cmd = ["docker", "push", image_name]
        push_result = subprocess.run(push_cmd, capture_output=True, text=True)
        
        if push_result.returncode != 0:
            print(f"Warning: Failed to push image: {push_result.stderr}")
        
    # Fluent interface methods
    
    # Location methods
    
    def region(self, region_name: str) -> Self:
        """Set deployment region (chainable)"""
        self.spec.region = region_name
        # Store region in metadata annotations for fingerprint lookup
        self.metadata.annotations["region"] = region_name
        return self
    
    def imported(self, cloud_id: str) -> Self:
        """Mark as imported resource with existing cloud ID (chainable)"""
        self.status.cloud_id = cloud_id
        self.status.state = ResourceState.ACTIVE
        # Store cloud_id in annotations for fingerprint lookup
        self.metadata.annotations["cloud_id"] = cloud_id
        return self
        
    # Container configuration
    
    def image(self, image_url: str) -> Self:
        """Set container image (chainable)"""
        self.spec.container.image = image_url
        return self
        
    def dockerfile(self, path: str, context: str = ".") -> Self:
        """Build from Dockerfile (chainable)"""
        self.spec.dockerfile_path = path
        self.spec.build_context = context
        return self
        
    def container_from_source(self, source_path: str, dockerfile_path: str = None) -> Self:
        """Build container from source directory with Dockerfile (chainable)"""
        dockerfile = dockerfile_path or os.path.join(source_path, "Dockerfile")
        self.spec.dockerfile_path = dockerfile
        self.spec.build_context = source_path
        return self
        
    def github_container_registry(self, org: str, repo: str, tag: str = "latest") -> Self:
        """Use GitHub Container Registry image (chainable)"""
        self.spec.container.image = f"ghcr.io/{org}/{repo}:{tag}"
        return self
        
    def docker_hub(self, image: str, tag: str = "latest") -> Self:
        """Use Docker Hub image (chainable)"""
        self.spec.container.image = f"{image}:{tag}"
        return self
        
    def google_container_registry(self, project: str, image: str, tag: str = "latest") -> Self:
        """Use Google Container Registry image (chainable)"""
        self.spec.container.image = f"gcr.io/{project}/{image}:{tag}"
        return self
        
    def artifact_registry(self, project: str, location: str, repo: str, image: str, tag: str = "latest") -> Self:
        """Use Google Artifact Registry image (chainable)"""
        self.spec.container.image = f"{location}-docker.pkg.dev/{project}/{repo}/{image}:{tag}"
        # Also store the region for consistency
        if not self.spec.region:
            self.spec.region = location
        return self
        
    def port(self, port_number: int) -> Self:
        """Set container port (chainable)"""
        self.spec.container.port = port_number
        return self
        
    def cpu(self, cpu_limit: str) -> Self:
        """Set CPU limit (chainable)"""
        self.spec.container.cpu = cpu_limit
        return self
        
    def memory(self, memory_limit: str) -> Self:
        """Set memory limit (chainable)"""
        self.spec.container.memory = memory_limit
        return self
        
    def timeout(self, seconds: int) -> Self:
        """Set request timeout (chainable)"""
        self.spec.container.timeout = seconds
        return self
        
    def concurrency(self, max_requests: int) -> Self:
        """Set max concurrent requests per container (chainable)"""
        self.spec.container.max_concurrency = max_requests
        return self
        
    # Scaling configuration
    
    def min_instances(self, count: int) -> Self:
        """Set minimum instances (chainable)"""
        self.spec.min_instances = count
        return self
        
    def max_instances(self, count: int) -> Self:
        """Set maximum instances (chainable)"""
        self.spec.max_instances = count
        return self
        
    def scale_to_zero(self) -> Self:
        """Allow scaling to zero (chainable)"""
        self.spec.min_instances = 0
        return self
        
    def keep_warm(self, instances: int = 1) -> Self:
        """Keep minimum instances warm (chainable)"""
        self.spec.min_instances = instances
        return self
        
    # Environment variables
    
    def env(self, key: str, value: str) -> Self:
        """Set environment variable (chainable)"""
        self.spec.container.env_vars[key] = value
        return self
        
    def env_vars(self, env_dict: Dict[str, str] = None, **env_vars) -> Self:
        """Set multiple environment variables (chainable)"""
        if env_dict:
            self.spec.container.env_vars.update(env_dict)
        if env_vars:
            self.spec.container.env_vars.update(env_vars)
        return self
        
    def env_from_secret(self, env_key: str, secret_name: str, secret_key: str = None) -> Self:
        """Set environment variable from Secret Manager (chainable)"""
        secret_ref = f"{secret_name}:{secret_key or env_key.lower()}"
        self.spec.container.secret_env_vars[env_key] = secret_ref
        return self
        
    def environment_variables(self, env_dict: Dict[str, str]) -> Self:
        """Set multiple environment variables (chainable)"""
        self.spec.container.env_vars.update(env_dict)
        return self
        
    # Network and security
    
    def public(self) -> Self:
        """Allow public access (chainable)"""
        self.spec.allow_unauthenticated = True
        self.spec.ingress = IngressType.ALL
        return self
        
    def private(self) -> Self:
        """Restrict to authenticated requests (chainable)"""
        self.spec.allow_unauthenticated = False
        self.spec.ingress = IngressType.INTERNAL
        return self
        
    def internal_only(self) -> Self:
        """VPC internal traffic only (chainable)"""
        self.spec.ingress = IngressType.INTERNAL
        return self
        
    def service_account(self, account: str) -> Self:
        """Set service account (chainable)"""
        self.spec.service_account = account
        return self
        
    def vpc_connector(self, connector_name: str) -> Self:
        """Connect to VPC (chainable)"""
        self.spec.vpc_connector = connector_name
        return self
        
    def vpc_egress_all(self) -> Self:
        """Route all egress through VPC (chainable)"""
        self.spec.vpc_egress = "all-traffic"
        return self
        
    def vpc_egress_private(self) -> Self:
        """Route only private ranges through VPC (chainable)"""
        self.spec.vpc_egress = "private-ranges-only"
        return self
        
    def allow_unauthenticated(self) -> Self:
        """Allow unauthenticated public access (chainable)"""
        self.spec.allow_unauthenticated = True
        self.spec.ingress = IngressType.ALL
        return self
        
    # Health checks
    
    def startup_probe(self, path: str) -> Self:
        """Configure startup probe (chainable)"""
        self.spec.container.startup_probe_path = path
        return self
        
    def liveness_probe(self, path: str) -> Self:
        """Configure liveness probe (chainable)"""
        self.spec.container.liveness_probe_path = path
        return self
        
    def health_check(self, path: str) -> Self:
        """Configure both startup and liveness probes (chainable)"""
        self.spec.container.startup_probe_path = path
        self.spec.container.liveness_probe_path = path
        return self
        
    # Custom domains
    
    def domain(self, domain_name: str) -> Self:
        """Add custom domain (chainable)"""
        if domain_name not in self.spec.custom_domains:
            self.spec.custom_domains.append(domain_name)
        return self
        
    # Build configuration
    
    def build_arg(self, key: str, value: str) -> Self:
        """Add build argument for Dockerfile (chainable)"""
        self.spec.build_args[key] = value
        return self
        
    def build_args(self, args_dict: Dict[str, str] = None, **build_args) -> Self:
        """Set multiple build arguments (chainable)"""
        if args_dict:
            self.spec.build_args.update(args_dict)
        if build_args:
            self.spec.build_args.update(build_args)
        return self
        
    # Labels and metadata
    
    def label(self, key: str, value: str) -> Self:
        """Add a label (chainable)"""
        self.spec.labels[key] = value
        return self
        
    def labels(self, labels_dict: Dict[str, str] = None, **labels) -> Self:
        """Set multiple labels (chainable)"""
        if labels_dict:
            self.spec.labels.update(labels_dict)
        if labels:
            self.spec.labels.update(labels)
        return self
        
    def annotation(self, key: str, value: str) -> Self:
        """Add annotation (chainable)"""
        self.spec.annotations[key] = value
        return self
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .keep_warm(2)
                .cpu("1000m")
                .memory("1Gi")
                .timeout(300)
                .execution_environment_gen2()
                .startup_probe("/health")
                .liveness_probe("/health")
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .keep_warm(1)
                .cpu("500m")
                .memory("512Mi")
                .timeout(300)
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .scale_to_zero()
                .cpu("1000m")
                .memory("512Mi")
                .timeout(60)
                .label("environment", "development"))
                
    # Execution environment
    
    def execution_environment_gen1(self) -> Self:
        """Use first generation execution environment (chainable)"""
        self.spec.execution_environment = ExecutionEnvironment.FIRST_GEN
        return self
        
    def execution_environment_gen2(self) -> Self:
        """Use second generation execution environment (chainable)"""
        self.spec.execution_environment = ExecutionEnvironment.SECOND_GEN
        return self
        
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the service via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        # Build image if Dockerfile specified
        if self.spec.dockerfile_path:
            self.spec.container.image = self._build_image_if_needed()
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the service via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.update_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type, updates=diff
        )

    def _provider_destroy(self) -> None:
        """Destroy the service via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        if not self.status.cloud_id:
            raise ValueError("Resource has no cloud ID")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        provider.delete_resource(
            resource_id=self.status.cloud_id, resource_type=resource_type
        )
        
    # Convenience methods
    
    def get_url(self) -> Optional[str]:
        """Get service URL"""
        return self.status.provider_data.get("url")
        
    def get_latest_revision(self) -> Optional[str]:
        """Get latest revision name"""
        return self.status.provider_data.get("latest_revision")