#!/bin/bash

PLAINTEXT="$1"

if [ -z "$PLAINTEXT" ]; then
    echo "WARN: Expected the name of the plaintext file as the first argument."
    echo "WARN: Unable to continue encrypting without a filename."
    exit 1
fi

ARCHIVE=$(basename `readlink -f "$PLAINTEXT"`)
gpg --encrypt --recipient "$BACKUPS_GPG_RECIPIENT" $ARCHIVE
