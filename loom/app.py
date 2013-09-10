from fabric.api import *
from fabric.contrib.files import exists
import os
from .tasks import restart
from .utils import upload_dir

__all__ = ['deploy', 'build', 'upload']

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
    execute(build, app, commit)
    execute(upload, app, role=env.apps[app]['role'])

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

@task
@parallel
def upload(app):
    """
    Upload the code for an app and restart its init script
    """
    symlink = os.path.join(env.app_root, app)
    previous = os.path.join(env.app_root, app+'-previous')
    current = os.path.join(env.app_root, app+'-current')

    # Remove previous code
    sudo('rm -rf "%s"' % previous)

    # Move current code to previous
    if exists(current):
        sudo('cp -al "%s" "%s"' % (current, previous))
        sudo('ln -sfn "%s" "%s"' % (previous, symlink))

    # Upload new code
    upload_dir('build/%s/*' % app, current, use_sudo=True)

    # Run post-upload
    if env.apps[app].get('post-upload'):
        with cd(current):
            sudo(env.apps[app].get('post-upload'))

    # Swap!
    sudo('ln -sfn "%s" "%s"' % (current, symlink))

    # Restart with upstart
    if env.apps[app].get('init'):
        restart(env.apps[app]['init'])



