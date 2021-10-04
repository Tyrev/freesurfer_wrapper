"""
Command-line wrapper tool to execute parallel runs of FreeSurfer recon-all and some pial edits algorithms.

This file can also be imported as a module and contains the following functions:

    * argument_parser -  parser for command-line options, arguments and sub-commands.
    * run_command - 
    * handle_workers - creates a pool of parallel worker processes running commands.
    * worker - invokes a subprocess running the command.
    * recon - formats recon-all command string.
    * edit - formats mri_gcut and mri_binarize command string.
    * recon_edit - formats a cp and recon-all command string.
    * parse_input_file - parses the input tables.

"""

import argparse
import multiprocessing as mp
import os
import subprocess
import sys


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

    recon = subparsers.add_parser('recon', help='Run FreeSurfer recon-all.')
    recon.add_argument('-i', '--input', type=str, help='Tab separated file. First column: unique ID. Second column: path to dcm/nii file.', required=True)
    recon.add_argument('-p', '--parallel', type=int, help='Number of parallel runs (default: number of CPUs).', default=mp.cpu_count())

    edit = subparsers.add_parser('edit', help='Run mri_gcut and mri_binarize for pial edits.')
    edit.add_argument('-i', '--input', type=str, help='Tab separated file. First column: unique ID. Second column: path to dcm/nii file. Third column: tissue ratio', required=True)
    edit.add_argument('-p', '--parallel', type=int, help='Number of parallel FS runs (default: number of CPUs).', default=mp.cpu_count())
    
    recon_edit = subparsers.add_parser('recon_edit', help='Re-run recon-all for pial edits.')
    recon_edit.add_argument('-i', '--input', type=str, help='Subject id list file.', required=True)
    recon_edit.add_argument('-p', '--parallel', type=int, help='Number of parallel FS runs (default: number of CPUs).', default=mp.cpu_count())
   
    return parser.parse_args()

def recon(recon_args: list) -> str:
    """
    Formats recon-all command string.
    
    Parameters
    ----------
    recon_args : list
        recon-all arguments list

    Returns
    -------
    recon-all [args]
    
    """

    subjid = recon_args[0]
    volume = recon_args[1]
    cmd_line = f"recon-all -all -s {subjid} -i {volume}"

    return cmd_line

def edit(edit_args: list) -> str:
    """
    Formats mri_gcut and mri_binarize command string.
    mri_gcut performs skull stripping algorithm based on graph cut.
    mri_binarize binarizes the edited mask.

    Parameters
    ----------
    edit_args : list
        mri_gcut and mri_binarize arguments list

    Returns
    -------
    mri_gcut [args] && mri_binarize [args]
    
    """

    subjid = edit_args[0]
    tissue_ratio = edit_args[2]
    subjects_dir = os.environ['SUBJECTS_DIR'] # SUBJECTS_DIR environment variable set in Dockerfile
    
    cmd_mri_gcut = f"mri_gcut -110 -T {tissue_ratio} -mult {subjects_dir}/{subjid}/mri/brainmask.auto.mgz {subjects_dir}/{subjid}/mri/T1.mgz {subjects_dir}/{subjid}/mri/brainmask.tmp{tissue_ratio}.mgz {subjects_dir}/{subjid}/mri/brainmask.gcutsT{tissue_ratio}.mgz"
    cmd_mri_binarize = f"mri_binarize --i {subjects_dir}/{subjid}/mri/brainmask.gcutsT{tissue_ratio}.mgz --o {subjects_dir}/{subjid}/mri/brainmask.gcutsT{tissue_ratio}.mgz --binval 999 --min 1"
    cmd_line = f"{cmd_mri_gcut} && {cmd_mri_binarize}"

    return cmd_line

def recon_edit(recon_edit_args: list) -> str:
    """
    Formats a cp and recon-all command string.
    cp replaces the original brainmask with the edited brainmask.gcutsT{tissue_ratio}.mgz.
    recon-all re-runs -autorecon2-wm -autorecon3 stream with the new mask.

    Parameters
    ----------
    recon_edit_args : list
        cp and recon-all arguments list

    Returns
    -------
    cp [args] && recon-all [args]
    
    """

    subjid = recon_edit_args[0]
    tissue_ratio = recon_edit_args[2]
    subjects_dir = os.environ['SUBJECTS_DIR'] # SUBJECTS_DIR environment variable set in Dockerfile
    
    cmd_brainmask_cp = f"cp {subjects_dir}/{subjid}/mri/brainmask.tmp{tissue_ratio}.mgz {subjects_dir}/{subjid}/mri/brainmask.auto.mgz && cp {subjects_dir}/{subjid}/mri/brainmask.tmp{tissue_ratio}.mgz {subjects_dir}/{subjid}/mri/brainmask.mgz"
    cmd_recon_all_edit = f"recon-all -autorecon2-wm -autorecon3 -s {subjid}"
    cmd_line = f"{cmd_brainmask_cp} && {cmd_recon_all_edit}"

    return cmd_line

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

def parse_input_file(input_file: str) -> "List[List[str]]":
    """
    Parses the input tables.

    Parameters
    ----------
    input_file : str
        Tab-separated .txt file.

    Returns
    -------
    File lines and columns parsed as a list of lists.
    
    """

    with open(input_file) as f:
        lines = [line.rstrip().split('\t') for line in f]
    return lines

def handle_workers(p: int, command: "function", input_file: str):
    """
    Creates a pool of parallel worker processes running commands.
    Workers will be called until all lines from the input file are processed.

    Parameters
    ----------
    p : int
        The number of parallel processes.
    command :  function
        Function returning the command-line string to pass the worker.
    input_file : str
        Tab-separated .txt file.

    Returns
    -------
    None
    
    """

    # FS args are parsed from the input files
    # and formatted into recon/edit/recon_edit command-lines
    fs_args = parse_input_file(input_file) 
    cmd_lines = [command(args) for args in fs_args] 

    with mp.Pool(p) as pool:
        res = pool.map_async(worker, cmd_lines) # Pass the command to the worker which will invoke a subprocess
        print(res.get())

def run_command(args):
    """
    Pass the appropriate command function to the worker handler.

    Parameters
    ----------
    args : list
        Command-line arguments list

    Returns
    -------
    None
    
    """

    if args.command == "recon":
        # QUICKFIX: use GNU parallel. The original code with multiprocessing is crashing.
        cmd=f"parallel --tmpdir tmpdir/ --lb -j {args.parallel} --colsep '\t' recon-all -all -s {{1}} -i {{2}} :::: {args.input}"
        worker(cmd)
        #handle_workers(p=args.parallel, command=recon, input_file=args.input)
    if args.command == "edit":
        handle_workers(p=args.parallel, command=edit, input_file=args.input)
    if args.command == "recon_edit":
        handle_workers(p=args.parallel, command=recon_edit, input_file=args.input)

if __name__ == '__main__':
    args = argument_parser(sys.argv[1:])
    run_command(args)
    
