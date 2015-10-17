These scripts provide utilities for (1) backing up the data kept in checkniner's
database and (2) restoring the database by using a backup archive.

### Dependencies ###

+ `dj\_database\_url` to parse the database connection parameters
+ `envoy` to run commands outside python
+ S3 `access` and `secret` keys for boto

Backup Overview
---------------

MIRs for the backup process:
1. Run automatically
2. Provide a data resolution of five minutes
3. Save an archive if the business data has changed since the last iteration
4. Distribute saved archives to a secondary location

Stages of the backup process:
1. Cron runs the backup script every five minutes
2. The backup script begins by creating a new data archive:
    + Using pg\_dump to get a SQL version of the checkniner database
    + Using django's dumpdata command to get JSON fixtures for each app
3. If a prior archive does not exist, assume this is the first run and go to 5
4. If the new dataset is identical to the existing one, exit the backup script
    + Comparing via SHA1 hashes of the new/existing auth and checkouts fixtures
5. Package the archive into a single .tar.gz
6. Upload the file to S3 via boto

Setting up Backups
------------------

The backup scripts in this directory take snapshots of application data and
upload the archives to S3 when the business data changes. To set up the
pipeline, start by adding the S3 `access` and `secret` keys, as well as the
desired S3 bucket name, to the virtualenv's shell activation script.

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
BACKUPS_ROOT=/home/checkniner/checkniner/scripts/backups
*/15 *    *   *   *   $BACKUPS_ROOT/run.sh
# On the first of the month, at 00:12, remove all local .tar.gz files leftover
# from prior backups (i.e. all except the latest)
12   0    1   *   *   $BACKUPS_ROOT/clean.sh
```

Restoring from a Backup
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
loaded (e.g. admin.json), but these are not strictly necessary for returning
the database to a usable state.

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
