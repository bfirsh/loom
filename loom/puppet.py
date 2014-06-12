from fabric.api import env, abort, put, cd, sudo, task, execute, settings
from fabric.contrib.files import upload_template
from StringIO import StringIO
import os
from .config import current_roles, has_puppet_installed, has_librarian_installed
from .decorators import requires_puppet
from .tasks import restart
from .utils import upload_dir

__all__ = ['update', 'update_configs', 'install', 'install_master', 'install_agent', 'apply', 'force']

files_path = os.path.join(os.path.dirname(__file__), 'files')


def get_puppetmaster_host():
    if env.get('puppetmaster_host'):
        return env['puppetmaster_host']
    if 'puppetmaster' in env.roledefs and env.roledefs['puppetmaster']:
        return env.roledefs['puppetmaster'][0]


def generate_site_pp():
    site = ''.join('include "roles::%s"\n' % role for role in sorted(current_roles()))
    return site


@task
@requires_puppet
def update():
    """
    Upload puppet modules
    """
    if not current_roles():
        abort('Host "%s" has no roles. Does it exist in this environment?' % env.host_string)

    # Install local modules
    module_dir = env.get('puppet_module_dir', 'modules/')
    if not module_dir.endswith('/'): module_dir+='/'
    upload_dir(module_dir, '/etc/puppet/modules', use_sudo=True)

    # Install vendor modules
    put('Puppetfile', '/etc/puppet/Puppetfile', use_sudo=True)
    with cd('/etc/puppet'):
        sudo('librarian-puppet install --path /etc/puppet/vendor')

    # Install site.pp
    sudo('mkdir -p /etc/puppet/manifests')
    put(StringIO(generate_site_pp()), '/etc/puppet/manifests/site.pp', use_sudo=True)


@task
def update_configs():
    """
    Upload puppet configs and manifests
    """
    sudo('mkdir -p /etc/puppet')
    # Allow the puppet master to automatically sign certificates
    if env.get('loom_puppet_autosign'):
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
    put(os.path.join(files_path, 'puppet/hiera.yaml'), '/etc/puppet/hiera.yaml', use_sudo=True)


def _gem_install(gem, version=None):
    version = '-v {version}'.format(version=version) if version else ''
    return ' '.join('gem install {gem} {version} --no-ri --no-rdoc'.format(gem=gem, version=version).split())

@task
def install():
    """
    Install Puppet and its configs without any agent or master.
    """
    sudo('apt-get update -qq')
    with settings(warn_only=True):
        sudo('apt-get -y -q install rubygems')
    sudo('apt-get -y -q install ruby ruby-dev git')

    puppet_version = env.get('loom_puppet_version')
    sudo(_gem_install('puppet', version=puppet_version))

    librarian_version = env.get('loom_librarian_version')
    sudo(_gem_install('librarian-puppet', version=librarian_version))

    # http://docs.puppetlabs.com/guides/installation.html
    sudo('puppet resource group puppet ensure=present')
    sudo("puppet resource user puppet ensure=present gid=puppet shell='/sbin/nologin'")
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
@requires_puppet
def apply():
    """
    Apply puppet locally
    """

    sudo('HOME=/root puppet apply /etc/puppet/manifests/site.pp')


@task
@requires_puppet
def force():
    """
    Force puppet agent run
    """

    sudo('HOME=/root puppet agent --onetime --no-daemonize --verbose --waitforcert 5')
