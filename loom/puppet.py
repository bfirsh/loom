from fabric.api import *
from fabric.contrib.files import upload_template
from StringIO import StringIO
import os
from .config import current_role
from .tasks import restart
from .utils import upload_dir

__all__ = ['update', 'install', 'install_master', 'install_agent', 'apply', 'force']

files_path = os.path.join(os.path.dirname(__file__), 'files')

def get_puppetmaster_host():
    if env.get('puppetmaster_host'):
        return env['puppetmaster_host']
    if 'puppetmaster' in env.roledefs and env.roledefs['puppetmaster']:
        return env.roledefs['puppetmaster'][0]

@task
def update():
    """
    Upload puppet modules
    """
    # Install local modules
    upload_dir('modules/', '/etc/puppet/modules', use_sudo=True)

    # Install vendor modules
    put('Puppetfile', '/etc/puppet/Puppetfile', use_sudo=True)
    with cd('/etc/puppet'):
        sudo('librarian-puppet install --path /etc/puppet/vendor')

@task
def update_configs():
    """
    Upload puppet configs and manifests
    """
    # Set role
    # TODO: this should be done with facts.d, but it was a pain in the arse to get it 
    # working
    put(StringIO(current_role()), '/etc/puppet/role', use_sudo=True)

    # Upload Puppet configs
    upload_template(os.path.join(files_path, 'puppet/puppet.conf'), '/etc/puppet/puppet.conf', {
        'server': get_puppetmaster_host() or '',
        'environment': env.environment,
    }, use_sudo=True)
    put(os.path.join(files_path, 'puppet/auth.conf'), '/etc/puppet/auth.conf', use_sudo=True)

    # Install manifest
    sudo('mkdir -p /etc/puppet/manifests')
    put(StringIO('include "roles::$role"\n'), '/etc/puppet/manifests/site.pp', use_sudo=True)


@task
def install():
    """
    Install Puppet and its configs without any agent or master.
    """
    with settings(hide('stdout'), show('running')):
        sudo('apt-get update')
    sudo('apt-get -y install rubygems git')
    # librarian-puppet does not yet support 3.0.0
    # https://github.com/rodjek/librarian-puppet/pull/37
    sudo('gem install puppet -v 2.7.19 --no-ri --no-rdoc')
    sudo('gem install librarian-puppet -v 0.9.6 --no-ri --no-rdoc')
    # http://docs.puppetlabs.com/guides/installation.html
    sudo('puppet resource group puppet ensure=present')
    sudo("puppet resource user puppet ensure=present gid=puppet shell='/sbin/nologin'")
    sudo('mkdir -p /etc/puppet')
    execute(update_configs)

@task
def install_master():
    """
    Install puppetmaster, update its modules and install agent.
    """
    execute(install_agent)
    execute(update)
    put(os.path.join(files_path, 'init/puppetmaster.conf'), '/etc/init/puppetmaster.conf', use_sudo=True)
    restart('puppetmaster')

@task
def install_agent():
    """
    Install the puppet agent.
    """
    execute(install)
    put(os.path.join(files_path, 'init/puppet.conf'), '/etc/init/puppet.conf', use_sudo=True)
    restart('puppet')

@task
def apply():
    """
    Apply puppet locally
    """
    sudo('HOME=/root FACTER_role=%s puppet apply /etc/puppet/manifests/site.pp' % current_role())

@task
def force():
    """
    Force puppet agent run
    """
    sudo('HOME=/root FACTER_role=%s puppet agent --onetime --no-daemonize --verbose --waitforcert 5' % current_role())



