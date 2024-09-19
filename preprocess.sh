#!/bin/bash

if [ $# -ne 1 ] ; then
    echo "must specify tar file"
    exit
fi

tarFile=${1}

config=config.yaml

shDir=$(grep shDir ${config} |awk '{print $2}')
config=${shDir}/config.yaml

moduleYear=`more ${config}|grep moduleYear |awk '{print $2}'`
fslRootDir=`more ${config}|grep FSL_ROOT_DIR |awk '{print $2}'`
fslVersion=`more ${config}|grep fslVersion |awk '{print $2}'`
FREESURFER_HOME=`more ${config}|grep FREESURFER_HOME |awk '{print $2}'`

module load ${moduleYear}
module load Python/3.10.4-GCCcore-11.3.0
export PYTHONPATH=${PYTHONPATH}:/home/genr/software/pyment-public

export FREESURFER_HOME
source ${FREESURFER_HOME}/SetUpFreeSurfer.sh

FSLDIR=${fslRootDir}/${fslVersion}
source ${FSLDIR}/etc/fslconf/fsl.sh
export PATH=${PATH}:${FSLDIR}/bin

python3 ${shDir}/preprocess.py -t ${tarFile}
