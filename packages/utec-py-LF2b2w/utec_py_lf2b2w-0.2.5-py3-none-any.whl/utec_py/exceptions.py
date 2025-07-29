"""U-Home API exceptions."""


class UHomeError(Exception):
    """Base exception for U-Home API."""

    pass


class AuthenticationError(UHomeError):
    """Authentication failed."""

    pass


class ApiError(UHomeError):
    """API call failed."""

    def __init__(self, status_code, message) -> None:
        super().__init__(f"API call failed: {status_code} - {message}")
        self.status_code = status_code
        self.message = message


class ValidationError(UHomeError):
    """Validation failed."""

    pass


class DeviceError(Exception):
    """Base exception for device-related errors."""

    pass


class UnsupportedFeatureError(DeviceError):
    """Exception raised when a feature is not supported by the device."""

    pass
