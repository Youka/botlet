""" Plugins to run a timed task """
from abc import ABC
from typing import Callable, Dict, List

from . import AbstractPlugin, AbstractThreadedPlugin, Event, EventData, StatusEventData


# Plugin template for common resources & operations
class _TimerPlugin(AbstractThreadedPlugin, ABC):
    def __init__(self, name: str, publish_event: Callable[[Event], None], interval: float, callback: Callable[[Callable[[EventData], None]], None]):
        def run():
            while not self._stopped.wait(interval):
                callback(self._publish_event_data)
        super().__init__(name, run, publish_event)

    def apply_event(self, event: Event):
        """ Unused """


class HeartbeatPlugin(_TimerPlugin):
    """ Heartbeat plugin class """
    def __init__(self, name: str, publish_event: Callable[[Event], None], interval: float, message: str):
        super().__init__(name, publish_event, interval, lambda publish_event_data: publish_event_data(StatusEventData(message)))


def register_plugins(workers: List[AbstractPlugin], publish_event: Callable[[Event], None], config: Dict[str,Dict[str,str]], _env: Dict[str, str]):
    """ Register local plugins to bot """
    heartbeat = config.get('plugin.heartbeat', {})
    heartbeat_interval = heartbeat.get('interval')
    heartbeat_message = heartbeat.get('message')
    if heartbeat_interval and heartbeat_message:
        workers.append(HeartbeatPlugin('heartbeat', publish_event, float(heartbeat_interval), heartbeat_message))
