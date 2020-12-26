""" Command line interface """
from argparse import ArgumentParser
from logging import getLogger

from . import __version__ as version
from .bot import run as bot_run
from .config import get_configuration, get_environment, init_logging


def main():
    """ Command line entry point """
    # Parse arguments
    parser = ArgumentParser(description='Communication and commands bot.')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)
    parser.add_argument('-e', '--env', metavar=('ENV_KEY', 'ENV_VAL'), dest='environment', action='append', nargs=2, help='adds an environment entry')
    parser.add_argument('-c', '--config', metavar='FILE', dest='config_file', help='loads configuration from file (overrides internal default)')
    parser.add_argument('-l', '--log', metavar='FILE', dest='logging_file', help='loads logging properties from file (overrides internal default)')
    args = parser.parse_args()
    # Initialize by inputs
    init_logging(args.logging_file)
    log = getLogger(__name__)
    config = get_configuration(args.config_file)
    env = get_environment(config.get('general', {}).get('environment_prefix'), args.environment)
    # Run bot
    log.info('Starting...')
    bot_run(config, env)
    log.info('Stopping...')
