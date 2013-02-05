from pspec import describe
from attest import assert_hook
from fabric.api import env
from loom.puppet import generate_site_pp

with describe('generate_site_pp'):
    def it_creates_an_include_statement_for_each_role():
        env.roledefs = {
            'app': 'server.example.com',
            'db': 'server.example.com',
        }
        env.host_string = 'server.example.com'
        site_pp = generate_site_pp()
        assert 'include "roles::app"' in site_pp
        assert 'include "roles::db"' in site_pp


