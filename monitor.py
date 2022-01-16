import json
import argparse
import os
from posixpath import basename
import shutil
import cv2
import sys
import process_video
from ct_utils import args_to_object
from send_email import send_email
import logging
from configparser import ConfigParser

'''
Sorts images into folders for indexing based on the category discoverted (vehicle, human, animal). In the event of two categories, vehicle gets priority, then person, then animal.
'''

def find_category(json_file): # returns int of category
    if not os.path.exists(json_file):
        return 0
    category = 0
    fp = open(json_file)
    data = json.load(fp)
    fp.close()
    for image in data['images']:
        for detection in image['detections']:
            if(int(detection['category']) > category):
                    category = int(detection['category'])
    return(category)

def find_video_files():
    allowed_video_formats = ('.mp4', '.webm')
    filenames = [f for f in os.listdir(uneval_dir) if os.path.isfile(os.path.join(uneval_dir, f)) and f.lower().endswith(allowed_video_formats)] # extracts filenames
    return filenames

# views added files to the evaluation directory
def process_directory():
    files = find_video_files()
    for file in files:
        basename = os.path.splitext(file)[0]
        json_file = os.path.join(uneval_dir, file+'.json')
        detections_file_basename = basename+'_detections.mp4'
        detections_file = os.path.join(uneval_dir, detections_file_basename)

        # move to evaling dir to remove race condition
        #shutil.move(os.path.join(uneval_dir, file), evaling_dir)
        
        # set process video options
        options = process_video.ProcessVideoOptions()
        options.model_file = model_file
        options.input_video_file = os.path.join(uneval_dir, file)

        options.output_json_file = json_file
        options.output_video_file = detections_file

        options.render_output_video = True
        options.delete_output_frames = True # we manually delete them later
        options.reuse_results_if_available = False

        options.confidence_threshold = 0.8
        options.n_cores = 4

        options.debug_max_frames = 3

        # process the video
        process_video.process_video(options)
        
        # sort video

        # json file should always be there, even on no detections
        category = find_category(json_file)
        logging.info("Max category was: {}, or {} for {}".format(category, categories[str(category)], json_file))

	    # make output video in correct folder

        if category == 0: # no detections were found
            os.remove(os.path.join(uneval_dir, file)) # delete the motion video file if nothing was in it
            os.remove(json_file) # remove json file
            os.remove(detections_file) # remove detections if it exists
        else:
            # Move original video into correct folder
            shutil.move(os.path.join(uneval_dir, file), os.path.join(media_dir, categories[str(category)], file))
            
            # move detections video into correct folder
            shutil.move(detections_file, os.path.join(media_dir, categories[str(category)], 'detections/', detections_file_basename))
    
            # delete json file
            os.remove(json_file)

            if(category > email_category_threshold): # send email if a concerning category, normally > 1
                hosted_file_location = os.path.join(server_ip, categories[str(category)], file).replace("\\","/")
                detections_file_location = os.path.join(server_ip, categories[str(category)], 'detections/', detections_file_basename).replace("\\","/")
                send_email(categories[str(category)], hosted_file_location, detections_file_location, email_config)

def check_dirs():
            # puts all directories into a single list
    dirs = [media_dir, uneval_dir] + \
            [os.path.join(media_dir, x[1]) for x in categories.items() if x[1] != 'none'] + \
            [os.path.join(media_dir, x[1], 'detections/') for x in categories.items() if x[1] != 'none']
        
    for dir in dirs:
        if not os.path.exists(dir):
            try:
                os.mkdir(dir)
                logging.info("Directory: {} not found. Created.".format(dir))
            except:
                logging.critical("Unable to make directory {}. Exiting.".format(dir))
                sys.exit(-1)

def clean_unevaluated_dir():
    filenames = [f for f in os.listdir(uneval_dir)]
    for filename in filenames:
        if not (filename.endswith(".mp4") and not 'detections' in filename):
            os.remove(filename)
            logging.debug("Removed {}".format(filename))
        

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("conf_file")
    args = ap.parse_args()

    config = ConfigParser()
    config.read(args.conf_file)

    logname = config.get('server', 'logfile')
    media_dir = config.get('server', 'media_dir')
    server_ip = config.get('server', 'server_ip')
    email_category_threshold = config.get('server', 'email_category_threshold')
    uneval_dir = os.path.join(media_dir,config.get('server', 'uneval_dir'))
    model_file = config.get('server', 'model_file')

    categories = dict(config.items('categories'))

    email_config = dict(config.items('email'))

    # setup logger
    file_handler = logging.FileHandler(filename=logname)
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.DEBUG, 
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers
    )

    check_dirs()
    clean_unevaluated_dir()
    process_directory()