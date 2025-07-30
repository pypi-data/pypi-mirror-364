from typing import Optional, Dict, Any, Self, List, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import os
import subprocess
import json

if TYPE_CHECKING:
    from infradsl.core.interfaces.provider import ProviderInterface

from ...core.nexus.base_resource import BaseResource, ResourceSpec


class SiteType(Enum):
    """Firebase Hosting site types"""
    STATIC = "static"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NEXTJS = "nextjs"
    NUXTJS = "nuxtjs"
    DOCUMENTATION = "documentation"
    CUSTOM = "custom"


@dataclass
class RedirectRule:
    """Firebase Hosting redirect rule"""
    source: str
    destination: str
    type: int = 301  # 301 or 302


@dataclass
class RewriteRule:
    """Firebase Hosting rewrite rule"""
    source: str
    destination: Optional[str] = None
    function: Optional[str] = None
    run: Optional[str] = None


@dataclass
class HeaderRule:
    """Firebase Hosting header rule"""
    source: str
    headers: List[Dict[str, str]]


@dataclass
class FirebaseHostingSpec(ResourceSpec):
    """Specification for Firebase Hosting site"""
    
    # Project configuration
    project_id: str = ""
    site_id: str = ""
    
    # Site configuration
    site_type: SiteType = SiteType.STATIC
    public_directory: str = "public"
    index_file: str = "index.html"
    error_file: str = "404.html"
    
    # Build configuration
    build_command: str = ""
    build_directory: str = "."
    build_env: Dict[str, str] = field(default_factory=dict)
    
    # Custom domains
    custom_domains: List[str] = field(default_factory=list)
    
    # Routing rules
    redirects: List[RedirectRule] = field(default_factory=list)
    rewrites: List[RewriteRule] = field(default_factory=list)
    headers: List[HeaderRule] = field(default_factory=list)
    
    # Security
    ignore_patterns: List[str] = field(default_factory=list)
    
    # Features
    clean_urls: bool = True
    trailing_slash_behavior: str = "auto"  # auto, add, remove
    
    # Authentication integration
    require_auth: bool = False
    auth_domains: List[str] = field(default_factory=list)
    
    # Labels
    labels: Dict[str, str] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_config: Dict[str, Any] = field(default_factory=dict)


