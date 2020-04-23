from typing import Tuple

class Terminal:
    clear_eos: str
    move_up: str
    def get_location(self) -> Tuple[int, int]: ...
    def move_x(self, x: int) -> str: ...
