""" Test configuration loading """
from logging import getLogger, INFO
from os import environ
from unittest import TestCase

from botlet.config import get_configuration, get_environment, init_logging


class TestConfig(TestCase):
    """ Test suite for configuration methods """
    def setUp(self):
        environ['BOTLET_TEST_FOO'] = 'bar'

    def test_get_configuration(self):
        """ Get default configuration """
        config = get_configuration()
        self.assertIn('general', config)
        general_section = config['general']
        self.assertIn('identity', general_section)
        self.assertIn('environment_prefix', general_section)

    def test_get_environment(self):
        """ Get dummy environment by both sources """
        actual = get_environment('BOTLET_TEST_', [['ANSWER', '42'], ['LEEROY', 'JENKINS', ':O']])
        expected = {
            'FOO': 'bar',
            'ANSWER': '42',
            'LEEROY': 'JENKINS,:O'
        }
        self.assertDictEqual(actual, expected)

    def test_init_logging(self):
        """ Check default logging works """
        self.assertRaises(FileNotFoundError, init_logging, './botlet/not_logging.ini')
        init_logging()
        root_logger = getLogger()
        self.assertEqual(root_logger.name, 'root')
        self.assertTrue(root_logger.isEnabledFor(INFO), 'Root logger is not enabled for infomation!')
        self.assertTrue(root_logger.hasHandlers(), 'Root logger has no handlers!')
