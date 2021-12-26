uneval_dir=/mnt/c/Users/user/Desktop/security_system/media/unevaluated/
evaling_dir=$uneval_dir/.evaluating/
wait=60
src_dir=/mnt/c/Users/user/Desktop/security_system/
model_file=/mnt/c/Users/user/Desktop/security_system/md_v4.1.0.pb

conda activate cameratraps-detector
#$model_dir/path.sh # add appropriate libraries to your path

while true; do
	for f in $(find "$uneval_dir" -type f -name "*.mp4"); do
		filename=$(basename $f)
		basename="${filename%.*}" # filename without extension
		# move file to another location so it isn't reprocessed at other steps
		mv $f $evaling_dir
		echo "Moved $f to evaluating status"
		# evaluate the video in the model
		echo "python $src_dir/process_video.py  $src_dir/md_v4.1.0.pb  $evaling_dir/$filename --render_output_video true --output_json_file $evaling_dir/$basename.json"
		python $src_dir/process_video.py $src_dir/md_v4.1.0.pb $evaling_dir/$filename --render_output_video true --output_json_file $evaling_dir/$basename.json
		# move the original video into the appropriate folder
		echo "python sort.py $evaling_dir/$filename $uneval_dir/.evaluating/$filename.json"
		python sort.py $f $uneval_dir/.evaluating/$filename.json
	done
	sleep $wait
done
