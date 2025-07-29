# Filters
import re
from typing import List, Union

from rubpy.bot.models import Update
from rubpy.bot.models import InlineMessage


class Filter:
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        return True

class TextFilter(Filter):
    def __init__(self, text: str, regex: bool = False):
        self.text = text
        self.regex = regex

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        import re
        text = update.new_message.text if isinstance(update, Update) and update.new_message else update.text if isinstance(update, InlineMessage) else ""
        if not text:
            return False
        return bool(re.match(self.text, text)) if self.regex else text == self.text

class CommandFilter(Filter):
    def __init__(self, command: Union[str, List[str]]):
        self.commands = [command] if isinstance(command, str) else command

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        text = update.new_message.text if isinstance(update, Update) and update.new_message else update.text if isinstance(update, InlineMessage) else ""
        if not text:
            return False
        return any(text.startswith(f"/{cmd}") for cmd in self.commands)

class ButtonFilter(Filter):
    def __init__(self, button_id: str):
        self.button_id = button_id

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        aux_data = None
        update_type = "InlineMessage" if isinstance(update, InlineMessage) else update.type
        if isinstance(update, Update) and (update.new_message or update.updated_message):
            message = update.new_message or update.updated_message
            aux_data = message.aux_data
        elif isinstance(update, InlineMessage):
            aux_data = update.aux_data

        if not aux_data:
            #logger.info(f"No aux_data for button_id={self.button_id} in {update_type}")
            return False

        button_id = aux_data.get("button_id") or aux_data.get("callback_data") or ""
        result = button_id == self.button_id
        #logger.info(f"ButtonFilter check for button_id={self.button_id} in {update_type}: {result}, aux_data={aux_data}")
        return result

class UpdateTypeFilter(Filter):
    def __init__(self, update_types: Union[str, List[str]]):
        self.update_types = [update_types] if isinstance(update_types, str) else update_types

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        result = (isinstance(update, Update) and update.type in self.update_types) or \
                 (isinstance(update, InlineMessage) and "InlineMessage" in self.update_types)
        #logger.info(f"UpdateTypeFilter check for types={self.update_types}, update={type(update).__name__}: {result}")
        return result

class ButtonRegexFilter(Filter):
    """Filter for button interactions using regex pattern."""
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        aux_data = None
        if isinstance(update, Update):
            message = update.new_message or update.updated_message
            if message:
                aux_data = message.aux_data
        elif isinstance(update, InlineMessage):
            aux_data = update.aux_data
        if aux_data:
            button_id = aux_data.get("button_id") or aux_data.get("callback_data")
            if not button_id:
                for key in aux_data:
                    if isinstance(aux_data[key], dict) and ("button_id" in aux_data[key] or "callback_data" in aux_data[key]):
                        button_id = aux_data[key].get("button_id") or aux_data[key].get("callback_data")
                        break
            if button_id:
                return bool(self.pattern.match(button_id))
        return False

class PV(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        sender_type = update.new_message.sender_type if isinstance(update, Update) and update.new_message else update.updated_message.sender_type if update.updated_message else ""
        if not sender_type:
            return False
        return sender_type == 'User'

class Group(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        sender_type = update.new_message.sender_type if isinstance(update, Update) and update.new_message else update.updated_message.sender_type if update.updated_message else ""
        if not sender_type:
            return False
        return sender_type == 'Group'

class Bot(Filter):
    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        sender_type = update.new_message.sender_type if isinstance(update, Update) and update.new_message else update.updated_message.sender_type if update.updated_message else ""
        if not sender_type:
            return False
        return sender_type == 'Bot'

class Chat(Filter):
    def __init__(self, chat_id: Union[list, str]):
        self.chats = [chat_id] if isinstance(chat_id, str) else chat_id

    async def check(self, update: Union[Update, InlineMessage]) -> bool:
        return update.chat_id in self.chats