web: python cotracker/manage.py collectstatic --noinput; gunicorn -w 3 -b 0.0.0.0:$PORT cotracker.wsgi
