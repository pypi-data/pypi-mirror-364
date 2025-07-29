from dataclasses import dataclass
from typing import Optional
from .file import File

@dataclass
class Bot:
    bot_id: str
    bot_title: str
    description: str
    username: str
    start_message: str
    share_url: str
    avatar: Optional[File] = None
