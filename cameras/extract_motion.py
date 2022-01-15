import argparse
import os
import re
import sys
import datetime
import subprocess
import tempfile
import logging
import shutil

def filename2numbers(filename):
    return int(''.join(os.path.splitext(os.path.basename(filename))[0].split('_')[2:]))

def filename2datetime(filename):
    numbers = str(filename2numbers(filename))
    return datetime.datetime(int(numbers[0:4]), int(numbers[4:6]), int(numbers[6:8]), int(numbers[8:10]), int(numbers[10:12]), int(numbers[12:14]))

def to_datetime(time):
    time = str(time)
    return datetime.datetime(int(time[0:4]), int(time[4:6]), int(time[6:8]), int(time[8:10]), int(time[10:12]), int(time[12:14]))

def make_dirs(dirs):
    for dir in dirs:
        if not os.path.exists(dir):
            os.mkdir(dir)

def motionlog2datetime(motionlog_entry):
    split = re.split('{|}|/|:|\s',motionlog_entry)
    return datetime.datetime(int(split[1]), int(split[2]), int(split[3]), int(split[4]), int(split[5]), int(split[6]))

def check_motionlog_entry(motion_log_entries):
    if 'Motion start detected' in motion_log_entries[0] and 'Motion start detected' in motion_log_entries[1]:
        return 1
    if not ('Motion start detected' in motion_log_entries[0] and 'Motion stop detected' in motion_log_entries[1]):
        return -1
    return 0

def seconds_from_epoch(time):
     return (time - datetime.datetime(1970, 1, 1)) / datetime.timedelta(seconds=1)

def get_hostname(hostname_file):
    try: 
        data = open(hostname_file, 'r').read().rstrip()
    except:
        logging.critical("Hostname file couldn't be read")
        return "hostnameError"
    return data

def get_video_length(input_video):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)

ap = argparse.ArgumentParser()
ap.add_argument("motion_file")
ap.add_argument("--dry_run")
args = ap.parse_args()

home_dir = os.path.split(args.motion_file)[0]
media_dir = os.path.join(home_dir, 'media/')
motion_dir = os.path.join(home_dir, 'motion/')
motion_log_dir = os.path.join(home_dir, 'motion_logs/')
processing_dir = os.path.join(media_dir, '.processing/')
logname = 'python_motion.log'

# setup logger
file_handler = logging.FileHandler(filename=logname)
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.INFO, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

try:
    make_dirs([media_dir, motion_dir, motion_log_dir])
except:
    logging.critical("Directories unable to be made")

# move log file to somewhere it can be manipulated
motion_log_file = os.path.join(motion_log_dir, datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + '_motionLog.txt')
if not args.dry_run:
    shutil.move(args.motion_file, motion_log_file)
else:
    motion_log_file = args.motion_file

try:
    fp = open(motion_log_file, 'r+')
    data = [x for x in fp.read().replace('\x00', '').split('\n') if x != '']
except:
    logging.error("Motion file not found")
    sys.exit()

if(len(data) % 2 != 0):
    logging.warning("Data length is an odd number, bad data somewhere in log.")

