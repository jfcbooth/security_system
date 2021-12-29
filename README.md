# Setup

To make this work, you need to setup both the server side and camera side.
## Server side installations
1. Clone [CameraTraps](https://github.com/microsoft/CameraTraps)
2. Clone [ai4eutils](https://github.com/microsoft/ai4eutils)
3. Download model [here](https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb), more info on the [Megadetector github page](https://github.com/microsoft/CameraTraps/blob/master/megadetector.md)
4. Install miniconda
5. Install cameratraps-detector environment in Cameratraps
6. Put libraries into conda environment: `cp -r CameraTraps/* ~/miniconda3/envs/cameratraps-detector/lib/python3.7/site-packages/
cp -r ai4eutils/* ~/miniconda3/envs/cameratraps-detector/lib/python3.7/site-packages/`
7. Set media directory in `monitor.py`
8. Setup apache server (set installation directory in httpd.conf) and install as a service


# security_system

This repo will serve to document my progress on building a cheap security system for my uncle.

As of Dec. 18th 2021, the workflow will go as follows:
1. Setup cheap motion detecting cameras throughout his kansas property using solar panels for power.
The property will have weak wifi, so we need to limit video throughput as much as possible

2. Video that has motion is transferred back to the central hub (hopefully just a GPU-enabled computer on his property) and the video is evaluated. It will be sorted into 3 categories: human, animal, vehicle, and others will be deleted

3. Notifications will be sent out appropriately depending on the videos added (mainly just humans or vehicles)

Notes:
Mark wants as much of the raw footage as possible, probably if an issue arises on his property. Most likely, we will only be able to store a week's worth of footage per camera. We should issue a command to stop recording if the footage needs to be manually collected.

# GPU support
Installation needs:
tensorflow-gpu=1.14.0
CUDA 10.0
cuDNN 7.4
nvidia driver (nvidia-smi)
To enable GPU:
Make sure tensorflow-gpu is set in the environment-detector.yml file and install the appropriate CUDA library listed here: https://www.tensorflow.org/install/source#linux


# Tasks:
1. ~~Setup the CameraTrap repo on a docker, so I don't have a dependency headache later~~
2. ~~Get the cameratrap repo to evaluate on an image to check if it's any good~~
3. ~~Setup 1 motion detecting camera~~
4. ~~feed it's footage into the cameratrap docker~~
5. ~~send emails on certain detections~~
6. attach video clip to email on detection
6. Setup camera to record and detect motion
7. daemonize sort.py
8. daemonize camera & streamline setup


12/18/21
I got the inferencing working on an image, the results turned out pretty well. I want to run it on a video and see if it can output the identified animals
One issue I had when doing video was the OpenCV library included was too old and giving an im.show() issue
To solve it, I did:
`sudo apt install libopencv-*
conda remove opencv
conda install -c conda-forge opencv=4.1.0`


Hierarchy:
/
	unevaluated/ - where all motion detected clips are sent to be run through the model
	vehicle/
		bounding_boxes/
		originals/
	human/
		bounding_boxes/
		originals/
	animal/
		bounding_boxes/
		originals/

One problem I need to make sure of is if i just check the unanalyzed folder for videos to process, will os.path.list show partial file transfers? I am going to write file_transfer_test.py to test this

# Cameras code:
Command to move from remote system to local system, and delete file from remote system if necessary
`rsync --compress --remove-source-files --progress --partial --partial-dir=.rsync_partial/ /home/user/send/* user@172.31.203.75:/mnt/c/Users/user/Desktop/security_system/unevaluated/`
`ssh-keygen -t rsa` - generate RSA keys, then add the public key to the host machine under `~/.ssh/authorized_keys`

After setting up ssh transfers, setup a crontab job for monitor.sh, which will handle moving the images into unevaluated/ without having to worry about race conditions and monitoring. monitor.sh waits 1 minute after the program was written to, just to make sure it is done. This stops rsync from transferring a partially written to file and isn't timer-based, which stops rsync from restarting or waiting so long before starting.
