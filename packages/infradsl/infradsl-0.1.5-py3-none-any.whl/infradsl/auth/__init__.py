"""
InfraDSL Authentication Module

Provides authentication services for the InfraDSL platform including
Firebase Auth integration and JWT token management.
"""

from .firebase_auth import FirebaseAuth, setup_firebase_auth_interactive

__all__ = [
    "FirebaseAuth",
    "setup_firebase_auth_interactive"
]