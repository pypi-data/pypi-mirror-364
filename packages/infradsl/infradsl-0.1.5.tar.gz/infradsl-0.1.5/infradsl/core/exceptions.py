class NexusException(Exception):
    """Base exception for Nexus Engine errors"""
    pass


class ResourceException(NexusException):
    """Exception related to resource operations"""
    pass


class ProviderException(NexusException):
    """Exception related to provider operations"""
    pass


class ValidationException(NexusException):
    """Exception for validation errors"""
    pass


class DriftException(NexusException):
    """Exception related to drift detection/remediation"""
    pass


class StateException(NexusException):
    """Exception related to state management"""
    pass