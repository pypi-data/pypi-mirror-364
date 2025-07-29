# Filters
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