"""
Connects to a postgres DB and counts all of the rows.
Tables are limited to the 'public' schema by default.
"""
import os

import dj_database_url
import psycopg2

db = dj_database_url.parse(os.getenv('DATABASE_URL'))

db.pop('ENGINE')
db['database'] = db['NAME']
db.pop('NAME')
kwargs = {}
for k,v in db.items():
    kwargs[k.lower()] = v

with psycopg2.connect(**kwargs) as connection:
    cursor = connection.cursor()
    q = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    cursor.execute(q)
    rows = cursor.fetchall()
    
    tables = [r[0] for r in rows]
    print "Retrieved %d tables" % len(tables)
    
    total_rows = 0
    for t in tables:
        q = "SELECT count(*) FROM %s" % t
        cursor.execute(q)
        rows = cursor.fetchone()
        count = rows[0]
        if count > 0:
            print "%s: %d" % (t, count)
            total_rows += count
    print "This database contains %d tables with %d rows" % (len(tables), total_rows)
    
    """
    # A method of estimating the number of rows in each table. Returns the row counts
    # all at once, instead of hitting each table. It is just an estimate, though, and
    # might be off (by a bit) during times of heavy load.
    # Thanks to SO: http://stackoverflow.com/a/2611745/564584
    
    print ""
    
    q = "SELECT schemaname,relname,n_live_tup FROM pg_stat_user_tables ORDER BY n_live_tup DESC"
    cursor.execute(q)
    print cursor.fetchall()
    """
        
    
print "Done!"
