""" Plugins to connect as chat bots """
from abc import ABC
from asyncio import new_event_loop, set_event_loop, sleep
from logging import getLogger
from threading import Event as ThreadEvent
from typing import Callable, Dict, List, NamedTuple, Union

from discord import Client as DiscordClient, Message as DiscordMessage, DMChannel
from discord.errors import DiscordException
from slack import RTMClient as SlackRTMClient
from slack.errors import SlackClientError

from . import AbstractPlugin, AbstractThreadedPlugin, ChatCommandEventData, ChatOutputEventData, Event, EventData, StatusEventData
from ..utils import SafeQueue


# Beginning of text to be recognized as command by chat bots
_CHAT_COMMAND_PREFIX = '$'


# Separator of commands in text
_CHAT_COMMAND_SEPARATOR = '&&'


# Command-only hint for direct messages
_CHAT_COMMAND_ONLY_HINT = 'Hi there. I am a command processing bot, reacting to messages with prefix "{}". No smalltalk!'.format(_CHAT_COMMAND_PREFIX)


# Message text with target channel
class _Message(NamedTuple):
    text: str
    channel_id: Union[str,int,None]


# Plugin template for common resources & operations
class _ChatPlugin(AbstractThreadedPlugin, ABC):
    def __init__(self, name: str, run: Callable[[], None], publish_event: Callable[[Event], None]):
        self._message_queue = SafeQueue[_Message]()
        super().__init__(name, run, publish_event)

    def apply_event(self, event: Event):
        if isinstance(event.data, ChatOutputEventData):
            data: ChatOutputEventData = event.data
            if data.target_publisher is None or data.target_publisher == self.name:
                if not self._message_queue.put(_Message(data.text, data.target_channel_id)):
                    self._log.warning('Message queue is full! Event: %s', event)


# DISCORD
class DiscordPlugin(_ChatPlugin):
    """ Discord plugin class """
    def __init__(self, name: str, publish_event: Callable[[Event], None], token: str, channel_id: int):
        def run():
            set_event_loop(new_event_loop())
            _DiscordClient(self._stopped, self._message_queue, channel_id, self._publish_event_data).run(token)
        super().__init__(name, run, publish_event)


class _DiscordClient(DiscordClient):
    """ Client connected to discord bot """
    def __init__(self, should_logout: ThreadEvent, message_queue: SafeQueue[_Message], default_channel_id: int, publish_event_data: Callable[[EventData], None]):
        super().__init__()
        self._should_logout = should_logout
        self._message_queue = message_queue
        self._default_channel_id = default_channel_id
        self._publish_event_data = publish_event_data
        self._log = getLogger(__name__)
        self.loop.create_task(self.background_task())

    async def on_ready(self):
        """ Callback after successful connection """
        self._publish_event_data(StatusEventData('Discord login: ' + str(self.user)))

    async def on_message(self, message: DiscordMessage):
        """ Callback on message receiving from connection """
        # Don't react to own message
        if message.author != self.user:
            text = message.content
            channel = message.channel
            # Process command
            if text.startswith(_CHAT_COMMAND_PREFIX):
                for command in map(str.strip, text[len(_CHAT_COMMAND_PREFIX):].split(_CHAT_COMMAND_SEPARATOR)):
                    self._publish_event_data(ChatCommandEventData(command, channel.id))
            # Respond with hint on direct message
            elif isinstance(channel, DMChannel):
                try:
                    for text in self._partition_text(_CHAT_COMMAND_ONLY_HINT):
                        await channel.send(text)
                except DiscordException as ex:
                    self._log.error('Discord message error: %s', ex)

    async def background_task(self):
        """ Background runner """
        await self.wait_until_ready()
        while not self._should_logout.is_set():
            message = self._message_queue.get()
            if message and message.text:
                try:
                    channel = self.get_channel(message.channel_id if isinstance(message.channel_id, int) else self._default_channel_id)
                    if channel:
                        for text in self._partition_text(message.text):
                            await channel.send(text)
                except DiscordException as ex:
                    self._log.error('Discord task error: %s', ex)
            await sleep(0.5)
        await self.logout()

    @staticmethod
    def _partition_text(text: str) -> List[str]:
        message_limit = 2000    # Message characters limit of discord
        return [
            text[i:i+message_limit]
            for i in range(0, min(len(text), message_limit * 5), message_limit)
        ]


