""" Test bot running """
from threading import Event, Thread
from time import sleep
from timeit import timeit
from unittest import TestCase

from botlet.bot import run as bot_run


class TestBot(TestCase):
    """ Test suite for bot methods """
    def test_dry_run(self):
        """ Dry run / do nothing """
        stop_event = Event()
        stop_event.set()
        self.assertLessEqual(
            timeit(lambda: bot_run({}, {}, stop_event), number=100),
            3.0,    # Loading plugins by dynamic import takes time
            'Bot dry run should not take more than 3 seconds!'
        )

    def test_logging_heartbeat_run(self):
        """ Run with logging and heartbeat plugin """
        with self.assertLogs(level='WARNING') as context_manager:
            stop_event = Event()
            thread = Thread(
                target=bot_run,
                args=[
                    {
                        'general': {'identity': 'Test'},
                        'plugin.logging': {'level': 'WARNING'},
                        'plugin.heartbeat': {'interval': '1.1', 'message': 'Test alive.'}
                    },
                    {},
                    stop_event
                ]
            )
            thread.start()
            sleep(2)
            stop_event.set()
            thread.join(5)
        self.assertIn('WARNING:Test:Event(publisher=\'heartbeat\', data=StatusEventData(status=\'Test alive.\'))', context_manager.output)
