checkniner
==========

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
+ PYTHONPATH (e.g. /home/user/checkniner/cotracker/)
+ DJANGO_SETTINGS_MODULE (e.g. cotracker.settings.production)
+ DATABASE_URL (e.g. postgres://user:pass@host:port/database)
+ SECRET_KEY (e.g. aV3ryLong14c0mpl1ca73dStRin9)
+ (Development only) INTERNAL_IP (e.g. 127.0.0.1)
+ (Production only) ALLOWED_HOST (e.g. example.com)

These can be set in checkniner/bin/activate to ensure that they will always be available
when running in the virtualenv.

```shell
$ echo "export PYTHONPATH=/home/user/checkniner/cotracker/" >> bin/activate
$ echo "export DJANGO_SETTINGS_MODULE=cotracker.settings.development" >> bin/activate
$ echo "export DATABASE_URL=sqlite:////home/user/checkniner/cotracker/dev.db" >> bin/activate
$ echo "export SECRET_KEY=aV3ryLong14c0mpl1ca73dStRin9" >> bin/activate
$ echo "export INTERNAL_IP=192.168.1.1" >> bin/activate
```

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
