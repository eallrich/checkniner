import os
import dj_database_url

def get_database_name(env='DATABASE_URL'):
    db_config = dj_database_url.config(env)
    return db_config['NAME']

