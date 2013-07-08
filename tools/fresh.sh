#!/bin/bash
# ============================================================================
# Configures a fresh checkniner server
# ------------------------------------
# Requires sudo
#
# + Installs OS package dependencies
# + Installs python packages to a virtualenv
# + Creates a user and database in postgres
# + Sets up environment variables in the virtualenv
# + Instructs django to prepare the database and static files
# + Configures supervisor to manage gunicorn
# + Configures nginx to reverse proxy for gunicorn
# 
# Usage:
#   ./fresh.sh hosted-domain sentry-dsn
#   E.g.
#   ./fresh.sh example.com https://access:key@example.com/2
# ============================================================================

ALLOWED_HOST=$1
SENTRY_DSN=$2

PG_DATABASE=checkniner
PG_USERNAME=`whoami`
SECRET_KEY=$(python -c "import base64, os; print base64.b64encode(os.urandom(40))")
SITE_ROOT=~/checkniner/

# For sudo
# When called by bootstrap.sh, the password is provided automatically
read -s -p "Password: " PASSWORD
echo ''

DEPENDENCIES="python-virtualenv python-dev postgresql libpq-dev nginx supervisor"
echo $PASSWORD | sudo -S apt-get install $DEPENDENCIES --assume-yes

# Make sure we've lost sudo so that we don't mess up a question from postgres
# by providing the password when it wasn't expected.
sudo -k

echo $PASSWORD | sudo -S -u postgres /bin/bash -c "echo ''; echo \"CREATE DATABASE $PG_DATABASE;\\q\" | psql"
echo $PASSWORD | sudo -S -u postgres /bin/bash -c "echo ''; echo \"CREATE USER $PG_USERNAME;\\q\" | psql"
echo $PASSWORD | sudo -S -u postgres /bin/bash -c "echo ''; echo \"GRANT ALL PRIVILEGES ON DATABASE $PG_DATABASE TO $PG_USERNAME;\\q\" | psql"

cd $SITE_ROOT
virtualenv .
source bin/activate
pip install -r requirements.txt

echo "export ALLOWED_HOST=$ALLOWED_HOST" >> bin/activate
echo "export DATABASE_URL=postgres://$PG_USERNAME@/$PG_DATABASE" >> bin/activate
echo "export DJANGO_SETTINGS_MODULE=cotracker.settings.production" >> bin/activate
echo "export PYTHONPATH=$SITE_ROOT/cotracker/" >> bin/activate
echo "export SECRET_KEY=$SECRET_KEY" >> bin/activate
echo "export SENTRY_DSN=$SENTRY_DSN" >> bin/activate

deactivate
source bin/activate

# Note that we're not creating a superuser here. If one is needed and initial
# data won't provide one when imported, run manage.py createsuperuser
python cotracker/manage.py syncdb --noinput --no-initial-data
python cotracker/manage.py migrate
python cotracker/manage.py collectstatic --noinput

# Ensure we'll be asked for the password
sudo -k

cd /etc/supervisor/conf.d/
echo $PASSWORD | sudo -S cp $SITE_ROOT/etc/supervisor.gunicorn.conf gunicorn.conf
ORIGINAL=\\/home\\/ubuntu\\/checkniner\\/
echo $PASSWORD | sudo -S sed -i s/$ORIGINAL/$SITE_ROOT/g gunicorn.conf
echo $PASSWORD | sudo -S service supervisor stop
echo $PASSWORD | sudo -S service supervisor start

cd /etc/nginx/sites-enabled/
echo $PASSWORD | sudo -S rm default
echo $PASSWORD | sudo -S cp $SITE_ROOT/etc/nginx.checkniner ../sites-available/checkniner
echo $PASSWORD | sudo -S ln -s ../sites-available/checkniner
ORIGINAL=\\/home\\/ubuntu\\/checkniner\\/
echo $PASSWORD | sudo -S sed -i s/$ORIGINAL/$SITE_ROOT/g checkniner
echo $PASSWORD | sudo -S sed -i s/example.com/$ALLOWED_HOST/g checkniner
echo $PASSWORD | sudo -S service nginx restart

echo ""
echo "Fresh deployment script complete"

