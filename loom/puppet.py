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
    if env.get('puppetmaster_host'):
        return env['puppetmaster_host']
    if 'puppetmaster' in env.roledefs and env.roledefs['puppetmaster']:
        return env.roledefs['puppetmaster'][0]

@task
def update():
    """
    Upload puppet modules
    """
    # Install local modules, manifests, and hieradata, if any.
    # Also making the assumption that modules will always exist.
    if path.exists('modules') and path.exists('manifests') and path.exists('hieradata'):
        upload_dir('modules manifests hieradata', '/etc/puppet', use_sudo=True)
    elif path.exists('modules') and path.exists('manifests'):
        upload_dir('modules manifests', '/etc/puppet', use_sudo=True)
    elif path.exists('modules') and path.exists('hieradata'):
        upload_dir('modules hieradata', '/etc/puppet', use_sudo=True)

    # Upload custom hiera.yaml if it exists
    if path.exists('hiera.yaml') and path.isfile('hiera.yaml'):
        put('hiera.yaml', '/etc/puppet/hiera.yaml', use_sudo=True)

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

    # Allow the puppet master to automatically sign certificates
    if env.get('loom_puppet_autosign'):
        put(StringIO('*'), '/etc/puppet/autosign.conf', use_sudo=True)
    else:
        put(StringIO(''), '/etc/puppet/autosign.conf', use_sudo=True)

    # If site.pp doesn't exist, create a basic one
    if not path.exists('manifests/site.pp') and not path.isfile('manifests/site.pp'):
        sudo('mkdir -p /etc/puppet/manifests')
        put(StringIO('include "roles::$role"\n'), '/etc/puppet/manifests/site.pp', use_sudo=True)

    # Upload Puppet configs
    upload_template(path.join(files_path, 'puppet/puppet.conf'), '/etc/puppet/puppet.conf', {
        'server': get_puppetmaster_host() or '',
        'certname': get_puppetmaster_host() or '',
        'dns_alt_names': get_puppetmaster_host() or '',
        'environment': env.environment,
    }, use_sudo=True)
    put(path.join(files_path, 'puppet/auth.conf'), '/etc/puppet/auth.conf', use_sudo=True)

    # Upload default heira.yaml if one doesn't exist.
    if not path.isfile('hiera.yaml'):
        put(path.join(files_path, 'puppet/hiera.yaml'), '/etc/puppet/hiera.yaml', use_sudo=True)

@task
def install():
    """
    Install Puppet and its configs without any agent or master.
    """
    with settings(hide('stdout'), show('running')):
        sudo('apt-get update')
    sudo('apt-get -y install rubygems git')

    # Allow specific versions
    if env.get('loom_puppet_version'):
        puppet_vercmd = '-v ' + env.get('loom_puppet_version')
    else:
        puppet_vercmd = ''
    if env.get('loom_librarian_version'):
        librarian_vercmd = '-v ' + env.get('loom_librarian_version')
    else:
        librarian_vercmd = ''

    sudo('gem install puppet ' + puppet_vercmd + ' --no-ri --no-rdoc')
    sudo('gem install librarian-puppet ' + librarian_vercmd + ' --no-ri --no-rdoc')
    # http://docs.puppetlabs.com/guides/installation.html
    # TODO: For some reason this fails on the first pass...
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
    put(path.join(files_path, 'init/puppetmaster.conf'), '/etc/init/puppetmaster.conf', use_sudo=True)
    service('puppetmaster', 'restart')

@task
def install_agent():
    """
    Install the puppet agent.
    """
    execute(install)
    put(path.join(files_path, 'init/puppet.conf'), '/etc/init/puppet.conf', use_sudo=True)
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

