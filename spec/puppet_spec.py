from pspec import describe
from attest import assert_hook
from fabric.api import env
from loom.puppet import generate_site_pp, get_puppetmaster_host
from mock import patch


with describe('get_puppetmaster_host'):
    def it_get_puppetmaster_from_env_single_host():
        newenv = {'puppetmaster_host': 'master.example.com'}
        with patch.dict('fabric.api.env', newenv):
            assert 'master.example.com' == get_puppetmaster_host()

with describe('get_puppetmaster_host'):
    def it_get_puppetmaster_from_roledefs_single_host():
        newenv = {'roledefs':
            {'puppetmaster': ['master.example.com']}
        }
        with patch.dict('fabric.api.env', newenv):
            assert 'master.example.com' == get_puppetmaster_host()

with describe('get_puppetmaster_host'):
    def it_get_puppetmaster_from_roledefs_multiple_hosts():
        newenv = {'roledefs':
            {'puppetmaster': ['master.example.com', 'master2.example.com']}
        }
        with patch.dict('fabric.api.env', newenv):
            assert 'master.example.com' == get_puppetmaster_host()

with describe('get_puppetmaster_host'):
    def it_get_puppetmaster_no_hosts():
        newenv = {'roledefs':
            {'puppetmaster': []}
        }
        with patch.dict('fabric.api.env', newenv):
            assert None == get_puppetmaster_host()

with describe('get_puppetmaster_host'):
    def it_get_puppetmaster_undefined():
        newenv = {'roledefs':{}}
        with patch.dict('fabric.api.env', newenv):
            assert None == get_puppetmaster_host()
