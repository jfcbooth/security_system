import json
import argparse
import os
from posixpath import basename
import shutil
import cv2
import sys
import process_video
from ct_utils import args_to_object


'''
Sorts images into folders for indexing based on the category discoverted (vehicle, human, animal). In the event of two categories, vehicle gets priority, then person, then animal.
'''

# input file: /security_system/media/unevaluated/.evaluating/test.mp4
# input json json: /security_system/media/unevaludated/.evaluating/test.mp4.json

media_dir = 'C:/Users/boothm/Desktop/security_system/media/'
uneval_dir = os.path.join(media_dir,'unevaluated/')
evaling_dir = os.path.join(uneval_dir, '.evaluating/')
categories = {'0': 'none', '1': 'animal', '2': 'person', '3': 'vehicle'}


def find_category(json_file):
    category = 0
    fp = open(json_file)
    data = json.load(fp)
    fp.close()
    # 0 = none
    # 1 = animal
    # 2 = human
    # 3 = vehicle
    for image in data['images']:
        for detection in image['detections']:
            if(int(detection['category']) > category):
                    category = int(detection['category'])
    return(category)

def to_video(image_folder, output_file, original_video_file):
    print("image folder: {}".format(image_folder))
    print("output_file: {}".format(output_file))
    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    images.sort()
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    # find FPS
    cap = cv2.VideoCapture(original_video_file)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print("FPS = {}".format(fps))

    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    video = cv2.VideoWriter(output_file, fourcc, fps, (width,height))
    #print(images)
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    cv2.destroyAllWindows()
    video.release()

def find_mp4s(media_dir):
    filenames = [f for f in os.listdir(uneval_dir) if os.path.isfile(os.path.join(uneval_dir, f)) and f.lower().endswith('.mp4')] # extracts filenames
    return filenames

# views added files to the evaluation directory
def process_directory():
    files = find_mp4s(media_dir)
    for file in files:
        basename = os.path.splitext(file)[0]
        extension = os.path.splitext(file)[1]
        json_file = os.path.join(evaling_dir, file+'.json')
        detections_file = os.path.join(evaling_dir, basename+'_detections.mp4')

        shutil.move(os.path.join(uneval_dir, file), evaling_dir) # move to evaling dir to remove race condition
        
        # process video
        options = process_video.ProcessVideoOptions()
        options.model_file = 'md_v4.1.0.pb'
        options.input_video_file = os.path.join(evaling_dir, file)

        options.output_json_file = json_file
        options.output_video_file = detections_file

        options.render_output_video = True
        options.delete_output_frames = True # we manually delete them later
        options.reuse_results_if_available = False

        options.confidence_threshold = 0.8
        options.n_cores = 1

        options.debug_max_frames = -1

        process_video.process_video(options)
        
        # sort video
        # json file should always be there, even on no detections
        category = find_category(json_file)
        print("Max category was: {}, or {} for {}".format(category, categories[str(category)], json_file))

	    # make output video in correct folder
        #detections_file = os.path.join(media_dir, categories[str(category)], basename+'_detections.mp4')
        #detections_path = os.path.join(temp_dir, file + '_detections')
        if category > 0: # detections were found
            #to_video(detections_path, detections_file, os.path.join(evaling_dir, file))
    
            # move detections video into correct folder
            shutil.move(detections_file, os.path.join(media_dir, categories[str(category)]))

            # Move original video into correct folder
            shutil.move(os.path.join(evaling_dir, file), os.path.join(media_dir, categories[str(category)], 'originals/'))

            # delete json file
            os.remove(json_file)

        else:
            os.remove(os.path.join(evaling_dir, file)) # delete the motion file if nothing was in it



        



if __name__ == "__main__":
    process_directory()

    # # send email