from fabric.api import *

# This class contains specific tasks that relate to Ubuntu.

def upgrade():
    with settings(hide('stdout'), show('running')):
        sudo('apt-get update')
    sudo("apt-get upgrade -y")

def service(name, command):
    with settings(warn_only=True):
        result = sudo('service %s %s' % (name, command))
    if result.failed:
        puts('Service %s failed to %s.' % (name, command))

