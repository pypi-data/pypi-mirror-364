from dataclasses import dataclass
from typing import Dict, Optional

import rubpy


@dataclass
class MessageId:
    message_id: Optional[str] = None
    new_message_id: Optional[str] = None
    file_id: Optional[str] = None
    chat_id: Optional[str] = None
    client: Optional["rubpy.BotClient"] = None

    async def delete(self):
        return await self.client.delete_message(self.chat_id, self.message_id or self.new_message_id)

    async def edit_text(self, new_text: str):
        return await self.client.edit_message_text(self.chat_id, self.message_id or self.new_message_id, new_text)


@dataclass
class Message:
    message_id: MessageId
    text: str
    time: str
    is_edited: bool
    sender_type: str
    sender_id: str
    aux_data: Optional[Dict] = None
    file: Optional[Dict] = None
    reply_to_message_id: Optional[str] = None
    forwarded_from: Optional[Dict] = None
    location: Optional[Dict] = None
    sticker: Optional[Dict] = None
    contact_message: Optional[Dict] = None
    poll: Optional[Dict] = None
    live_location: Optional[Dict] = None
