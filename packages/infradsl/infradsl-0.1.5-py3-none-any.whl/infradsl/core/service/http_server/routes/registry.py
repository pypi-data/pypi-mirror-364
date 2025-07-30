"""
Registry Routes - Web interface endpoints for template registry management

Provides web interface for:
- User authentication with Firebase
- Template browsing (public/private)  
- Template details and management
- Workspace management
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, Depends, Request, Response, Form, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from infradsl.cli.registry import TemplateRegistryClient
from infradsl.core.config import get_config

logger = logging.getLogger(__name__)


class RegistryRoutes:
    """Handles template registry web interface endpoints"""
    
    def __init__(self, templates: Jinja2Templates, host: str, port: int):
        self.templates = templates
        self.host = host
        self.port = port
        self.registry_client = None
        
    def setup_routes(self, app, auth_dependency):
        """Setup template registry web routes"""
        
        @app.get("/registry", response_class=HTMLResponse, tags=["Registry"])
        async def registry_home(request: Request):
            """Registry landing page"""
            try:
                # Check if user is authenticated
                config = get_config()
                auth_data = config.get("auth", {})
                
                context = {
                    "request": request,
                    "title": "InfraDSL Template Registry",
                    "authenticated": bool(auth_data.get("id_token")),
                    "user_email": auth_data.get("email", ""),
                    "workspace": auth_data.get("workspace", ""),
                    "firebase_config": self._get_firebase_config()
                }
                
                return self.templates.TemplateResponse("registry/home.html", context)
                
            except Exception as e:
                logger.error(f"Registry home error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.get("/registry/login", response_class=HTMLResponse, tags=["Registry"])
        async def registry_login(request: Request):
            """Registry login page"""
            try:
                context = {
                    "request": request,
                    "title": "Login - InfraDSL Registry", 
                    "firebase_config": self._get_firebase_config()
                }
                
                return self.templates.TemplateResponse("registry/login.html", context)
                
            except Exception as e:
                logger.error(f"Registry login error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.get("/registry/register", response_class=HTMLResponse, tags=["Registry"])
        async def registry_register(request: Request):
            """Registry registration page"""
            try:
                context = {
                    "request": request,
                    "title": "Register - InfraDSL Registry",
                    "firebase_config": self._get_firebase_config()
                }
                
                return self.templates.TemplateResponse("registry/register.html", context)
                
            except Exception as e:
                logger.error(f"Registry register error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.get("/registry/dashboard", response_class=HTMLResponse, tags=["Registry"])
        async def registry_dashboard(request: Request):
            """Registry dashboard - main template browser"""
            try:
                # Check authentication
                config = get_config()
                auth_data = config.get("auth", {})
                
                if not auth_data.get("id_token"):
                    return RedirectResponse("/registry/login", status_code=302)
                    
                context = {
                    "request": request,
                    "title": "Template Dashboard - InfraDSL Registry",
                    "user_email": auth_data.get("email", ""),
                    "workspace": auth_data.get("workspace", ""),
                    "display_name": auth_data.get("display_name", ""),
                    "firebase_config": self._get_firebase_config()
                }
                
                return self.templates.TemplateResponse("registry/dashboard.html", context)
                
            except Exception as e:
                logger.error(f"Registry dashboard error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.get("/api/registry/templates", tags=["Registry API"])
        async def get_templates(
            workspace: Optional[str] = None,
            public_only: bool = False,
            search: Optional[str] = None
        ):
            """Get templates for dashboard"""
            try:
                # Mock data for now - replace with actual registry client calls
                templates = [
                    {
                        "id": "generic-vm",
                        "name": "GenericVM",
                        "version": "1.0.0",
                        "description": "Basic virtual machine template",
                        "author": "InfraDSL Team",
                        "category": "compute",
                        "tags": ["vm", "basic"],
                        "providers": ["aws", "gcp", "azure"],
                        "visibility": "public",
                        "workspace": "infradsl",
                        "downloads": 125,
                        "created_at": "2024-01-15T10:00:00Z",
                        "updated_at": "2024-01-20T15:30:00Z"
                    },
                    {
                        "id": "web-app",
                        "name": "WebApp",
                        "version": "2.1.0", 
                        "description": "Full-stack web application template with auto-scaling",
                        "author": "DevOps Team",
                        "category": "web",
                        "tags": ["web", "app", "scalable"],
                        "providers": ["aws", "gcp"],
                        "visibility": "public",
                        "workspace": "infradsl",
                        "downloads": 89,
                        "created_at": "2024-01-10T14:20:00Z",
                        "updated_at": "2024-01-25T09:45:00Z"
                    },
                    {
                        "id": "database-cluster",
                        "name": "DatabaseCluster", 
                        "version": "1.5.0",
                        "description": "High-availability database cluster template",
                        "author": "Data Team",
                        "category": "database",
                        "tags": ["database", "ha", "cluster"],
                        "providers": ["aws", "gcp"],
                        "visibility": "private",
                        "workspace": "infradsl",
                        "downloads": 34,
                        "created_at": "2024-01-08T11:15:00Z",
                        "updated_at": "2024-01-22T16:20:00Z"
                    }
                ]
                
                # Filter by search if provided
                if search:
                    search_lower = search.lower()
                    templates = [
                        t for t in templates 
                        if search_lower in t["name"].lower() 
                        or search_lower in t["description"].lower()
                        or any(search_lower in tag for tag in t["tags"])
                    ]
                
                # Filter by visibility
                if public_only:
                    templates = [t for t in templates if t["visibility"] == "public"]
                    
                # Filter by workspace
                if workspace:
                    templates = [t for t in templates if t["workspace"] == workspace]
                
                return {"templates": templates}
                
            except Exception as e:
                logger.error(f"Get templates error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.get("/registry/template/{template_id}", response_class=HTMLResponse, tags=["Registry"])
        async def template_detail(request: Request, template_id: str):
            """Template detail page"""
            try:
                # Check authentication
                config = get_config()
                auth_data = config.get("auth", {})
                
                if not auth_data.get("id_token"):
                    return RedirectResponse("/registry/login", status_code=302)
                
                # Mock template data - replace with actual lookup
                template_data = {
                    "id": template_id,
                    "name": "GenericVM" if template_id == "generic-vm" else "WebApp",
                    "version": "1.0.0",
                    "description": "A comprehensive template description goes here...",
                    "author": "InfraDSL Team",
                    "category": "compute",
                    "tags": ["vm", "basic", "compute"],
                    "providers": ["aws", "gcp", "azure"],
                    "visibility": "public",
                    "workspace": "infradsl",
                    "downloads": 125,
                    "created_at": "2024-01-15T10:00:00Z",
                    "updated_at": "2024-01-20T15:30:00Z",
                    "readme": """# GenericVM Template

