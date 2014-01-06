from fabric.api import env
from pspec import describe
from loom.tasks import all, ssh, upgrade
from mock import patch, call

with describe('loom.tasks.all'):
    def it_sets_env_hsots_to_contain_all_hosts_in_roledefs():
        env.roledefs = {
            'app1': ['app1.com', 'app2.com'],
            'app2': ['app1.com', 'app2.com'],
            'db': ['db.com']
        }

        all()

        assert set(['app1.com', 'app2.com', 'db.com']) == set(env.hosts)


with describe('loom.tasks.ssh'):
    @patch('loom.tasks.subprocess')
    def it_calls_ssh(mock):
        env.user = 'user'
        env.host_string = 'example.com'
        env.key_filename = None
        ssh()

        expected = [call('ssh -A -t user@example.com'.split())]
        assert mock.call.call_args_list == expected

    @patch('loom.tasks.subprocess')
    def it_calls_ssh_with_a_key_filename(mock):
        env.user = 'user'
        env.host_string = 'example.com'
        env.key_filename = 'test.pem'
        ssh()

        expected = [call('ssh -A -t -i test.pem user@example.com'.split())]
        assert mock.call.call_args_list == expected

    @patch('loom.tasks.subprocess')
    def it_calls_ssh_with_a_key_filename_list(mock):
        env.user = 'user'
        env.host_string = 'example.com'
        env.key_filename = ['test.pem']
        ssh()

        expected = [call('ssh -A -t -i test.pem user@example.com'.split())]
        assert mock.call.call_args_list == expected

    @patch('loom.tasks.subprocess')
    def it_calls_ssh_with_a_complex_host(mock):
        env.host_string = 'test@example.com:9999'
        env.key_filename = None
        ssh()

        expected = [call('ssh -A -t -p 9999 test@example.com'.split())]
        print mock.call.call_args_list
        assert mock.call.call_args_list == expected


with describe('loom.tasks.upgrade'):
    @patch('loom.tasks.sudo')
    def it_calls_apt_get_upgrade(sudo_mock):

        upgrade()

        expected = [call('apt-get update'), call('apt-get upgrade')]
        assert sudo_mock.call_args_list == expected

    @patch('loom.tasks.sudo')
    def it_calls_apt_get_upgrade_without_prompting_for_confirmation(sudo_mock):

        upgrade(True)

        expected = [call('apt-get update'), call('apt-get upgrade -y')]
        assert sudo_mock.call_args_list == expected


