#!/bin/bash
# ============================================================================
# Bootstrap deployment of checkniner
# ----------------------------------
# Requires ssh access and sudo privileges on the target
# 
# Begins by installing a few core packages, then continues with updating the
# rest of the system. Once a clone of the repository is available, it
# kickstarts the full deployment script to complete the process.
#
# Usage:
#   ./bootstrap.sh ssh-connection hosted-domain sentry-dsn
#   E.g.
#   ./bootstrap.sh ubuntu@example.com example.com https://access:key@example.com/2
# ============================================================================

CONNECTION=$1
ALLOWED_HOST=$2
SENTRY_DSN=$3

# + byobu because it's awesome and if I have to SSH in I'll want it
# + git to retrieve the repository
# + language-pack-en to resolve locale issues in some environments (e.g. LXC)
# + fail2ban to provide desirable defense against some attacks
CORE="byobu git language-pack-en fail2ban"

REPOSITORY=https://github.com/eallrich/checkniner.git
SSH_ID=~/.ssh/id_rsa.pub

# For sudo on the remote
read -s -p "Password: " PASSWORD
echo ''

ssh-copy-id -i $SSH_ID $CONNECTION

echo $PASSWORD | ssh $CONNECTION "sudo -S apt-get update"
echo $PASSWORD | ssh $CONNECTION "sudo -S apt-get install $CORE --assume-yes"
echo $PASSWORD | ssh $CONNECTION "sudo -S apt-get dist-upgrade --assume-yes"

ssh $CONNECTION "git clone $REPOSITORY"

echo ""
echo "Bootstrap complete, initiating fresh deployment"

echo $PASSWORD | ssh $CONNECTION "~/checkniner/tools/fresh.sh $ALLOWED_HOST $SENTRY_DSN"

echo ""
echo "Done!"
