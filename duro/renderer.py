from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, IO, Protocol

import duro


class Render(Protocol):
    def __call__(
        self, tt: duro.TaskTree, *, spinner_frame: duro.spinner.Frame, now: datetime
    ):
        ...


class Write(Protocol):
    def __call__(
        self,
        *objects: List[Any],
        sep: str = " ",
        end: str = "\n",
        file: IO,
        flush: bool = False,
    ) -> None:
        ...


@dataclass(frozen=True)
class Renderer:
    render: Render
    render_stop: Render
    write: Write
