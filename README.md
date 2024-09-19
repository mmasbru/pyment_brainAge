# pyment_brainAge
pyment BrainAge examples


# Getting Started

See here for getting started with Pyment:
https://github.com/estenhl/pyment-public?tab=readme-ov-file

# Basic Steps

1.) Process your data through freesurfer if you haven't already. technically you only need to run autorecon-1, as you need the brainmask.mgz file from freesurfer.

2.) Run the "preprocess" code. The main code is preprocess.py. this follows the steps from the original pyment repo. This python code is called by process.sh, which is called by a slurm job script. The input here is a tar.gz file (we tar our freesurfer output to reduce file counts), so you can also simply input a freesurfer folder and remove the un-tar commands.

3.) run the predict code....this is a predict.py script which is called by predict.job, a slurm job script. 


