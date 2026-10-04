
import re

from algorithms.step_log import StepLog
from config import VALUE_MAX, VALUE_MIN
from errors import InvalidInputError
from services.complexity import get_complexity
from services.pseudocode import get_pseudocode


def parse_int_value(raw, name="value"):
    """Accept an int or a numeric string; reject everything else (ER2)."""
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        raise InvalidInputError("Please enter a %s" % name)
    if isinstance(raw, bool):
        raise InvalidInputError("The %s must be a whole number" % name)
    if isinstance(raw, int):
        value = raw
    elif isinstance(raw, float) and raw.is_integer():
        value = int(raw)
    elif isinstance(raw, str) and re.fullmatch(r"[+-]?\d+", raw.strip()):
        value = int(raw.strip())
    else:
        raise InvalidInputError("'%s' is not a whole number" % (raw,))
    if not VALUE_MIN <= value <= VALUE_MAX:
        raise InvalidInputError("Values must be between %d and %d" % (VALUE_MIN, VALUE_MAX))
    return value


def build_response(log, final_state, key):
    """Standard response for one operation (A2, section 5.5)."""
    return {
        "operation": key,
        "steps": log.steps,
        "finalState": final_state,
        "complexity": get_complexity(key),
        "pseudocode": get_pseudocode(key),
        "result": log.result,
    }


def single_step_response(structure_type, action, description, state, key,
                         current=None, result=None, line=0):
    """For operations that are a single step (graph edits, generation)."""
    log = StepLog(structure_type)
    log.add(action, description, state, line=line, current=current)
    log.result = result or {}
    return build_response(log, state, key)
