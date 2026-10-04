"""FIFO queue backed by collections.deque (front on the left).

JSON form:  {"items": [1, 2, 3]}   (first item is the front)
"""
from collections import deque

from config import MAX_NODES
from errors import EmptyStructureError, InvalidInputError, SizeLimitError


class Queue:
    def __init__(self, items=None):
        self.items = deque(items) if items else deque()

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return cls()
        if not isinstance(data, dict) or not isinstance(data.get("items", []), list):
            raise InvalidInputError("Malformed queue state")
        items = data.get("items", [])
        for x in items:
            if isinstance(x, bool) or not isinstance(x, int):
                raise InvalidInputError("Malformed queue state: values must be integers")
        if len(items) > MAX_NODES:
            raise SizeLimitError(
                "The queue is too large to visualise clearly (limit: %d items)" % MAX_NODES
            )
        return cls(items)

    def to_dict(self):
        return {"items": list(self.items)}

    def is_empty(self):
        return not self.items

    def size(self):
        return len(self.items)

    def enqueue(self, value):
        self.items.append(value)

    def dequeue(self):
        if not self.items:
            raise EmptyStructureError("Queue is empty")
        return self.items.popleft()

    def front(self):
        if not self.items:
            raise EmptyStructureError("Queue is empty")
        return self.items[0]

    def rear(self):
        if not self.items:
            raise EmptyStructureError("Queue is empty")
        return self.items[-1]
