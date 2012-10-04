from fabric.api import *
from fabric.contrib.project import rsync_project
from StringIO import StringIO
from .config import current_role

__all__ = ['update', 'install_master', 'install_agent', 'apply']

env.puppet_conf = """
[main]
logdir=/var/log/puppet
vardir=/var/lib/puppet
ssldir=/var/lib/puppet/ssl
rundir=/var/run/puppet
factpath=$vardir/lib/facter
templatedir=$confdir/templates
prerun_command=/etc/puppet/etckeeper-commit-pre
postrun_command=/etc/puppet/etckeeper-commit-post
modulepath=/etc/puppet/modules:/etc/puppet/vendor

[master]
# These are needed when the puppetmaster is run by passenger
# and can safely be removed if webrick is used.
ssl_client_header = SSL_CLIENT_S_DN 
ssl_client_verify_header = SSL_CLIENT_VERIFY

"""

@task
def update():
    """
    Upload puppet modules and manifests
    """
    # Install local modules
    rsync_project(
        local_dir="modules/",
        remote_dir="/etc/puppet/modules",
        delete=True,
        extra_opts='--rsync-path="sudo rsync" --exclude=".git*" --copy-links',
        ssh_opts='-oStrictHostKeyChecking=no'
    )

    # Install vendor modules
    put('Puppetfile', '/etc/puppet/Puppetfile', use_sudo=True)
    with cd('/etc/puppet'):
        sudo('librarian-puppet install --path /etc/puppet/vendor --verbose')

    put(StringIO('include "roles::$role"\n'), '/etc/puppet/manifests/site.pp', use_sudo=True)
    

@task
def install_master():
    """
    Install puppetmaster, update its modules and install agent.
    """
    # librarian-puppet depends on git
    with settings(hide('stdout'), show('running')):
        sudo('apt-get update')
    sudo('apt-get -y install puppetmaster rubygems git')
    # TODO: this installs a later version of puppet than the system version
    # which might cause trouble.
    sudo('gem install librarian-puppet --no-ri --no-rdoc')
    put(StringIO(env.puppet_conf), '/etc/puppet/puppet.conf', use_sudo=True)
    execute(update)
    execute(install_agent)

@task
def install_agent():
    """
    Install the puppet agent.
    """
    with settings(hide('stdout'), show('running')):
        sudo('apt-get update')
    sudo('apt-get -y install puppet')
    defaults = """
START=yes
DAEMON_OPTS="--server %(server)s --environment %(environment)s"
export FACTER_role="%(role)s"
""" % {
        'server': env.get('puppetmaster_host', env.roledefs['puppetmaster'][0]),
        'environment': env.environment,
        'role': current_role(),
    }
    put(StringIO(env.puppet_conf), '/etc/puppet/puppet.conf', use_sudo=True)
    put(StringIO(defaults), '/etc/default/puppet', use_sudo=True)
    sudo('/etc/init.d/puppet restart')

@task
def apply():
    """
    Apply puppet locally
    """
    sudo('HOME=/root FACTER_role=%s puppet apply --modulepath=/etc/puppet/vendor:/etc/puppet/modules /etc/puppet/manifests/site.pp' % current_role())




