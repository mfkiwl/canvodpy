"""RINEX reader exceptions."""


class RinexError(Exception):
    """Base exception for RINEX reader errors."""


class AttributeOverrideError(RinexError):
    """Raised when attempting to override an attribute after initialization."""

    def __init__(self, attribute: str) -> None:
        super().__init__(
            f"Overriding attribute '{attribute}' is not allowed after initialization."
        )


class MissingEpochError(RinexError):
    """Raised when missing epochs are detected in RINEX data."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CorruptedFileError(RinexError):
    """Raised when a corrupted RINEX file is detected."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class IncompleteEpochError(RinexError):
    """Raised when an incomplete epoch is detected."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidEpochError(RinexError):
    """Raised when an invalid epoch is detected."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class FileNotExistError(RinexError):
    """Raised when a RINEX file does not exist."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
