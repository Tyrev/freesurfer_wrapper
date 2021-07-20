---
description: |
    API documentation for modules: freesurfer_wrapper, freesurfer_wrapper.run, freesurfer_wrapper.scripts, freesurfer_wrapper.scripts.check_logs, freesurfer_wrapper.scripts.create_recon_input.

lang: en

classoption: oneside
geometry: margin=1in
papersize: a4

linkcolor: blue
links-as-notes: true
...


    
# Module `freesurfer_wrapper` {#freesurfer_wrapper}

# freesurfer_wrapper
> **freesurfer_wrapper** aims to facilitate the creation of a multiprocessing pipeline using FreeSurfer.
> It is a Python wrapper to execute parallel runs of recon-all and some pial edits algorithms.

## Requirements
 - [Docker](https://www.docker.com/)
 - [FreeSurfer license key](https://surfer.nmr.mgh.harvard.edu/registration.html)

## Usage

## Example


    
## Sub-modules

* [freesurfer_wrapper.run](#freesurfer_wrapper.run)
* [freesurfer_wrapper.scripts](#freesurfer_wrapper.scripts)






    
# Module `freesurfer_wrapper.run` {#freesurfer_wrapper.run}

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




    
## Functions


    
### Function `argument_parser` {#freesurfer_wrapper.run.argument_parser}




>     def argument_parser(
>         args: list
>     ) ‑> ArgumentParser.parse_args


Parser for command-line options, arguments and sub-commands.

###### Parameters

**```args```** :&ensp;<code>list</code>
:   Command-line arguments list

###### Returns

<code>Parser</code>
:   &nbsp;



    
### Function `edit` {#freesurfer_wrapper.run.edit}




>     def edit(
>         edit_args: list
>     ) ‑> str


Formats mri_gcut and mri_binarize command string.
mri_gcut performs skull stripping algorithm based on graph cut.
mri_binarize binarizes the edited mask.

###### Parameters

**```edit_args```** :&ensp;<code>list</code>
:   mri_gcut and mri_binarize arguments list

###### Returns

`mri_gcut [args] && mri_binarize [args]`
:   &nbsp;



    
### Function `handle_workers` {#freesurfer_wrapper.run.handle_workers}




>     def handle_workers(
>         p: int,
>         command: function,
>         input_file: str
>     )


Creates a pool of parallel worker processes running commands.
Workers will be called until all lines from the input file are processed.

###### Parameters

**```p```** :&ensp;<code>int</code>
:   The number of parallel processes.


**```command```** :&ensp;<code> function</code>
:   Function returning the command-line string to pass the worker.


**```input_file```** :&ensp;<code>str</code>
:   Tab-separated .txt file.

###### Returns

<code>None</code>
:   &nbsp;



    
### Function `parse_input_file` {#freesurfer_wrapper.run.parse_input_file}




>     def parse_input_file(
>         input_file: str
>     ) ‑> List[List[str]]


Parses the input tables.

###### Parameters

**```input_file```** :&ensp;<code>str</code>
:   Tab-separated .txt file.

###### Returns

File lines and columns parsed as a list of lists.

    
### Function `recon` {#freesurfer_wrapper.run.recon}




>     def recon(
>         recon_args: list
>     ) ‑> str


Formats recon-all command string.

###### Parameters

**```recon_args```** :&ensp;<code>list</code>
:   recon-all arguments list

###### Returns

`recon-all [args]`
:   &nbsp;



    
### Function `recon_edit` {#freesurfer_wrapper.run.recon_edit}




>     def recon_edit(
>         recon_edit_args: list
>     ) ‑> str


Formats a cp and recon-all command string.
cp replaces the original brainmask with the edited brainmask.gcutsT{tissue_ratio}.mgz.
recon-all re-runs -autorecon2-wm -autorecon3 stream with the new mask.

###### Parameters

**```recon_edit_args```** :&ensp;<code>list</code>
:   cp and recon-all arguments list

###### Returns

`cp [args] && recon-all [args]`
:   &nbsp;



    
### Function `run_command` {#freesurfer_wrapper.run.run_command}




>     def run_command(
>         args
>     )


Pass the appropriate command function to the worker handler.

###### Parameters

**```args```** :&ensp;<code>list</code>
:   Command-line arguments list

###### Returns

<code>None</code>
:   &nbsp;



    
### Function `worker` {#freesurfer_wrapper.run.worker}




>     def worker(
>         cmd: str
>     ) ‑> <function run at 0x7ffb9dabb0e0>


Invokes a subprocess running the command.

###### Parameters

**```cmd```** :&ensp;<code>str</code>
:   Command-line string

###### Returns

<code>subprocess.run()</code>
:   &nbsp;






    
# Namespace `freesurfer_wrapper.scripts` {#freesurfer_wrapper.scripts}




    
## Sub-modules

* [freesurfer_wrapper.scripts.check_logs](#freesurfer_wrapper.scripts.check_logs)
* [freesurfer_wrapper.scripts.create_recon_input](#freesurfer_wrapper.scripts.create_recon_input)






    
# Module `freesurfer_wrapper.scripts.check_logs` {#freesurfer_wrapper.scripts.check_logs}

Script to check recon-all logs for each run

usage: python check_logs.py <done|error>

Please edit the **PATH_PATTERN** variable with the appropriate
pathname pattern to find each file.

This file can also be imported as a module and contains the following
functions:

    * get_logs - get the path for each log based on pathname pattern.
    * print_id_from_logs - prints the IDs from a list of logs.




    
## Functions


    
### Function `get_logs` {#freesurfer_wrapper.scripts.check_logs.get_logs}




>     def get_logs(
>         path_pattern: str
>     ) ‑> list


Get the path for each log based on pathname pattern.

###### Parameters

**```path_pattern```** :&ensp;<code>str</code>
:   Glob pathname pattern to find each log.

###### Returns

<code>List</code> of <code>log paths</code>
:   &nbsp;



    
### Function `print_id_from_logs` {#freesurfer_wrapper.scripts.check_logs.print_id_from_logs}




>     def print_id_from_logs(
>         logs: list
>     )


Prints the IDs from a list of logs.

###### Parameters

**```logs```** :&ensp;<code>list</code>
:   List of log paths

###### Returns

<code>None</code>
:   &nbsp;






    
# Module `freesurfer_wrapper.scripts.create_recon_input` {#freesurfer_wrapper.scripts.create_recon_input}

Script to create recon input table

This script creates an input table based on the directory organization
of the image files. 

Please edit the **PATH_PATTERN** variable with the appropriate
pathname pattern to find each file.

This file can also be imported as a module and contains the following
functions:

    * create_input_file - creates the input table.




    
## Functions


    
### Function `create_input_file` {#freesurfer_wrapper.scripts.create_recon_input.create_input_file}




>     def create_input_file(
>         path_pattern: str
>     )


Creates a two column text file to be used as input for the main script recon command.
First column: unique ID (combines SUBJECT ID and SESSION ID).
Second column: path to DICOM file.

###### Parameters

**```path_pattern```** :&ensp;<code>str</code>
:   Glob pathname pattern to find each DICOM file.

###### Returns

<code>None</code>
:   &nbsp;





-----
Generated by *pdoc* 0.9.2 (<https://pdoc3.github.io>).
