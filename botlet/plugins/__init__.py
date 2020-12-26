""" Plugins collection """
from abc import ABC, abstractmethod
from logging import getLogger
from threading import Event as ThreadEvent, Thread
from typing import Callable, NamedTuple, Optional, Union


# EVENTS
class ChatCommandEventData(NamedTuple):
    """ Command input by chat as event data """
    command: str
    channel_id: Union[str,int]


class ChatOutputEventData(NamedTuple):
    """ Text output to chat as event data """
    text: str
    target_publisher: Optional[str]
    target_channel_id: Union[str,int,None]


class StatusEventData(NamedTuple):
    """ Status text as event data """
    status: str


EventData = Union[ChatCommandEventData, ChatOutputEventData, StatusEventData]


class Event(NamedTuple):
    """ Data container for communication between plugins """
    publisher: str  # Worker name
    data: EventData


# PLUGINS
class AbstractPlugin(ABC):
    """ Base class to process events """
    def __init__(self, name: str, publish_event: Optional[Callable[[Event], None]] = None):
        self.__name = name
        self.__publish_event = publish_event
        self._log = getLogger(name)
        self._log.debug("Initialize plugin.")

    def close(self):
        """ Gets called at end-of-life """
        self._log.debug("Close plugin.")

    @property
    def name(self) -> str:
        """ Get plugin instance name """
        return self.__name

    def _publish_event_data(self, data: EventData):
        if self.__publish_event:
            self.__publish_event(Event(self.__name, data))

    @abstractmethod
    def apply_event(self, event: Event):
        """ Gets called to apply events """


class AbstractThreadedPlugin(AbstractPlugin):
    """ Base class to process events in new thread """
    def __init__(self, name: str, run: Callable[[], None], publish_event: Optional[Callable[[Event], None]] = None):
        super().__init__(name, publish_event)
        self.__thread = Thread(target=run)
        self._stopped = ThreadEvent()
        self.__thread.start()

    def close(self):
        super().close()
        self._stopped.set()
        self.__thread.join(30)
