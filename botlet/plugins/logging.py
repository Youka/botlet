""" Plugins to log events """
from logging import getLevelName
from typing import Callable, Dict, List

from . import AbstractPlugin, Event


class LoggingPlugin(AbstractPlugin):
    """ Logging plugin class """
    def __init__(self, name: str, level: int):
        super().__init__(name)
        self._level = level

    def apply_event(self, event: Event):
        self._log.log(self._level, event)


def register_plugins(workers: List[AbstractPlugin], _publish_event: Callable[[Event], None], config: Dict[str,Dict[str,str]], _env: Dict[str, str]):
    """ Register local plugins to bot """
    logging_level = config.get('plugin.logging', {}).get('level')
    if logging_level:
        workers.append(LoggingPlugin(config.get('general', {}).get('identity') or '', getLevelName(logging_level)))
