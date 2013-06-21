from fabric.api import abort, env
from functools import wraps
from .config import has_puppet_installed, has_librarian_installed


def requires_puppet(func):

    @wraps(func)
    def _requires_puppet(*args, **kwargs):
        if not has_puppet_installed():
            abort('Host "%s" does not have puppet installed. Try "fab puppet.install".' % env.host_string)
        if not has_librarian_installed():
            abort('Host "%s" does not have librarian-puppet installed. Try "fab puppet.install".' % env.host_string)
        func(*args, **kwargs)

    return _requires_puppet
