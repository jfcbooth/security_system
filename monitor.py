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

'''
Sorts images into folders for indexing based on the category discoverted (vehicle, human, animal). In the event of two categories, vehicle gets priority, then person, then animal.
'''

media_dir = 'C:/Users/user/Desktop/security_system/media/'
hosted_name = 'localhost'
email_category_threshold = 0

uneval_dir = os.path.join(media_dir,'unevaluated/')
evaling_dir = os.path.join(uneval_dir, '.evaluating/')
categories = {'0': 'none', '1': 'animal', '2': 'person', '3': 'vehicle'}


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

def find_video_files(media_dir):
    allowed_video_formats = ('.mp4', '.webm')
    filenames = [f for f in os.listdir(uneval_dir) if os.path.isfile(os.path.join(uneval_dir, f)) and f.lower().endswith(allowed_video_formats)] # extracts filenames
    return filenames

# views added files to the evaluation directory
def process_directory():
    files = find_video_files(media_dir)
    for file in files:
        basename = os.path.splitext(file)[0]
        json_file = os.path.join(evaling_dir, file+'.json')
        detections_file_basename = basename+'_detections.mp4'
        detections_file = os.path.join(evaling_dir, detections_file_basename)

        # move to evaling dir to remove race condition
        shutil.move(os.path.join(uneval_dir, file), evaling_dir)
        
        # set process video options
        options = process_video.ProcessVideoOptions()
        options.model_file = 'md_v4.1.0.pb'
        options.input_video_file = os.path.join(evaling_dir, file)

        options.output_json_file = json_file
        options.output_video_file = detections_file

        options.render_output_video = True
        options.delete_output_frames = True # we manually delete them later
        options.reuse_results_if_available = False

        options.confidence_threshold = 0.8
        options.n_cores = 3

        options.debug_max_frames = 3

        # process the video
        process_video.process_video(options)
        
        # sort video

        # json file should always be there, even on no detections
        category = find_category(json_file)
        print("Max category was: {}, or {} for {}".format(category, categories[str(category)], json_file))

	    # make output video in correct folder

        if not category: # no detections were found
            os.remove(os.path.join(evaling_dir, file)) # delete the motion file if nothing was in it
        else:
            # Move original video into correct folder
            shutil.move(os.path.join(evaling_dir, file), os.path.join(media_dir, categories[str(category)], file))
            
            # move detections video into correct folder
            shutil.move(detections_file, os.path.join(media_dir, categories[str(category)], 'detections/', detections_file_basename))
    
            # delete json file
            os.remove(json_file)

            if(category > email_category_threshold): # send email if a concerning category, normally > 1
                hosted_file_location = os.path.join(hosted_name, categories[str(category)], file)
                detections_file_location = os.path.join(hosted_name, categories[str(category)], 'detections/', detections_file_basename)
                send_email(categories[str(category)], hosted_file_location, detections_file_location)

def check_dirs():
    if not os.path.exists(media_dir):
        print("Media directiory {} does not exist. Exiting.".format(media_dir))
        sys.exit(-1)

    
    
    # puts all directories into a single list
    dirs = [uneval_dir, evaling_dir] + \
            [os.path.join(media_dir, x[1]) and os.path.join(media_dir, x[1], 'detections/') for x in categories.items() if x[1] != 'none']
    
    for dir in dirs:
        if not os.path.exists(dir):
            try:
                os.mkdir(dir)
                print("Directory: {} not found. Created.".format(dir))
            except:
                print("Unable to make directory {}. Exiting.".format(dir))
                sys.exit(-1)
   

if __name__ == "__main__":
    check_dirs()
    process_directory()