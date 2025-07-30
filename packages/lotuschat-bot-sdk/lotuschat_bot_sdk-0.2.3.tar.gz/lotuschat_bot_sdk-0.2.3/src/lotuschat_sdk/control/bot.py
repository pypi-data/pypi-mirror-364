import json
from concurrent.futures.thread import ThreadPoolExecutor

import aiohttp
from aiohttp import FormData
from asgiref.sync import async_to_sync
from flask import request as flask_request
from multidict import MultiDict
from quart import request as quart_request

from .const import Argument, TYPE_TEXT, TYPE_UNKNOWN, FAILED_REQUEST, TYPE_BOT_COMMAND, ErrorType, CODE_FAIL_BOT, \
    CODE_SUCCESS, CODE_FAIL_MESSAGE, CODE_FAIL_CALLBACK_QUERY
from ..model.message import Message, MessageEntity, Updates
from ..model.notify import NewChatMemberPayload, LeftChatMemberPayload, NotifyEvent
from ..model.query import CallbackQuery
from ..model.request import ParseModeType, BaseKeyboard, Command, ChatAction, PromotePermission, RestrictChatPermission, \
    ChatPermission
from ..utility.logger import log_info, log_debug, log_error, log_verbose, log_warning
from ..utility.utility import is_not_empty, extract_last_url, print_form_data, response_success, \
    response_error, error_message


