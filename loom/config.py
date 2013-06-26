from fabric.api import env, run, settings, hide

# Default system user
env.user = 'ubuntu'

# Default puppet environment
env.environment = 'prod'

# Default puppet module directory
env.puppet_module_dir = 'modules/'

# Default puppet version
# If loom_puppet_version is None, loom installs the latest version
env.loom_puppet_version = '3.1.1'

# Default librarian version
# If loom_librarian_version is None, loom installs the latest version
env.loom_librarian_version = '0.9.9'


def host_roles(host_string):
    """
    Returns the role of a given host string.
    """
    roles = set()
    for role, hosts in env.roledefs.items():
        if host_string in hosts:
            roles.add(role)
    return list(roles)


def current_roles():
    return host_roles(env.host_string)


def has_puppet_installed():
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        result = run('which puppet')
    return result.succeeded


def has_librarian_installed():
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        librarian = run('which librarian-puppet')
    return librarian.succeeded
