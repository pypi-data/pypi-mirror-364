from dataclasses import dataclass
from typing import Optional

from typing import Dict
from rubpy.bot.enums import ButtonTypeEnum


@dataclass
class Button:
    id: str
    type: ButtonTypeEnum
    button_text: str
    button_selection: Optional[Dict] = None
    button_calendar: Optional[Dict] = None
    button_number_picker: Optional[Dict] = None
    button_string_picker: Optional[Dict] = None
    button_location: Optional[Dict] = None
    button_textbox: Optional[Dict] = None