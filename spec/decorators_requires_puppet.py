from pspec import describe
from loom.decorators import requires_puppet
from mock import patch


with describe('requires_puppet'):

    @patch('loom.decorators.has_librarian_installed')
    @patch('loom.decorators.has_puppet_installed')
    def it_has_puppet_setup(puppet_mock, librarian_mock):
        puppet_mock.return_value = True
        librarian_mock.return_value = True

        requires_puppet(lambda: 1)()

        assert puppet_mock.called
        assert librarian_mock.called

    @patch('loom.decorators.has_librarian_installed')
    @patch('loom.decorators.has_puppet_installed')
    @patch('loom.decorators.abort')
    def it_doesnt_have_puppet_setup(abort_mock, puppet_mock, librarian_mock):
        puppet_mock.return_value = False
        librarian_mock.return_value = True

        requires_puppet(lambda: 1)()

        assert puppet_mock.called
        assert " puppet" in abort_mock.call_args[0][0]

    @patch('loom.decorators.has_librarian_installed')
    @patch('loom.decorators.has_puppet_installed')
    @patch('loom.decorators.abort')
    def it_doesnt_have_librarian_setup(abort_mock, puppet_mock, librarian_mock):
        puppet_mock.return_value = True
        librarian_mock.return_value = False

        requires_puppet(lambda: 1)()

        assert puppet_mock.called
        assert librarian_mock.called
        assert "librarian-puppet" in abort_mock.call_args[0][0]
