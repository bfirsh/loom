from fabric.api import env, put, task
import json
from StringIO import StringIO

# Default system user
env.user = 'ubuntu'

# Default puppet environment
env.environment = 'prod'

def host_role(host_string):
    """
    Returns the role of a given host string.
    """
    for role, hosts in env.roledefs.items():
        if host_string in hosts:
            return role

def current_role():
    return host_role(env.host_string)


