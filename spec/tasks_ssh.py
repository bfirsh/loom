from fabric.api import env
from pspec import describe
from loom.tasks import ssh
from mock import patch, call

with describe('loom.tasks'):

    @patch('loom.tasks.subprocess')
    def it_ssh_simple_host_no_keyfilename(mock):

        env.user = 'user'
        env.host_string = 'example.com'
        ssh()

        expected = [call('ssh -A -t user@example.com'.split())]
        assert mock.call.call_args_list == expected

    @patch('loom.tasks.subprocess')
    def it_ssh_simple_host_with_string_keyfilename(mock):

        env.user = 'user'
        env.host_string = 'example.com'
        env.key_filename = 'test.pem'
        ssh()

        expected = [call('ssh -A -t -i test.pem user@example.com'.split())]
        assert mock.call.call_args_list == expected

    @patch('loom.tasks.subprocess')
    def it_ssh_complex_host(mock):

        env.user = 'user'
        env.host_string = 'test@example.com:9999'
        ssh()

        expected = [call('ssh -A -t -p 9999 user@example.com'.split())]
