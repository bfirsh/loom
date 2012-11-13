from fabric.api import *
from .utils import detect_os
import ubuntu, freebsd
import subprocess

from .config import host_role, current_role

# This class contains tasks that are common to all
# operating systems.

__all__ = ['ssh', 'all', 'uptime', 'upgrade', 'service']

@task
def all():
    """
    Select all hosts
    """
    env.hosts = []
    for hosts in env.roledefs.values():
        env.hosts.extend(hosts)
    # remove dupes
    env.hosts = list(set(env.hosts))

@task
def uptime():
    """
    Display the uptime of a given host
    """
    run('uptime')

@task
def ssh(*cmd):
    """
    Open an interactive ssh session
    """
    run = ['ssh', '-A', '-t']
    if env.key_filename:
        run.extend(["-i", env.key_filename])
    run.append('%s@%s' % (env.user, env.host_string))
    run += cmd
    subprocess.call(run)

@task
def upgrade():
    """
    Update & upgrade installed packages.
    """
    osname = detect_os()
    if osname in 'Ubuntu':
        ubuntu.upgrade()
    elif osname in 'FreeBSD':
        freebsd.upgrade()

@task
def service(name, command):
    """
    start, stop, or restart a service
    """
    osname = detect_os()
    if osname in 'Ubuntu':
        ubuntu.service(name, command)
    elif osname in 'FreeBSD':
        freebsd.service(name, command)
