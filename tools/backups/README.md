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
+ TODO: What will distribute the saved archives?
