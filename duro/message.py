from dataclasses import dataclass
from datetime import datetime
from typing import cast, Union
from queue import Queue

import duro

PathQ = duro.Queue[duro.tasktree.Path]


@dataclass(frozen=True)
class NewTask:
    path: duro.tasktree.Path
    task: duro.Task
    response_q: PathQ = cast(PathQ, Queue())


@dataclass(frozen=True)
class Success:
    path: duro.tasktree.Path
    time: datetime


@dataclass(frozen=True)
class Fail:
    path: duro.tasktree.Path
    time: datetime
    error: Exception


@dataclass(frozen=True)
class Stop:
    """Sentinel value to stop refreshing"""

    pass


Message = Union[NewTask, Success, Fail, Stop]
MessageQ = duro.Queue[Message]

STOP = Stop()
