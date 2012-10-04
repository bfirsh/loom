from fabric.api import *
from fabric.contrib.project import rsync_project

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



