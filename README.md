checkniner
==========

[![Build Status](https://travis-ci.org/eallrich/checkniner.png)](https://travis-ci.org/eallrich/checkniner)

Tracking and reporting of airstrip/aircraft checkout information for pilots.

Down and Dirty for Development
------------------------------

The two biggest differences between this dev environment and the production
env are replacing postgres with sqlite for the database and replacing both
nginx (reverse proxy) & supervisor (process formation controller) with honcho.
With these two changes, the checkniner app can be setup & served without any
root access required.

```shell
$ git clone https://github.com/eallrich/checkniner.git
$ cd checkniner
$ virtualenv .
```

Set the required configuration values by following the steps in Environment
Variables, then continue here.

```shell
# Pick up the new env vars
$ source bin/activate
$ pip install -r requirements/development.txt
$ python cotracker/manage.py syncdb
$ python cotracker/manage.py migrate
$ honcho start
```

### Testing ###

```shell
# Run the tests using the provided script
$ scripts/test
# If desired, generate a visual HTML report of the coverage
$ cd cotracker
$ coverage html --include="./*"
```

Up and Running for Production
-----------------------------

The scripts in `scripts/` help automate the tedious bits. Descriptions for the
various utilities are available in the [scripts/ readme](scripts) document. Be
sure to review the set of assumptions these scripts make as they perform their
setup duties, such as assuming the app will be executed by a user named
`checkniner`.

There are three configuration values required by the scripts during the initial
setup:
+ The URL at which the app will be served (`ALLOWED_HOSTS`)
+ A Sentry DSN (`SENTRY_DSN`)
+ A string to be prefixed onto some exported static files (`EXPORT_PREFIX`)

An optional fourth parameter is the name of the host user under whose account
the application is run. Example names include 'staging' and 'checkniner\_prod'.
This name is also used for PostgreSQL configuration as both the postgres DB
user & the DB name.

If the scripts aren't used, there are several additional variables the user
must specify. All these configuration options are covered in the Environment
Variables section.

The two deployment possibilities are to install the checkniner app locally or
remotely. If you're already connected to the machine which will be hosting the
app, then setting up is as simple as:

```shell
$ git clone https://github.com/eallrich/checkniner.git
$ checkniner/scripts/setup example.com https://access:key@sentry.example.com/2 zyxwvutsr staging
```

Only slightly more complicated than installing locally, to get a remote server
ready to serve checkniner we'll also need to pass the SSH connection string of
the remote machine.

```shell
$ git clone https://github.com/eallrich/checkniner.git
$ checkniner/scripts/remote_init ubuntu@example.com example.com https://access:key@sentry.example.com/2 zyxwvutsr staging
```

### Backups and Restores ###

Details for backing up and restoring the checkniner database are available in
the [scripts/backups/ readme](scripts/backups) document.

### Sending Emails ###

The pilot weights feature supports the ability to send notification emails
when a weight value is modified. Sending email is currently accomplished
through the [Mailgun](https://mailgun.com/) API. To enable these email
notifications, provide definitions for the email-related environment variables
(as discussed in the Environment Variables section).

### TLS via Let's Encrypt ###

After the initial setup (via `scripts/setup`), run `scripts/prep_production` to
obtain & configure TLS certificates from the Let's Encrypt CA.

Certificates from Let's Encrypt have a validity period of 90 days. Once the
initial certificate is obtained and installed, it is _highly_ recommended that
the root crontab be updated to include a monthly "certificate renewal" task.
For an example entry, see the [etc/root.crontab](etc/root.crontab) file in this
repository.

Once the template values in `etc/root.crontab` have been updated, install via:
```shell
# As the root user
$ crontab -l > ~/existing.crontab
$ cat etc/root.crontab >> ~/existing.crontab
$ crontab ~/existing.crontab
```

Environment Variables
---------------------

The following environment variables are always required:
+ `DATABASE_URL` (e.g. postgres://user:pass@host:port/database)
+ `DJANGO_SETTINGS_MODULE` (e.g. cotracker.settings.production)
+ `PYTHONPATH` (e.g. /home/user/checkniner/cotracker/)
+ `SECRET_KEY` (e.g. 0123456789ABCDEF)
+ `SENTRY_DSN` (e.g. https://access:key@example.com/2)
+ `EXPORT_PREFIX` (e.g. ZYXWVUTSR)

These can be set in `checkniner/bin/activate` to ensure that they will always be available
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
+ `ALLOWED_HOSTS` (e.g. example.com or example.com,www.example.com)

Optional environment variables:
+ `FORCE_DEBUG_MODE` (e.g. true) -- Override the DEBUG flag when using settings.production
+ `INTERNAL_IPS` (e.g. 10.31.41.59) -- Required to view django-debug-toolbar; DEBUG must be True
    - A comma-separated list is acceptable: 10.31.41.59,10.27.182.8

To enable sending emails (e.g. notification of pilot weight updates), set the following:
```shell
$ echo "export MAILGUN_SENDER=\"Checkniner <mailgun@example.com>\"" >> bin/activate
$ echo "export MAILGUN_API_URL=https://api.mailgun.net/v3/example.com/messages" >> bin/activate
$ echo "export MAILGUN_API_KEY=key-0123456789abcdef" >> bin/activate
$ echo "export NOTIFY_WEIGHT_TO=receiver@example.com" >> bin/activate
# Optional additional recipients
$ echo "export NOTIFY_WEIGHT_CC=carbon@example.com" >> bin/activate
$ echo "export NOTIFY_WEIGHT_BCC=quiet@example.com" >> bin/activate
```

