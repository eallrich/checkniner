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
$ git clone git://github.com/eallrich/checkniner.git
$ cd checkniner
$ virtualenv .
```

The following environment variables are expected:
+ DATABASE_URL (e.g. postgres://user:pass@host:port/database)
+ DJANGO_SETTINGS_MODULE (e.g. cotracker.settings.production)
+ PYTHONPATH (e.g. /home/user/checkniner/cotracker/)
+ SECRET_KEY (e.g. aV3ryLong14c0mpl1ca73dStRin9)
+ SENTRY_DSN (e.g. https://user:key@host.com/3)

These can be set in checkniner/bin/activate to ensure that they will always be available
when running in the virtualenv.

```shell
$ echo "export DATABASE_URL=sqlite:////home/user/checkniner/cotracker/dev.db" >> bin/activate
$ echo "export DJANGO_SETTINGS_MODULE=cotracker.settings.development" >> bin/activate
$ echo "export PYTHONPATH=/home/user/checkniner/cotracker/" >> bin/activate
$ echo "export SECRET_KEY=aV3ryLong14c0mpl1ca73dStRin9" >> bin/activate
```

Optional environment variables:
+ ALLOWED_HOST (e.g. example.com) -- Required when DEBUG is False
+ FORCE_DEBUG_MODE (e.g. true) -- Override the DEBUG flag when using settings.production
+ INTERNAL_IPS (e.g. 10.31.41.59) -- Required to view django-debug-toolbar; DEBUG must be True
    - A comma-separated list is acceptable: 10.31.41.59,10.27.182.8
+ SERVE_STATIC (when present and true, the URLconf will route static asset requests)

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
