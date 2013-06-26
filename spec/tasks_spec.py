from fabric.api import env
from pspec import describe
from loom.tasks import all


with describe('loom.tasks.all'):

    def it_get_all_hosts():

        env.roledefs = {
            'app1': ['app1.com', 'app2.com'],
            'app2': ['app1.com', 'app2.com'],
            'db': ['db.com']
        }

        all()

        assert set(['app1.com', 'app2.com', 'db.com']) == set(env.hosts)
