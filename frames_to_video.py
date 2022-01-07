import cv2

#%% Function for rendering frames to video and vice-versa

# http://tsaith.github.io/combine-images-into-a-video-with-python-3-and-opencv-3.html

def frames_to_video(images, Fs, output_file_name, codec_spec='h264'):
    """
    Given a list of image files and a sample rate, concatenate those images into
    a video and write to [output_file_name].
    """
    
    if len(images) == 0:
        return

    # Determine the width and height from the first image
    frame = cv2.imread(images[0])
    #cv2.imshow('video',frame)
    height, width, channels = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*codec_spec)
    out = cv2.VideoWriter(output_file_name, fourcc, Fs, (width, height))

    for image in images:
        frame = cv2.imread(image)
        out.write(frame)

    out.release()
    cv2.destroyAllWindows()