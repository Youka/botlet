""" Test plugins functionaliy"""
from datetime import date
from unittest import TestCase

from botlet.plugins.chat import _CHAT_COMMAND_ONLY_HINT, _CHAT_COMMAND_PREFIX, _DiscordClient, _SlackClient
from botlet.plugins.git import _get_repository_branches, _get_repository_branch_commits
from botlet.plugins.webcrawl import _get_anisearch_birthday_characters


class TestPlugins(TestCase):
    """ Test suite for plugins methods """
    def test_chat(self):
        """ Chat utilities """
        self.assertIn(_CHAT_COMMAND_PREFIX, _CHAT_COMMAND_ONLY_HINT)
        self.assertGreater(
            len(_DiscordClient._partition_text('0123456789' * 201)),    # pylint: disable=W0212
            1,
            'Discord text should be too long without partitioning!'
        )
        self.assertEqual(
            _SlackClient._escape_text('& and < and >'), # pylint: disable=W0212
            '&amp; and &lt; and &gt;',
            'Slack text escape has to work!'
        )
        self.assertEqual(
            _SlackClient._unescape_text('&amp; and &lt; and &gt;'), # pylint: disable=W0212
            '& and < and >',
            'Slack text unescape has to work!'
        )


    def test_git(self):
        """ Request public git repository """
        repository = 'https://github.com/microsoft/vscode.git'
        branch = 'master'
        self.assertIn(
            branch,
            _get_repository_branches(repository),
            '"{}" has no branch "{}" anymore?!'.format(repository, branch)
        )
        self.assertGreater(
            len(_get_repository_branch_commits(repository, branch).splitlines()),
            0,
            '"{}" on branch "{}" should have any commit.'.format(repository, branch)
        )

    def test_anime_birthdays(self):
        """ Fetch birthdays """
        self.assertIn(
            'Miku Hatsune',
            map(lambda character: character.name, _get_anisearch_birthday_characters(date(2020, 8, 31))),
            'But Miku has her birthday on 31th August.'
        )
