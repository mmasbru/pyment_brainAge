import os
import argparse
import subprocess
import nibabel as nib
from typing import Tuple

#wd_in = '/home/mireia/Desktop/00_DataProva/'
#wd_log = '/home/mireia/Desktop/01_PreprocessedData/log_file.txt'
#wd_ref = '/home/mireia/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz' 
#wd_out = '/home/mireia/Desktop/01_PreprocessedData/'

def mgz2nii(wd_mgz:str, wd_log:str) -> str: 
    """mgz to nii converter using mri_convert.
    INPUTS: 
        - wd_mgz: path to mgz file of interest.
        - wd_log: path to control error file. 
    OUTPUT: 
        - wd_out: path to transformed nii file.
    """
    name, ext = os.path.splitext(wd_mgz)
    wd_out = name+'.nii.gz'
    cmd = 'mri_convert {} {}'.format(wd_mgz, wd_out)

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("Command Output:\n", result.stdout)

    if result.stderr:
        # Open the file in append mode
        with open(wd_log, "a") as log_file:  # Specify your file path here if needed
            log_file.write(f"Error converting {wd_mgz}:\t")
            log_file.write(result.stderr + "\n")
        print(f"Error logged for {wd_mgz}")

    return(wd_out)

def reo2std(wd_nii:str, wd_log:str) -> str:
    """Reorient images 2 std position. Based on fsl.
    INPUTS: 
        - wd_nii: path to .nii file.
    OUTPUT: 
        - wd_nii: path to .nii file, which is now reoriented 2 std.
    """

    cmd = 'fslreorient2std {} {}'.format(wd_nii, wd_nii)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("Command Output:\n", result.stdout)

    if result.stderr:
        # Open the file in append mode
        with open(wd_log, "a") as log_file:  # Specify your file path here if needed
            log_file.write(f"Error orienting {wd_nii}:\t")
            log_file.write(result.stderr + "\n")
        print(f"Error logged for {wd_nii}")
    
    return(wd_nii)

def nii2mni(wd_nii:str, wd_ref:str, wd_log:str) -> str: 
    """Rigidly register nii images to MNI space.
    INPUTS: 
        - wd_nii: path to .nii file. 
        - wd_red: path to .nii template file. 
        - wd_log: path to log file.
    OUTPUT:
        - wd_out: path to mni registered file."""
    
    root, file = os.path.split(wd_nii)
    wd_out = os.path.join(root, 'brainmask2nii.nii.gz')
    cmd = 'flirt -in {} -ref {} -out {} -dof 6'.format(wd_nii, wd_ref,wd_out)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("Command Output:\n", result.stdout)

    if result.stderr:
        # Open the file in append mode
        with open(wd_log, "a") as log_file:  # Specify your file path here if needed
            log_file.write(f"Error registering {wd_nii}:\t")
            log_file.write(result.stderr + "\n")
        print(f"Error logged for {wd_nii}")
    
    return(wd_out)

def crop_mri(wd_nii:str, wd_out:str, bounds:Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]], wd_log:str) -> str:
    """Crop mri image according to bounds. 
    INPUTS: 
        - wd_nii: path to mni-registered nii image.
        - wd_out: path to export all cropped images.
        - bounds: bounds for each direction cropping.
"""
    
    try:
        img = nib.load(wd_nii)
        data = img.get_fdata()

        subj = wd_nii.split('/')[-3]
        wd_out = os.path.join(wd_out, subj+'.nii')

        cropped_data = data[bounds[0][0]:bounds[0][1], 
                            bounds[1][0]:bounds[1][1], 
                            bounds[2][0]:bounds[2][1]]

        cropped_img = nib.Nifti1Image(cropped_data, img.affine, img.header)
        nib.save(cropped_img, wd_out)

    except Exception as e: 
        with open(wd_log, "a") as log_file: 
            log_file.write(f"Error cropping {wd_nii}:\t")
            log_file.write(e + "\n")
        print(f"Error logged for {wd_nii}")
    
    return(wd_out)

def main(wd_in: str, wd_log: str, wd_ref: str, wd_out: str, bounds: Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int]]):
    """Main function to process MRI images."""
    for root, dirs, files in os.walk(wd_in):
        file = [file for file in files if 'brainmask.mgz' in file]
        if file:
            try:
                wd_mgz = os.path.join(root, file[0])
                wd_nii = mgz2nii(wd_mgz, wd_log)
                wd_reo = reo2std(wd_nii, wd_log)
                wd_reg = nii2mni(wd_reo, wd_ref, wd_log)
                crop_mri(wd_reg, wd_out, bounds, wd_log)

            except Exception as e: 
                with open(wd_log, "a") as log_file: 
                    log_file.write(f"Error in file {file}:\t")
                    log_file.write(e + "\n")
                print(f"Error logged for {file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run T1w preprocessing for BrainAge use.')
    parser.add_argument('-i', '--input', help='Input directory containing .mgz files.', required=True)
    parser.add_argument('-r', '--ref', help='Path to MNI reference file.', required=True)
    parser.add_argument('-o', '--output', help='Output directory for processed files.', required=True)
    args = parser.parse_args()

    # Define cropping bounds
    bounds = ((6, 173), (2, 214), (0, 160))
    log = os.path.join(args.output, 'log.txt')
    main(args.input, log, args.ref, args.output, bounds)