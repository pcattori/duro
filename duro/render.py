from datetime import datetime, timedelta
from itertools import cycle
from time import sleep
from typing import Protocol

import duro

dots: duro.spinner.Frames = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")


class Now(Protocol):
    def __call__(self) -> datetime:
        ...


def loop(
    renderer: duro.Renderer,
    message_q: duro.MessageQ,
    refresh_rate: timedelta = timedelta(seconds=0.06),
    spinner_frames: duro.spinner.Frames = dots,
    now: Now = datetime.now,
):
    spinner = cycle(spinner_frames)

    # wait for first task
    tt = _seed(message_q)
    _idle_rerender(
        renderer,
        tt,
        message_q=message_q,
        spinner=spinner,
        refresh_rate=refresh_rate,
        now=now,
    )

    while True:
        msg = message_q.get()

        # check if refresh should stop
        if isinstance(msg, duro.message.Stop):
            renderer.render_stop(tt, spinner_frame=next(spinner), now=now())
            message_q.task_done()
            return

        # modify task tree based on message
        tt = _branch(tt, msg)

        # check if there are newer messages
        if not message_q.empty():
            # skip rendering, process newer messages instead
            message_q.task_done()
            continue

        _idle_rerender(
            renderer,
            tt,
            message_q=message_q,
            spinner=spinner,
            refresh_rate=refresh_rate,
            now=now,
        )


def _seed(q: duro.MessageQ) -> duro.TaskTree:
    while True:
        msg = q.get()
        if isinstance(msg, duro.message.NewTask):
            assert len(msg.path) == 0
            msg.response_q.put(tuple())
            return duro.TaskTree(msg.task)
        else:
            # TODO(pcattori): log warning for ignored messages
            print("ignore non-seed")
            q.task_done()
            pass


def _branch(tt: duro.TaskTree, msg: duro.Message) -> duro.TaskTree:
    if isinstance(msg, duro.message.NewTask):
        tt, path = duro.tasktree.new_task_at(tt, msg.path, msg.task)
        msg.response_q.put(path)
        return tt
    elif isinstance(msg, duro.message.Success):
        return duro.tasktree.success_at(tt, msg.path, msg.time)
    elif isinstance(msg, duro.message.Fail):
        return duro.tasktree.fail_at(tt, msg.path, msg.time, msg.error)
    else:
        raise TypeError(msg)


def _idle_rerender(
    renderer: duro.Renderer,
    tt: duro.TaskTree,
    *,
    message_q: duro.MessageQ,
    spinner: duro.Spinner,
    refresh_rate: timedelta,
    now: Now,
):
    while message_q.empty():
        # no newer messages, keep refreshing current task tree
        renderer.render(tt, spinner_frame=next(spinner), now=now())

        if refresh_rate is None:
            # do not continue refreshing current task tree
            # instead, idly wait for next message
            break
        sleep(refresh_rate.total_seconds())
    message_q.task_done()
