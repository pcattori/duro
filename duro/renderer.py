from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from blessed import Terminal

import duro


class Render(Protocol):
    def __call__(
        self, tt: duro.TaskTree, *, spinner_frame: duro.spinner.Frame, now: datetime
    ):
        ...


@dataclass(frozen=True)
class Renderer:
    render: Render
    render_stop: Render


# tty
#####


def _tty_compose(content: str) -> str:
    comp = ""

    term = Terminal()
    comp += term.clear_eos
    _, col = term.get_location()
    if col != 0:
        comp += "\n"
    comp += content
    height = len(content.split("\n"))
    comp += term.move_up * height
    if col != 0:
        comp += term.move_up + term.move_x(col)

    return comp


def _tty_render_cursor_before(tt: duro.TaskTree, *, spinner_frame: str, now: datetime):
    drawn = duro.draw.tasktree(tt, spinner=spinner_frame, now=now)
    print(_tty_compose(drawn))


def _tty_render_cursor_after(tt: duro.TaskTree, *, spinner_frame: str, now: datetime):
    drawn = duro.draw.tasktree(tt, spinner=spinner_frame, now=now)
    print(drawn)


def _tty_render_clear(tt: duro.TaskTree, *, spinner_frame: str, now: datetime):
    term = Terminal()
    print(term.clear_eos, end="")


def tty(clear=False) -> Renderer:
    render_stop = _tty_render_clear if clear else _tty_render_cursor_after
    return Renderer(render=_tty_render_cursor_before, render_stop=render_stop)
