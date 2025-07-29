from dataclasses import dataclass
from typing import Optional
import rubpy


@dataclass
class MessageId:
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    client: Optional["rubpy.BotClient"] = None

    async def delete(self):
        return await self.client.delete_message(self.chat_id, self.message_id)

    async def edit_text(self, new_text: str):
        return await self.client.edit_message_text(self.chat_id, self.message_id, new_text)