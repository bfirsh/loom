from fabric.api import abort, env
from functools import wraps
from .config import has_puppet_installed, has_librarian_installed


REQUIRES_GEM = 'Host "{host}" does not have {gem} installed. Try "fab puppet.install".'


def requires_puppet(func):

    @wraps(func)
    def _requires_puppet(*args, **kwargs):
        if not has_puppet_installed():
            abort(REQUIRES_GEM.format(host=env.host_string, gem='puppet'))
        if not has_librarian_installed():
            abort(REQUIRES_GEM.format(host=env.host_string, gem='librarian-puppet'))
        func(*args, **kwargs)

    return _requires_puppet
