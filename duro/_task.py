from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Union


@dataclass(frozen=True)
class InProgress:
    description: str
    begin: datetime


@dataclass(frozen=True)
class Success:
    description: str
    begin: datetime
    end: datetime


@dataclass(frozen=True)
class Fail:
    description: str
    begin: datetime
    end: datetime
    error: Exception  # TODO(pcattori): optional?


Task = Union[InProgress, Success, Fail]


def duration(t: Task, *, now: datetime) -> timedelta:
    if isinstance(t, InProgress):
        return now - t.begin
    elif isinstance(t, (Success, Fail)):
        return t.end - t.begin
    else:
        raise TypeError(t)


def to_success(t: InProgress, *, end: datetime) -> Success:
    return Success(t.description, begin=t.begin, end=end)


def to_fail(t: InProgress, *, end: datetime, error: Exception) -> Fail:
    return Fail(t.description, begin=t.begin, end=end, error=error)
