from fabric.api import *
from fabric.network import parse_host_string
import subprocess

__all__ = ['ssh', 'all', 'uptime', 'upgrade', 'restart', 'reboot']

@task
def all():
    """
    Select all hosts
    """
    host_set = set()
    for hosts in env.roledefs.values():
        host_set.update(hosts)
    # remove dupes
    env.hosts = list(host_set)

@task
def uptime():
    run('uptime')

@task
def upgrade(non_interactive=False):
    """
    Upgrade apt packages
    """
    with settings(hide('stdout'), show('running')):
        sudo('apt-get update')
    upgrade_command = ['apt-get', 'upgrade']
    if non_interactive:
        upgrade_command.append('-y')
    sudo(' '.join(upgrade_command))

@task
def ssh(*cmd):
    """
    Open an interactive ssh session
    """
    run = ['ssh', '-A', '-t']
    if env.key_filename:
        run.extend(["-i", env.key_filename])
    parsed = parse_host_string(env.host_string)
    if parsed['port']:
        run.extend(['-p', parsed['port']])
    user = parsed['user'] if parsed['user'] else env.user
    run.append('%s@%s' % (parsed['user'] if parsed['user'] else env.user, parsed['host']))
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

@task
def reboot():
    """
    Reboot a host
    """
    sudo('reboot')


