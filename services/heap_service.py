
from algorithms import heap_ops
from algorithms.step_log import StepLog
from config import MAX_NODES
from errors import SizeLimitError
from models.priority_queue import PriorityQueue
from services.common import build_response, parse_int_value


def _load(payload):
    return PriorityQueue.from_dict(payload.get("heap"))


def insert(payload):
    pq = _load(payload)
    value = parse_int_value(payload.get("value"))
    if pq.size() >= MAX_NODES:
        raise SizeLimitError(
            "The heap is too large to visualise clearly (limit: %d nodes); further insertion is blocked" % MAX_NODES)
    log = StepLog("heap")
    heap_ops.insert(pq, value, log)
    return build_response(log, pq.to_dict(), "heap.insert")


def extract_min(payload):
    pq = _load(payload)
    log = StepLog("heap")
    heap_ops.extract_min(pq, log)
    return build_response(log, pq.to_dict(), "heap.extract_min")


def peek(payload):
    pq = _load(payload)
    smallest = pq.peek()               # raises EmptyStructureError (ER1)
    log = StepLog("heap")
    log.add("visit", "Peek: the minimum is %d (heap unchanged)" % smallest,
            pq.to_dict(), line=0, current=[0])
    log.result = {"value": smallest}
    return build_response(log, pq.to_dict(), "heap.peek")
