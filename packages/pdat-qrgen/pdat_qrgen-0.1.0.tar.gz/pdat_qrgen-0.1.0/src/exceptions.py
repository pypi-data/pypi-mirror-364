class QRGenException(Exception):
    """Base exception for all QRGen errors."""

    pass


class InvalidInputError(QRGenException):
    """Raised when input validation fails."""

    pass


class LogoNotFoundError(QRGenException, FileNotFoundError):
    """Raised when logo file is not found."""

    pass
