from fabric.api import env, put, task
import json
from StringIO import StringIO

# Default system user
env.user = 'ubuntu'

# Default puppet environment
env.environment = 'prod'

def host_roles(host_string):
    """
    Returns the role of a given host string.
    """
    roles = []
    for role, hosts in env.roledefs.items():
        if host_string in hosts and role not in roles:
            roles.append(role)
    return roles

def current_roles():
    return host_roles(env.host_string)


