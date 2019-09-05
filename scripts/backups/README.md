These scripts provide utilities for (1) backing up the data kept in checkniner's
database and (2) restoring the database by using a backup archive.

### Dependencies ###

+ `dj_database_url` to parse the database connection parameters
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
    + Using `pg_dump` to get a SQL version of the checkniner database
    + Using django's `dumpdata` command to get JSON fixtures for each app
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

Note that bucket names with dots are **not supported** by boto at this time
(at least v2.43.0). See https://github.com/boto/boto/issues/2836 for details.
My preferred alternative is to use hyphens in bucket names instead of dots.

```shell
$ echo "export S3_ACCESS_KEY=0123456789ABCDEF" >> bin/activate
$ echo "export S3_SECRET_KEY=ABCDEFGHIJKLMNOPQRSTUVWXYZ" >> bin/activate
$ echo "export S3_BUCKET_NAME=snapshots-example-com" >> bin/activate
```

Encrypting the backup archives before they leave the server is accomplished by
using GPG. Only the public key for a key-pair needs to be on the Checkniner
server. To import the public key from another computer, you can follow steps
similar to these. On the other computer (not the Checkniner server), create a
GPG key-pair if you don't already have one (or if you want to use a dedicated
key-pair for the backups) and then export the GPG public key:

```shell
# Create a GPG key. If you're unsure of which options to pick at the prompts,
# use '(1)' for 'RSA and RSA', 4096 bits, and '(0)' for 'No expiration'. An
# example user ID is 'Checkniner (backups) <checkniner@example.com>'.
$ gpg --gen-key
# Get the key ID from the list of public keys.
$ gpg --list-keys --keyid-format short
# Find the uid matching the GPG key. The 8-digit key ID immediately follows the
# 'rsa4096/' section on the 'pub' line above (not the 'sub' line below).
# Now export the public key.
$ gpg --output checkniner_public.gpg --export [8-digit key ID copied above]
```

After transferring the exported public key file (`checkniner_public.gpg`) to
the Checkniner server, you can import the GPG key:

```shell
$ gpg --import checkniner_public.gpg
# Now set the trust level for the newly imported public key
$ gpg --edit-key [8-digit key ID for the public key]
$ gpg> trust
$ gpg> (5)
$ gpg> quit
```

Now we're ready to configure the backup pipeline to use our GPG public key for
encrypting the archives before they get uploaded to S3. All you need to do is
add the following line to the virtualenv's shell activation script:

```shell
# Replace the user ID with the actual user ID of the public key
$ echo "export BACKUPS_GPG_RECIPIENT='Checkniner (backups) <checkniner@example.com>'" >> bin/activate
```

Install the python packages needed to collect and upload the snapshots:

```shell
$ pip install -r requirements/backups.txt
```

Cron is recommended for setting up the backup schedule, and having the scripts
check in with a watchdog service is encouraged but not required:

```shell
# m h  dom mon dow   command
BACKUPS_ROOT=/home/checkniner/checkniner/scripts/backups
# Ping the watchdog on success. After too many failures, the service should
# send us an alert so that we can know to look into why it's failing.
*/5 *    *   *   *   $BACKUPS_ROOT/run.sh && curl -m 30 https://example.com/ping/IDENTIFIER
# On the first of the month, at 00:12, remove all local .tar.gz files leftover
# from prior backups (i.e. all except the latest). We don't have to alert any
# watchdogs for our cron commands (it's just good practice), and here's an
# example of staying quiet. If the script fails it will just leave every old
# backup archive of the database on the server.
12   0    1   *   *   $BACKUPS_ROOT/clean.sh
```

Restoring from a Backup
-----------------------

The backup scripts discussed above provide for two sources of data from which
restores may be made: Django fixtures (in json) and PostgreSQL commands. The
steps below will cover how to restore a database to the state as captured in a
backup archive, starting with retrieving a latest.tar.gz backup file from S3.

### Retrieving a backup snapshot ###

The `get_latest_archive.py` script searches through the S3 bucket containing
backup archives, finds the latest, and downloads it for local access. The file
is named latest.tar.gz and will be placed in the current working directory. If
encryption of backups has been enabled, then the extension '.gpg' will be added
to the file name.

```shell
$ cd ~/checkniner/
$ source bin/activate
$ python scripts/backups/get_latest_archive.py
# Most recent backup archive is now available at ~/checkniner/latest.tar.gz or,
# if it was encrypted on the server, ~/checkniner/latest.tar.gz.gpg.
# If encrypted, to decrypt the backup archive (assuming you have the private
# key for the GPG keypair used to encrypt the archive):
$ gpg --decrypt latest.tar.gz.gpg > latest.tar.gz
```

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

### Post-restore activities ###

Following a successful restore, regenerate any files created from data in the
the database. For the pilot weight static export files, simply run:

```shell
$ source bin/activate
$ echo "from checkouts import util; util.export_pilotweights()" | django-admin shell
```
