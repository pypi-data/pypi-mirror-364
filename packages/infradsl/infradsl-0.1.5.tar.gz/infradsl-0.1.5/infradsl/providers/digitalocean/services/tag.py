"""
DigitalOcean Tag Service
"""

import digitalocean as do_client
from typing import Dict, Any, Optional
from ....core.exceptions import ProviderException


class TagService:
    """Handles tagging operations for DigitalOcean"""

    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        self._credentials = credentials

    def tag_droplet(self, droplet_id: str, tags: Dict[str, str]) -> None:
        """Apply tags to a DigitalOcean Droplet (only user-defined and infradsl.id)"""
        try:
            if not self._credentials:
                raise ProviderException("No credentials configured")

            # Include ALL tags (management + user-defined) for consistency
            allowed_tags = tags

            # Convert tags to DigitalOcean format - replace dots with underscores
            tag_list = []
            for k, v in allowed_tags.items():
                # DigitalOcean doesn't allow dots in tag names, replace with underscores
                k_safe = k.replace(".", "_")
                tag_list.append(f"{k_safe}:{v}")

            # Get current droplet to check existing tags
            droplet = do_client.Droplet(token=self._credentials["token"], id=droplet_id)
            droplet.load()
            existing_tags = set(droplet.tags) if droplet.tags else set()

            print(f"[DEBUG] DigitalOcean tagging: tag_list={tag_list}")
            print(f"[DEBUG] DigitalOcean tagging: existing_tags={existing_tags}")

            # Only add tags that don't already exist
            token = self._credentials["token"]
            for tag_name in tag_list:
                if tag_name not in existing_tags:
                    print(f"[DEBUG] Adding tag: {tag_name}")

                    # Check if tag already exists first
                    try:
                        tag = do_client.Tag(token=token, name=tag_name)
                        tag.load()  # Try to load existing tag
                        print(f"[DEBUG] Tag {tag_name} already exists")
                    except Exception:
                        # Tag doesn't exist, create it
                        try:
                            tag = do_client.Tag(token=token, name=tag_name)
                            tag.create()
                            print(f"[DEBUG] Created new tag: {tag_name}")
                        except Exception as create_error:
                            print(f"[DEBUG] Tag create error: {create_error}")
                            continue  # Skip this tag if creation fails

                    # Add tag to droplet
                    try:
                        # Convert droplet_id to integer if it's a string
                        droplet_id_int = (
                            int(droplet_id)
                            if isinstance(droplet_id, str)
                            else droplet_id
                        )
                        tag.add_droplets([droplet_id_int])
                        print(f"[DEBUG] Tag {tag_name} added to droplet {droplet_id}")
                    except Exception as add_error:
                        print(f"[DEBUG] Tag add error: {add_error}")
                else:
                    print(
                        f"[DEBUG] Tag {tag_name} already present on droplet {droplet_id}"
                    )

        except Exception as e:
            print(f"[DEBUG] Failed to tag droplet: {e}")
            raise ProviderException(f"Failed to tag droplet: {e}")

    def convert_tags_from_digitalocean(self, droplet_tags: list) -> list:
        """Convert tags back - replace underscores with dots for infradsl tags"""
        converted_tags = []
        for tag in droplet_tags:
            if tag.startswith("infradsl_") and ":" in tag:
                # Convert infradsl_id:xxx back to infradsl.id:xxx
                key, value = tag.split(":", 1)
                key_restored = key.replace("_", ".")
                converted_tags.append(f"{key_restored}:{value}")
            else:
                # Keep other tags as-is
                converted_tags.append(tag)
        return converted_tags

    def convert_tags_to_digitalocean(self, tags_dict: Dict[str, str]) -> list:
        """Convert tags - replace dots with underscores for DigitalOcean compatibility"""
        tag_list = []
        for k, v in tags_dict.items():
            # DigitalOcean doesn't allow dots in tag names
            k_safe = k.replace(".", "_")
            tag_list.append(f"{k_safe}:{v}")
        return tag_list
