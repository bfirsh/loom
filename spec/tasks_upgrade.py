from pspec import describe
from loom.tasks import upgrade
from mock import patch, call


with describe('tasks.upgrade'):

    @patch('loom.tasks.sudo')
    def it_upgrade_interactive(sudo_mock):

        upgrade()

        expected = [call('apt-get update'), call('apt-get upgrade')]
        assert sudo_mock.call_args_list == expected

    @patch('loom.tasks.sudo')
    def it_upgrade_non_interactive(sudo_mock):

        upgrade(True)

        expected = [call('apt-get update'), call('apt-get upgrade -y')]
        assert sudo_mock.call_args_list == expected
