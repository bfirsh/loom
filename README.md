Loom
====

Elegant deployment with Fabric and Puppet.

Loom fills the gaps that Puppet doesn't fill: bootstrapping machines, giving them roles, deploying Puppet code and installing third party Puppet modules. It's useful for both serverless and master/agent Puppet installations.

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
        'app': ['prod-app-1.example.com', 'prod-app-2.example.com'],
        'db': ['prod-db-1.example.com'],
    }

You can then define any third-party Puppet modules you want in a file called `Puppetfile`:

    forge "http://forge.puppetlabs.com"
    mod "puppetlabs/nodejs"
    mod "puppetlabs/mysql"

Local modules are put in a directory called `modules/` in the same directory as `fabfile.py`. Roles are defined in a magic module called `roles`, which contains manifests for each role. For example, `modules/roles/manifests/db.pp`:

    class roles::db {
      include mysql
      # ... etc
    }

And that's it!

Let's set up a database server. First, bootstrap a host (in this example, the single host you defined in `env.roledefs`):

    $ fab -R db puppet.install

Then you can install third party Puppet modules, upload your local modules, and apply them:

    $ fab -R db puppet.update puppet.apply

Every time you make a change to your modules, you can run that command to apply them. Because this is just Fabric, you can write a task in `fabfile.py` to that too:

    @task
    def deploy_puppet():
        execute(puppet.update)
        execute(puppet.apply)

OS support
----------

It's only been tested on Ubuntu 12.04. I would like to support more things. Send patches!

API
---

Look at the source for now. It's all Fabric tasks, and they're pretty easy to read. (Sorry.)


