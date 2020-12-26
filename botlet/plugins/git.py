""" Plugins to work with git repositories """
from logging import getLogger
from re import compile as regex_compile
from shutil import which
from subprocess import CalledProcessError, run as process_run, DEVNULL
from threading import Thread
from typing import Callable, Dict, List

from . import AbstractPlugin, ChatCommandEventData, ChatOutputEventData, Event
from ..utils import SafeTemporaryDirectory


# PLUGINS
class GitPlugin(AbstractPlugin):
    """ Git plugin class """
    def __init__(self, name: str, publish_event: Callable[[Event], None], repositories: Dict[str, str]):
        super().__init__(name, publish_event)
        self._repositories = repositories
        self._branch_pattern = regex_compile(r'[a-zA-Z0-9/_:\.\-\+\*]+')

    def apply_event(self, event: Event):
        # Is valid plugin command?
        if isinstance(event.data, ChatCommandEventData):
            data: ChatCommandEventData = event.data
            args = data.command.split(maxsplit=3)
            args_number = len(args)
            if args_number == 1 and args[0] == 'help':
                self._publish_event_data(ChatOutputEventData('Command: git [<REPOSITORY> [<BRANCH>]]', event.publisher, data.channel_id))
            if args_number >= 1 and args[0] == 'git':
                # Evaluate command arguments
                if args_number == 1:
                    # Show available repositories
                    self._publish_event_data(ChatOutputEventData('Repositories: ' + ', '.join(sorted(self._repositories.keys())), event.publisher, data.channel_id))
                else:
                    repository = self._repositories.get(args[1])
                    if not repository:
                        self._publish_event_data(ChatOutputEventData('Repository not found!', event.publisher, data.channel_id))
                    else:
                        if args_number == 2:
                            # Show available repository branches
                            def run():
                                try:
                                    self._publish_event_data(ChatOutputEventData(
                                        'Branches: ' + ', '.join(_get_repository_branches(repository)),
                                        event.publisher, data.channel_id
                                    ))
                                except (OSError, CalledProcessError) as ex:
                                    self._log.error('Git failed: %s', ex)
                                    self._publish_event_data(ChatOutputEventData('Branches request failed!', event.publisher, data.channel_id))
                            Thread(target=run, daemon=True).start()
                        else:   # args_number == 3
                            branch = args[2]
                            if not self._branch_pattern.fullmatch(branch):
                                self._publish_event_data(ChatOutputEventData('Invalid branch name!', event.publisher, data.channel_id))
                            else:
                                # Show last commits of repository branch
                                def run():
                                    try:
                                        self._publish_event_data(ChatOutputEventData(
                                            'Commits:\n' + _get_repository_branch_commits(repository, branch),
                                            event.publisher, data.channel_id
                                        ))
                                    except (OSError, CalledProcessError) as ex:
                                        self._log.error('Git failed: %s', ex)
                                        self._publish_event_data(ChatOutputEventData('Commits request failed!', event.publisher, data.channel_id))
                                Thread(target=run, daemon=True).start()


# REGISTRATION
def register_plugins(workers: List[AbstractPlugin], publish_event: Callable[[Event], None], config: Dict[str,Dict[str,str]], _env: Dict[str, str]):
    """ Register local plugins to bot """
    repositories = config.get('plugin.git')
    if repositories:
        if which('git'):
            workers.append(GitPlugin('git', publish_event, repositories))
        else:
            getLogger(__name__).warning('Git plugins require git installed!')


# HELPERS
def _get_repository_branches(repository: str) -> List[str]:
    return list(sorted(filter(
        None,
        map(
            lambda line: line.partition('refs/heads/')[2],
            process_run(
                ['git', 'ls-remote', '-h', repository],
                capture_output=True, text=True, check=True
            ).stdout.splitlines()
        )
    )))


def _get_repository_branch_commits(repository: str, branch: str) -> str:
    with SafeTemporaryDirectory(prefix='botlet_', suffix='.git') as dir_path:
        process_run(
            ['git', 'clone', repository, '-b', branch, '--depth=3', '--bare', '--filter=blob:none', '-q', dir_path],
            stdout=DEVNULL, stderr=DEVNULL, check=True
        )
        return process_run(
            ['git', 'log', '-n3', '--no-decorate', '--format=[%h] %s (by %cn, %cr)'],
            cwd=dir_path, capture_output=True, text=True, check=True
        ).stdout.strip()
