from fabric.api import *
import subprocess

from .config import host_role, current_role

__all__ = ['ssh', 'all', 'uptime', 'upgrade', 'restart']

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
    run('uptime')

@task
def upgrade():
    """
    Upgrade apt packages
    """
    with settings(hide('stdout'), show('running')):
        sudo('apt-get update')
    sudo("apt-get upgrade -y")

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
def restart(service):
    """
    Restart or start an upstart service
    """
    with settings(warn_only=True):
        result = sudo('restart %s' % service)
    if result.failed:
        sudo('start %s' % service)

