#!/usr/bin/env bash
# Usage: certify.sh example.com
# Assumes the executing user is root

set -e

DOMAIN=$1 # The domain for which we'll be getting a certificate
LOGFILE=/tmp/letsencrypt.$(basename $0).log
# Directories
LE_ROOT="/etc/letsencrypt"
CHALLENGES="$LE_ROOT/challenges"
KEYS="$LE_ROOT/keys"

function log_major { echo "=====> $1"; }
function log_minor { echo "-----> $1"; }
function log_print { echo "       $1"; }

function initialize {
    log_minor "Initializing"
    if [ ! -d $CHALLENGES ] || [ ! -d $KEYS ]; then
        log_print "Creating directory structure"
        mkdir -p $CHALLENGES
        mkdir -p $KEYS
    fi
    log_print "Updating permissions"
    # Permissions need to allow nginx to access keys & certificates
    chmod 755 $LE_ROOT
    chmod 755 $CHALLENGES
    chmod 700 $KEYS # These will _not_ be served by nginx

    # Don't trust the default parameters for DH. It's easy to create our own.
    DH_PARAMS=$LE_ROOT/dhparams.pem
    if [ ! -f $DH_PARAMS ]; then
        log_print "Generating diffie-hellman parameters"
        openssl dhparam -out $LE_ROOT/dhparams.pem 2048 2>>$LOGFILE
    fi

    # This self-signed cert enables trapping of unrecognized hosts requested
    # over TLS. To drastically reduce the chance that the certificate will
    # expire, we'll regenerate it every time this function is called.
    SELFSIGN_KEY=$KEYS/selfsign.key
    SELFSIGN_CERT=$LE_ROOT/selfsign.crt
    DAYS=1095 # 3 years
    log_print "Regenerating self-signed catch-all certificate"
    openssl req -x509 -nodes -days $DAYS -subj "/CN=*" -newkey rsa:2048 -keyout $SELFSIGN_KEY -out $SELFSIGN_CERT 2>>$LOGFILE

    ACCOUNT_KEY=$KEYS/account.key
    if [ ! -f $ACCOUNT_KEY ]; then
        log_print "Creating account key..."
        openssl genrsa 4096 > $ACCOUNT_KEY 2>>$LOGFILE
        chmod 600 $ACCOUNT_KEY
    fi
}

function request_and_sign {
    log_minor "Obtaining signed certificate for $DOMAIN"
    DOMAIN_KEY=$KEYS/$DOMAIN.key
    if [ ! -f $DOMAIN_KEY ]; then
        log_print "Creating domain key"
        openssl genrsa 4096 > $DOMAIN_KEY 2>>$LOGFILE
        chmod 600 $DOMAIN_KEY
    fi

    log_print "Creating Certificate Signing Request"
    openssl req -new -sha256 -key $DOMAIN_KEY -subj "/CN=$DOMAIN" > $LE_ROOT/$DOMAIN.csr 2>>$LOGFILE

    log_minor "Verifying domain ownership"
    python $LE_ROOT/acme_tiny.py --account-key $ACCOUNT_KEY --csr $LE_ROOT/$DOMAIN.csr --acme-dir $CHALLENGES > $LE_ROOT/$DOMAIN.signed.crt 2>>$LOGFILE

    log_minor "Chaining intermediate certificate"
    LE_INTERMEDIATE_URL=https://letsencrypt.org/certs/lets-encrypt-x1-cross-signed.pem
    wget -O $LE_ROOT/intermediate.pem $LE_INTERMEDIATE_URL 2>>$LOGFILE
    cat $LE_ROOT/$DOMAIN.signed.crt $LE_ROOT/intermediate.pem > $LE_ROOT/$DOMAIN.chained.pem

    log_minor "Cleaning up"
    rm $LE_ROOT/$DOMAIN.signed.crt
    rm $LE_ROOT/$DOMAIN.csr
    rm $LE_ROOT/intermediate.pem
}

log_major "Preparing TLS for $DOMAIN"
initialize
request_and_sign
log_major "Done"

