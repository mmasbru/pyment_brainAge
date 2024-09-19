# pyment_brainAge
pyment BrainAge examples


# Getting Started

See here for getting started with Pyment:
https://github.com/estenhl/pyment-public?tab=readme-ov-file

# Basic Steps

1.) Process your data through freesurfer if you haven't already. technically you only need to run autorecon-1, as you need the brainmask.mgz file from freesurfer.

2.) Run the "preprocess" code. The main code is preprocess.py. this follows the steps from the original pyment repo. This python code is called by process.sh, which is called by a slurm job script. The input here is a tar.gz file (we tar our freesurfer output to reduce file counts), so you can also simply input a freesurfer folder and remove the un-tar commands.

3.) run the predict code....this is a predict.py script which is called by predict.job, a slurm job script. 

# general notes

you will notice the job scripts and the sh/py code also rely on a config.yaml file. you can simply hard code those things in the code if you like to simplify.  Further, you will notice the job scripts utilize the array functionality of slurm. We use setup_slurm_array.py to create a text file with "tasks" to feed to the slurm job. For this script, that is a simple text file with 1 line per "task" (particpant dataset/tar.gz file). The setup_slurm_array.py takes this text file as an input, and adds additional info, that can then be parsed by the slurm scheduler.  


Running for example looks like:
sbatch --array=1-100 preprocess.job

The ${A} variable inside of the job script will inherit the slurm array ID (1, 2, ..., 100) to help distribute the tasks across the compute.  Our nodes are 192 cores in size, and thus ${J} can be ~192 in size. you can of course skip all of this and run in serial....




