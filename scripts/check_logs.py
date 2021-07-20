"""Script to check recon-all logs for each run

usage: python check_logs.py <done|error>

Please edit the **PATH_PATTERN** variable with the appropriate
pathname pattern to find each file.

This file can also be imported as a module and contains the following
functions:

    * get_logs - get the path for each log based on pathname pattern.
    * print_id_from_logs - prints the IDs from a list of logs.

"""

from glob import glob
import os
import sys

# Pathname pattern to find each log
# * is a wildcard standing for "any string of characters"
# FS_OUTPUTS/ALL_SUBJECTS/MP-scripts/recon-all
# This pattern is concatenated with the "done" or "error" extension when running as script
PATH_PATTERN = "FS_OUTPUTS/*/scripts/recon-all"

def get_logs(path_pattern: str) -> list:
    """
    Get the path for each log based on pathname pattern.

    Parameters
    ----------
    path_pattern : str
        Glob pathname pattern to find each log.

    Returns
    -------
    List of log paths
    """

    return glob(path_pattern)

def print_id_from_logs(logs: list):
    """
    Prints the IDs from a list of logs.

    Parameters
    ----------
    logs : list
        List of log paths

    Returns
    -------
    None
    """
    
    for log in logs:
        print(log.split("/")[-3])

if __name__ == '__main__':
    try:
        log_type = sys.argv[1]
        print_id_from_logs(get_logs(f"{PATH_PATTERN}.{log_type}"))
    except(IndexError):
        print("ERROR: please specify log type (done or error)")
        print("Example: python check_logs.py done")

