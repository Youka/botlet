""" Plugins to analyze websites """
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from html.parser import HTMLParser
from http.client import HTTPResponse
from logging import getLogger
from urllib.error import URLError
from urllib.request import Request, urlopen
from threading import Thread
from typing import Callable, Dict, List, Optional, Tuple

from . import AbstractPlugin, ChatCommandEventData, ChatOutputEventData, Event


# PLUGINS
class AnimeBirthdaysPlugin(AbstractPlugin):
    """ Anime birthdays plugin class """
    def __init__(self, name: str, publish_event: Callable[[Event], None]):
        super().__init__(name, publish_event)

    def apply_event(self, event: Event):
        # Is valid plugin command?
        if isinstance(event.data, ChatCommandEventData):
            data: ChatCommandEventData = event.data
            if data.command == 'help':
                self._publish_event_data(ChatOutputEventData('Command: anime_birthdays', event.publisher, data.channel_id))
            elif data.command == 'anime_birthdays':
                # Show characters with todays birthday from anisearch.com
                def run():
                    try:
                        self._publish_event_data(ChatOutputEventData(
                            'Anime birthdays:\n' + '\n'.join(map(
                                lambda character: '{} ({}) [{}]:\n{}'.format(character.name, character.anime, character.rating, character.url),
                                _get_anisearch_birthday_characters()
                            )),
                            event.publisher, data.channel_id
                        ))
                    except URLError as ex:
                        self._log.error('Loading characters failed: %s', ex)
                Thread(target=run, daemon=True).start()


# REGISTRATION
def register_plugins(workers: List[AbstractPlugin], publish_event: Callable[[Event], None], _config: Dict[str,Dict[str,str]], _env: Dict[str, str]):
    """ Register local plugins to bot """
    workers.append(AnimeBirthdaysPlugin('anime_birthdays', publish_event))


# HELPERS
@dataclass
class _AnisearchCharacter:
    name: str
    anime: Optional[str]
    rating: int
    url: str


class _AnisearchBirthdayCharactersParser(HTMLParser):
    def __init__(self, day: int):
        # Initialization
        super().__init__()
        self._day = day
        self._rating_suffix = ' ❤'  # Text node ends with unicode heart symbol
        # Results
        self._characters: List[_AnisearchCharacter] = []
        self._log = getLogger(__name__)
        # Parser state
        self._section_today = False

    def get_characters(self) -> List[_AnisearchCharacter]:
        """ Get parsed characters """
        return self._characters

    def error(self, message: str):
        self._log.error(message)

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        attrs_dict = dict(attrs)
        if tag == 'section' and attrs_dict.get('id') == 'day-' + str(self._day):
            self._section_today = True
        elif self._section_today and tag == 'a' and 'data-title' in attrs_dict and 'href' in attrs_dict:
            self._characters.append(_AnisearchCharacter(
                attrs_dict['data-title'].replace('Character: ', '').title(),
                None,
                0,
                'http://www.anisearch.com/' + attrs_dict['href']
            ))

    def handle_endtag(self, tag: str):
        if tag == 'section':
            self._section_today = False

    def handle_data(self, data: str):
        if self._section_today and self._characters and data.endswith(self._rating_suffix):
            try:
                self._characters[-1].rating =  int(data.replace(self._rating_suffix, ''))
            except ValueError as ex:
                self._log.error('Rating for %s: %s', self._characters[-1], ex)


class _AnisearchCharacterAnimeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self._anime = None
        self._log = getLogger(__name__)

    def get_anime(self) -> str:
        """ Get parsed anime """
        return self._anime

    def error(self, message: str):
        self._log.error(message)

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str]]):
        if tag == 'a':
            anime = [attr[1].replace('Anime: ', '') for attr in attrs if attr[0] == 'data-title' and attr[1].startswith('Anime: ')]
            if anime:
                self._anime = anime[0] # Always overrides, results in last / oldest anime


@lru_cache(7)
def _get_anisearch_birthday_characters(birthday: date = date.today()) -> List[_AnisearchCharacter]:
    user_agent_headers = {'User-Agent': 'Mozilla/5.0'}  # Hack to prevent websites blocking bots
    http_response: HTTPResponse = None  # Typing for url responses of http requests
    # Find characters by birthday
    with urlopen(Request(
        'http://www.anisearch.com/character/birthdays?month=' + str(birthday.month),
        headers=user_agent_headers
    )) as http_response:
        parser = _AnisearchBirthdayCharactersParser(birthday.day)
        parser.feed(str(http_response.read(), 'utf-8'))
        characters = parser.get_characters()
        # Add anime to characters
        def add_anime(character: _AnisearchCharacter):
            with urlopen(Request(
                character.url,
                headers=user_agent_headers
            )) as http_response:
                parser = _AnisearchCharacterAnimeParser()
                parser.feed(str(http_response.read(), 'utf-8'))
                character.anime = parser.get_anime()
        with ThreadPoolExecutor() as pool:
            pool.map(add_anime, characters)
        # Restrict to anime characters and sort by rating
        return list(sorted(
            filter(
                lambda character: character.anime,
                characters
            ),
            key=lambda c: c.rating,
            reverse=True
        ))
