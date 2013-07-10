Backing Up Checkniner
=====================

MIRs
----

The backup process should:

1. Run automatically
2. Provide a data resolution of five minutes
3. Save an archive if the data has changed since the last iteration
4. Distribute saved archives to a secondary location

Components
----------

+ PostgreSQL archive formats
    - pg\_dump: SQL
    - django-admin.py dumpdata: JSON fixtures
+ Cron for running on a schedule
+ Hash algorithm for comparing archives
+ S3 as a secondary location
+ Boto providing an interface to S3

Stages
------

1. Cron runs the backup script every five minutes
2. The backup script begins by creating a new data archive:
    1. Using pg\_dump to get a SQL version of the checkniner database
    2. Using django's dumpdata command to get JSON fixtures for each app
3. If a prior archive does not exist, assume this is the first run and go to 5
4. If the new archive is identical to the existing one, exit the backup script
5. Package the archive into a single compressed file
6. Upload the file to S3
