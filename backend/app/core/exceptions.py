class ApplicationError(Exception):
    """Base exception raised for application-level errors."""


class ResourceNotFoundError(ApplicationError):
    """Raised when an expected resource does not exist."""


class DomainValidationError(ApplicationError):
    """Raised when domain validation fails."""


class ExternalServiceError(ApplicationError):
    """Raised when an external dependency call fails."""


class ServiceConfigurationError(ApplicationError):
    """Raised when a service provider is not configured correctly."""


class StartupConfigurationError(ServiceConfigurationError):
    """Raised when startup configuration is not deployable."""