# SLACK
class SlackPlugin(_ChatPlugin):
    """ Slack plugin class """
    def __init__(self, name: str, publish_event: Callable[[Event], None], token: str, channel_id: str):
        def run():
            set_event_loop(new_event_loop())
            _SlackClient(token, self._stopped, self._message_queue, channel_id, self._publish_event_data).start()
        super().__init__(name, run, publish_event)


class _SlackClient(SlackRTMClient):
    """ Client connected to slack legacy bot """
    def __init__(self, token: str, should_logout: ThreadEvent, message_queue: SafeQueue[_Message], default_channel_id: str, publish_event_data: Callable[[EventData], None]):
        super().__init__(token=token)
        self._log = getLogger(__name__)
        self._user = None

        def on_ready(**payload):
            self._user = payload['data']['self'] # Base client just saves token, not user information
            publish_event_data(StatusEventData('Slack login: ' + str(self._user)))
        self.on(event='open', callback=on_ready)

        def on_message(**payload):
            data: dict = payload['data']
            if 'text' in data and 'channel' in data and 'user' in data:
                text: str = self._unescape_text(data['text'])
                channel_id: str = data['channel']
                author: str = data['user']
                # Don't react to own message
                if author != self._user['id']:
                    # Process command
                    if text.startswith(_CHAT_COMMAND_PREFIX):
                        for command in map(str.strip, text[len(_CHAT_COMMAND_PREFIX):].split(_CHAT_COMMAND_SEPARATOR)):
                            publish_event_data(ChatCommandEventData(command, channel_id))
                    # Respond with hint on direct message
                    else:
                        try:
                            conversation = self._web_client.conversations_info(channel=channel_id)
                            if conversation.get('channel', {}).get('is_im'):
                                self._web_client.chat_postMessage(
                                    channel=channel_id,
                                    text=self._escape_text(_CHAT_COMMAND_ONLY_HINT)
                                )
                        except SlackClientError as ex:
                            self._log.error('Slack message error: %s', ex)
        self.on(event='message', callback=on_message)

        async def background_task():
            while not should_logout.is_set():
                message = message_queue.get()
                if message and message.text:
                    try:
                        self._web_client.chat_postMessage(
                            channel=message.channel_id if isinstance(message.channel_id, str) else default_channel_id,
                            text=self._escape_text(message.text)
                        )
                    except SlackClientError as ex:
                        self._log.error('Slack task error: %s', ex)
                await sleep(0.5)
            self.stop()
        self._event_loop.create_task(background_task())

    # Special text characters to escape, see <https://api.slack.com/reference/surfaces/formatting#escaping>
    _TEXT_ESCAPES = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;'
    }
    @classmethod
    def _escape_text(cls, text: str) -> str:
        for character, escape in cls._TEXT_ESCAPES.items():
            text = text.replace(character, escape)
        return text[:40000] # Message characters limit of slack

    @classmethod
    def _unescape_text(cls, text: str) -> str:
        for character, escape in cls._TEXT_ESCAPES.items():
            text = text.replace(escape, character)
        return text


# REGISTRATION
def register_plugins(workers: List[AbstractPlugin], publish_event: Callable[[Event], None], _config: Dict[str,Dict[str,str]], env: Dict[str, str]):
    """ Register local plugins to bot """
    # Discord
    discord_token = env.get('DISCORD_TOKEN')
    discord_channel_id = env.get('DISCORD_CHANNEL_ID')
    if discord_token and discord_channel_id:
        workers.append(DiscordPlugin('discord', publish_event, discord_token, int(discord_channel_id)))
    # Slack
    slack_token = env.get('SLACK_TOKEN')
    slack_channel_id = env.get('SLACK_CHANNEL_ID')
    if slack_token and slack_channel_id:
        workers.append(SlackPlugin('slack', publish_event, slack_token, slack_channel_id))
