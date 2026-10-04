
from algorithms import linear_ops
from algorithms.step_log import StepLog
from config import MAX_NODES
from errors import SizeLimitError
from models.queue import Queue
from services.common import build_response, parse_int_value


def _load(payload):
    return Queue.from_dict(payload.get("queue"))


def enqueue(payload):
    queue = _load(payload)
    value = parse_int_value(payload.get("value"))
    if queue.size() >= MAX_NODES:
        raise SizeLimitError(
            "The queue is too large to visualise clearly (limit: %d items); further enqueues are blocked" % MAX_NODES)
    log = StepLog("queue")
    linear_ops.queue_enqueue(queue, value, log)
    return build_response(log, queue.to_dict(), "queue.enqueue")


def dequeue(payload):
    queue = _load(payload)
    log = StepLog("queue")
    linear_ops.queue_dequeue(queue, log)
    return build_response(log, queue.to_dict(), "queue.dequeue")


def front(payload):
    queue = _load(payload)
    log = StepLog("queue")
    linear_ops.queue_front(queue, log)
    return build_response(log, queue.to_dict(), "queue.front")


def rear(payload):
    queue = _load(payload)
    log = StepLog("queue")
    linear_ops.queue_rear(queue, log)
    return build_response(log, queue.to_dict(), "queue.rear")


def is_empty(payload):
    queue = _load(payload)
    log = StepLog("queue")
    linear_ops.queue_is_empty(queue, log)
    return build_response(log, queue.to_dict(), "queue.is_empty")
