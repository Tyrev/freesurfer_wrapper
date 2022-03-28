"""Script to create a new input file after a PC failure (power, restart, ...).
This will remove all "done" samples from the original input.
It will also delete the folders from the samples that were running when the failure happened. These samples will run again from scratch.

This file can also be imported as a module and contains the following
functions:

    * update_recon_all_input - updates the recon-all input table.
    * update_recon_base_long_input - updates the recon-all base or long input table.

"""

import sys
import argparse
from glob import glob
import pandas as pd
from datetime import date

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

    parser = argparse.ArgumentParser(description="Create a new recon_input file after a PC failure (power, restart, ...)")
    subparsers = parser.add_subparsers(dest="command")

    all = subparsers.add_parser('all', help='Update input for recon-all [CROSS].')
    all.add_argument('-i', '--input', type=str, help='recon_all_input.txt file used for cross processing.', required=True)
    
    base = subparsers.add_parser('base', help='Update input for recon-all [BASE].')
    base.add_argument('-i', '--input', type=str, help='recon_base_input.txt file used for base processing.', required=True)
    
    long = subparsers.add_parser('long', help='Update input for recon-all [LONG].')
    long.add_argument('-i', '--input', type=str, help='recon_long_input.txt file used for long processing.', required=True)
    
    return parser.parse_args()


def update_recon_all_input(recon_input: str):
    """
    Updates the recon_all_input.txt file to remove successfully processed data.

    Parameters
    ----------
    recon_input : str
        Path to recon_all_input.txt file used for cross processing.

    Returns
    -------
    None

    """
    
    original_input = pd.read_csv(recon_input, sep='\t')
    not_done = list()
    for id in original_input['id']:
        done = glob(f"FS_OUTPUTS/{id}/scripts/*.done")
        if len(done) == 0:
            not_done.append(id)
    
    not_done = original_input[original_input['id'].isin(not_done)]
    date_today = date.today().strftime("%Y-%m-%d")
    not_done.to_csv(f"{date_today}_{recon_input}", sep="\t", index=False, header=True)

def update_recon_base_long_input(recon_input: str, long=False):

    """
    Updates the recon_base_input.txt or recon_long_input.txt file to remove successfully processed data.

    Parameters
    ----------
    recon_input : str
        Path to recon_base_input.txt or recon_long_input.txt file used for base or long processing.

    Returns
    -------
    None

    """
    
    not_done = list()
    with open(recon_input) as f:
        lines = f.readlines()
        for line in lines:
            subject = line.split(" ")[2]
            if long:
                done = glob(f"FS_OUTPUTS/{subject}.long.*/scripts/*.done")
            else:
                done = glob(f"FS_OUTPUTS/{subject}/scripts/*.done")
            if len(done) == 0:
                not_done.append(line)
    
    date_today = date.today().strftime("%Y-%m-%d")
    with open(f"{date_today}_{recon_input}",'w') as f:
        for cmd in not_done:
            f.write(cmd)
    
if __name__ == '__main__':
    args = argument_parser(sys.argv[1:])
    if args.command == 'all':
        update_recon_all_input(args.input)
    if (args.command == 'base') or (args.command == 'long'):
        update_recon_base_long_input(args.input)