import asyncio
import dataclasses
from pathlib import Path
import aiohttp
from aiohttp import web
import json
import logging
import os
import time
import uuid
from collections import deque
from typing import Any, Callable, Dict, List, Literal, Optional, Union, Tuple

from rubpy.bot.enums import ChatKeypadTypeEnum, UpdateTypeEnum
from rubpy.bot.filters import Filter
from rubpy.bot.models import Keypad, Button, InlineMessage, Update, Message
from rubpy.bot.models.bot import Bot
from rubpy.bot.models.chat import Chat
from rubpy.bot.models.message import MessageId

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, rate: float):
        self.rate = rate
        self._last = 0.0

    async def __aenter__(self):
        elapsed = time.time() - self._last
        if elapsed < self.rate:
            await asyncio.sleep(self.rate - elapsed)
        self._last = time.time()

    async def __aexit__(self, exc_type, exc, tb):
        pass


class BotClient:
    BASE_URL = 'https://botapi.rubika.ir/v3/'

    def __init__(
        self,
        token: str,
        state_file: str = "bot_state.json",
        rate_limit: float = 0.5,
        use_webhook: bool = False
    ):
        self.token = token
        self.base_url = f"{self.BASE_URL}{token}/"
        self.handlers: Dict[str, List[Tuple[Tuple[Filter, ...], Callable]]] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self.next_offset_id: Optional[str] = None
        self.processed_messages: deque = deque(maxlen=10000)
        self.state_file = state_file
        self.rate_limiter = RateLimiter(rate_limit)
        self.use_webhook = use_webhook

        if not use_webhook and os.path.exists(state_file):
            self._load_state()
        logger.info("Rubika client initialized, use_webhook=%s", use_webhook)

    def _load_state(self) -> None:
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                self.next_offset_id = data.get('next_offset_id')
                self.processed_messages.extend(data.get('processed_messages', []))
            logger.info("Loaded state: %s", self.next_offset_id)
        except Exception as e:
            logger.error("Failed to load state: %s", e)

    def _save_state(self) -> None:
        if self.use_webhook:
            return
        try:
            with open(self.state_file, 'w') as f:
                json.dump({
                    'next_offset_id': self.next_offset_id,
                    'processed_messages': list(self.processed_messages)
                }, f)
            logger.debug("State saved")
        except Exception as e:
            logger.error("Failed saving state: %s", e)

    async def _request(self, method: str, payload: Dict[str, Any]) -> Any:
        async with self.rate_limiter:
            if self.session is None:
                self.session = aiohttp.ClientSession()
            url = self.base_url + method
            async with self.session.post(url, json=payload) as resp:
                text = await resp.text()
                if resp.status != 200:
                    logger.error("%s failed: %s", method, text)
                    raise aiohttp.ClientResponseError(
                        resp.request_info, resp.history, status=resp.status, message=text
                    )
                result = await resp.json()
        if result.get('status') != 'OK':
            msg = result.get('message', '')
            logger.error("API %s error: %s", method, msg)
            raise RuntimeError(f"API {method} error: {msg}")
        return result.get('data')

    async def get_me(self) -> Dict[str, Any]:
        result = await self._request('getMe', {})
        return Bot(**result['bot'])

    async def _post_and_track(
        self,
        method: str,
        payload: Dict[str, Any],
        track_id: str = 'message_id'
    ) -> Any:
        data = await self._request(method, payload)
        mid = data.get(track_id) or data.get('new_message_id')
        if mid:
            self.processed_messages.append(str(mid))
            self._save_state()
        return data

    async def send_message(
        self,
        chat_id: str,
        text: str,
        chat_keypad: Optional[Keypad] = None,
        inline_keypad: Optional[Keypad] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: ChatKeypadTypeEnum = ChatKeypadTypeEnum.NONE
    ) -> MessageId:
        payload = {
            'chat_id': chat_id,
            'text': text,
            'disable_notification': disable_notification,
            'chat_keypad_type': chat_keypad_type.value,
        }
        if chat_keypad:
            payload['chat_keypad'] = dataclasses.asdict(chat_keypad)
        if inline_keypad:
            payload['inline_keypad'] = dataclasses.asdict(inline_keypad)
        if reply_to_message_id:
            payload['reply_to_message_id'] = str(reply_to_message_id)

        result = await self._post_and_track('sendMessage', payload)
        result['chat_id'] = chat_id
        result['client'] = self
        return MessageId(**result)
    
    async def send_sticker(
        self,
        chat_id: str,
        sticker_id: str,
        chat_keypad: Optional[Keypad] = None,
        inline_keypad: Optional[Keypad] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: ChatKeypadTypeEnum = ChatKeypadTypeEnum.NONE
    ) -> MessageId:
        payload = {
            'chat_id': chat_id,
            'sticker_id': sticker_id,
            'disable_notification': disable_notification,
            'chat_keypad_type': chat_keypad_type.value,
        }
        if chat_keypad:
            payload['chat_keypad'] = dataclasses.asdict(chat_keypad)
        if inline_keypad:
            payload['inline_keypad'] = dataclasses.asdict(inline_keypad)
        if reply_to_message_id:
            payload['reply_to_message_id'] = str(reply_to_message_id)

        result = await self._post_and_track('sendSticker', payload)
        result['chat_id'] = chat_id
        result['client'] = self
        return MessageId(**result)
    
    async def send_file(
        self,
        chat_id: str,
        file: Optional[Union[str, Path]] = None,
        file_id: Optional[str] = None,
        text: Optional[str] = None,
        file_name: Optional[str] = None,
        type: Literal['File', 'Image', 'Voice', 'Music', 'Gif'] = 'File',
        chat_keypad: Optional[Keypad] = None,
        inline_keypad: Optional[Keypad] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: ChatKeypadTypeEnum = ChatKeypadTypeEnum.NONE
    ) -> MessageId:
        if file:
            file_name = file_name or Path(file).name
            upload_url = await self.request_send_file(type)
            file_id = await self.upload_file(upload_url, file_name, file)

        payload = {
            'chat_id': chat_id,
            'file_id': file_id,
            'text': text,
            'disable_notification': disable_notification,
            'chat_keypad_type': chat_keypad_type.value,
        }
        if chat_keypad:
            payload['chat_keypad'] = dataclasses.asdict(chat_keypad)
        if inline_keypad:
            payload['inline_keypad'] = dataclasses.asdict(inline_keypad)
        if reply_to_message_id:
            payload['reply_to_message_id'] = str(reply_to_message_id)

        result = await self._post_and_track('sendFile', payload)
        result['chat_id'] = chat_id
        result['client'] = self
        result['file_id'] = file_id
        return MessageId(**result)

    async def send_poll(self, chat_id: str, question: str, options: List[str]) -> MessageId:
        result = await self._post_and_track('sendPoll', {'chat_id': chat_id, 'question': question, 'options': options})
        result['chat_id'] = chat_id
        result['client'] = self
        return MessageId(**result)

    async def send_location(
        self,
        chat_id: str,
        latitude: Union[str, float],
        longitude: Union[str, float],
        **kwargs
    ) -> MessageId:
        payload = {'chat_id': chat_id, 'latitude': str(latitude), 'longitude': str(longitude)}
        payload.update(kwargs)
        result = await self._post_and_track('sendLocation', payload)
        result['chat_id'] = chat_id
        result['client'] = self
        return MessageId(**result)

    async def send_contact(
        self,
        chat_id: str,
        first_name: str,
        last_name: str,
        phone_number: str,
        **kwargs
    ) -> MessageId:
        payload = {
            'chat_id': chat_id,
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': phone_number
        }
        payload.update(kwargs)
        result = await self._post_and_track('sendContact', payload)
        result['chat_id'] = chat_id
        result['client'] = self
        return MessageId(**result)

    async def request_send_file(self, type: Literal['File', 'Image', 'Voice', 'Music', 'Gif']) -> str:
        if type not in ['File', 'Image', 'Voice', 'Music', 'Gif']:
            raise ValueError("type is just be in ['File', 'Image', 'Voice', 'Music', 'Gif']")

        result = await self._request('requestSendFile', {'type': type})
        return result['upload_url']
    
    async def upload_file(self, url: str, file_name: str, file_path: str) -> str:
        form = aiohttp.FormData()
        form.add_field(
            name='file',
            value=open(file_path, 'rb'),
            filename=file_name,
            content_type='application/octet-stream'  # یا نوع فایل واقعی مثل image/png
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form, ssl=False) as res:
                if res.status != 200:
                    text = await res.text()
                    raise aiohttp.ClientResponseError(
                        res.request_info, res.history, status=res.status, message=text
                    )

                data = await res.json()
                return data['data']['file_id']  # اطمینان حاصل کن که ساختار JSON این‌طوریه

    async def get_file(self, file_id: str) -> str:
        result = self._request('getFile', {'file_id': file_id})
        return result['download_url']

    async def get_chat(self, chat_id: str) -> Any:
        result = await self._request('getChat', {'chat_id': chat_id})
        return Chat(**result['chat'])

    async def get_updates(self, limit: int = 100) -> List[Union[Update, InlineMessage]]:
        payload = {'limit': limit}
        if self.next_offset_id:
            payload['offset_id'] = self.next_offset_id
        data = await self._request('getUpdates', payload)
        updates_raw = data.get('updates', [])
        updates = []
        for item in updates_raw:
            parsed = self._parse_update(item)
            if parsed:
                updates.append(parsed)
        self.next_offset_id = data.get('next_offset_id')
        self._save_state()
        return updates

    async def forward_message(
        self,
        from_chat_id: str,
        message_id: str,
        to_chat_id: str,
        disable_notification: bool = False
    ) -> Any:
        result = await self._post_and_track(
            'forwardMessage',
            {'from_chat_id': from_chat_id, 'message_id': str(message_id), 'to_chat_id': to_chat_id, 'disable_notification': disable_notification}
        )
        result['chat_id'] = to_chat_id
        result['client'] = self
        return MessageId(**result)

    async def edit_message_text(self, chat_id: str, message_id: str, text: str) -> Any:
        result = await self._request('editMessageText', {'chat_id': chat_id, 'message_id': str(message_id), 'text': text})
        if result == {}:
            return True
        return False

    async def edit_message_keypad(self, chat_id: str, message_id: str, inline_keypad: Keypad) -> Any:
        result = await self._request('editMessageKeypad', {'chat_id': chat_id, 'message_id': str(message_id), 'inline_keypad': dataclasses.asdict(inline_keypad)})
        if result == {}:
            return True
        return False

    async def delete_message(self, chat_id: str, message_id: str) -> Any:
        result = await self._request('deleteMessage', {'chat_id': chat_id, 'message_id': str(message_id)})
        if result == {}:
            return True
        return False

    async def set_commands(self, commands: List[Dict[str, str]]) -> Any:
        result = await self._request('setCommands', {'bot_commands': commands})
        if result == {}:
            return True
        return False

    async def update_bot_endpoints(self, url: str, endpoint_type: str) -> Any:
        return await self._request('updateBotEndpoints', {'url': url, 'type': endpoint_type})

    async def edit_chat_keypad(self, chat_id: str, keypad_type: ChatKeypadTypeEnum, keypad: Optional[Keypad] = None) -> Any:
        payload = {'chat_id': chat_id, 'chat_keypad_type': keypad_type.value}
        if keypad:
            payload['chat_keypad'] = dataclasses.asdict(keypad)
        result = await self._request('editChatKeypad', payload)
        if result == {}:
            return True
        return False

    def on_update(self, *filters: Filter) -> Callable:
        def decorator(fn: Callable) -> Callable:
            key = str(uuid.uuid4())
            self.handlers.setdefault(key, []).append((filters, fn))
            logger.info("Handler %s registered", fn.__name__)
            return fn
        return decorator

    def _parse_update(self, item: Dict[str, Any]) -> Optional[Union[Update, InlineMessage]]:
        ut = item.get('type')
        chat_id = item.get('chat_id', '')
        if ut == UpdateTypeEnum.REMOVED_MESSAGE:
            return Update(client=self, type=ut, chat_id=chat_id, removed_message_id=str(item.get('removed_message_id')))
        if ut in {UpdateTypeEnum.NEW_MESSAGE, UpdateTypeEnum.UPDATED_MESSAGE}:
            key = 'new_message' if ut == UpdateTypeEnum.NEW_MESSAGE else 'updated_message'
            data = item.get(key)
            if data:
                data['message_id'] = str(data.get('message_id'))
                msg = Message(**data)
                return Update(client=self, type=ut, chat_id=chat_id,
                              new_message=msg if ut == UpdateTypeEnum.NEW_MESSAGE else None,
                              updated_message=msg if ut == UpdateTypeEnum.UPDATED_MESSAGE else None)
        if 'inline_message' in item or ut == 'InlineMessage':
            src = item.get('inline_message', item)
            return InlineMessage(
                sender_id=src.get('sender_id', ''), text=src.get('text', ''),
                message_id=str(src.get('message_id', '')), chat_id=chat_id,
                file=src.get('file'), location=src.get('location'), aux_data=src.get('aux_data')
            )
        logger.debug("Unknown update type: %s", ut)
        return None

    async def process_update(self, update: Union[Update, InlineMessage]) -> None:
        mid = getattr(update, 'message_id', getattr(update, 'new_message', {}).get('message_id', None))
        if isinstance(update, Update) and mid in self.processed_messages:
            return
        if mid and isinstance(update, Update):
            self.processed_messages.append(mid)
            self._save_state()

        handled = False
        for handlers in self.handlers.values():
            for filters, fn in handlers:
                if all(await f.check(update) for f in filters):
                    await fn(self, update)
                    handled = True
        if not handled:
            logger.warning("No handler for update: %s", update)

    async def handle_webhook(self, request: web.Request) -> web.Response:
        if request.method != 'POST':
            return web.Response(status=405)
        data = await request.json()
        updates = []
        if 'inline_message' in data:
            updates.append(self._parse_update({'type': 'InlineMessage', **data['inline_message'], 'chat_id': data['inline_message'].get('chat_id')}))
        elif 'update' in data:
            upd = self._parse_update(data['update'])
            if upd:
                updates.append(upd)
        for u in updates:
            asyncio.create_task(self.process_update(u))
        return web.json_response({'status': 'OK'})

    async def run(self,
                  webhook_url: Optional[str] = None,
                  path: str = '/webhook',
                  host: str = '0.0.0.0',
                  port: int = 8080) -> None:
        await self.start()
        if webhook_url:
            app = web.Application()
            base = path.rstrip('/')
            app.router.add_post(base, self.handle_webhook)
            for t in ['ReceiveUpdate', 'ReceiveInlineMessage']:
                await self.update_bot_endpoints(f"{webhook_url.rstrip('/')}{base}", t)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()
            while True:
                await asyncio.sleep(3600)
        else:
            while True:
                updates = await self.get_updates()
                for u in updates:
                    asyncio.create_task(self.process_update(u))
                await asyncio.sleep(0.1)