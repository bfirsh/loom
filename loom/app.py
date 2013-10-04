import datetime
from fabric.api import *
from fabric.contrib.files import exists
import os
from .tasks import restart
from .utils import upload_dir

__all__ = ['deploy', 'build', 'upload', 'versions', 'update_version']

# The definition of your apps as a dictionary. This can have four keys:
#
# - repo (required): A Git URL of the repo that contains your app
# - role (required): The role of the hosts that this app will be uploaded to
# - build: A script to run locally before uploading (e.g. to build static assets)
# - init: The name of the upstart script to start/restart after uploading
#
# Example:
#
# env.app_root = "/apps"
# env.apps['api'] = {
#   "repo": "https://user:pass@github.com/mycompany/mycompany-api.git",
#   "role": "api",
#   "build": "script/build",
#   "init": "api",
# }
env.apps = {}

# The directory that contains your apps
env.app_root = '/home/ubuntu'

@task
def deploy(app, commit='origin/master'):
    """
    Build and upload an app.
    """
    kwargs = {}
    # If no hosts have been set by the user, default to this app's role
    if not env.hosts:
        kwargs['role'] = env.apps[app]['role']

    execute(build, app, commit)
    version = datetime.datetime.now().replace(microsecond=0).isoformat().replace(':', '-')
    execute(upload, app, version, **kwargs) 
    execute(update_version, app, version, **kwargs)

@task
@runs_once
def build(app, commit='origin/master'):
    """
    Build the code for an app locally
    """
    # Set up build directory
    if not os.path.exists('build'):
        local('mkdir build')
    path = 'build/%s' % app

    # Fetch or clone repo
    if os.path.exists(path):
        with lcd(path):
            local('git fetch')
    else:
        local('git clone "%s" "build/%s"' % (env.apps[app]['repo'], app))
    with lcd(path):
        local('git checkout %s' % commit)

    # Run build command (e.g., "script/build")
    if env.apps[app].get('build'):
        with lcd(path):
            local(env.apps[app]['build'])

def _versions(app):
    return sudo('ls "%s"' % os.path.join(env.app_root, app+'-versions')).split()

def _current_version_path(app):
    return sudo('readlink "%s"' % os.path.join(env.app_root, app))

@task
def versions(app):
    """
    Print the versions of an app that are available
    """
    print '\n'.join(_versions(app))

@task
def update_version(app, version):
    """
    Switch the symlink for an app to point at a new version and restart its init script
    """
    symlink = os.path.join(env.app_root, app)
    version_path = os.path.join(env.app_root, app+'-versions', version)
    sudo('ln -sfn "%s" "%s"' % (version_path, symlink))

    # Restart with upstart
    if env.apps[app].get('init'):
        restart(env.apps[app]['init'])

@task
@parallel
def upload(app, version):
    """
    Upload the code for a version
    """
    all_versions_path = os.path.join(env.app_root, app+'-versions')
    current_version_path = _current_version_path(app)
    version_path = os.path.join(all_versions_path, version)

    if not exists(all_versions_path):
        sudo('mkdir "%s"' % all_versions_path)

    # Copy existing code if it exists
    if exists(os.path.join(env.app_root, app)):
        sudo('cp -a "%s" "%s"' % (current_version_path, version_path))

    # Upload new code
    upload_dir('build/%s/*' % app, version_path, use_sudo=True)

    # Run post-upload
    if env.apps[app].get('post-upload'):
        with cd(version_path):
            sudo(env.apps[app].get('post-upload'))



