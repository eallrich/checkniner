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
+ EXPORT_PREFIX (e.g. ZYXWVUTSR)

These can be set in checkniner/bin/activate to ensure that they will always be available
when running in the virtualenv.

```shell
$ echo "export DATABASE_URL=sqlite:////home/user/checkniner/cotracker/dev.db" >> bin/activate
$ echo "export DJANGO_SETTINGS_MODULE=cotracker.settings.development" >> bin/activate
$ echo "export PYTHONPATH=/home/user/checkniner/cotracker/" >> bin/activate
$ echo "export SECRET_KEY=0123456789ABCDEF" >> bin/activate
$ echo "export SENTRY_DSN=https://access:key@example.com/2" >> bin/activate
$ echo "export EXPORT_PREFIX=ZYXWVUTSR" >> bin/activate
```

When running in a production configuration (i.e. DEBUG is False), the following env vars are also required:
+ ALLOWED_HOSTS (e.g. example.com or example.com,www.example.com)

Optional environment variables:
+ FORCE_DEBUG_MODE (e.g. true) -- Override the DEBUG flag when using settings.production
+ INTERNAL_IPS (e.g. 10.31.41.59) -- Required to view django-debug-toolbar; DEBUG must be True
    - A comma-separated list is acceptable: 10.31.41.59,10.27.182.8

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
$ cd cotracker
$ coverage run manage.py test --settings=cotracker.settings.test
# To generate a visual coverage report:
$ coverage html --include="./*"
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
$ echo "export ALLOWED_HOSTS=example.com" >> bin/activate
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

Backups
-------

Scripts to take snapshots of application data and upload the archives to S3
when the business data changes are available in checkniner/tools/backups/. To
set up the pipeline, add S3 Access and Secret keys, as well as the desired
bucket name, to the virtualenv's shell activation script.

```shell
$ echo "export S3_ACCESS_KEY=0123456789ABCDEF" >> bin/activate
$ echo "export S3_SECRET_KEY=ABCDEFGHIJKLMNOPQRSTUVWXYZ" >> bin/activate
$ echo "export S3_BUCKET_NAME=snapshots.example.com" >> bin/activate
```

Install the python packages needed to collect and upload the snapshots:

```shell
$ pip install -r requirements/backups.txt
```

Cron is recommended for setting up the backup schedule:

```shell
# m  h  dom mon dow   command
BACKUPS_ROOT=/home/ubuntu/checkniner/tools/backups
*/15 *    *   *   *   $BACKUPS_ROOT/run.sh
# On the first of the month, at 00:12, remove all .tar.gz files (except the latest)
12   0    1   *   *   $BACKUPS_ROOT/clean.sh
```

Restoring from a backup
-----------------------

The backup scripts discussed above provide for two sources of data from which
restores may be made: Django fixtures (in json) and PostgreSQL commands. The
steps below will cover how to restore a database to the state as captured in a
backup archive, assuming you already have a latest.tar.gz file available
locally.

### Django fixtures ###

Because fixtures are not (strictly) tied to a particular database, they allow
for a restore to be made to a database engine which differs from the one in use
at the time the backup was made. It's also possible to return the database to a
workable state by only loading a subset of the available fixtures instead of
all of them. Although this means the restored database will not exactly match
the database which was backed up, this may be acceptable (e.g. for development
or testing purposes).

```shell
# Assumes the database backup is available at ~/latest.tar.gz
# Assumes that the checkniner virtualenv has already been activated
$ tar -xzf ~/latest.tar.gz auth.json checkouts.json
$ django-admin.py loaddata auth.json
$ django-admin.py loaddata checkouts.json
```

There are several additional fixtures in the backup archive which may also be
loaded (e.g. south.json, admin.json), but these are not strictly necessary for
returning the database to a usable state.

### PostgreSQL archive ###

Restoring from the PostgreSQL command file provides a database which precisely
matches the originating database.

```shell
# Assumes the database backup is available at ~/latest.tar.gz
$ tar -xzf ~/latest.tar.gz checkniner.sql
$ psql checkniner < checkniner.sql
```

Errors (due to duplicate keys or pre-existing tables) will likely be seen when
using this method, but they should not cause any problems if the import is
allowed to continue running. Note the _should_ qualifier! Be sure to verify!