class FirebaseHosting(BaseResource):
    """
    Firebase Hosting for static sites, SPAs, and web applications with Rails-like conventions.
    
    Examples:
        # Simple static site
        site = (FirebaseHosting("my-site")
                .project("my-project")
                .static_site()
                .public_directory("dist")
                .custom_domain("myapp.com"))
        
        # React app with authentication
        app = (FirebaseHosting("react-app")
               .project("my-project") 
               .react_app()
               .build_command("npm run build")
               .build_directory(".")
               .public_directory("build")
               .auth()
               .custom_domain("app.mycompany.com")
               .spa_fallback())
        
        # Documentation site
        docs = (FirebaseHosting("docs")
                .project("my-project")
                .documentation_site()
                .build_command("mkdocs build")
                .public_directory("site")
                .custom_domain("docs.myapp.com")
                .redirect("/old-docs", "/", 301))
        
        # Next.js application
        nextjs = (FirebaseHosting("nextjs-app")
                  .project("my-project")
                  .nextjs_app()
                  .build_command("npm run build && npm run export")
                  .public_directory("out")
                  .custom_domain("nextjs.myapp.com")
                  .production())
    """
    
    def __init__(self, name: str):
        super().__init__(name)
        self.spec: FirebaseHostingSpec = self._create_spec()
        self.metadata.annotations["resource_type"] = "FirebaseHosting"
        
    def _create_spec(self) -> FirebaseHostingSpec:
        # Initialize with sensible defaults
        spec = FirebaseHostingSpec(
            site_id=self.name,
            ignore_patterns=[
                "firebase.json",
                "**/.*",
                "**/node_modules/**"
            ]
        )
        return spec
        
    def _validate_spec(self) -> None:
        """Validate Firebase Hosting specification"""
        if not self.spec.project_id:
            raise ValueError("Firebase project ID is required")
            
        if not self.spec.site_id:
            self.spec.site_id = self.name
            
        if self.spec.require_auth and not self.spec.auth_domains:
            self.spec.auth_domains.append(f"{self.spec.project_id}.firebaseapp.com")
            
    def _to_provider_config(self) -> Dict[str, Any]:
        """Convert to provider-specific configuration"""
        if not self._provider:
            raise ValueError("No provider attached")

        config = {
            "project_id": self.spec.project_id,
            "site_id": self.spec.site_id,
            "hosting_config": self._generate_hosting_config(),
            "labels": {**self.spec.labels, **self.metadata.to_tags()},
        }

        # Provider-specific mappings
        if hasattr(self._provider, 'config') and hasattr(self._provider.config, 'type'):
            provider_type_str = self._provider.config.type.value.lower()
        else:
            provider_type_str = str(self._provider).lower()

        if provider_type_str == "gcp":
            config.update(self._to_gcp_config())

        # Apply provider-specific overrides
        config.update(self.spec.provider_config)

        return config
        
    def _generate_hosting_config(self) -> Dict[str, Any]:
        """Generate Firebase hosting configuration"""
        config = {
            "public": self.spec.public_directory,
            "ignore": self.spec.ignore_patterns.copy(),
            "cleanUrls": self.spec.clean_urls,
        }
        
        # Redirects
        if self.spec.redirects:
            config["redirects"] = [
                {
                    "source": redirect.source,
                    "destination": redirect.destination,
                    "type": redirect.type
                }
                for redirect in self.spec.redirects
            ]
            
        # Rewrites
        if self.spec.rewrites:
            config["rewrites"] = []
            for rewrite in self.spec.rewrites:
                rule = {"source": rewrite.source}
                if rewrite.destination:
                    rule["destination"] = rewrite.destination
                elif rewrite.function:
                    rule["function"] = rewrite.function
                elif rewrite.run:
                    rule["run"] = {"serviceId": rewrite.run}
                config["rewrites"].append(rule)
                
        # Headers
        if self.spec.headers:
            config["headers"] = [
                {
                    "source": header.source,
                    "headers": header.headers
                }
                for header in self.spec.headers
            ]
            
        # Trailing slash behavior
        if self.spec.trailing_slash_behavior != "auto":
            config["trailingSlash"] = self.spec.trailing_slash_behavior == "add"
            
        return config

    def _to_gcp_config(self) -> Dict[str, Any]:
        """Convert to GCP Firebase configuration"""
        config = {
            "resource_type": "firebase_hosting_site"
        }
        
        # Custom domains configuration
        if self.spec.custom_domains:
            config["custom_domains"] = self.spec.custom_domains
            
        return config
        
    # Fluent interface methods
    
    # Project configuration
    
    def project(self, project_id: str) -> Self:
        """Set Firebase project ID (chainable)"""
        self.spec.project_id = project_id
        return self
        
    def site_id(self, site_id: str) -> Self:
        """Set site ID (chainable)"""
        self.spec.site_id = site_id
        return self
        
    # Site type configurations
    
    def static_site(self) -> Self:
        """Configure as static site (chainable)"""
        self.spec.site_type = SiteType.STATIC
        self.spec.public_directory = "public"
        return self
        
    def react_app(self) -> Self:
        """Configure as React application (chainable)"""
        self.spec.site_type = SiteType.REACT
        self.spec.public_directory = "build"
        self.spec.build_command = "npm run build"
        return self._add_spa_rewrites()
        
    def vue_app(self) -> Self:
        """Configure as Vue.js application (chainable)"""
        self.spec.site_type = SiteType.VUE
        self.spec.public_directory = "dist"
        self.spec.build_command = "npm run build"
        return self._add_spa_rewrites()
        
    def angular_app(self) -> Self:
        """Configure as Angular application (chainable)"""
        self.spec.site_type = SiteType.ANGULAR
        self.spec.public_directory = "dist"
        self.spec.build_command = "ng build --prod"
        return self._add_spa_rewrites()
        
    def nextjs_app(self) -> Self:
        """Configure as Next.js application (chainable)"""
        self.spec.site_type = SiteType.NEXTJS
        self.spec.public_directory = "out"
        self.spec.build_command = "npm run build && npm run export"
        return self
        
    def nuxtjs_app(self) -> Self:
        """Configure as Nuxt.js application (chainable)"""
        self.spec.site_type = SiteType.NUXTJS
        self.spec.public_directory = "dist"
        self.spec.build_command = "npm run generate"
        return self
        
    def documentation_site(self) -> Self:
        """Configure as documentation site (chainable)"""
        self.spec.site_type = SiteType.DOCUMENTATION
        self.spec.public_directory = "site"
        self.spec.build_command = "mkdocs build"
        self.spec.clean_urls = True
        return self
        
    def _add_spa_rewrites(self) -> Self:
        """Add SPA routing rewrites"""
        self.spec.rewrites.append(
            RewriteRule(source="**", destination="/index.html")
        )
        return self
        
    # Build configuration
    
    def build_command(self, command: str) -> Self:
        """Set build command (chainable)"""
        self.spec.build_command = command
        return self
        
    def build_directory(self, directory: str) -> Self:
        """Set build working directory (chainable)"""
        self.spec.build_directory = directory
        return self
        
    def build_env(self, env_dict: Dict[str, str] = None, **env_vars) -> Self:
        """Set build environment variables (chainable)"""
        if env_dict:
            self.spec.build_env.update(env_dict)
        if env_vars:
            self.spec.build_env.update(env_vars)
        return self
        
    def public_directory(self, directory: str) -> Self:
        """Set public/output directory (chainable)"""
        self.spec.public_directory = directory
        return self
        
    def index_file(self, filename: str) -> Self:
        """Set index file (chainable)"""
        self.spec.index_file = filename
        return self
        
    def error_file(self, filename: str) -> Self:
        """Set 404 error file (chainable)"""
        self.spec.error_file = filename
        return self
        
    # Custom domains
    
    def custom_domain(self, domain: str) -> Self:
        """Add custom domain (chainable)"""
        if domain not in self.spec.custom_domains:
            self.spec.custom_domains.append(domain)
        return self
        
    def custom_domains(self, domains: List[str]) -> Self:
        """Set multiple custom domains (chainable)"""
        self.spec.custom_domains = domains.copy()
        return self
        
    # Routing rules
    
    def redirect(self, source: str, destination: str, redirect_type: int = 301) -> Self:
        """Add redirect rule (chainable)"""
        self.spec.redirects.append(
            RedirectRule(source=source, destination=destination, type=redirect_type)
        )
        return self
        
    def rewrite(self, source: str, destination: str = None, function: str = None, 
               cloud_run: str = None) -> Self:
        """Add rewrite rule (chainable)"""
        self.spec.rewrites.append(
            RewriteRule(source=source, destination=destination, 
                       function=function, run=cloud_run)
        )
        return self
        
    def spa_fallback(self, fallback: str = "/index.html") -> Self:
        """Add SPA fallback rewrite (chainable)"""
        return self.rewrite("**", fallback)
        
    def api_rewrite(self, path: str, function_name: str) -> Self:
        """Rewrite API path to Cloud Function (chainable)"""
        return self.rewrite(f"/api/{path}/**", function=function_name)
        
    def cloud_run_rewrite(self, path: str, service_id: str) -> Self:
        """Rewrite path to Cloud Run service (chainable)"""
        return self.rewrite(f"/{path}/**", cloud_run=service_id)
        
    # Security headers
    
    def security_headers(self) -> Self:
        """Add standard security headers (chainable)"""
        headers = [
            {"key": "X-Content-Type-Options", "value": "nosniff"},
            {"key": "X-Frame-Options", "value": "DENY"},
            {"key": "X-XSS-Protection", "value": "1; mode=block"},
            {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
            {"key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'"}
        ]
        
        self.spec.headers.append(
            HeaderRule(source="/**", headers=headers)
        )
        return self
        
    def cors_headers(self, origins: List[str] = None) -> Self:
        """Add CORS headers (chainable)"""
        origins = origins or ["*"]
        headers = [
            {"key": "Access-Control-Allow-Origin", "value": ",".join(origins)},
            {"key": "Access-Control-Allow-Methods", "value": "GET, POST, PUT, DELETE, OPTIONS"},
            {"key": "Access-Control-Allow-Headers", "value": "Content-Type, Authorization"}
        ]
        
        self.spec.headers.append(
            HeaderRule(source="/api/**", headers=headers)
        )
        return self
        
    def cache_headers(self, max_age: int = 3600, paths: str = "/**") -> Self:
        """Add cache headers (chainable)"""
        headers = [
            {"key": "Cache-Control", "value": f"public, max-age={max_age}"}
        ]
        
        self.spec.headers.append(
            HeaderRule(source=paths, headers=headers)
        )
        return self
        
    # Authentication
    
    def auth(self, required: bool = True) -> Self:
        """Require authentication (chainable)"""
        self.spec.require_auth = required
        return self
        
    def auth_domain(self, domain: str) -> Self:
        """Add authorized domain (chainable)"""
        if domain not in self.spec.auth_domains:
            self.spec.auth_domains.append(domain)
        return self
        
    # Configuration
    
    def clean_urls(self, enabled: bool = True) -> Self:
        """Enable/disable clean URLs (chainable)"""
        self.spec.clean_urls = enabled
        return self
        
    def trailing_slash(self, behavior: str = "auto") -> Self:
        """Set trailing slash behavior: auto, add, remove (chainable)"""
        if behavior not in ["auto", "add", "remove"]:
            raise ValueError("Trailing slash behavior must be 'auto', 'add', or 'remove'")
        self.spec.trailing_slash_behavior = behavior
        return self
        
    def ignore(self, *patterns: str) -> Self:
        """Add ignore patterns (chainable)"""
        self.spec.ignore_patterns.extend(patterns)
        return self
        
    # Labels
    
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
        
    # Environment-based conveniences
    
    def production(self) -> Self:
        """Configure for production environment (chainable)"""
        return (self
                .security_headers()
                .cache_headers(max_age=86400)  # 24 hours
                .label("environment", "production"))
                
    def staging(self) -> Self:
        """Configure for staging environment (chainable)"""
        return (self
                .cache_headers(max_age=300)  # 5 minutes
                .label("environment", "staging"))
                
    def development(self) -> Self:
        """Configure for development environment (chainable)"""
        return (self
                .cache_headers(max_age=0)  # No cache
                .label("environment", "development"))
                
    # Build and deployment helpers
    
    def build(self) -> Self:
        """Run build command if specified (chainable)"""
        if not self.spec.build_command:
            return self
            
        print(f"🔨 Building {self.name}...")
        
        # Change to build directory
        original_dir = os.getcwd()
        if self.spec.build_directory and self.spec.build_directory != ".":
            os.chdir(self.spec.build_directory)
            
        try:
            # Set build environment
            env = os.environ.copy()
            env.update(self.spec.build_env)
            
            # Run build command
            result = subprocess.run(
                self.spec.build_command,
                shell=True,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Build failed: {result.stderr}")
                raise RuntimeError(f"Build command failed: {result.stderr}")
            else:
                print(f"✅ Build completed successfully")
                
        finally:
            # Restore original directory
            os.chdir(original_dir)
            
        return self
        
    def deploy(self) -> Self:
        """Deploy to Firebase Hosting"""
        self.build()
        
        # Generate firebase.json
        self._generate_firebase_config()
        
        print(f"🚀 Deploying {self.name} to Firebase Hosting...")
        
        # Deploy using Firebase CLI
        deploy_cmd = f"firebase deploy --only hosting:{self.spec.site_id}"
        if self.spec.project_id:
            deploy_cmd += f" --project {self.spec.project_id}"
            
        result = subprocess.run(deploy_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Deployment failed: {result.stderr}")
            raise RuntimeError(f"Deployment failed: {result.stderr}")
        else:
            print(f"✅ Deployed successfully")
            
        return self
        
    def _generate_firebase_config(self) -> None:
        """Generate firebase.json configuration file"""
        config = {
            "hosting": {
                "site": self.spec.site_id,
                **self._generate_hosting_config()
            }
        }
        
        with open("firebase.json", "w") as f:
            json.dump(config, f, indent=2)
            
        print(f"📝 Generated firebase.json")
        
    # Provider implementation methods
    
    def _provider_create(self) -> Dict[str, Any]:
        """Create the Firebase Hosting site via provider"""
        if not self._provider:
            raise ValueError("No provider attached")
        
        from typing import cast
        provider = cast("ProviderInterface", self._provider)
        
        config = self._to_provider_config()
        resource_type = config.pop("resource_type")
        
        return provider.create_resource(
            resource_type=resource_type, config=config, metadata=self.metadata
        )

    def _provider_update(self, diff: Dict[str, Any]) -> Dict[str, Any]:
        """Update the Firebase Hosting site via provider"""
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
        """Destroy the Firebase Hosting site via provider"""
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
    
    def get_url(self) -> str:
        """Get hosting URL"""
        if self.spec.custom_domains:
            return f"https://{self.spec.custom_domains[0]}"
        return f"https://{self.spec.site_id}.web.app"
        
    def get_all_urls(self) -> List[str]:
        """Get all hosting URLs"""
        urls = [f"https://{self.spec.site_id}.web.app"]
        urls.extend([f"https://{domain}" for domain in self.spec.custom_domains])
        return urls