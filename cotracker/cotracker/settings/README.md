Settings
========

Always Needed
-------------

The following environment variables are always required:

| Name | Example Value | Purpose |
| ---- | ------------- | ------- |
| `DATABASE_URL` | `postgres://user:pass@host:port/database` | Connection string for the DB |
| `DJANGO_SETTINGS_MODULE` | `cotracker.settings.production` | The desired app configuration |
| `PYTHONPATH` | `/home/checkniner/checkniner/cotracker` | Python's search path for modules |
| `SECRET_KEY` | `J2mhhdGlTF1itOxtzLKV` | Django's key for any secrets it keeps |
| `SENTRY_DSN` | `https://key@sentry.io/1` | The URL to which Sentry reports exceptions |
| `EXPORT_PREFIX` | `C068CKVYjXML` | The access key used to protect access to exported files |

The configuration files in this directory expect to find env vars for each of
these names. For convenience they may be set in the activation script for the
application's virtualenv (e.g. `checkniner/bin/activate`). This is the approach
taken by the scripts which set up a production-ready instance.

In Dev and Prod but not in Test
-------------------------------

In order to view the `django-debug-toolbar` it's necessary to set the
`INTERNAL_IPS` env var. In production the toolbar will not appear by default
since `DEBUG=False`. This can be overridden by setting an env var for
`FORCE_DEBUG_MODE`. The `ALLOWED_HOSTS` value is required for production
deployments.

| Name | Example Value | Purpose | Required? |
| ---- | ------------- | ------- | --------- |
| `ALLOWED_HOSTS` | `example.com,www.example.com` | Django will only respond to requests targeting these hostnames | Yes if in prod (i.e. `DEBUG=False`) |
| `FORCE_DEBUG_MODE` | `true` | Override the `DEBUG` flag when using `settings.production` | Only when using the `django-debug-toolbar` in prod |
| `INTERNAL_IPS` | `10.31.41.59,10.27.182.8` | The `django-debug-toolbar` will only respond to requests from these IPs | Only when using the `django-debug-toolbar` (dev or prod) |

Sending Emails
--------------

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
