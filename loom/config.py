from fabric.api import env, run, settings, hide

# Default system user
env.user = 'ubuntu'

# Default puppet environment
env.environment = 'prod'

# Default puppet module directory
env.puppet_module_dir = 'modules/'


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


def has_puppet_installed():
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        result = run('which puppet')
    return result.succeeded


