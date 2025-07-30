"""
Google Cloud Run Service Implementation
"""

from typing import Any, Dict, Optional, List
import logging

from ....core.exceptions import ProviderException
from ....core.interfaces.provider import ResourceMetadata

logger = logging.getLogger(__name__)


class CloudRunService:
    """Handles Cloud Run operations for GCP provider"""
    
    def __init__(self, provider):
        self.provider = provider
        self._run_client = None
        self._iam_client = None
        
    @property
    def run_client(self):
        """Get or create Cloud Run client"""
        if self._run_client is None:
            try:
                from google.cloud import run_v2
                self._run_client = run_v2.ServicesClient()
            except ImportError:
                raise ProviderException(
                    "Google Cloud Run SDK not installed. Run: pip install google-cloud-run"
                )
        return self._run_client
        
    @property
    def iam_client(self):
        """Get or create IAM client for managing access"""
        if self._iam_client is None:
            try:
                from google.iam.v1 import iam_policy_pb2
                from google.iam.v1.policy_pb2 import Policy, Binding
                self._iam_client = {"Policy": Policy, "Binding": Binding}
            except ImportError:
                raise ProviderException(
                    "Google IAM SDK not installed. Run: pip install google-iam"
                )
        return self._iam_client
        
    def create_service(self, config: Dict[str, Any], metadata: ResourceMetadata) -> Dict[str, Any]:
        """Create a Cloud Run service using gcloud CLI for simplicity"""
        try:
            import subprocess
            import json
            
            # Build gcloud command to create Cloud Run service
            container_spec = config["template"]["spec"]["containers"][0]
            
            cmd = [
                "gcloud", "run", "deploy", config["name"],
                "--image", container_spec["image"],
                "--region", config["location"],
                "--platform", "managed",
                "--quiet",
                "--format", "json"
            ]
            
            # Cloud Run automatically handles port configuration via PORT env var
            # No need to specify --port flag as it can cause conflicts
                
            # Add memory limit
            if "resources" in container_spec and "limits" in container_spec["resources"]:
                if "memory" in container_spec["resources"]["limits"]:
                    cmd.extend(["--memory", container_spec["resources"]["limits"]["memory"]])
                if "cpu" in container_spec["resources"]["limits"]:
                    cmd.extend(["--cpu", container_spec["resources"]["limits"]["cpu"]])
                    
            # Add environment variables
            if "env" in container_spec:
                env_vars = []
                for env_var in container_spec["env"]:
                    if "value" in env_var:
                        env_vars.append(f"{env_var['name']}={env_var['value']}")
                if env_vars:
                    cmd.extend(["--set-env-vars", ",".join(env_vars)])
                    
            # Add scaling settings
            template_annotations = config.get("template", {}).get("metadata", {}).get("annotations", {})
            if "autoscaling.knative.dev/minScale" in template_annotations:
                cmd.extend(["--min-instances", template_annotations["autoscaling.knative.dev/minScale"]])
            if "autoscaling.knative.dev/maxScale" in template_annotations:
                cmd.extend(["--max-instances", template_annotations["autoscaling.knative.dev/maxScale"]])
                
            # Add concurrency
            if "containerConcurrency" in config["template"]["spec"]:
                cmd.extend(["--concurrency", str(config["template"]["spec"]["containerConcurrency"])])
                
            # Add timeout
            if "timeoutSeconds" in config["template"]["spec"]:
                cmd.extend(["--timeout", f"{config['template']['spec']['timeoutSeconds']}s"])
                
            # Add public access
            if config.get("members") and "allUsers" in config["members"]:
                cmd.append("--allow-unauthenticated")
            else:
                cmd.append("--no-allow-unauthenticated")
                
            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Parse the response
            service_info = json.loads(result.stdout)
            
            return {
                "id": service_info["metadata"]["name"],
                "name": service_info["metadata"]["name"].split("/")[-1],
                "url": service_info["status"]["url"],
                "latest_revision": service_info["status"].get("latestReadyRevisionName", ""),
                "status": "deployed",
                "region": config["location"]
            }
            
        except subprocess.CalledProcessError as e:
            logger.error(f"gcloud command failed: {e.stderr}")
            raise ProviderException(f"Failed to create Cloud Run service: {e.stderr}")
        except Exception as e:
            logger.error(f"Failed to create Cloud Run service: {e}")
            raise ProviderException(f"Failed to create Cloud Run service: {str(e)}")
            
    def update_service(self, resource_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Cloud Run service"""
        try:
            from google.cloud import run_v2
            from google.protobuf import field_mask_pb2
            
            # Get current service
            request = run_v2.GetServiceRequest(name=resource_id)
            service = self.run_client.get_service(request=request)
            
            # Apply updates
            update_mask = []
            
            # Update container image if provided
            if "image" in updates:
                service.template.containers[0].image = updates["image"]
                update_mask.append("template.containers")
                
            # Update resources if provided
            if "cpu" in updates or "memory" in updates:
                if "cpu" in updates:
                    service.template.containers[0].resources.limits["cpu"] = updates["cpu"]
                if "memory" in updates:
                    service.template.containers[0].resources.limits["memory"] = updates["memory"]
                update_mask.append("template.containers")
                
            # Update environment variables
            if "env_vars" in updates:
                service.template.containers[0].env.clear()
                for key, value in updates["env_vars"].items():
                    env = service.template.containers[0].env.add()
                    env.name = key
                    env.value = value
                update_mask.append("template.containers")
                
            # Update scaling
            if "min_instances" in updates:
                service.template.annotations["autoscaling.knative.dev/minScale"] = str(updates["min_instances"])
                update_mask.append("template.annotations")
            if "max_instances" in updates:
                service.template.annotations["autoscaling.knative.dev/maxScale"] = str(updates["max_instances"])
                update_mask.append("template.annotations")
                
            # Update the service
            update_request = run_v2.UpdateServiceRequest(
                service=service,
                update_mask=field_mask_pb2.FieldMask(paths=update_mask)
            )
            
            operation = self.run_client.update_service(request=update_request)
            response = operation.result()
            
            return {
                "id": response.name,
                "name": response.name.split("/")[-1],
                "url": response.uri,
                "latest_revision": response.latest_ready_revision,
                "status": "updated"
            }
            
        except Exception as e:
            logger.error(f"Failed to update Cloud Run service: {e}")
            raise ProviderException(f"Failed to update Cloud Run service: {str(e)}")
            
    def delete_service(self, resource_id: str) -> None:
        """Delete a Cloud Run service"""
        try:
            from google.cloud import run_v2
            
            request = run_v2.DeleteServiceRequest(name=resource_id)
            operation = self.run_client.delete_service(request=request)
            operation.result()  # Wait for deletion to complete
            
        except Exception as e:
            logger.error(f"Failed to delete Cloud Run service: {e}")
            raise ProviderException(f"Failed to delete Cloud Run service: {str(e)}")
            
    def get_service(self, name: str, location: str) -> Optional[Dict[str, Any]]:
        """Get a Cloud Run service by name"""
        try:
            from google.cloud import run_v2
            
            service_name = f"projects/{self.provider.project_id}/locations/{location}/services/{name}"
            request = run_v2.GetServiceRequest(name=service_name)
            
            service = self.run_client.get_service(request=request)
            
            return {
                "id": service.name,
                "name": service.name.split("/")[-1],
                "url": service.uri,
                "latest_revision": service.latest_ready_revision,
                "status": "deployed",
                "region": location,
                "image": service.template.containers[0].image if service.template.containers else None
            }
            
        except Exception as e:
            logger.debug(f"Service not found: {e}")
            return None
            
    def list_services(self, location: str = None) -> List[Dict[str, Any]]:
        """List all Cloud Run services"""
        try:
            from google.cloud import run_v2
            
            services = []
            
            # If location specified, list for that location
            if location:
                locations = [location]
            else:
                # List common Cloud Run locations
                locations = ["us-central1", "europe-north1", "asia-northeast1"]
                
            for loc in locations:
                try:
                    parent = f"projects/{self.provider.project_id}/locations/{loc}"
                    request = run_v2.ListServicesRequest(parent=parent)
                    
                    for service in self.run_client.list_services(request=request):
                        services.append({
                            "id": service.name,
                            "name": service.name.split("/")[-1],
                            "url": service.uri,
                            "latest_revision": service.latest_ready_revision,
                            "status": "deployed",
                            "region": loc,
                            "image": service.template.containers[0].image if service.template.containers else None
                        })
                except Exception as e:
                    logger.debug(f"Could not list services in {loc}: {e}")
                    continue
                    
            return services
            
        except Exception as e:
            logger.error(f"Failed to list Cloud Run services: {e}")
            return []
            
    def _set_public_access(self, service_name: str) -> None:
        """Set IAM policy to allow public access"""
        try:
            from google.cloud import run_v2
            from google.iam.v1 import iam_policy_pb2
            
            # Create IAM policy binding
            policy = self.run_client.get_iam_policy(
                request=iam_policy_pb2.GetIamPolicyRequest(resource=service_name)
            )
            
            # Add allUsers binding for Cloud Run invoker role
            binding = policy.bindings.add()
            binding.role = "roles/run.invoker"
            binding.members.append("allUsers")
            
            # Update the policy
            self.run_client.set_iam_policy(
                request=iam_policy_pb2.SetIamPolicyRequest(
                    resource=service_name,
                    policy=policy
                )
            )
            
        except Exception as e:
            logger.warning(f"Failed to set public access policy: {e}")