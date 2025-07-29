from dataclasses import dataclass
from typing import Optional

from rubpy.bot.enums.chat_type import ChatTypeEnum


@dataclass
class Chat:
    chat_id: str
    chat_type: ChatTypeEnum
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None