while len(data) > 0: # while there is an even number of lines and there is data
    
    video_files = [os.path.join(media_dir,x) for x in os.listdir(media_dir) if x.endswith('.mp4')]

    motion_times = data[:2] # time length to extract

    # check for abnormal motion logs
    if check_motionlog_entry(motion_times) == 1:
        logging.warning("Double start event detected at 0: {} and 1: {}. Moving to next entry.".format(motion_times[0], motion_times[1]))
        data = data[1:] # fix data then restart loop
        continue
    elif check_motionlog_entry(motion_times) == -1:
        logging.critical("Bad motion log entries 0: {} and 1: {}".format(motion_times[0], motion_times[1]))
        sys.exit()

    motion_start_time = motionlog2datetime(motion_times[0])
    motion_end_time = motionlog2datetime(motion_times[1])
    logging.debug("Data len: {}, Motion start time: {}, Motion end time: {}".format(len(data), motion_start_time, motion_end_time))

    # get video files that fall in time range
    video_info = {'motion_videos': [], 'start_time': None, 'stop_time': None}
    for i in range(len(video_files)):
        if motion_start_time >= filename2datetime(video_files[i]) and motion_end_time < filename2datetime(video_files[i]) + datetime.timedelta(seconds=get_video_length(video_files[i])):
            video_info['motion_videos'].append(video_files[i])

    if len(video_info['motion_videos']) == 0:
        logging.critical("No videos found in the time range. Skipping entry.")
        data = data[2:]
        continue

    logging.debug("Videos found for time range: {}".format(video_info['motion_videos']))

    # combine video files in motion occurs in multiple clips
    if len(video_info['motion_videos']) > 1:
        try:
            combined_videos = open(os.path.join(processing_dir, 'videos.txt'), 'w')
        except:
            logging.critical("videos.txt is unable to be opened.")
        for f in video_info['motion_videos']:
            combined_videos.write("file {}\n".format(os.path.join(media_dir, f)))
        combined_videos.flush()
        combined_videos.close()
        # combine all videos into 1 video for splitting
        #ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.mp4
        try:
            cmd = "ffmpeg -y -f concat -safe 0 -i {} -c copy {}".format(os.path.join(processing_dir, "videos.txt"), os.path.join(processing_dir, video_info['motion_videos'][0]))
            subprocess.call(cmd.split())
        except:
            logging.critical("Error concatenating videos")
            if not os.path.exists(os.path.join(processing_dir, video_info['motion_videos'][0])):
                logging.critical("Merged video doesn't exist. Exiting.")
                sys.exit()
        
        video_info['motion_videos'] = [os.path.join(processing_dir, video_info['motion_videos'][0])]
        logging.debug("After concatenation, vidoes in time range: {}".format(video_info))

    video_info['start_time'] = filename2datetime(video_info['motion_videos'][0])
    video_info['stop_time'] = filename2datetime(video_info['motion_videos'][-1]) + datetime.timedelta(seconds=get_video_length(video_files[i]))

    if(video_info['stop_time'] <= motion_end_time):
        logging.debug("End time too close to end of video. video_info['stop_time']: {}, motion_end_time: {}".format(video_info['stop_time'], motion_end_time))
        motion_end_time = video_info['stop_time'] - datetime.timedelta(seconds=2) # subtract 2 seconds as a buffer

    motion_start_from_epoch = seconds_from_epoch(motion_start_time)
    video_start_from_epoch = seconds_from_epoch(video_info['start_time'])
    elapsed_time = seconds_from_epoch(motion_end_time) - motion_start_from_epoch

    if not motion_start_from_epoch > video_start_from_epoch:
        logging.warning("Motion start from epoch > video start from epoch {}, {}".format(motion_start_from_epoch, video_start_from_epoch))

    start_time_offset = motion_start_from_epoch - video_start_from_epoch # the motion starts after the video, so it should always be a smaller number
    end_time_offset = start_time_offset + elapsed_time

    start_time_offset_hhmmss = str(datetime.timedelta(seconds=start_time_offset))
    end_time_offset_hhmmss = str(datetime.timedelta(seconds=end_time_offset-3)) # subtract 3 seconds for buffer


    camera_name = get_hostname('/etc/hostname')
    # hostname first
    #output_filename = os.path.join(motion_dir, camera_name + '_' + os.path.basename(video_info['motion_videos'][0]).split('_',2)[-1])
    # hostname last
    output_filename = os.path.join(motion_dir, os.path.splitext(os.path.basename(video_info['motion_videos'][0]).split('_',2)[-1])[0] + '_' + camera_name + '.mp4')

    # input file, start time, end time, output file, times need to be in HH:MM:SS form
    # formats: HH:MM:SS for start of video
    #ffmpeg -i ORIGINALFILE.mp4 -acodec copy -vcodec copy -ss 00:15:00 -t 00:15:00 OUTFILE-2.mp4
    logging.debug("Important values: video_info['start_time']: {} video_info['stop_time']: {} motion_start_from_epoch: {} video start_from_epoch: {}\
         elapsed_time: {} start_time_offset: {} end_time_offset: {} start_time_offset_hhmmss: {}, end_time_offset_hhmmss: {}".format(\
        video_info['start_time'], video_info['stop_time'], motion_start_from_epoch, video_start_from_epoch, elapsed_time, start_time_offset, end_time_offset,\
            start_time_offset_hhmmss, end_time_offset_hhmmss))
    logging.info("Cutting {} from {} to {} to output file {}".format(video_info['motion_videos'][0], start_time_offset_hhmmss, \
        end_time_offset_hhmmss, output_filename))

    try:
        command = "ffmpeg -y -i {} -hide_banner -loglevel warning -acodec copy -vcodec copy -ss {} -to {} {}".format(video_info['motion_videos'][0], \
            start_time_offset_hhmmss, end_time_offset_hhmmss, output_filename)
        subprocess.call(command.split())
    except:
        logging.critical("Splitting video failed with command {}".format(command))

    # clean up
    for f in os.listdir(processing_dir):
        os.remove(os.path.join(processing_dir, f))

    # remove motion entry from log
    if not args.dry_run:
        logging.debug("Full motion event written. Removing {} to {} from log.".format(motion_times[0], motion_times[1]))
        fp.seek(0)
        fp.write('\n'.join(data[2:]))
        fp.truncate()
        # move to the next piece of data
        if len(data) >= 2:
            data = data[2:]
    else:
        data = []
fp.close()

# remove bad files, but keep the log
for bad_file in [os.path.join(media_dir,x) for x in os.listdir(media_dir) if x.endswith('.bad')]:
    os.remove(bad_file)