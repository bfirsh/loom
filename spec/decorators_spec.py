from pspec import describe
from loom.decorators import requires_puppet, REQUIRES_GEM
from mock import patch
from fabric.api import env

with describe('loom.decorations.requires_puppet'):
    @patch('loom.decorators.has_librarian_installed')
    @patch('loom.decorators.has_puppet_installed')
    def it_does_not_do_anything_if_puppet_and_librarian_are_installed(puppet_mock, librarian_mock):
        env.host_string = 'app.example.com'
        puppet_mock.return_value = True
        librarian_mock.return_value = True

        requires_puppet(lambda: 1)()

        assert puppet_mock.called
        assert librarian_mock.called

    @patch('loom.decorators.has_librarian_installed')
    @patch('loom.decorators.has_puppet_installed')
    @patch('loom.decorators.abort')
    def it_aborts_if_puppet_is_not_installed(abort_mock, puppet_mock, librarian_mock):
        env.host_string = 'app.example.com'
        puppet_mock.return_value = False
        librarian_mock.return_value = True

        requires_puppet(lambda: 1)()

        assert puppet_mock.called
        assert REQUIRES_GEM.format(host=env.host_string, gem='puppet') == abort_mock.call_args[0][0]

    @patch('loom.decorators.has_librarian_installed')
    @patch('loom.decorators.has_puppet_installed')
    @patch('loom.decorators.abort')
    def it_aborts_if_librarian_is_not_installed(abort_mock, puppet_mock, librarian_mock):
        env.host_string = 'app.example.com'
        puppet_mock.return_value = True
        librarian_mock.return_value = False

        requires_puppet(lambda: 1)()

        assert puppet_mock.called
        assert librarian_mock.called
        assert REQUIRES_GEM.format(host=env.host_string, gem='librarian-puppet') == abort_mock.call_args[0][0]


