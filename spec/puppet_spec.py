from pspec import describe
from attest import assert_hook
from fabric.api import env
from loom.puppet import generate_site_pp, get_puppetmaster_host, _gem_install, generate_site_pp
from mock import patch

with describe('loom.puppet.get_puppetmaster_host'):
    def it_returns_env_puppetmaster_host_when_it_is_defined():
        newenv = {'puppetmaster_host': 'master.example.com'}
        with patch.dict('fabric.api.env', newenv):
            assert 'master.example.com' == get_puppetmaster_host()

    def it_returns_the_host_in_the_puppetmaster_role():
        newenv = {'roledefs':
            {'puppetmaster': ['master.example.com']}
        }
        with patch.dict('fabric.api.env', newenv):
            assert 'master.example.com' == get_puppetmaster_host()

    def it_returns_the_first_puppetmaster_host_when_multiple_are_defined():
        newenv = {'roledefs':
            {'puppetmaster': ['master.example.com', 'master2.example.com']}
        }
        with patch.dict('fabric.api.env', newenv):
            assert 'master.example.com' == get_puppetmaster_host()

    def it_returns_none_when_no_puppetmaster_is_defined():
        newenv = {'roledefs':
            {'puppetmaster': []}
        }
        with patch.dict('fabric.api.env', newenv):
            assert None == get_puppetmaster_host()

    def it_returns_none_when_no_roles_are_defined():
        newenv = {'roledefs':{}}
        with patch.dict('fabric.api.env', newenv):
            assert None == get_puppetmaster_host()


with describe('loom.puppet._gem_install'):
    def it_generates_a_gem_install_command_without_a_version():
        assert 'gem install mygem --no-ri --no-rdoc' == _gem_install('mygem')

    def it_generates_a_gem_install_comamnd_with_a_version():
        assert 'gem install mygem -v 3.2.1 --no-ri --no-rdoc' == _gem_install('mygem', '3.2.1')


with describe('loom.puppet.generate_site_pp'):
    def it_creates_an_include_statement_for_each_role_sorted():
        env.roledefs = {
            'app': 'server.example.com',
            'db': 'server.example.com',
            'zapp': 'server.example.com',
        }
        env.host_string = 'server.example.com'

        expected = 'include "roles::app"\ninclude "roles::db"\ninclude "roles::zapp"\n'
        assert generate_site_pp() == expected



