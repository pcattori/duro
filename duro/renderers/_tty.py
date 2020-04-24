from datetime import datetime
import sys

from blessed import Terminal

import duro


def compose(content: str) -> str:
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


def render(tt: duro.TaskTree, *, spinner_frame: str, now: datetime):
    if not sys.stdout.isatty():
        return

    drawn = duro.draw.tasktree(tt, spinner=spinner_frame, now=now)
    composed = compose(drawn)
    print(composed)


def _render_cursor_after(tt: duro.TaskTree, *, spinner_frame: str, now: datetime):
    drawn = duro.draw.tasktree(tt, spinner=spinner_frame, now=now)
    print(drawn)


def _render_clear(tt: duro.TaskTree, *, spinner_frame: str, now: datetime):
    term = Terminal()
    print(term.clear_eos, end="")


def write(*args, **kwargs):
    term = Terminal()
    first, *rest = args
    print(term.clear_eos + str(first), *rest, **kwargs)


def tty(clear=False) -> duro.Renderer:
    render_stop = _render_clear if clear else _render_cursor_after
    return duro.Renderer(render=render, render_stop=render_stop, write=write)
