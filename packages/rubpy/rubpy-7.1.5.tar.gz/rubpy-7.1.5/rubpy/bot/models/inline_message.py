from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class InlineMessage:
    sender_id: str
    text: str
    message_id: str
    chat_id: str
    file: Optional[Dict] = None
    location: Optional[Dict] = None
    aux_data: Optional[Dict] = None