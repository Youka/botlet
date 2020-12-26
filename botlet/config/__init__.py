""" Configuration loading by files & environment """
from configparser import ConfigParser, ExtendedInterpolation
from logging.config import fileConfig as loggingConfig
from os import environ
from typing import Dict, List, Optional
from pkg_resources import resource_string


def get_environment(global_prefix: Optional[str] = None, entries: Optional[List[List[str]]] = None) -> Dict[str,str]:
    """ Extracts module parameters from process environment variables """
    global_prefix_upper = (global_prefix or '').upper()
    env = {
        key[len(global_prefix_upper):]: value
        for (key, value) in environ.items()
        if key.upper().startswith(global_prefix_upper)
    }
    if entries:
        env.update({
            entry[0]: ','.join(entry[1:])
            for entry in entries
            if len(entry) >= 2
        })
    return env


def get_configuration(filepath: Optional[str] = None) -> Dict[str,Dict[str,str]]:
    """ Loads module packaged configuration """
    config = _read_file_config(filepath) if filepath else _read_package_config('config.ini')
    return {
        section_name: dict(section.items())
        for (section_name, section) in config.items()
    }


def init_logging(filepath: Optional[str] = None):
    """ Configure global logging by configuration in package """
    loggingConfig(_read_file_config(filepath) if filepath else _read_package_config('logging.ini'))


def _read_file_config(filepath: str) -> ConfigParser:
    config = ConfigParser(interpolation=ExtendedInterpolation())
    with open(filepath) as file:
        config.read_file(file)
    return config


def _read_package_config(filename: str) -> ConfigParser:
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read_string(str(resource_string(__name__, filename), 'utf-8'))
    return config
