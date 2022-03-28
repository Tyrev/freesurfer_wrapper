"""
Command-line wrapper tool to execute parallel runs of FreeSurfer recon-all and some pial edits algorithms.

This file can also be imported as a module and contains the following functions:

    * argument_parser -  parser for command-line options, arguments and sub-commands.
    * run_command - select and run the commands
    * worker - invokes a subprocess running the command.

"""

import argparse
import multiprocessing as mp
import subprocess
import sys
import pandas as pd


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

    parser = argparse.ArgumentParser(description="Command-line wrapper tool to execute parallel runs of FreeSurfer recon-all and some pial edits algorithms.")
    subparsers = parser.add_subparsers(dest="command")

    recon = subparsers.add_parser('recon_all', help='Run FreeSurfer recon-all [CROSS].')
    recon.add_argument('-i', '--input', type=str, help='Tab separated file. Required columns: id (unique ID), dcm_path (path to dcm/nii file).', required=True)
    recon.add_argument('-p', '--parallel', type=int, help='Number of parallel runs (default: number of CPUs).', default=mp.cpu_count())
   
    recon_base = subparsers.add_parser('recon_base', help='Run FreeSurfer recon-all [BASE].')
    recon_base.add_argument('-i', '--input', type=str, help='Path to recon_base_input.txt file used for base processing. Each line must be a command "recon-all -base <subject> -tp <unique_id> -tp <unique_id> ... -all"', required=True)
    recon_base.add_argument('-p', '--parallel', type=int, help='Number of parallel runs (default: number of CPUs).', default=mp.cpu_count())
    
    recon_long = subparsers.add_parser('recon_long', help='Run FreeSurfer recon-all [LONG].')
    recon_long.add_argument('-i', '--input', type=str, help='Path to recon_long_input.txt file used for long processing. Each line must be a command "recon-all -long <unique_id> <subject> -all', required=True)
    recon_long.add_argument('-p', '--parallel', type=int, help='Number of parallel runs (default: number of CPUs).', default=mp.cpu_count())
   
    segHA = subparsers.add_parser('segment_HA', help='Run [CROSS] segmentation of hippocampal subfields and nuclei of the amygdala.')
    segHA.add_argument('-i', '--input', type=str, help='Tab separated file. Required columns: id (unique ID) from subject processed with recon-all [CROSS]', required=True)
    segHA.add_argument('-p', '--parallel', type=int, help='Number of parallel FS runs (default: number of CPUs).', default=mp.cpu_count())
    
    segHA_long = subparsers.add_parser('segment_HA_long', help='Run [LONG] segmentation of hippocampal subfields and nuclei of the amygdala.')
    segHA_long.add_argument('-i', '--input', type=str, help='Tab separated file. Required columns: subject (base ID) from subject processed with recon-all [BASE])', required=True)
    segHA_long.add_argument('-p', '--parallel', type=int, help='Number of parallel FS runs (default: number of CPUs).', default=mp.cpu_count())
    
    edit = subparsers.add_parser('edit', help='Run mri_gcut and mri_binarize for pial edits.')
    edit.add_argument('-i', '--input', type=str, help='Tab separated file. Required columns column: id (unique ID) from subject processed with recon-all [CROSS], ratio: threshold to value (%) of WM intensity.', required=True)
    edit.add_argument('-p', '--parallel', type=int, help='Number of parallel FS runs (default: number of CPUs).', default=mp.cpu_count())
    
    recon_edit = subparsers.add_parser('recon_edit', help='Re-run recon-all for pial edits.')
    recon_edit.add_argument('-i', '--input', type=str, help='Subject id list file.', required=True)
    recon_edit.add_argument('-p', '--parallel', type=int, help='Number of parallel FS runs (default: number of CPUs).', default=mp.cpu_count())
   
    return parser.parse_args()

def worker(cmd: str) -> "subprocess.run":
    """
    Invokes a subprocess running the command.

    Parameters
    ----------
    cmd : str
        Command-line string

    Returns
    -------
    subprocess.run()
    
    """

    return subprocess.run(cmd, shell=True)

def run_command(args: list):
    """
    Pass the appropriate command function to the worker.

    Parameters
    ----------
    args : list
        Command-line arguments list

    Returns
    -------
    None
    
    """

    if args.command == "recon_all":
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --header : recon-all -all -s {{id}} -i {{dcm_path}} :::: {args.input}"
        worker(cmd)
        
    if args.command == "recon_base":
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --colsep '\t' {{1}} :::: {args.input}"
        worker(cmd)
    
    if args.command == "recon_long":
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --colsep '\t' {{1}} :::: {args.input}"
        worker(cmd)
        
    if args.command == "segment_HA":
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --header : segmentHA_T1.sh {{id}} :::: {args.input}"
        worker(cmd)
    
    if args.command == "segment_HA_long":
        subjects = pd.read_csv(args.input, sep='\t', usecols=['subject'])['subject'].unique()
        subjects_str = ' '.join(subjects)
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} segmentHA_T1_long.sh ::: {subjects_str}"
        worker(cmd)
        
    if args.command == "edit":  
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --header : mri_gcut -110 -T {{ratio}} -mult $SUBJECTS_DIR/{{id}}/mri/brainmask.auto.mgz $SUBJECTS_DIR/{{id}}/mri/T1.mgz $SUBJECTS_DIR/{{id}}/mri/brainmask.tmp{{ratio}}.mgz $SUBJECTS_DIR/{{id}}/mri/brainmask.gcutsT{{ratio}}.mgz :::: {args.input}"
        worker(cmd)
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --header : mri_binarize --i $SUBJECTS_DIR/{{id}}/mri/brainmask.gcutsT{{ratio}}.mgz --o $SUBJECTS_DIR/{{id}}/mri/brainmask.gcutsT{{ratio}}.mgz --binval 999 --min 1 :::: {args.input}"
        worker(cmd)
        
    if args.command == "recon_edit":
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --header : cp $SUBJECTS_DIR/{{id}}/mri/brainmask.tmp{{ratio}}.mgz $SUBJECTS_DIR/{{id}}/mri/brainmask.auto.mgz :::: {args.input}"
        worker(cmd)
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --header : cp $SUBJECTS_DIR/{{id}}/mri/brainmask.tmp{{ratio}}.mgz $SUBJECTS_DIR/{{id}}/mri/brainmask.mgz :::: {args.input}"
        worker(cmd)
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --header : recon-all -autorecon2-wm -autorecon3 -s {{id}} :::: {args.input}"
        worker(cmd)

if __name__ == '__main__':
    args = argument_parser(sys.argv[1:])
    run_command(args)
    
