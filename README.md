checkniner
==========

[![Build Status](https://travis-ci.org/eallrich/checkniner.png)](https://travis-ci.org/eallrich/checkniner)

This application provides a database for tracking pilot-airstrip-aircraft
checkout tuples. Once recorded the tuples can be searched to find available
flight scheduling assignments based on the known parameters or to identify
checkouts which should be prioritized for new training to alleviate scheduling
constraints. A reporting feature allows analyzing checkouts per pilot, per
airstrip, or per base of operations.

Development Setup
-----------------

The only firm requirement for developing and testing `checkniner` is an
installation of Python 3.{5,6,7}. The steps below will also assume the presence
of `git`, `virtualenv`, and `pip`.

First let's get the repository and set up the virtual environment.

```shell
$ git clone https://github.com/eallrich/checkniner.git
$ cd checkniner
$ virtualenv --python=python3 .
```

Next we'll provide a few dev settings and install the python dependencies.

```shell
$ echo "export DATABASE_URL='sqlite://$(pwd)/cotracker/dev.db'"       >> bin/activate
$ echo "export DJANGO_SETTINGS_MODULE=cotracker.settings.development" >> bin/activate
$ echo "export PYTHONPATH='$(pwd)/cotracker/'"                        >> bin/activate
$ echo "export SECRET_KEY='$(head -c 15 /dev/urandom | base64)'"      >> bin/activate
$ echo "export SENTRY_DSN=https://key@sentry.io/2"                    >> bin/activate
$ echo "export EXPORT_PREFIX=zyxwvutsr"                               >> bin/activate
$ source bin/activate
$ pip install -r requirements/development.txt
```

Then we have a bit of database set up work.

```shell
$ python cotracker/manage.py migrate --noinput
```

Finally we're ready to run our application!

```shell
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

Unlike setting up for development, deploying a production-ready instance is
intended to be as automated as practical. You'll only need to provide:

- A fresh Ubuntu 18.04 64-bit server
- A domain name pointing to the server's IP address
- A [Sentry](https://sentry.io/) DSN
- A secret key to restrict access to exported files

If you have SSH access to the server you can use `scripts/remote_init` to take
care of everything. Otherwise you'll need to connect to the server and do a few
things yourself before picking up with `scripts/setup` - just follow what's in
`scripts/remote_init` and perform those steps manually on your server.

We're going to assume these values for the above requirements:

- `DOMAIN`: `checkouts.example.com`
- `SENTRY_DSN`: `https://key@sentry.io/1`
- `EXPORT_PREFIX`: `zyxwvutsr`

The simplest option is to check out this repository locally and then run the
`scripts/remote_init` script. Let's say the server's SSH connection string is
`root@10.31.41.59` and that you've set up SSH keys.

```shell
$ git clone https://github.com/eallrich/checkniner.git
$ checkniner/scripts/remote_init root@10.31.41.59 checkouts.example.com https://key@sentry.io/1 zyxwvutsr
```

After waiting approximately five minutes you should be able to visit your new
instance at https://checkouts.example.com/ and be presented with the login
screen.

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

