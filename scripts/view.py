"""Script to open the scans in sequence and register if passed or not in QC analysis

This script identifies the subjects present in the folder set in SUBJECTS_DIR environment variable. 
Using this list, it automatically opens freeview and asks the user input for the result of QC analysis.
Results are saved in manual_QC.txt file.

This file can also be imported as a module and contains the following
functions:

    * get_subjects - returns a list of subjects inside the folder.
    * freeview - returns a freeview command formated as string

"""

import os
import subprocess
import sys

def get_subjects(subjects_dir=os.environ['SUBJECTS_DIR']):
    """
    Returns a list of subjects inside the folder.

    Parameters
    ----------
    subjects_dir : str, default=os.environ['SUBJECTS_DIR']
        FreeSurfer SUBJECTS_DIR.

    Returns
    -------
    list

    """
    
    subjects = os.listdir(subjects_dir)
    
    ignore = [".gitignore","fsaverage",".DS_Store","thumbs.db","desktop.ini"]
    for file in ignore:
        try:
            subjects.remove(file)
        except ValueError:
            pass
    
    return subjects

def freeview(subject_id: str):
    """
    Returns a freeview command formated as string.

    Parameters
    ----------
    subject_id : str
        FreeSurfer subject_id.

    Returns
    -------
    str

    """
    
    subject_path = os.path.join(os.environ['SUBJECTS_DIR'], subject_id)
    return (f"freeview -v {subject_path}/mri/T1.mgz " 
     f"{subject_path}/mri/wm.mgz " 
     f"{subject_path}/mri/brainmask.mgz " 
     f"{subject_path}/mri/aseg.mgz:colormap=lut:opacity=0.2 " 
     f"-f {subject_path}/surf/lh.white:edgecolor=blue "
     f"{subject_path}/surf/lh.pial:edgecolor=red "
     f"{subject_path}/surf/rh.white:edgecolor=blue "
     f"{subject_path}/surf/rh.pial:edgecolor=red")

if __name__ == '__main__':
    
    subjects = get_subjects()
    if os.path.exists("manual_QC.txt"):
        print("Manual QC file found. Checking subjects...")
        with open("manual_QC.txt", 'r') as file:
            lines = file.readlines()        
        already_evaluated = [line.split("\t")[0] for line in lines]
        subjects = list(set(subjects).difference(already_evaluated))
    
    for subject in subjects:
        try:
            print(f"SUBJECT: {subject}")
            subprocess.run(freeview(subject).split())
        except FileNotFoundError:
            print(f"FileNotFoundError: {os.path.join(os.environ['SUBJECTS_DIR'], subject)} No such file or directory.\nCheck if SUBJECTS_DIR environment variable is correctly set and if the path name doesn't contain spaces.")
            sys.exit(1)
        
        while True:
            qc_status=input("Passed quality control? [Y/N]: ")
            comments=input("Type any observations: ")
            if qc_status.upper() not in ['Y','N']:
                print("Please answer with Y or N")
                continue
            else:
                break
        
        with open("manual_QC.txt", "a") as file:
            file.write(f"{subject}\t{qc_status.upper()}\t{comments}\n")
        