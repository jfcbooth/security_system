#!/bin/bash
local_sync_dir=/var/www/motion/
sync_ip=10.0.0.30
username=boothm
remote_sync_dir=C:\\Users\\boothm\\Desktop\\security_system\\unevaluated\\
sleep_time=60
failover_time=30

# move old files out of syncing directory
for f in $(find "$local_sync_dir/.syncing" -type f -name "*.mp4"); do
    echo "Found $f stucking in .syncing/. It was moved out."
	mv $f $local_sync_dir/$(basename $f) # after the file has been written to, move it into the syncing directory
done

# check if syncing directory 1 exists
if [ ! -d $local_sync_dir ]
then
        echo "Sync directory not found. Exiting."
	exit
fi

# check if syncing directory exists
if [ ! -d $local_sync_dir/.syncing/ ]
then
	mkdir $local_sync_dir/.syncing/
	echo "Made $local_sync_dir/.syncing/"
fi

while true; do
	for f in $(find "$local_sync_dir" -type f -name "*.mp4" -mmin +1); do
		mv $f $local_sync_dir/.syncing/$(basename $f) # after the file has been written to, move it into the syncing directory
		echo "Syncing $f"
		echo "Running: rsync -e 'ssh -o StrictHostKeyChecking=no' --compress --remove-source-files --progress --partial --partial-dir=.rsync_partial/ $local_sync_dir/.syncing/$(basename $f) $username@$sync_ip:$remote_sync_dir/$(basename $f)"
		while ! rsync -e "ssh -o StrictHostKeyChecking=no" --compress --remove-source-files --progress --partial --partial-dir=.rsync_partial/ $local_sync_dir/.syncing/$(basename $f) $username@$sync_ip:$remote_sync_dir/$(basename $f); do
			sleep $failover_time; # restarts the rsync after 30 seconds if it fails. This is to make sure we don't DDOS the server when we get to scale
			echo "Sync of $f fail. Retrying..."
		done
		echo "Sycned: $f"
		echo "Deleting thumbnail"
		rm $f.*.th.jpg
	done
	sleep $sleep_time
done

