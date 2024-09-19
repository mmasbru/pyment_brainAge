import os as os
import tarfile as tf
import shutil
import yaml 
import argparse as argparse
import logging

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Run pyment pre-processing')
parser.add_argument("-t", "--tarFile", help="FreeSurfer tar file for sub", required=True, nargs=1)
args = parser.parse_args()

tarFile = args.tarFile[0]

config='config.yaml'

with open(config) as y_file:
    proj_parameters = yaml.safe_load(y_file)

y_file.close()

tarDir = proj_parameters['tarDir']
oDir = proj_parameters['oDir']

#create output folder, if not already exists
if not os.path.exists(oDir):
    os.makedirs(oDir)

#set endswith string for tar extractor
ew = ('brainmask.mgz')

#get members from tar file
def get_members(members):
    for tarinfo in members:
        if tarinfo.name.endswith(ew):
            yield tarinfo

#extract brainmask 
def extractTar(tarFile):
    tarBase = tarFile.strip('.tar.gz')
    oFile = os.path.join(oDir, os.path.basename(tarBase))
    if tarFile.endswith('tar.gz') and not os.path.exists(oFile) and not os.path.exists(os.path.join(tarDir, tarBase)):
        print('processing: ', tarFile) 
        tarFile = os.path.join(tarDir, tarFile)
        t = tf.open(tarFile)
        t.extractall(path = oDir, members=get_members(t))
        t.close()
    else:
        print('Skipping: ', tarFile, '   Not a Tar file or already extracted...')
    return oFile

#set full path to tar file
tarFile  = os.path.join(tarDir, tarFile)
#extract brainmask, set subjDir after successful extraction
#logging.info('extracting tarFile %s', tarFile)
#subjDir = extractTar(tarFile)
###change for GenR.
tarBase = tarFile.strip('.tar.gz')
subjDir = os.path.join(oDir, os.path.basename(tarBase))

#from here on out, we follow this tutorial
#https://github.com/estenhl/pyment-public

#convert brainmask mgz to nii.gz
#import modules
from pyment.utils.preprocessing import convert_mgz_to_nii_gz
#set nifti dir
niiDir = os.path.join(oDir, 'nifti')
#create it if not already there
if not os.path.exists(niiDir):
    os.makedirs(niiDir)

#set the input file brainmask.mgz
iFile = os.path.join(subjDir, 'mri', 'brainmask.mgz')
#set the output file, nii.gz extension
oFile = os.path.join(niiDir, os.path.basename(subjDir) + '.nii.gz')
#run conversion if not done
if not os.path.exists(oFile):
    logging.info('Converting to nii %s', iFile)
    convert_mgz_to_nii_gz(iFile, oFile)
    #remove the stuff extacted by tar file extractor
    shutil.rmtree(subjDir)

#reorient to std space
from pyment.utils.preprocessing import reorient2std
#set reorient dir
reoDir = os.path.join(oDir, 'reoriented')
#if not present, make it
if not os.path.exists(reoDir):
    os.makedirs(reoDir)

#set the input file to the previous output file
iFile = oFile
#set output file to reoriented folder
oFile = os.path.join(reoDir, os.path.basename(iFile))
#run reorientation if not already done
if not os.path.exists(oFile):
    logging.info('reorienting to std space %s', iFile)
    reorient2std(iFile, oFile)
    #get rid of intermediate step file
    os.remove(iFile)

#run flirst, 6dof to mni space
from pyment.utils.preprocessing import flirt
#set mni template folder
mni_template = os.path.join('/home/genr/software/fsl/6.0.5.1', 'data', 'linearMNI', 
                            'MNI152lin_T1_1mm_brain.nii.gz')

#set output folder and make if not existing
mniDir = os.path.join(oDir, 'mni152')
if not os.path.exists(mniDir):
    os.makedirs(mniDir)

#set the input file to the previous output file
iFile = oFile
#set output file to the mni folder
oFile = os.path.join(mniDir, os.path.basename(iFile))
#run flirt 6dof if not alredady done
if not os.path.exists(oFile):
    logging.info('6dof to mni space %s', iFile)
    flirt(iFile, oFile, template = mni_template)
    #remove intermediate file when done
    os.remove(iFile)

#last step, crop out the background pixels
from pyment.utils.preprocessing import crop_mri
cropDir = os.path.join(oDir, 'cropped', 'images')
if not os.path.exists(cropDir):
    os.makedirs(cropDir)

iFile = oFile
oFile = os.path.join(cropDir, os.path.basename(iFile))
bounds = ((6, 173), (2, 214), (0, 160))

if not os.path.exists(oFile):
    logging.info('cropping scan... %s', iFile)
    crop_mri(iFile, oFile, bounds)
    os.remove(iFile)

