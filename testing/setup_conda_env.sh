wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
conda env create -f CameraTraps/environment-detector.yml
conda activate cameratraps-detector
cp -r CameraTraps/* ~/miniconda3/envs/cameratraps-detector/lib/python3.7/site-packages/
cp -r ai4eutils/* ~/miniconda3/envs/cameratraps-detector/lib/python3.7/site-packages/

