""" Convenience queues """
from queue import Empty, Full, Queue
from typing import Generic, Optional, TypeVar


# Any type variable for following generics
T = TypeVar('T')    # pylint: disable=C0103


class SafeQueue(Generic[T]):
    """ Thread-safe queue simplified and generic """
    def __init__(self, maxsize: int = 256):
        self._queue = Queue(maxsize)

    def get(self, timeout: Optional[float] = None) -> Optional[T]:
        """ Extracts an item from queue if not empty """
        try:
            return self._queue.get_nowait() if timeout is None else self._queue.get(timeout=timeout)
        except Empty:
            return None

    def put(self, item: T) -> bool:
        """ Puts an item into queue, return True on success or False on already full """
        try:
            self._queue.put_nowait(item)
            return True
        except Full:
            return False
