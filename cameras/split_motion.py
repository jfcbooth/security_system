import argparse
import os
import re
import sys
import datetime
import subprocess
import tempfile

media_dir = 'media/'
motion_dir = 'motion/'
processing_dir = os.path.join(media_dir, '.processing/')

def filename2numbers(filename):
    return int(''.join(os.path.splitext(os.path.basename(filename))[0].split('_')[2:]))

def get_sec(time):
    """Get Seconds from time."""
    #HHMMSS
    h = 0
    m = 0
    s = 0
    if time > 9999:
        h = time//10000
        time = time-((time//10000)*10000)
    if time > 99:
        m = time//100
        time = time-((time//100)*100)
    s = time
    return int(h) * 3600 + int(m) * 60 + int(s)

def to_datetime(time):
    time = str(time)
    # print("time")
    # print(time)
    return datetime.datetime(int(time[0:4]), int(time[4:6]), int(time[6:8]), int(time[8:10]), int(time[10:12]), int(time[12:14]))

def make_dirs():
    if not os.path.exists(motion_dir):
        os.mkdir(motion_dir)
    if not os.path.exists(processing_dir):
        os.mkdir(processing_dir)

ap = argparse.ArgumentParser()
ap.add_argument("motion_file")
ap.add_argument("--dry_run")
args = ap.parse_args()


make_dirs()

data = []
fp = open(args.motion_file, 'r+')
data = fp.read().split('\n')
important_times = data[:2]

# make sure there isn't an error in the log and remove entry from log
if 'Motion stop detected' in important_times[1] and not args.dry_run:
    print("Full motion event located, re-writing log without this entry...")
    fp.seek(0)
    fp.write('\n'.join(data[2:]))
    fp.truncate()
fp.close()

video_files = [os.path.join(media_dir,x) for x in os.listdir(media_dir) if x.endswith('.mp4')]
#filename2numbers(video_files[0])
motion_start_time = int(''.join(re.split('{|}|/|:|\s',important_times[0])[1:7]))
motion_end_time = int(''.join(re.split('{|}|/|:|\s',important_times[1])[1:7]))

# get video files that fall in time range
video_info = {'motion_videos': [], 'next_video': None}
for i in range(len(video_files)):
    if motion_start_time >= filename2numbers(video_files[i]) and motion_start_time < filename2numbers(video_files[i+1]) :
        video_info['motion_videos'].append(video_files[i])
        i+=1
        video_time = filename2numbers(video_files[i])
        while(video_time <= motion_end_time):
            video_info['motion_videos'].append(video_files[i])
        video_info['next_video'] = video_files[i]
        break

# makes extraction only need to occur from 1 video file
if len(video_info['motion_videos']) > 1:
    combined_videos = open(os.path.join(processing_dir, 'videos.txt'), 'w')
    for f in video_info['motion_videos']:
        combined_videos.write("file {}\n".format(os.path.join(media_dir, f)))
    combined_videos.flush()
    combined_videos.close()
    # combine all videos into 1 video for splitting
    #ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.mp4
    cmd = "ffmpeg -y -f concat -safe 0 -i {} -c copy {}".format(os.path.join(processing_dir, "videos.txt"), os.path.join(processing_dir, video_info['motion_videos'][0]))
    subprocess.call(cmd.split())
    if not os.path.exists(os.path.join(processing_dir, video_info['motion_videos'][0])):
        print("Merge fail. Exiting.")
        sys.exit()
    video_info['motion_videos'] = [os.path.join(processing_dir, video_info['motion_videos'][0])]
#print(video_info['motion_videos'])
#print(video_info['next_video'])
video_start_time = filename2numbers(video_info['motion_videos'][0])
video_end_time = filename2numbers(video_info['next_video'])

if(video_end_time < motion_end_time):
    motion_end_time = video_end_time
    print("End time too close to end of video. Compensating...")

motion_start_from_epoch = (to_datetime(motion_start_time) - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)
video_start_from_epoch = (to_datetime(video_start_time) - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)
elapsed_time = (to_datetime(motion_end_time) - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1) - motion_start_from_epoch

start_time_offset = motion_start_from_epoch - video_start_from_epoch # video starts before motion, so it will be a smaller number
end_time_offset = start_time_offset + elapsed_time

start_time_offset_hhmmss = str(datetime.timedelta(seconds=start_time_offset))
end_time_offset_hhmmss = str(datetime.timedelta(seconds=end_time_offset-3)) # subtract 3 seconds for buffer

# input file, start time, end time, output file, times need to be in HH:MM:SS form
# formats: HH:MM:SS for start of video
#ffmpeg -i ORIGINALFILE.mp4 -acodec copy -vcodec copy -ss 00:15:00 -t 00:15:00 OUTFILE-2.mp4
print("Cutting {} from {} to {}".format(video_info['motion_videos'][0], start_time_offset_hhmmss, end_time_offset_hhmmss))

command = "ffmpeg -y -i {} -acodec copy -vcodec copy -ss {} -to {} {}".format(video_info['motion_videos'][0], start_time_offset_hhmmss, end_time_offset_hhmmss,os.path.join(motion_dir, os.path.split(video_info['motion_videos'][0])[1]))
subprocess.call(command.split())

# clean up
for f in os.listdir(processing_dir):
    os.remove(os.path.join(processing_dir, f))