
from algorithms import linear_ops
from algorithms.step_log import StepLog
from config import MAX_NODES
from errors import SizeLimitError
from models.stack import Stack
from services.common import build_response, parse_int_value


def _load(payload):
    return Stack.from_dict(payload.get("stack"))


def push(payload):
    stack = _load(payload)
    value = parse_int_value(payload.get("value"))
    if stack.size() >= MAX_NODES:
        raise SizeLimitError(
            "The stack is too large to visualise clearly (limit: %d items); further pushes are blocked" % MAX_NODES)
    log = StepLog("stack")
    linear_ops.stack_push(stack, value, log)
    return build_response(log, stack.to_dict(), "stack.push")


def pop(payload):
    stack = _load(payload)
    log = StepLog("stack")
    linear_ops.stack_pop(stack, log)
    return build_response(log, stack.to_dict(), "stack.pop")


def peek(payload):
    stack = _load(payload)
    log = StepLog("stack")
    linear_ops.stack_peek(stack, log)
    return build_response(log, stack.to_dict(), "stack.peek")


def is_empty(payload):
    stack = _load(payload)
    log = StepLog("stack")
    linear_ops.stack_is_empty(stack, log)
    return build_response(log, stack.to_dict(), "stack.is_empty")
