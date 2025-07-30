import threading as threading
from queue import Queue


def thread(function, args=(), kwargs={}):
    t = threading.Thread(target=function, args=args, kwargs=kwargs)
    return t


def run_new_thread(function, *args, **kwargs):
    t = thread(function, args, kwargs)
    t.start()
    return t


def run_new_daemon_thread(function, *args, **kwargs):
    t = thread(function, args, kwargs)
    t.daemon = True
    t.start()
    return t


def exit_thread(thread: threading.Thread):
    """
    This function is not safe. You should use thread.join() instead.
    """
    thread._tstate_lock.release()


def run_with_timeout(func, timeout, *args, **kwargs):
    queue = Queue()

    def target():
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            res = e

        queue.put(res)

    thread = run_new_thread(target)
    try:
        thread.join(timeout)
    except RuntimeError as e:
        raise e

    result = queue.get()

    if isinstance(result, Exception):
        raise result
    return result


def run_in_thread(func, *args, **kwargs):
    queue = Queue()

    def target():
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            res = e

        queue.put(res)

    return queue, run_new_thread(target)


def run_in_thread_with_timeout(func, timeout, *args, **kwargs):
    def target():
        return run_with_timeout(func, timeout, *args, **kwargs)

    return run_in_thread(target)


def get_tid():
    return threading.get_ident()
