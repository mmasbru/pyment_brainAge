#!/bin/bash


iDir=/gpfs/nvme1/0/genr/data/pyment/data/genr

for i in `ls $iDir/cropped/images|grep sub|grep nii` ; do
	sub=`echo $i |awk -F.nii '{print $1}'`
	ses=`echo $sub |awk -F_ '{print $2}'`
	case $ses in
		ses-F05)
			age=`more f05.age.csv |grep ${sub} |awk -F, '{print $4}'`
			;;
		ses-F09)
		        age=`more f09.age.csv |grep ${sub} |awk -F, '{print $4}'`
			;;
		ses-F13)
                        age=`more f13.age.csv |grep ${sub} |awk -F, '{print $4}'`
			;;
			*)
			continue
			;;
	esac
	echo ${sub},${age} >> labels.csv
done

