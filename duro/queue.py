from typing import Generic, TypeVar

T = TypeVar("T")


class Queue(Generic[T]):
    def get(self) -> T:
        ...

    def put(self, m: T) -> None:
        ...

    def empty(self) -> bool:
        ...

    def task_done(self) -> None:
        ...

    def join(self) -> None:
        ...
