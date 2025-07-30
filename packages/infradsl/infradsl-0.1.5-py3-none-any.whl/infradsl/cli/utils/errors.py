"""
CLI error handling
"""


class InfraDSLCLIError(Exception):
    """Base exception for CLI errors"""
    pass


class CommandError(InfraDSLCLIError):
    """Error executing a command"""
    pass


class ConfigurationError(InfraDSLCLIError):
    """Configuration error"""
    pass


class ProviderError(InfraDSLCLIError):
    """Provider-related error"""
    pass


class ResourceError(InfraDSLCLIError):
    """Resource-related error"""
    pass


class ValidationError(InfraDSLCLIError):
    """Validation error"""
    pass