"""
Firebase services for authentication, database, and serverless functions
"""

from .firebase_auth import FirebaseAuth
from .firebase_hosting import FirebaseHosting

__all__ = ["FirebaseAuth", "FirebaseHosting"]