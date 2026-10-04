"""Min-heap priority queue model, stored as a plain list.

The children of index i are 2i+1 and 2i+2. 

JSON form:  {"array": [3, 7, 5]}
"""
from config import MAX_NODES
from errors import EmptyStructureError, InvalidInputError, SizeLimitError


class PriorityQueue:
    def __init__(self, array=None):
        self.array = list(array) if array else []

    @staticmethod
    def parent(i):
        return (i - 1) // 2

    @staticmethod
    def children(i):
        return 2 * i + 1, 2 * i + 2

    @classmethod
    def from_dict(cls, data):
        if data is None:
            return cls()
        if not isinstance(data, dict) or not isinstance(data.get("array", []), list):
            raise InvalidInputError("Malformed heap state")
        arr = data.get("array", [])
        for x in arr:
            if isinstance(x, bool) or not isinstance(x, int):
                raise InvalidInputError("Malformed heap state: values must be integers")
        if len(arr) > MAX_NODES:
            raise SizeLimitError(
                "The heap is too large to visualise clearly (limit: %d nodes)" % MAX_NODES
            )
        pq = cls(arr)
        if not pq.is_valid_heap():
            raise InvalidInputError("Malformed heap state: heap order is violated")
        return pq

    def to_dict(self):
        return {"array": list(self.array)}

    def is_empty(self):
        return not self.array

    def size(self):
        return len(self.array)

    def peek(self):
        if not self.array:
            raise EmptyStructureError("Priority queue is empty")
        return self.array[0]

    def is_valid_heap(self):
        return all(self.array[self.parent(i)] <= self.array[i] for i in range(1, len(self.array)))
