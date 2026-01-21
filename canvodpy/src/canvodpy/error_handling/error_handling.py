class AttributeOverrideError(Exception):
    """Custom exception raised when attempting to override an attribute."""

    def __init__(self, attribute):
        super().__init__(
            f"Overriding attribute '{attribute}' is not allowed after initialization."
        )


class MissingEpochError(Exception):
    """Custom exception raised when missing epochs are detected."""

    def __init__(self, message):
        super().__init__(message)


class CorruptedFileError(Exception):
    """Custom exception raised when a corrupted file is detected."""

    def __init__(self, message):
        super().__init__(message)


class IncompleteEpochError(Exception):
    """Custom exception raised when an invalid epoch is detected."""

    def __init__(self, message):
        super().__init__(message)


class InvalidEpochError(Exception):
    """Custom exception raised when an invalid epoch is detected."""

    def __init__(self, message):
        super().__init__(message)


class FileNotExistError(Exception):
    """Custom exception raised when an invalid file is detected."""

    def __init__(self, message):
        super().__init__(message)
