from pspec import describe
from attest import assert_hook
from fabric.api import env
from loom.config import host_roles, current_roles

with describe('host_roles'):

    def it_returns_the_role_for_a_host_with_a_single_role():
        env.roledefs = {'app': 'app.example.com'}
        assert host_roles('app.example.com') == ['app']

    def it_returns_the_roles_for_a_host_with_multiple_roles():
        env.roledefs = {
            'app': 'server.example.com',
            'db': 'server.example.com',
        }
        assert host_roles('server.example.com') == ['app', 'db']

    def it_returns_the_role_for_multiple_hosts_with_a_single_role():
        env.roledefs = {'app': ['app1.example.com', 'app2.example.com']}
        assert host_roles('app1.example.com') == ['app']
        assert host_roles('app2.example.com') == ['app']

    def it_returns_the_role_for_multiple_hosts_with_multiple_roles():
        env.roledefs = {
            'app': ['app1.example.com', 'app2.example.com'],
            'db': ['app1.example.com', 'app2.example.com']
        }
        assert host_roles('app1.example.com') == ['app', 'db']
        assert host_roles('app2.example.com') == ['app', 'db']

with describe('current_roles'):
    def it_returns_the_roles_for_the_current_host():
        env.roledefs = {'app': 'app.example.com'}
        env.host_string = 'app.example.com'
        assert current_roles() == ['app']
