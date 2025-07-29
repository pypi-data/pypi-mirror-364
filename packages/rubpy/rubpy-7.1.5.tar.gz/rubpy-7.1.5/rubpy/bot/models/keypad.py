from dataclasses import dataclass
from typing import List
from rubpy.bot.models import KeypadRow


@dataclass
class Keypad:
    rows: List[KeypadRow]
    resize_keyboard: bool = True
    on_time_keyboard: bool = False
