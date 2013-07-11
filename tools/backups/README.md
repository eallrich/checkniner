Backing Up Checkniner
=====================

MIRs
----

The backup process should:

1. Run automatically
2. Provide a data resolution of five minutes
3. Save an archive if the business data has changed since the last iteration
4. Distribute saved archives to a secondary location

Stages
------

1. Cron runs the backup script every five minutes
2. The backup script begins by creating a new data archive:
    + Using pg\_dump to get a SQL version of the checkniner database
    + Using django's dumpdata command to get JSON fixtures for each app
3. If a prior archive does not exist, assume this is the first run and go to 5
4. If the new dataset is identical to the existing one, exit the backup script
    + Comparing via SHA1 hashes of the new/existing auth and checkouts fixtures
5. Package the archive into a single .tar.gz
6. Upload the file to S3 via boto
