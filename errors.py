"""Exceptions raised by the data-model, algorithm and service layers.

Every exception derives from VisualizerError, so the Flask layer can turn any of
them into a clean ``{"error": "..."}`` response without crashing the app.
"""


class VisualizerError(Exception):
    """Base class for all expected, user-facing errors."""


class EmptyStructureError(VisualizerError):
    """ER1: operation attempted on an empty structure (pop, dequeue, peek ...)."""


class InvalidInputError(VisualizerError):
    """ER2/ER4: bad value, bad vertex, bad algorithm start, malformed state."""


class DuplicateValueError(InvalidInputError):
    """ER2: duplicate BST key, duplicate vertex or duplicate edge."""


class NotFoundError(InvalidInputError):
    """ER2: value / vertex / edge does not exist in the structure."""


class SizeLimitError(VisualizerError):
    """ER3: structure would exceed the readable size limit."""
