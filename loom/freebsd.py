from fabric.api import *
from fabric.contrib import files

# This class contains specific tasks that relate to FreeBSD.

def upgrade():
    sudo('portsnap fetch')
    with settings(hide('stdout'), show('running')):
        result = sudo('portsnap update')
        if result.failed:
            sudo('portsnap extract')

def service(name, command):
    if files.exists('/etc/rc.d/' % name):
        with settings(warn_only=True):
            result = sudo('/etc/rc.d/' % (name, command))
    elif files.exists('/usr/local/etc/rc.d/' % name):
            with settings(warn_only=True):
                result = sudo('/usr/local/etc/rc.d/' % (name, command))
    else:
        puts('Service %s not found.' % name)

    if result.failed:
        puts('Service %s failed to %s.' % (name, command))
