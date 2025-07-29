from dataclasses import dataclass
from typing import List
from rubpy.bot.models import Button


@dataclass
class KeypadRow:
    buttons: List[Button]