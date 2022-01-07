# Setup

## Server side setup
This setup is fairly in-depth since the project specifiecations wanted a windows machine to be the server. THis requires a lot of workarounds, though most of elegant.  
1. Install [miniconda](https://docs.conda.io/en/latest/miniconda.html#windows-installers) and create environment (`conda env create -f environment-detector.yml`)
2. Clone [CameraTraps](https://github.com/microsoft/CameraTraps) and [ai4eutils](https://github.com/microsoft/ai4eutils) and move them into the anaconda environment (`cp -r CameraTraps/* ai4eutils/* ~/miniconda3/envs/cameratraps-detector/Lib/site-packages/`)
3. Download model [here](https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb), more info on the [Megadetector github page](https://github.com/microsoft/CameraTraps/blob/master/megadetector.md)
4. Install apache server. I used [Apache Lounge](https://www.apachelounge.com/download/) (set folder in httpd.conf) and enable start on boot (`Set-Service -Name Apache2.4 -StartupType 'Automatic'` from admin powershell)
5. Install [cygwin](https://www.cygwin.com/) with rsync package and add bin to the path `C:\cygwin64\bin`
6. Install openssh for windows by running the below commands in an admin powershell:
	1. Check if it's installed: `Get-WindowsCapability -Online | ? Name -like 'OpenSSH*'`
	2. If not, install it: `Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0`
	3. Start service: `Start-Service sshd`
	4. Check if its running: `Get-Service sshd`
	5. Set to automatically start: `Set-Service -Name sshd -StartupType 'Automatic'`
7. Test rsync installation

## Rpi setup
1. Install raspian lite
2. Install rpi cam web interface
3. Enable camera
4. Enable ssh
5. Write to wpa_supplicant
6. Give static IP
7. Setup config file
8. clone repo
9. run daemons
10. set hostname

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
1. Setup actual server with needed software
2. Setup cameras to sync folder with windows
3. Make cameras record constantly
4. Setup way to pause cameras overwriting data
5. Streamline camera setup

# Cameras code:
Command to move from remote system to local system, and delete file from remote system if necessary
`rsync --compress --remove-source-files --progress --partial --partial-dir=.rsync_partial/ /home/user/send/* user@172.31.203.75:/mnt/c/Users/user/Desktop/security_system/unevaluated/`
`ssh-keygen -t rsa` - generate RSA keys, then add the public key to the host machine under `~/.ssh/authorized_keys`

After setting up ssh transfers, setup a crontab job for monitor.sh, which will handle moving the images into unevaluated/ without having to worry about race conditions and monitoring. monitor.sh waits 1 minute after the program was written to, just to make sure it is done. This stops rsync from transferring a partially written to file and isn't timer-based, which stops rsync from restarting or waiting so long before starting.
