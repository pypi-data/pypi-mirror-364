"""
DigitalOcean SSH Key Service
"""

import digitalocean as do_client
from typing import Dict, Any, Optional, List
from ....core.exceptions import ProviderException


class SSHKeyService:
    """Handles SSH key operations for DigitalOcean"""

    def __init__(self, client, credentials: Optional[Dict[str, Any]] = None):
        self._client = client
        self._credentials = credentials

    def ensure_ssh_key_uploaded(self, key_name: str, key_content: str) -> str:
        """Ensure SSH key is uploaded to DigitalOcean, return the key identifier"""
        try:
            if not self._client:
                raise ProviderException("Client not initialized")

            # Check if key already exists by name OR by public key content
            existing_keys = self._client.get_all_sshkeys()
            for key in existing_keys:
                if key.name == key_name:
                    print(
                        f"[DEBUG] SSH key '{key_name}' already exists by name, using existing key"
                    )
                    return str(key.id)

                # Also check if the same public key content exists with a different name
                if (
                    hasattr(key, "public_key")
                    and key.public_key
                    and key.public_key.strip() == key_content.strip()
                ):
                    print(
                        f"[DEBUG] SSH key content already exists as '{key.name}', using existing key"
                    )
                    return str(key.id)

            # Upload new key
            print(f"[DEBUG] Uploading SSH key '{key_name}' to DigitalOcean")

            if not self._credentials:
                raise ProviderException("No credentials configured")
            ssh_key = do_client.SSHKey(
                token=self._credentials["token"],
                name=key_name,
                public_key=key_content,
            )
            ssh_key.create()

            print(
                f"[DEBUG] SSH key '{key_name}' uploaded successfully with ID: {ssh_key.id}"
            )
            return str(ssh_key.id)

        except Exception as e:
            # Handle specific DigitalOcean errors
            error_msg = str(e).lower()
            if "already in use" in error_msg or "already exists" in error_msg:
                # The key content is already uploaded, try to find it
                print(
                    f"[DEBUG] SSH key content already exists, searching for existing key..."
                )
                try:
                    existing_keys = self._client.get_all_sshkeys()
                    for key in existing_keys:
                        if (
                            hasattr(key, "public_key")
                            and key.public_key
                            and key.public_key.strip() == key_content.strip()
                        ):
                            print(
                                f"[DEBUG] Found existing key with same content: '{key.name}', using it"
                            )
                            return str(key.id)
                except:
                    pass

                # If we can't find the existing key, generate a unique name
                import time

                unique_name = f"{key_name}-{int(time.time())}"
                print(f"[DEBUG] Trying with unique name: '{unique_name}'")

                if not self._credentials:
                    raise ProviderException("No credentials configured")
                ssh_key = do_client.SSHKey(
                    token=self._credentials["token"],
                    name=unique_name,
                    public_key=key_content,
                )
                ssh_key.create()
                print(
                    f"[DEBUG] SSH key '{unique_name}' uploaded successfully with ID: {ssh_key.id}"
                )
                return str(ssh_key.id)

            if "Fingerprint could not be generated" in str(e):
                raise ProviderException(
                    f"Invalid SSH key content. Make sure the key is a valid public key, not a file path. Error: {e}"
                )
            raise ProviderException(f"Failed to upload SSH key '{key_name}': {e}")

    def process_ssh_keys(
        self, ssh_keys: List[str], ssh_key_content: Dict[str, str]
    ) -> List[int]:
        """Process SSH keys and return list of key IDs"""
        processed_ssh_keys = []
        for key_name in ssh_keys:
            if key_name in ssh_key_content:
                # Upload the key to DigitalOcean and get the key object
                uploaded_key_id = self.ensure_ssh_key_uploaded(
                    key_name, ssh_key_content[key_name]
                )
                processed_ssh_keys.append(
                    int(uploaded_key_id)
                )  # DigitalOcean expects integer IDs
            else:
                # Use existing key name or ID
                processed_ssh_keys.append(key_name)
        return processed_ssh_keys
