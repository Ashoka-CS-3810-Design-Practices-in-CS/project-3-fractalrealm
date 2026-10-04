
from errors import EmptyStructureError


def sift_up(pq, i, log):
    a = pq.array
    while i > 0:
        p = pq.parent(i)
        if a[i] < a[p]:
            log.add("compare", "Compare %d with its parent %d: smaller, so swap" % (a[i], a[p]),
                    pq.to_dict(), line=4, current=[i], compared=[p])
            a[i], a[p] = a[p], a[i]
            log.add("swap", "Swap index %d and index %d" % (i, p),
                    pq.to_dict(), line=4, current=[p], compared=[i])
            i = p
        else:
            log.add("compare", "Compare %d with its parent %d: not smaller, heap order holds" % (a[i], a[p]),
                    pq.to_dict(), line=5, current=[i], compared=[p])
            return
    log.add("visit", "Reached the root: heap order restored",
            pq.to_dict(), line=2, current=[0])


def sift_down(pq, i, log):
    a = pq.array
    n = len(a)
    while True:
        left, right = pq.children(i)
        if left >= n:
            log.add("visit", "Index %d has no children: heap order restored" % i,
                    pq.to_dict(), line=3, current=[i])
            return
        smallest = left
        if right < n and a[right] < a[left]:
            smallest = right
        if a[smallest] < a[i]:
            log.add("compare", "Smaller child is %d: it is smaller than %d, so swap" % (a[smallest], a[i]),
                    pq.to_dict(), line=5, current=[i], compared=[smallest])
            a[i], a[smallest] = a[smallest], a[i]
            log.add("swap", "Swap index %d and index %d" % (i, smallest),
                    pq.to_dict(), line=5, current=[smallest], compared=[i])
            i = smallest
        else:
            log.add("compare", "Smaller child is %d: not smaller than %d, heap order holds" % (a[smallest], a[i]),
                    pq.to_dict(), line=6, current=[i], compared=[smallest])
            return


def insert(pq, value, log):
    pq.array.append(value)
    i = len(pq.array) - 1
    log.add("insertNode", "Append %d at the end of the array (index %d)" % (value, i),
            pq.to_dict(), line=0, current=[i])
    sift_up(pq, i, log)
    log.result = {"inserted": value}
    return log


def extract_min(pq, log):
    if pq.is_empty():
        raise EmptyStructureError("Priority queue is empty")
    a = pq.array
    smallest = a[0]
    log.add("removeNode", "Extract the minimum: %d is at the root" % smallest,
            pq.to_dict(), line=0, current=[0])
    last = a.pop()
    if not a:
        log.add("removeNode", "That was the only element: the heap is now empty",
                pq.to_dict(), line=7)
    else:
        a[0] = last
        log.add("swap", "Move the last element %d to the root" % last,
                pq.to_dict(), line=1, current=[0])
        sift_down(pq, 0, log)
    log.result = {"min": smallest}
    return log
