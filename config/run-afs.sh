#!/bin/bash
# Modified from https://github.com/mit-scripts/sql-backup/blob/master/run-afs.sh

# We can't do an AFS backup unless
#  a) we're under the lock
#  b) we have tokens
#
# unfortunately, we can't guarantee both of these at the same time,
# but we can guarantee a valid token once we get one, using k5start.
# As a result, we're going to use a clever scheme, in which we
# premptively lock, run k5start, and if that succeeds, we can then do
# the backup.  If not, we release the lock and try again.
#
# For this to work, we need to run k5start in "kinit daemon" mode,
# which means we need a pid fie.

base=/srv/data/mysql/db
# Remember that du reports values in kb
max_size=$((100 * 1024))
kstartpid=$(mktemp /tmp/backup-ng-k5start.XXXXXXXXXX)
kstartret=1

while [ $kstartret -ne 0 ]; do
    echo "trying";
    (
	flock --exclusive 200
	k5start -f /etc/daemon.keytab -u daemon/froyo-machine.mit.edu -t -K 15 -l6h -b -p "$kstartpid" || exit 1
	# If we get here, we're under both the lock and the k5start
    aklog -force
    aklog -c sipb
	RETENTION='5D'

    ROOT="/home/minecraft/creative"
    BACKUP_ROOT="/afs/sipb/project/minecraft/backups/creative"

    mkdir -p "$BACKUP_ROOT"

    cd "$ROOT"
    for dir in mitworld; do
        echo "Backing up $dir"
        rdiff-backup "$ROOT/$dir" "$BACKUP_ROOT/$dir" || echo "Failed to backup"
        rdiff-backup "$ROOT/$dir" "/mnt/gdrive/" || echo "Failed to gbackup"
        #rdiff-backup --force --remove-older-than "$RETENTION" "$BACKUP_ROOT/$dir" >/dev/null || "Failed to purge old backups"
        echo "Done Backing up $dir"
    done

	# Okay, we're all done. Kill k5start
	kill -TERM $(cat "$kstartpid")
	exit 0
    ) 200> /home/minecraft/.lock/backup-ng.lock
    kstartret=$?
done

rm -f "$kstartpid"
