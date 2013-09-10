Loom 
====
[![Build Status](https://travis-ci.org/bfirsh/loom.png?branch=master)](https://travis-ci.org/bfirsh/loom)

Elegant deployment with [Fabric](http://fabfile.org) and Puppet.

Loom does the stuff Puppet doesn't do well or at all: bootstrapping machines, giving them roles, deploying Puppet code and installing reusable Puppet modules. It's useful for both serverless and master/agent Puppet installations.

It also includes some Fabric tasks for building and uploading app code – something that is particularly complex to do with Puppet.

Install
-------

    $ sudo pip install loom

Getting started
---------------

First of all, you create `fabfile.py` and define your hosts:

    from fabric.api import *
    from loom import puppet
    from loom.tasks import *

    env.user = 'root'
    env.environment = 'prod'
    env.roledefs = {
        'web': ['prod-web-1.example.com', 'prod-web-2.example.com'],
        'db': ['prod-db-1.example.com'],
    }

You can then define any third-party Puppet modules you want in a file called `Puppetfile`:

    forge "http://forge.puppetlabs.com"
    mod "puppetlabs/nodejs"
    mod "puppetlabs/mysql"

(This is for [librarian-puppet](http://librarian-puppet.com/), a tool for installing reusable Puppet modules. It can also install from Git, etc.)

Your own modules are put in a directory called `modules/` in the same directory as `fabfile.py`. Roles are defined in a magic module called `roles` which contains manifests for each role. (If you've used Puppet before, this is a replacement for `node` definitions.)

For example, `modules/roles/manifests/db.pp` defines what the db role is:

    class roles::db {
      include mysql
      # ... etc
    }

And that's it!

Let's set up a database server. First, bootstrap the host (in this example, the single db host you defined in `env.roledefs`):

    $ fab -R db puppet.install

Then install third party Puppet modules, upload your local modules, and apply them:

    $ fab -R db puppet.update puppet.apply

Every time you make a change to your modules, you can run that command to apply them. Because this is just Fabric, you can write a task in `fabfile.py` to do it too:

    @task
    def deploy_puppet():
        execute(puppet.update)
        execute(puppet.apply)

Then you could use the included "all" task to update Puppet on all your hosts:

    $ fab all deploy_puppet

Apps
----

Loom includes a bunch of Fabric tasks for building and uploading code. It assumes you've set up a role for the app (e.g., "web"), and that role has all of the packages you require and an Upstart init script to start the app.

Apps in Loom are configured using `env.apps`. It is a dictionary where the key is the name of the app and the value is a dictionary with these keys:

  - **repo** (required): A Git URL of the repo that contains your app.
  - **role** (required): The role that the app will be uploaded to.
  - **build**: A script to run locally before uploading (e.g. to build static assets or install local dependencies).
  - **post-upload**: A script to run on each server after uploading.
  - **init**: The name of the Upstart script to start/restart after uploading.

You must also define a directory for your apps to live in with `env.app_root`.

For example, suppose this was your `fabfile.py`:

    from fabric.api import *
    from loom import app, puppet
    from loom.tasks import *

    env.user = 'root'
    env.environment = 'prod'
    env.roledefs = {
        'web': ['prod-web-1.example.com', 'prod-web-2.example.com'],
        'db': ['prod-db-1.example.com'],
    }
    env.app_root = '/home/ubuntu'
    env.apps['web'] = {
        "repo": "https://user:pass@github.com/mycompany/mycompany-web.git",
        "role": "web",
        "build": "script/build",
        "init": "web",
    }

You then need a `modules/roles/manifests/web.pp` that sets up `/etc/init/web.conf` to run your app in `/home/ubuntu/web`.

To deploy your app, run:

    $ fab app.deploy:web

This will: 

  1. Pull your GitHub repository locally.
  2. Run `script/build`.
  3. Upload your code to `/home/ubuntu/web` on both `prod-app-1.example.com` and `prod-app-2.example.com`.
  4. Run `sudo restart web`.


OS support
----------

It's only been tested on Ubuntu 12.04. I would like to support more things. Send patches!

API
---

Look at the source for now. It's all Fabric tasks, and they're pretty easy to read. (Sorry.)

Contributors
------------
 * [Ben Firshman](https://fir.sh)
 * [Andreas Jansson](http://andreas.jansson.me.uk/)
 * [Steffen L. Norgren](http://github.com/xironix)
 * [Spencer Herzberg](https://github.com/sherzberg)
