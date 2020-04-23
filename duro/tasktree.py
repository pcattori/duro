from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Tuple
import dataclasses

import duro

Path = Tuple[int, ...]
PathQ = duro.Queue[Path]


@dataclass(frozen=True)
class TaskTree:
    task: duro.Task
    subtrees: Tuple[TaskTree, ...] = tuple()


def get_at(tt: TaskTree, path: Path) -> TaskTree:
    if len(path) == 0:
        return tt
    ix, rest = path[0], path[1:]
    return get_at(tt.subtrees[ix], rest)


def new_task_at(tt: TaskTree, path: Path, t: duro.Task) -> Tuple[TaskTree, Path]:
    def new_task(tt: TaskTree, t: duro.Task) -> TaskTree:
        return dataclasses.replace(tt, subtrees=tt.subtrees + (TaskTree(t),))

    tt = _replace_at(tt, path, lambda x: new_task(x, t))
    x = get_at(tt, path)
    ix = len(x.subtrees) - 1
    return tt, path + (ix,)


def success_at(tt: TaskTree, path: Path, end: datetime) -> TaskTree:
    def to_success(x: TaskTree) -> TaskTree:
        if isinstance(x.task, duro._task.InProgress):
            return dataclasses.replace(x, task=duro._task.to_success(x.task, end=end))
        elif isinstance(x.task, (duro._task.Success, duro._task.Fail)):
            raise TypeError(x.task)
        else:
            raise TypeError(x.task)

    return _replace_at(tt, path, to_success)


def fail_at(tt: TaskTree, path: Path, end: datetime, error: Exception) -> TaskTree:
    def to_fail(x: TaskTree) -> TaskTree:
        if isinstance(x.task, duro._task.InProgress):
            return dataclasses.replace(
                x, task=duro._task.to_fail(x.task, end=end, error=error)
            )
        elif isinstance(x.task, (duro._task.Success, duro._task.Fail)):
            raise TypeError(x.task)
        else:
            raise TypeError(x.task)

    return _replace_at(tt, path, to_fail)


def _replace_at(
    tt: TaskTree, path: Path, replace: Callable[[TaskTree], TaskTree]
) -> TaskTree:
    if len(path) == 0:
        return replace(tt)
    ix, rest = path[0], path[1:]
    sts = (
        *tt.subtrees[:ix],
        _replace_at(tt.subtrees[ix], rest, replace),
        *tt.subtrees[ix + 1 :],
    )
    return dataclasses.replace(tt, subtrees=sts)
