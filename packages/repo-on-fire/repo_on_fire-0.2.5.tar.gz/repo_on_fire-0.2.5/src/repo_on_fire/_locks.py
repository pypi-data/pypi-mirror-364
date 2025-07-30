"""Locking and synchronization mechanisms."""

from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from threading import Semaphore, Thread

from flufl.lock import Lock


@contextmanager
def lock_path(path: Path):
    # Create the lock on the path. The lock will remain active
    # for 5s, afterwards it is automatically freed.
    lock_path = path.with_name(f"{path.name}-rof.lock")
    lock_folder = lock_path.parent
    lock_folder.mkdir(parents=True, exist_ok=True)
    lock = Lock(str(lock_path), lifetime=timedelta(seconds=5))

    # Lock the path.
    lock.lock()

    try:
        # Set up a semaphore. This is needed to communicate with the thread and
        # let it terminate once we are done:
        semaphore = Semaphore()
        semaphore.acquire()

        # Start a background thread, running the lock refresher with the lock
        # and semaphore
        thread = Thread(target=_refresh_lock, args=[lock, semaphore])
        thread.start()

        # Yield control to the caller:
        yield
    finally:
        # Release the semaphore - this ensures the background thread terminates:
        semaphore.release()
        thread.join()

        # Finally, unlock:
        lock.unlock()


def _refresh_lock(lock: Lock, semaphore: Semaphore):
    """Keep a lock alive.

    This function is run once by the background thread started in lock_path().
    It basically runs a loop as long as the semaphore is locked. In that loop,
    we refresh the lock again for at most 5s.

    Args:
        lock: The lock to keep locked.
        semaphore: A semaphore that - as long as it is blocked - keeps the loop
                   running.
    """
    while not semaphore.acquire(timeout=1):
        lock.refresh(lifetime=timedelta(seconds=5))

    # Also release this instance of the semaphore - that way, the counter is
    # finally at zero.
    semaphore.release()
