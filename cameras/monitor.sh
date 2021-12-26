#!/bin/bash
local_sync_dir=/home/user/send/
sync_ip=172.31.203.75
username=user
remote_sync_dir=/mnt/c/Users/user/Desktop/security_system/unevaluated/
sleep_time=60
failover_time=30

while true; do
	for f in $(find "$local_sync_dir" -type f -name "*.mp4" -mmin +1); do
		mv $f $local_sync_dir/.syncing/$(basename $f) # after the file has been written to, move it into the syncing directory
		echo "Syncing $f"
		echo "Running: rsync --compress --remove-source-files --progress --partial --partial-dir=.rsync_partial/ $local_sync_dir/.syncing/$(basename $f) $username@$sync_ip:$remote_sync_dir/$(basename $f)"
		while ! rsync --compress --remove-source-files --progress --partial --partial-dir=.rsync_partial/ $local_sync_dir/.syncing/$(basename $f) $username@$sync_ip:$remote_sync_dir/$(basename $f); do
			sleep $failover_time; # restarts the rsync after 30 seconds if it fails. This is to make sure we don't DDOS the server when we get to scale
			echo "Sync of $f fail. Retrying..."
		done
		echo "Sycned: $f"
	done
	sleep $sleep_time
done

