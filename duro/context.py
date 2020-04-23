from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from queue import Queue
from threading import Thread
from typing import cast, Optional
import sys

import duro


# context
#########

# intentionally mutable context
@dataclass
class Context:
    thread: Thread
    message_q: duro.MessageQ
    path: duro.Path = tuple()


def setup(renderer: duro.Renderer) -> Context:
    message_q = cast(duro.MessageQ, Queue())

    def render_loop():
        return duro.render.loop(renderer, message_q, now=datetime.now)

    thread = Thread(target=render_loop)
    thread.start()
    return Context(thread, message_q)


def teardown(c: Context):
    c.message_q.put(duro.message.STOP)
    c.thread.join()
    c.message_q.join()


# intentially global context
context: Optional[Context] = None

# context managers
##################

# TODO(pcattori): yield a printer that clear_eos before printing text
@contextmanager
def task(task_description: str):
    if not sys.stdout.isatty():
        yield
        return

    if context is None:
        with _context():
            with _task(task_description):
                yield
    else:
        with _task(task_description):
            yield


@contextmanager
def _context():
    global context
    context = setup(duro.options.renderer)
    try:
        yield
    finally:
        teardown(context)
        context = None


@contextmanager
def _task(task_description: str):
    assert context is not None
    t = duro._task.InProgress(task_description, begin=datetime.now())

    response_q: duro.PathQ = cast(duro.PathQ, Queue())
    context.message_q.put(duro.message.NewTask(context.path, t, response_q))
    context.path = response_q.get()

    try:
        yield
    except Exception as e:
        context.message_q.put(
            duro.message.Fail(context.path, time=datetime.now(), error=e)
        )
        raise e
    else:
        context.message_q.put(duro.message.Success(context.path, time=datetime.now()))
    finally:
        context.path = context.path[:-1]
