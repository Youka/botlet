""" Bot logic """
from importlib import import_module
from logging import getLogger
from pkgutil import iter_modules
from threading import Event as ThreadEvent
from typing import Callable, Dict, List, Optional

from . import plugins
from .plugins import AbstractPlugin, Event
from .utils import SafeQueue


def run(config: Dict[str,Dict[str,str]], env: Dict[str, str], stop_event: Optional[ThreadEvent] = None):
    """ Bot main loop """
    # Give input feedback
    log = getLogger(__name__)
    log.debug('Configuration: %s', config)
    log.debug('Environment (keys-only): %s', list(env.keys()))
    # Setup event queue
    event_queue = SafeQueue[Event](1024)
    def publish_event(event: Event):
        if not event_queue.put(event):
            log.warning('Bot event queue is full! Event: %s', event)
    # Register workers by plugins and process their events
    workers: List[AbstractPlugin] = []
    try:
        _register_plugins(workers, publish_event, config, env)
        _process_events(workers, event_queue, stop_event)
    finally:
        # Terminate workers
        for worker in workers:
            worker.close()


def _register_plugins(workers: List[AbstractPlugin], publish_event: Callable[[Event], None], config: Dict[str,Dict[str,str]], env: Dict[str, str]):
    # Load plugins dynamically
    for module_info in iter_modules(plugins.__path__):
        if not module_info.ispkg:
            module_register_plugins = import_module('.' + module_info.name, plugins.__package__).__dict__.get('register_plugins')
            if module_register_plugins:
                module_register_plugins(workers, publish_event, config, env)


def _process_events(workers: List[AbstractPlugin], event_queue: SafeQueue[Event], stop_event: Optional[ThreadEvent]):
    if workers:
        try:
            while not (stop_event and stop_event.is_set()):
                event = event_queue.get(1)  # Timeout required because SIGINT / KeyboardInterrupt gets blocked too
                if event:
                    for worker in workers:
                        if worker.name != event.publisher:
                            worker.apply_event(event)
        except KeyboardInterrupt:
            pass
