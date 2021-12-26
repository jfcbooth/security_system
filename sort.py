import json
import argparse
import os
import shutil
import cv2
import sys
'''
Sorts images into folders for indexing based on the category discoverted (vehicle, human, animal). In the event of two categories, vehicle gets priority, then person, then animal.
'''

# input file: /security_system/media/unevaluated/.evaluating/test.mp4
# input json json: /security_system/media/unevaludated/.evaluating/test.mp4.json
output_base_dir = '/mnt/c/Users/user/Desktop/security_system/media/'
categories = {'1': 'animal', '2': 'person', '3': 'vehicle'}


def find_category(json_file):
    category = 0
    fp = open(json_file)
    data = json.load(fp)
    fp.close()
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="Video file")
    ap.add_argument("json", help="JSON file")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print("Error: File not found")
        sys.exit(-1)
    if not os.path.exists(args.json):
        print("Error: JSON not found")
        sys.exit(-1)

    category = find_category(args.json)
    print("Max category was: {}, or {} for {}".format(category, categories[str(category)], args.json))


    # Stitch together detections into proper folder
    to_video('/tmp/process_camera_trap_video/'+ os.path.basename(args.file) + '_detections/', output_base_dir + categories[str(category)] + '/' + os.path.splitext(os.path.basename(args.file))[0] + '_detections.mp4', args.file)

    # Move original video into folder
    src = args.file
    dest = 'media/' + categories[str(category)] + '/originals/'
    print("Moving {} to {}".format(src, dest))
    shutil.move(src, dest)

    # send email

    # Remove detections
    shutil.rmtree('/tmp/process_camera_trap_video/' + os.path.basename(args.file) + '_detections')
    # Remove frames
    shutil.rmtree('/tmp/process_camera_trap_video/' + os.path.basename(args.file) + '_frames')
    # Remove json file
    os.remove(output_base_dir + '/unevaluated/.evaluating/' + os.path.basename(os.path.basename(args.file)) + '.json')
