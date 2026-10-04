


# ------------------------------------------------------------------ stack
def stack_push(stack, value, log):
    stack.push(value)
    log.add("push", "Push %d onto the top of the stack" % value,
            stack.to_dict(), line=0, current=[stack.size() - 1])
    log.result = {"pushed": value}
    return log


def stack_pop(stack, log):
    top = stack.peek()                       # raises EmptyStructureError first (ER1)
    log.add("visit", "The top element is %d: it will be removed" % top,
            stack.to_dict(), line=1, current=[stack.size() - 1])
    stack.pop()
    log.add("pop", "Pop %d from the stack" % top, stack.to_dict(), line=1)
    log.result = {"popped": top}
    return log


def stack_peek(stack, log):
    top = stack.peek()
    log.add("visit", "Peek: the top element is %d (stack unchanged)" % top,
            stack.to_dict(), line=0, current=[stack.size() - 1])
    log.result = {"value": top}
    return log


def stack_is_empty(stack, log):
    empty = stack.is_empty()
    log.add("visit", "isEmpty() = %s" % ("True: the stack is empty" if empty else "False: the stack has %d item(s)" % stack.size()),
            stack.to_dict(), line=0)
    log.result = {"empty": empty}
    return log


# ------------------------------------------------------------------ queue
def queue_enqueue(queue, value, log):
    queue.enqueue(value)
    log.add("enqueue", "Enqueue %d at the rear of the queue" % value,
            queue.to_dict(), line=0, current=[queue.size() - 1])
    log.result = {"enqueued": value}
    return log


def queue_dequeue(queue, log):
    front = queue.front()                    # raises EmptyStructureError first (ER1)
    log.add("visit", "The front element is %d: it will be removed" % front,
            queue.to_dict(), line=1, current=[0])
    queue.dequeue()
    log.add("dequeue", "Dequeue %d from the front of the queue" % front, queue.to_dict(), line=1)
    log.result = {"dequeued": front}
    return log


def queue_front(queue, log):
    value = queue.front()
    log.add("visit", "Front: the first element is %d (queue unchanged)" % value,
            queue.to_dict(), line=0, current=[0])
    log.result = {"value": value}
    return log


def queue_rear(queue, log):
    value = queue.rear()
    log.add("visit", "Rear: the last element is %d (queue unchanged)" % value,
            queue.to_dict(), line=0, current=[queue.size() - 1])
    log.result = {"value": value}
    return log


def queue_is_empty(queue, log):
    empty = queue.is_empty()
    log.add("visit", "isEmpty() = %s" % ("True: the queue is empty" if empty else "False: the queue has %d item(s)" % queue.size()),
            queue.to_dict(), line=0)
    log.result = {"empty": empty}
    return log
