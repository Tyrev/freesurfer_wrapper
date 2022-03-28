"""Script to create recon input tables

This file can also be imported as a module and contains the following
functions:

    * create_recon_all_input - creates the recon-all input table.
    * create_recon_base_input - creates the recon-all base input table.
    * create_recon_long_input - creates the recon-all base input table.

"""

import sys
import argparse
import os
from glob import glob
import pandas as pd
from datetime import datetime

# Folder organization is assumed to be in the following ADNI format:
# ADNI/ALL_SUBJECTS/MP-RAGE/ALL_TIME_POINTS/SESSION_ID/FIRST_DCM_FILE

def argument_parser(args: list) -> "ArgumentParser.parse_args":
    """
    Parser for command-line options, arguments and sub-commands.
    
    Parameters
    ----------
    args : list
        Command-line arguments list

    Returns
    -------
    Parser
    
    """

    parser = argparse.ArgumentParser(description="Command-line script to create recon inputs.")
    subparsers = parser.add_subparsers(dest="command")

    all = subparsers.add_parser('all', help='Create input for recon-all [CROSS].')
    all.add_argument('-i', '--input', type=str, help='Path to directory containing the samples.', required=True)
    
    base = subparsers.add_parser('base', help='Create input for recon-all [BASE].')
    base.add_argument('-i', '--input', type=str, help='Path to recon_all_input.txt file used for cross processing.', required=True)
    
    long = subparsers.add_parser('long', help='Create input for recon-all [LONG].')
    long.add_argument('-i', '--input', type=str, help='Path to recon_all_input.txt file used for cross processing.', required=True)
    
    return parser.parse_args()

def create_recon_all_input(base_dir: str):
    """
    Creates a 6 column text file to be used as input for the main script recon-all command.
    First column: unique ID (combines SUBJECT ID and SESSION ID).
    Second column: SUBJECT ID.
    Third column: SESSION ID.
    Fourth column: Scan date.
    Fifth column: Time point relative to the ones contained in the subject folder.
    Sixth column: path to DICOM file.

    Parameters
    ----------
    base_dir : str
        Path to directory containing the samples.

    Returns
    -------
    None

    """
    
    df_input = pd.DataFrame()
    
    base_dir = base_dir.split('/')[0]
    subjects_dir = os.listdir(base_dir)
    
    for subject in subjects_dir:
        time_points = glob(os.path.join(base_dir,subject,'*','*'))
        time_points.sort(key=lambda x: datetime.strptime(x.split('/')[-1], '%Y-%m-%d_%H_%M_%S.%f'))
        
        for visit,tp in enumerate(time_points):
            session = os.listdir(tp)
            assert len(session) == 1, "More than one session per date"
            session = session[0]
            time_str = tp.split('/')[-1]
            dcm_path = glob(os.path.join(tp, session, '*_1_*'))
        
            df_temp = pd.DataFrame()
            df_temp['id'] = pd.Series(f"{subject}_{session}")
            df_temp['subject'] = pd.Series(subject)
            df_temp['session'] = pd.Series(session)
            df_temp['date'] = pd.Series(time_str)
            df_temp['visit'] = pd.Series(visit+1)
            df_temp['dcm_path'] = pd.Series(dcm_path)
            
            df_input = pd.concat([df_input, df_temp])
            
    df_input.to_csv("recon_all_input.txt", sep="\t", index=False, header=True)
    

def create_recon_base_input(recon_input: str):
    """
    Creates a single column text file to be used as input for the main script recon-all base command.
    Each line is a complete command to execute.

    Parameters
    ----------
    recon_input : str
        Path to recon_all_input.txt file used for cross processing.

    Returns
    -------
    None

    """
    
    df_recon = pd.read_csv(recon_input, sep="\t", index_col=False)
    subjects = df_recon['subject'].unique()
    base_commands = list()
    for subject in subjects:
        subject_tp = df_recon[df_recon['subject']==subject]
        subject_tp = subject_tp.reset_index()
        subject_tp.sort_values(by=['visit'], ascending=True, inplace=True)
        tp_flags = ' '.join([f"-tp {subject_tp.iloc[tp]['id']}" for tp in range(len(subject_tp))])
        base_commands.append(f"recon-all -base {subject} {tp_flags} -all")
    
    with open('recon_base_input.txt', 'w') as f:
        f.write("\n".join(str(cmd) for cmd in base_commands))
            
    
def create_recon_long_input(recon_input: str):
    """
    Creates a single column text file to be used as input for the main script recon-all long command.
    Each line is a complete command to execute.

    Parameters
    ----------
    recon_input : str
        Path to recon_all_input.txt file used for cross processing.

    Returns
    -------
    None

    """
    
    df_recon = pd.read_csv(recon_input, sep="\t", index_col=False)
    subjects = df_recon['subject'].unique()
    long_commands = list()
    for subject in subjects:
        subject_tp = df_recon[df_recon['subject']==subject]
        subject_tp = subject_tp.reset_index()
        subject_tp.sort_values(by=['visit'], ascending=True, inplace=True)
        for tp in range(len(subject_tp)):
            long_commands.append(f"recon-all -long {subject_tp.iloc[tp]['id']} {subject} -all")

    with open('recon_long_input.txt', 'w') as f:
        f.write("\n".join(str(cmd) for cmd in long_commands))
        
if __name__ == '__main__':
    args = argument_parser(sys.argv[1:])
    if args.command == 'all':
        create_recon_all_input(args.input)
    if args.command == 'base':
        create_recon_base_input(args.input)
    if args.command == 'long':
        create_recon_long_input(args.input)