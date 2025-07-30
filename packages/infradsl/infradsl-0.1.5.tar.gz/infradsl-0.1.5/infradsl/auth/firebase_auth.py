#!/usr/bin/env python3
"""
Firebase Authentication for InfraDSL Template Registry

Provides Firebase-based authentication for the template registry system.
Users can authenticate using Firebase Auth and get JWT tokens for API access.
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm

console = Console()

class FirebaseAuth:
    """Firebase Authentication client for InfraDSL registry"""
    
    def __init__(self, 
                 api_key: str = None,
                 project_id: str = None,
                 config_path: Path = None):
        """
        Initialize Firebase Auth client
        
        Args:
            api_key: Firebase Web API key
            project_id: Firebase project ID
            config_path: Path to Firebase config file
        """
        # Check environment variables first
        self.api_key = api_key or os.environ.get('FIREBASE_API_KEY')
        self.project_id = project_id or os.environ.get('FIREBASE_PROJECTID')
        self.config_path = config_path or Path.home() / ".infradsl" / "firebase_config.json"
        
        # Load config if not provided
        if not self.api_key or not self.project_id:
            self._load_config()
            
        # Firebase Auth REST API endpoints
        self.auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts"
        self.token_refresh_url = f"https://securetoken.googleapis.com/v1/token"
        
    def _load_config(self):
        """Load Firebase configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key')
                    self.project_id = config.get('project_id')
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load Firebase config: {e}")
                
    def _save_config(self, config: Dict[str, Any]):
        """Save Firebase configuration to file"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not save Firebase config: {e}")
            
    def setup_firebase_project(self, api_key: str, project_id: str) -> bool:
        """
        Set up Firebase project configuration
        
        Args:
            api_key: Firebase Web API key
            project_id: Firebase project ID
            
        Returns:
            True if setup successful
        """
        self.api_key = api_key
        self.project_id = project_id
        
        # Save configuration
        config = {
            'api_key': api_key,
            'project_id': project_id,
            'auth_domain': f"{project_id}.firebaseapp.com"
        }
        self._save_config(config)
        
        console.print(f"[green]✅ Firebase project configured: {project_id}")
        return True
        
    def sign_up_with_email(self, email: str, password: str, display_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Sign up new user with email and password
        
        Args:
            email: User email address
            password: User password
            display_name: Optional display name
            
        Returns:
            User data if successful, None if failed
        """
        if not self.api_key:
            console.print("[red]Firebase API key not configured. Run 'infra auth setup' first.")
            return None
            
        try:
            # Create user account
            url = f"{self.auth_url}:signUp"
            params = {"key": self.api_key}
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            if display_name:
                data["displayName"] = display_name
                
            response = requests.post(url, params=params, json=data)
            
            if response.status_code == 200:
                user_data = response.json()
                console.print(f"[green]✅ Successfully created account for {email}")
                return user_data
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                console.print(f"[red]❌ Sign up failed: {error_msg}")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Sign up error: {e}")
            return None
            
    def sign_in_with_email(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Sign in user with email and password
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            User data with tokens if successful, None if failed
        """
        if not self.api_key:
            console.print("[red]Firebase API key not configured. Run 'infra auth setup' first.")
            return None
            
        try:
            url = f"{self.auth_url}:signInWithPassword"
            params = {"key": self.api_key}
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, params=params, json=data)
            
            if response.status_code == 200:
                user_data = response.json()
                console.print(f"[green]✅ Successfully signed in as {email}")
                return user_data
            else:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Unknown error")
                
                # Provide user-friendly error messages
                if "EMAIL_NOT_FOUND" in error_msg:
                    console.print("[red]❌ No account found with this email address")
                elif "INVALID_PASSWORD" in error_msg:
                    console.print("[red]❌ Invalid password")
                elif "USER_DISABLED" in error_msg:
                    console.print("[red]❌ Account has been disabled")
                else:
                    console.print(f"[red]❌ Sign in failed: {error_msg}")
                    
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Sign in error: {e}")
            return None
            
    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh ID token using refresh token
        
        Args:
            refresh_token: Firebase refresh token
            
        Returns:
            New token data if successful, None if failed
        """
        try:
            params = {"key": self.api_key}
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }
            
            response = requests.post(self.token_refresh_url, params=params, json=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                console.print("[red]❌ Token refresh failed")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Token refresh error: {e}")
            return None
            
    def verify_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Firebase ID token and get user info
        
        Args:
            id_token: Firebase ID token
            
        Returns:
            User info if valid, None if invalid
        """
        try:
            url = f"{self.auth_url}:lookup"
            params = {"key": self.api_key}
            data = {"idToken": id_token}
            
            response = requests.post(url, params=params, json=data)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                if users:
                    return users[0]  # Return first (should be only) user
            return None
            
        except Exception as e:
            console.print(f"[red]❌ Token verification error: {e}")
            return None
            
    def get_workspace_from_email(self, email: str) -> str:
        """
        Generate workspace name from email address
        
        For example:
        - user@company.com -> company
        - user@gmail.com -> user (personal workspace)
        - user@university.edu -> university
        
        Args:
            email: User email address
            
        Returns:
            Workspace name
        """
        domain = email.split('@')[1].lower()
        
        # Personal email domains get username as workspace
        personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com']
        if domain in personal_domains:
            return email.split('@')[0].lower()
            
        # Corporate/organizational domains
        # Remove common TLD suffixes to get organization name
        workspace = domain.split('.')[0]
        
        # Handle common patterns
        if workspace in ['mail', 'email', 'webmail']:
            # For domains like mail.company.com
            parts = domain.split('.')
            if len(parts) > 2:
                workspace = parts[1]
                
        return workspace
        
    def create_custom_token(self, uid: str, workspace: str = None) -> Optional[str]:
        """
        Create custom token for API access (requires Firebase Admin SDK)
        
        Note: This would typically be done server-side with the Admin SDK.
        For now, we'll use the ID token directly.
        
        Args:
            uid: User ID
            workspace: User workspace
            
        Returns:
            Custom token or None
        """
        # This is a placeholder - in a real implementation,
        # custom tokens would be created server-side
        console.print("[yellow]Custom token creation requires server-side implementation")
        return None


def setup_firebase_auth_interactive() -> bool:
    """
    Interactive setup for Firebase authentication
    
    Returns:
        True if setup successful
    """
    console.print("[bold cyan]🔥 Firebase Authentication Setup[/bold cyan]")
    console.print("\nTo use Firebase authentication, you'll need:")
    console.print("1. A Firebase project")
    console.print("2. Firebase Web API key")
    console.print("3. Authentication enabled in Firebase Console")
    console.print("\nVisit: https://console.firebase.google.com/")
    
    if not Confirm.ask("\nDo you have a Firebase project ready?"):
        console.print("\n[yellow]Please create a Firebase project first:")
        console.print("1. Go to https://console.firebase.google.com/")
        console.print("2. Create a new project")
        console.print("3. Enable Authentication")
        console.print("4. Add Email/Password provider")
        console.print("5. Get your Web API key from Project Settings")
        return False
        
    # Get project details
    import click
    project_id = click.prompt("Firebase Project ID")
    api_key = click.prompt("Firebase Web API Key")
    
    if not project_id or not api_key:
        console.print("[red]❌ Project ID and API key are required")
        return False
        
    # Test the configuration
    auth = FirebaseAuth(api_key=api_key, project_id=project_id)
    
    # Save configuration
    success = auth.setup_firebase_project(api_key, project_id)
    
    if success:
        console.print("\n[green]🎉 Firebase authentication configured successfully!")
        console.print(f"Project: {project_id}")
        console.print("You can now use 'infra registry login' to authenticate.")
        
    return success


# Example usage and testing
if __name__ == "__main__":
    # Interactive setup
    setup_firebase_auth_interactive()