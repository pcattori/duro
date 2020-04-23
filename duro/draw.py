from datetime import datetime, timedelta

import crayons

import duro


def tasktree(tt: duro.TaskTree, *, spinner: str, now: datetime, tab: int = 0) -> str:
    drawn = ""
    drawn += _task(tt.task, spinner=spinner, now=now, tab=tab)
    if len(tt.subtrees) == 0:
        return drawn

    drawn += "\n"
    drawn += "\n".join(
        tasktree(st, spinner=spinner, now=now, tab=tab + 1) for st in tt.subtrees
    )
    return drawn


def _task(t: duro.Task, *, spinner: str, now: datetime, tab: int) -> str:
    indent = " " * 4 * tab
    if isinstance(t, duro._task.InProgress):
        return (
            indent + f"{crayons.blue(spinner)} {t.description} {_duration(t, now=now)}"
        )
    elif isinstance(t, duro._task.Success):
        return indent + f"{crayons.green('✓')} {t.description} {_duration(t, now=now)}"
    elif isinstance(t, duro._task.Fail):
        return indent + f"{crayons.red('✗')} {t.description} {_duration(t, now=now)}"
    else:
        raise TypeError(t)


def _duration(t: duro.Task, *, now: datetime) -> str:
    if isinstance(t, duro._task.InProgress):
        fbegin = _datetime(t.begin)
        fduration = _timedelta(duro._task.duration(t, now=now))
        return f"[{fbegin}|{fduration}]"
    elif isinstance(t, (duro._task.Success, duro._task.Fail)):
        fbegin = _datetime(t.begin)
        fduration = _timedelta(duro._task.duration(t, now=now))
        fend = _datetime(t.end)
        return f"[{fbegin}|{fduration}|{fend}]"
    else:
        raise TypeError(t)


def _datetime(dt: datetime) -> str:
    return dt.strftime("%H:%M:%S")


def _timedelta(td: timedelta) -> str:
    s = int(td.seconds)
    d, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    if d > 0:
        return f"{d}d{h}h{m}m{s}s"
    elif h > 0:
        return f"{h}h{m}m{s}s"
    elif m > 0:
        return f"{m}m{s}s"
    else:
        return f"{s}s"
    return str(d)
