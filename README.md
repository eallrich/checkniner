checkniner
==========

[![Build Status](https://travis-ci.org/eallrich/checkniner.png)](https://travis-ci.org/eallrich/checkniner)

Tracking and reporting of airstrip/aircraft checkout information for pilots.

Installing
----------

Overview:
+ Clone the repository
+ Configure the environment
+ Install the dependencies
+ Set up the database
+ Run it!

```shell
$ git clone https://github.com/eallrich/checkniner.git
$ cd checkniner
$ virtualenv .
```

The following environment variables are always required:
+ DATABASE_URL (e.g. postgres://user:pass@host:port/database)
+ DJANGO_SETTINGS_MODULE (e.g. cotracker.settings.production)
+ PYTHONPATH (e.g. /home/user/checkniner/cotracker/)
+ SECRET_KEY (e.g. 0123456789ABCDEF)
+ SENTRY_DSN (e.g. https://access:key@example.com/2)

These can be set in checkniner/bin/activate to ensure that they will always be available
when running in the virtualenv.

```shell
$ echo "export DATABASE_URL=sqlite:////home/user/checkniner/cotracker/dev.db" >> bin/activate
$ echo "export DJANGO_SETTINGS_MODULE=cotracker.settings.development" >> bin/activate
$ echo "export PYTHONPATH=/home/user/checkniner/cotracker/" >> bin/activate
$ echo "export SECRET_KEY=0123456789ABCDEF" >> bin/activate
$ echo "export SENTRY_DSN=https://access:key@example.com/2" >> bin/activate
```

When running in a production configuration (i.e. DEBUG is False), the following env vars are also required:
+ ALLOWED_HOST (e.g. example.com)

Optional environment variables:
+ FORCE_DEBUG_MODE (e.g. true) -- Override the DEBUG flag when using settings.production
+ INTERNAL_IPS (e.g. 10.31.41.59) -- Required to view django-debug-toolbar; DEBUG must be True
    - A comma-separated list is acceptable: 10.31.41.59,10.27.182.8
+ SERVE_STATIC (e.g. true) -- Enables the URLconf to route static asset requests
    - This option is not recommended for use in production, but it will work if configured to do so

Once the env vars are configured, activate the virtualenv and install the dependencies:

```shell
$ source bin/activate
$ pip install -r requirements/development.txt
```

Database setup will involve syncing and then running a schema migration:

```shell
$ python cotracker/manage.py syncdb
$ python cotracker/manage.py migrate
```

If foreman is installed, you should be able to run the project:

```shell
$ foreman start
```

Testing
-------

First make sure the dependencies are met:

```shell
$ cd checkniner
$ source bin/activate
$ pip install -r requirements/development.txt
```

Then run the tests via coverage:

```shell
$ coverage run cotracker/manage.py test --settings=cotracker.settings.test
```

A visual coverage report is available:

```shell
$ coverage html --include="./cotracker/*"
```

Production
----------

These steps walk through a single-node deployment on Ubuntu 12.04 using:
+ PostgreSQL as a backing data store
+ Gunicorn as an application server
+ Supervisor as a process formation controller
+ Nginx as a reverse proxy

### Quick start using scripts ###

If you're already connected to the target server:
```shell
$ sudo apt-get update && sudo apt-get dist-upgrade
# Postgres installation will fail if locales are not set correctly, so set them
$ sudo apt-get install git language-pack-en
$ git clone https://github.com/eallrich/checkniner.git
# Call fresh.sh with the ALLOWED_HOST value and the SENTRY_DSN
$ ~/checkniner/tools/fresh.sh example.com https://access:key@example.com/2
```

If you want to set up the app on a different server:
```shell
# Assuming you already have a copy of the repository locally
# Call bootstrap.sh with the SSH connection string of the target server, the
# ALLOWED_HOST value, and the SENTRY_DSN
$ checkniner/tools/bootstrap.sh user@example.com example.com https://access:key@example.com/2
```

### Assumptions ###

+ The domain name for the site is example.com
+ The user is 'ubuntu' with HOME at /home/ubuntu/
+ The following commands, or equivalents, have already been run:

```shell
$ sudo apt-get update && sudo apt-get dist-upgrade
$ sudo apt-get install language-pack-en
```

### Dependencies ###

Assuming a clean and fully-upgraded host, begin by installing APT packages:

```shell
$ sudo apt-get install git python-virtualenv python-dev postgresql libpq-dev nginx supervisor
```

Grab a copy of the repository and set up the virtualenv:

```shell
$ cd ~
$ git clone https://github.com/eallrich/checkniner.git
$ cd checkniner
$ virtualenv .
$ source bin/activate
```

Install the necessary python packages:

```shell
$ pip install -r requirements.txt
```

### Postgres ###

Create a database and a user for accessing it:

```shell
$ sudo su - postgres
$ psql
=> CREATE DATABASE checkniner;
=> CREATE USER ubuntu;
=> GRANT ALL PRIVILEGES ON DATABASE checkniner TO ubuntu;
=> \q
$ exit
```

A couple of items to note in this configuration:
+ Because we're using peer authentication, we don't need a password or a hostname
+ This will work as long as django is running on the same host as the database

### Environment Variables ###

When running Django's administrative commands, a few env vars will be required.
I think it's easiest to save these to the virtualenv's activation script so
that they're always defined when we need them:

```shell
$ echo "export ALLOWED_HOST=example.com" >> bin/activate
$ echo "export DATABASE_URL=postgres://ubuntu@/checkniner" >> bin/activate
$ echo "export DJANGO_SETTINGS_MODULE=cotracker.settings.production" >> bin/activate
$ echo "export PYTHONPATH=/home/ubuntu/checkniner/cotracker/" >> bin/activate
$ echo "export SECRET_KEY=0123456789ABCDEF" >> bin/activate
$ echo "export SENTRY_DSN=https://access:key@example.com/2" >> bin/activate
```

Reactivate the virtualenv and have Django do some preparation work:

```shell
$ deactivate
$ source bin/activate
$ python cotracker/manage.py syncdb
$ python cotracker/manage.py migrate
$ python cotracker/manage.py collectstatic --noinput
```

### Supervisor ###

Give Supervisor a config file to help it manage our gunicorn processes:

```shell
$ cd /etc/supervisor/conf.d/
$ sudo cp ~/checkniner/etc/supervisor.gunicorn.conf ./gunicorn.conf
```

Change values (e.g. path to gunicorn) in the config as necessary, then restart
Supervisor with the new config file (and start gunicorn, if it does not auto-start):

```shell
$ sudo service supervisor stop
$ sudo service supervisor start
$ sudo supervisorctl start gunicorn
```

### Nginx ###

Remove default nginx config and add our own:

```shell
$ cd /etc/nginx/sites-enabled/
$ sudo rm default
$ sudo cp ~/checkniner/etc/nginx.checkniner ../sites-available/checkniner
$ sudo ln -s ../sites-available/checkniner
```

Change values (e.g. server_name, static files directory) in the config as 
necessary, then restart nginx so that it picks up the new configuration:

```shell
$ sudo service nginx restart
```

### Verification ###

If you visit http://example.com, things should be working!