A basic virtual machine template for quick deployments.

## Usage

```python
from infradsl.templates import Template

# Basic usage
vm = Template.GenericVM("my-server")

# With customization  
vm = (Template.GenericVM("my-server")
      .with_parameters(
          instance_type="large",
          environment="production"
      )
      .production())
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| instance_type | string | medium | Instance size |
| environment | string | development | Environment type |

## Outputs

- `instance_id`: The created instance ID
- `public_ip`: The public IP address
"""
                }
                
                context = {
                    "request": request,
                    "title": f"{template_data['name']} - InfraDSL Registry",
                    "template": template_data,
                    "user_email": auth_data.get("email", ""),
                    "workspace": auth_data.get("workspace", ""),
                    "can_edit": template_data["workspace"] == auth_data.get("workspace", ""),
                    "firebase_config": self._get_firebase_config()
                }
                
                return self.templates.TemplateResponse("registry/template_detail.html", context)
                
            except Exception as e:
                logger.error(f"Template detail error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.post("/api/registry/templates/{template_id}/delete", tags=["Registry API"])
        async def delete_template(template_id: str):
            """Delete a template (owner only)"""
            try:
                # Check authentication  
                config = get_config()
                auth_data = config.get("auth", {})
                
                if not auth_data.get("id_token"):
                    raise HTTPException(status_code=401, detail="Authentication required")
                
                # TODO: Implement actual template deletion via registry client
                # For now, just return success
                
                return {"success": True, "message": f"Template {template_id} deleted successfully"}
                
            except Exception as e:
                logger.error(f"Delete template error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.post("/api/registry/auth/logout", tags=["Registry API"]) 
        async def logout():
            """Logout user and clear auth data"""
            try:
                # Clear auth data from config
                config = get_config()
                if "auth" in config:
                    del config["auth"]
                if "registry" in config:
                    if "auth_token" in config["registry"]:
                        del config["registry"]["auth_token"]
                
                # Would save config here
                # set_config(config)
                
                return {"success": True, "message": "Logged out successfully"}
                
            except Exception as e:
                logger.error(f"Logout error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
                
    def _get_firebase_config(self) -> Dict[str, str]:
        """Get Firebase configuration for frontend"""
        import os
        
        return {
            "apiKey": os.environ.get("FIREBASE_API_KEY", ""),
            "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN", "infradsl.firebaseapp.com"),
            "projectId": os.environ.get("FIREBASE_PROJECTID", "infradsl"),
            "storageBucket": os.environ.get("STORAGE_BUCKET", "infradsl.firebasestorage.app"),
            "messagingSenderId": os.environ.get("MESSAGING_SENDER_ID", "245449489626"),
            "appId": os.environ.get("FIREBASE_APP_ID", "1:245449489626:web:bfb84212b555a63e8739e3")
        }