class ChatBot:
    _command_listeners = {}

    def __init__(self, name, token, max_threads: int = 5, is_vpn=False, is_log_curl_command=False):
        self._name = name
        self._token = token
        self._executor = ThreadPoolExecutor(max_workers=max_threads)
        self._error_listener = None
        self._self_messages_listener = None
        self._messages_listener = None
        self._messages_no_command_listener = None
        self._commands_listener = None
        self._notify_listener = None
        self._on_query_callback = None
        self.is_log_curl_command = is_log_curl_command
        if is_vpn:
            # dev mode
            self._domain = "http://bot.kingtalk.vn/bot"
        else:
            self._domain = "http://bot.lotuschat.vn/bot"

    def __str__(self):
        return f"Chatbot name[{self._name}] - token[{self._token}] - url[{self._domain}]"

    def set_on_messages(self, callback, is_get_command=True):
        log_info(f"register get all message")
        if is_get_command:
            self._messages_listener = callback
        else:
            self._messages_no_command_listener = callback

    def set_on_notify(self, callback):
        self._notify_listener = callback

    def set_on_callback_query(self, callback):
        self._on_query_callback = callback

    def set_on_commands(self, callback):
        self._commands_listener = callback

    def set_on_command(self, command: str, callback):
        log_info(f"register command {command}")
        self._command_listeners[command] = callback

    def set_on_errors(self, callback):
        self._error_listener = callback

    def set_self_messages(self, callback):
        self._self_messages_listener = callback

    def web_hook_flask(self):
        try:
            json_data = flask_request.get_json()
            return async_to_sync(self._handle_message_hook)(json_data)
        except Exception as e:
            log_error(f"web_hook has error: {e}")
            if self._error_listener:
                async_to_sync(self._error_listener)(ErrorType.BOT, error_message("web_hook_flask", f"{e}"))
            return response_error(CODE_FAIL_BOT, f"{e}"), CODE_FAIL_BOT

    async def web_hook_quart(self):
        try:
            json_data = await quart_request.get_json()
            return await self._handle_message_hook(json_data)
        except Exception as e:
            log_error(f"web_hook has error: {e}")
            if self._error_listener:
                await self._error_listener(ErrorType.BOT, error_message("web_hook_quart", f"{e}"))
            return response_error(CODE_FAIL_BOT, f"{e}"), CODE_FAIL_BOT

    async def _handle_message_hook(self, json_data):
        try:
            updates = await self._get_updates(json_data=json_data)
            if updates is None:
                msg = f"no receive message or response not json"
                log_error(msg)
                if self._error_listener:
                    await self._error_listener(ErrorType.MESSAGE, error_message("_verify_message", msg))
                return response_error(CODE_FAIL_MESSAGE, msg), CODE_FAIL_MESSAGE
            else:
                if updates.callback_query:
                    is_query_valid = await self._verify_callback_query(updates.update_id, updates.callback_query)
                    if is_query_valid:
                        await self._send_callback_query_listener(updates.callback_query)
                        return response_success(CODE_SUCCESS), CODE_SUCCESS
                    else:
                        return response_error(CODE_FAIL_CALLBACK_QUERY, "callback query has error"), CODE_FAIL_CALLBACK_QUERY
                else:
                    message = await self._get_message(updates=updates)
                    is_valid_message = await self._verify_message(update_id=updates.update_id, message=message)
                    if is_valid_message:
                        if self._is_notify(message):
                            await self._send_notify_listener(message, updates)
                        else:
                            await self._send_message_listener(message, updates)
                        return response_success(CODE_SUCCESS), CODE_SUCCESS
                    else:
                        return response_error(CODE_FAIL_MESSAGE, "message has error"), CODE_FAIL_MESSAGE
        except Exception as e:
            log_error(f"handle message has error: {e}")
            if self._error_listener:
                await self._error_listener(ErrorType.BOT, error_message("_handle_message_hook", f"{e}"))
            return response_error(CODE_FAIL_BOT, f"{e}"), CODE_FAIL_BOT

    async def _send_message_listener(self, message: Message, updates: Updates):
        text = message.text
        from_user = message.from_user
        chat = message.chat
        if from_user.username == self._name:
            if self._self_messages_listener:
                await self._self_messages_listener(text, chat.id, message, updates)
        else:
            if self._messages_listener:
                await self._messages_listener(text, chat.id, message, updates)

            is_command = self._is_command(message)
            if is_command:
                info = self._get_command(text=message.text, units=message.entities)
                if info is None:
                    if self._messages_no_command_listener:
                        await self._messages_no_command_listener(text, chat.id, message, updates)
                else:
                    command = info[0].text
                    args = info[1]
                    if self._commands_listener:
                        await self._commands_listener(command, args, chat.id, message, updates)
                    listener = self._command_listeners.get(command)
                    if listener:
                        await listener(args, chat.id, message, updates)
            else:
                if self._messages_no_command_listener:
                    await self._messages_no_command_listener(text, chat.id, message, updates)

    async def _send_notify_listener(self, message: Message, updates: Updates):
        if self._notify_listener:
            if message.new_chat_members:
                await self._notify_listener(NotifyEvent.NEW_CHAT_MEMBERS,
                                            NewChatMemberPayload(payload=message.new_chat_members), message,
                                            updates)
            if message.left_chat_member:
                await self._notify_listener(NotifyEvent.LEFT_CHAT_MEMBERS,
                                            LeftChatMemberPayload(payload=message.left_chat_member),
                                            message, updates)

    async def _send_callback_query_listener(self, callback_query: CallbackQuery):
        if self._on_query_callback:
            await self._on_query_callback(callback_query)

    async def _get_updates(self, json_data):
        log_info(f"{self._name} get updates from json")
        log_verbose(json_data)
        if json_data:
            log_info(f"convert to Message class")
            updates = Updates(**json_data)
            log_debug(updates)
            return updates
        return None

    async def _get_message(self, updates: Updates):
        log_info(f"{self._name} choose message from update")
        if updates.message:
            return updates.message
        elif updates.edited_message:
            return updates.edited_message
        elif updates.channel_post:
            return updates.channel_post
        elif updates.edited_channel_post:
            return updates.edited_channel_post
        else:
            return None

    async def _verify_message(self, update_id: int, message: Message | None):
        if message is None:
            msg = f"message no info, only update_id {update_id}"
            log_error(msg)
            if self._error_listener:
                await self._error_listener(ErrorType.MESSAGE, error_message("_verify_message", msg))
            return False
        if message.chat is None:
            msg = f"not found chat object in message with update_id {update_id}"
            log_error(msg)
            if self._error_listener:
                await self._error_listener(ErrorType.MESSAGE, error_message("_verify_message", msg))
            return False
        if message.from_user is None:
            msg = f"not found from object in message with update_id {update_id}"
            log_error(msg)
            if self._error_listener:
                await self._error_listener(ErrorType.MESSAGE, error_message("_verify_message", msg))
            return False
        return True

    async def _verify_callback_query(self, update_id: int, callback_query: CallbackQuery):
        if callback_query is None:
            msg = f"callback_query no info, only update_id {update_id}"
            log_error(msg)
            if self._error_listener:
                await self._error_listener(ErrorType.CALLBACK_QUERY, error_message("_verify_callback_query", msg))
            return False
        if callback_query.data is None:
            msg = f"not found data object in callback_query with update_id {update_id}"
            log_error(msg)
            if self._error_listener:
                await self._error_listener(ErrorType.MESSAGE, error_message("_verify_callback_query", msg))
            return False
        if callback_query.message is None:
            msg = f"not found message object in callback_query with update_id {update_id}"
            log_error(msg)
            if self._error_listener:
                await self._error_listener(ErrorType.MESSAGE, error_message("_verify_callback_query", msg))
            return False
        return True

    def _is_command(self, message: Message):
        log_info(f"{self} check message is command or normal text")
        units = message.entities
        if units:
            for entity in units:
                if entity.type == TYPE_BOT_COMMAND and entity.offset == 0:
                    return True
        return False

    def _is_notify(self, message: Message):
        log_info(f"{self} check message is notify message or not")
        if message.new_chat_members or message.left_chat_member:
            return True
        else:
            return False

    def _get_command(self, text: str, units: list[MessageEntity]):
        log_info(f"extract command")
        parts = self.entity_extract(text=text, units=units)
        if not parts:
            return None
        command = parts[0]
        args = parts[1:]
        return command, args

    def entity_extract(self, text: str, units: list[MessageEntity]) -> list[Argument]:
        log_info(f"{self} extract text {text}")
        units = sorted(units, key=lambda e: e.offset)
        result = []
        cursor = 0

        for entity in units:
            if entity.type == TYPE_UNKNOWN:
                continue

            # Add plain text before the entity
            if cursor < entity.offset:
                temp = text[cursor:entity.offset].strip()
                if is_not_empty(temp):
                    result.append(Argument(text=temp, type=TYPE_TEXT, entity=None))

            # Add the entity chunk
            end = entity.offset + entity.length
            temp = text[entity.offset:end].strip()
            result.append(Argument(text=temp, type=entity.type, entity=entity))
            cursor = end

        # Add trailing text after last entity
        if cursor < len(text):
            temp = text[cursor:].strip()
            if is_not_empty(temp):
                result.append(Argument(text=temp, type=TYPE_TEXT, entity=None))

        return result

    async def _request(self, url: str, payload: FormData):
        try:
            log_info(f"{self._name} request {url} with payload[{print_form_data(payload)}]")
            self.__generate_curl_command(url, payload)
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload) as response:
                    response.raise_for_status()
                    text = await response.text()
                    try:
                        result = json.loads(text)
                    except json.JSONDecodeError:
                        result = text
                    log_debug(f"{extract_last_url(url)} response: {result}")
                    return result
        except Exception as e:
            log_warning(FAILED_REQUEST.format("set_command", e))
            return None

    def __generate_curl_command(self, url: str, payload: FormData):
        if self.is_log_curl_command:
            curl_cmd = f"curl --location '{url}' --header 'Content-Type: application/x-www-form-urlencoded'"
            for field in payload._fields:
                name_dict = field[0]
                value = field[2]
                if isinstance(name_dict, MultiDict) and 'name' in name_dict:
                    key = name_dict['name']
                else:
                    continue
                curl_cmd += f" --data-urlencode '{key}={value}'"
            log_debug(curl_cmd)

    # ####################################################################################################
    # interface api_message.py
    # ####################################################################################################
    async def get_messages(self, offset: int, limit: int, timeout: int = None, allowed_updates: list[str] = None):
        """Stub for IDE. Implemented in api_message.py."""

    async def send_message(self, chat_id: int, text: str,
                           parse_mode: ParseModeType = None,
                           reply_to_message_id: int = None,
                           peer_id: int = None,
                           disable_web_page_preview: bool = None, disable_notification: bool = None,
                           reply_markup: BaseKeyboard = None,
                           entities: list[MessageEntity] = None):
        """Stub for IDE. Implemented in api_message.py."""

    async def send_document(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                            disable_notification: bool = None):
        """Stub for IDE. Implemented in api_message.py."""

    async def send_photo(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                         disable_notification: bool = None):
        """Stub for IDE. Implemented in api_message.py."""

    async def send_video(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                         disable_notification: bool = None):
        """Stub for IDE. Implemented in api_message.py."""

    async def send_audio(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                         disable_notification: bool = None):
        """Stub for IDE. Implemented in api_message.py."""

    async def send_voice(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                         disable_notification: bool = None):
        """Stub for IDE. Implemented in api_message.py."""

    async def send_animation(self, chat_id: int, file_path: str, caption: str = None, reply_id: int = None,
                             disable_notification: bool = None):
        """Stub for IDE. Implemented in api_message.py."""

    async def send_chat_action(self, chat_id: int, action: ChatAction):
        """Stub for IDE. Implemented in api_message.py."""

    async def edit_message(self, chat_id: int, message_id: int, text: str):
        """Stub for IDE. Implemented in api_message.py."""

    async def edit_message_caption(self, chat_id: int, message_id: int, caption: str):
        """Stub for IDE. Implemented in api_message.py."""

    async def edit_message_media(self, chat_id: int, message_id: int, file_path: str):
        """Stub for IDE. Implemented in api_message.py."""

    async def forward_message(self, chat_id: int, from_chat_id: int, message_id: int,
                              disable_notification: bool = None):
        """Stub for IDE. Implemented in api_message.py."""

    async def delete_message(self, chat_id: int, message_id: int):
        """Stub for IDE. Implemented in api_message.py."""

    # ####################################################################################################
    # interface api_command.py
    # ####################################################################################################
    async def set_command(self, commands: list[Command]):
        """Stub for IDE. Implemented in api_command.py."""

    async def get_command(self):
        """Stub for IDE. Implemented in api_command.py."""

    async def delete_command(self, commands: list[Command]):
        """Stub for IDE. Implemented in api_command.py."""

    # ####################################################################################################
    # interface api_group.py
    # ####################################################################################################
    async def get_chat(self, chat_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def get_chat_administrators(self, chat_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def get_chat_member(self, chat_id: int, user_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def get_chat_member_count(self, chat_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def leave_chat(self, chat_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def ban_chat_member(self, chat_id: int, user_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def un_ban_chat_member(self, chat_id: int, user_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def restrict_chat_member(self, chat_id: int, user_id: int, until_date: int,
                                   permissions: RestrictChatPermission):
        """Stub for IDE. Implemented in api_group.py."""

    async def promote_chat_member(self, chat_id: int, user_id: int, is_anonymous: bool,
                                  disable_admin_setting_notify: bool,
                                  promote_permission: PromotePermission):
        """Stub for IDE. Implemented in api_group.py."""

    async def approve_chat_join_request(self, chat_id: int, user_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def decline_chat_join_request(self, chat_id: int, user_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def set_chat_permission(self, chat_id: int, permissions: ChatPermission):
        """Stub for IDE. Implemented in api_group.py."""

    async def get_user_profile_photos(self, user_id: int):
        """Stub for IDE. Implemented in api_group.py."""

    async def set_chat_title(self, chat_id: int, title: str):
        """Stub for IDE. Implemented in api_group.py."""

    async def set_chat_description(self, chat_id: int, description: str):
        """Stub for IDE. Implemented in api_group.py."""
