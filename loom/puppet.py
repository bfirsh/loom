from fabric.api import *
from fabric.contrib.files import upload_template
from StringIO import StringIO
from os import path
from .config import current_role
from .utils import upload_dir
import ubuntu, freebsd

__all__ = ['update', 'update_configs', 'install', 'install_master', 'install_agent', 'apply', 'force']

files_path = path.join(path.dirname(__file__), 'files')

def get_puppetmaster_host():
    if env.loom.puppet.master.get('host'):
        return env.loom.puppet.master['host']
    if 'puppetmaster' in env.loom.roledefs and env.loom.roledefs['puppetmaster']:
        return env.loom.roledefs['puppetmaster'][0]

@task
def update():
    """
    Upload puppet modules
    """
    # Install local modules and manifests
    upload_dir('modules manifests', '/etc/puppet', use_sudo=True)

    # Install vendor modules
    put('Puppetfile', '/etc/puppet/Puppetfile', use_sudo=True)
    with cd('/etc/puppet'):
        sudo('librarian-puppet install --path /etc/puppet/vendor')

    # If site.pp doesn't exist, create a basic one
    if not path.exists('manifests/site.pp') and path.isfile('manifests/site.pp'):
        sudo('mkdir -p /etc/puppet/manifests')
        put(StringIO('include "roles::$role"\n'), '/etc/puppet/manifests/site.pp', use_sudo=True)

@task
def update_configs():
    """
    Upload puppet configs and manifests
    """
    # Set role
    # TODO: this should be done with facts.d, but it was a pain in the arse to get it 
    # working
    put(StringIO(current_role()), '/etc/puppet/role', use_sudo=True)

    # Allow the puppet master to automatically sign certificates
    if env.loom.puppet.get('autosign'):
        put(StringIO('*'), '/etc/puppet/autosign.conf', use_sudo=True)
    else:
        put(StringIO(''), '/etc/puppet/autosign.conf', use_sudo=True)

    # Upload Puppet configs
    upload_template(os.path.join(files_path, 'puppet/puppet.conf'), '/etc/puppet/puppet.conf', {
        'server': get_puppetmaster_host() or '',
        'certname': get_puppetmaster_host() or '',
        'dns_alt_names': get_puppetmaster_host() or '',
        'environment': env.environment,
    }, use_sudo=True)
    put(os.path.join(files_path, 'puppet/auth.conf'), '/etc/puppet/auth.conf', use_sudo=True)

@task
def install():
    """
    Install Puppet and its configs without any agent or master.
    """
    with settings(hide('stdout'), show('running')):
        sudo('apt-get update')
    sudo('apt-get -y install rubygems git')

    # Allow specific versions
    if env.loom.puppet.get('version'):
        puppet_vercmd = '-v ' + env.loom.puppet.get('version')
    else:
        puppet_verion = None
    if env.loom.librarian.get('version'):
        librarian_vercmd = '-v ' + env.loom.librarian.get('version')
    else:
        librarian_version = None

    sudo('gem install puppet ' + puppet_vercmd + ' --no-ri --no-rdoc')
    sudo('gem install librarian-puppet ' + librarian_vercmd + ' --no-ri --no-rdoc')
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
    service('puppetmaster', 'restart')

@task
def install_agent():
    """
    Install the puppet agent.
    """
    execute(install)
    put(os.path.join(files_path, 'init/puppet.conf'), '/etc/init/puppet.conf', use_sudo=True)
    service('puppet', 'restart')

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

