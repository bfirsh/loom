from fabric.api import *
from fabric.contrib.project import rsync_project

DETECTION_ERROR_MESSAGE = """
OS detection failed. This probably means your OS is not
currently supported by loom.

Currently supported operating systems:
    Ubuntu
    FreeBSD

If you believe the OS is supported, but detection fails
or you want to get your OS supported, please file an
issue at: https://github.com/bfirsh/loom/issues/new
"""

def upload_dir(src, dest, use_sudo=False):
    """
    Fabric's rsync_project with some sane settings
    """
    extra_opts = ['--exclude=".git*"', '--copy-links']
    if use_sudo:
        extra_opts.append('--rsync-path="sudo rsync"')
    rsync_project(
        local_dir=src,
        remote_dir=dest,
        delete=True,
        extra_opts=' '.join(extra_opts),
        ssh_opts='-oStrictHostKeyChecking=no'
    )

def detect_os():
    """
    Determine the node's operating system
    """

    # Determine system type
    with settings(hide('stdout'), show('running')):
        system = run('python -c "import platform; print platform.system()"')

    if not system in ['Linux', 'FreeBSD']:
        abort(DETECTION_ERROR_MESSAGE)
    elif system is 'FreeBSD':
        return system
    else:
        with settings(hide('stdout'), show('running')):
            distro = run('python -c "import platform; print platform.linux_distribution()"')
        if eval(distro)[0] in 'Ubuntu':
            return eval(distro)[0]
        else:
            abort(DETECTION_ERROR_MESSAGE)

