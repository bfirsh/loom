from pspec import describe
from attest import assert_hook
from fabric.api import env
from loom.puppet import generate_site_pp, get_puppetmaster_host
from mock import patch


with describe('generate_site_pp'):
    def it_creates_an_include_statement_for_each_role():
        env.roledefs = {
            'app': 'server.example.com',
            'db': 'server.example.com',
        }
        env.host_string = 'server.example.com'
        site_pp = generate_site_pp()

        expected = []
        expected.append('include "roles::app"\n')
        expected.append('include "roles::db"\n')

        assert ''.join(expected) == site_pp
