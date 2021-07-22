# freesurfer_wrapper
> **freesurfer_wrapper** aims to facilitate the creation of a multiprocessing pipeline using FreeSurfer.
> It is a Python wrapper to execute parallel runs of recon-all and some pial edits algorithms.

## Requirements
 - [Docker](https://www.docker.com/)
 - [FreeSurfer license key](https://surfer.nmr.mgh.harvard.edu/registration.html)

## Preparation
1) Place the license in a `license.txt` file in the same folder as the Dockerfile.

2) Place your dataset folder in the same folder as the Dockerfile.

3) Build the docker image:

```bash
docker build -t fs_wrapper .
```
## Overview run

The main script has 3 commands, each of them is explained below.


```bash
python run.py -h
usage: run.py [-h] {recon,edit,recon_edit} ...

Command-line wrapper tool to execute parallel runs of FreeSurfer recon-all and
some pial edits algorithms.

positional arguments:
  {recon,edit,recon_edit}
    recon               Run FreeSurfer recon-all.
    edit                Run mri_gcut and mri_binarize for pial edits.
    recon_edit          Re-run recon-all for pial edits.

optional arguments:
  -h, --help            show this help message and exit
```

### recon
Run FreeSurfer recon-all.

```bash
python run.py recon -h
usage: run.py recon [-h] -i INPUT [-p PARALLEL]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Tab separated file. First column: unique ID. Second
                        column: path to dcm/nii file.
  -p PARALLEL, --parallel PARALLEL
                        Number of parallel runs (default: number of CPUs).
```
### edit
Run mri_gcut and mri_binarize for pial edits.

```bash
python run.py edit -h
usage: run.py edit [-h] -i INPUT [-p PARALLEL]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Tab separated file. First column: unique ID. Second
                        column: path to dcm/nii file. Third column: tissue
                        ratio
  -p PARALLEL, --parallel PARALLEL
                        Number of parallel FS runs (default: number of CPUs).
```

### recon_edit
Re-run recon-all for pial edits.

```bash
python run.py recon_edit -h
usage: run.py recon_edit [-h] -i INPUT [-p PARALLEL]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Subject id list file.
  -p PARALLEL, --parallel PARALLEL
                        Number of parallel FS runs (default: number of CPUs).
```

## How to run recon
### Create the input file
A tab-separated file is needed as input with the following characteristics:

- Each line must represent a single scan.
- First column: unique ID. 
- Second column: path to dcm/nii file.

For the ADNI dataset, you can create this file using the `create_recon_input.py` script. This will create a `recon_input.txt` file. The script will combine the subject ID and the session ID to create a unique ID.

```bash
docker run --rm -it -v $(pwd):/root/freesurfer_wrapper fs_wrapper \
python scripts/create_recon_input.py
```

As an example, a `recon_input.txt` file for some ADNI records will look like this:
```bash
137_S_1414_S46193	ADNI/137_S_1414/MP-RAGE/2008-02-26_11_57_53.0/S46193/ADNI_137_S_1414_MR_MP-RAGE__br_raw_20080226130530486_1_S46193_I92752.dcm
137_S_1414_S72806	ADNI/137_S_1414/MP-RAGE/2009-08-26_11_06_33.0/S72806/ADNI_137_S_1414_MR_MP-RAGE__br_raw_20090827101803061_1_S72806_I153787.dcm
```

For other datasets you can try to edit the PATH_PATTERN variable in `scripts/create_recon_input.py`.

### Run **recon**
Now you can run the `recon` command using Docker.
This can take several hours.

```bash
docker run --rm -it -v $(pwd):/root/freesurfer_wrapper fs_wrapper \
python run.py recon -i recon_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

## How to run edit
### Create the input file
After running `recon` you can check your results using `freeview`. 
It is not possible to run `freeview` using Docker, the graphical user interface cannot be displayed. Therefore, use your host machine `freeview` command to check the results.

```bash
SUBJECTS_DIR=$(pwd)/FS_OUTPUTS 
freeview -recon <UNIQUE_ID>
```

If any skull edits are necessary, you need to create an input table to run `edit` with the following characteristics:

- Each line must represent a single scan.
- First column: unique ID. 
- Second column: path to dcm/nii file.
- Third column: the tissue ratio for WM edits.

Tissue ratio is the threshold to value (%) of WM intensity. The value should be >0 and <1; larger values would correspond to cleaner skull-strip but higher chance of brain erosion.

You can copy the recon input table, keep only the lines for the scans that need pial edits, and add the column with the tissue ratio values.

As an example, a `edit_input.txt` file for some ADNI records will look like this:

```bash
137_S_1414_S46193	ADNI/137_S_1414/MP-RAGE/2008-02-26_11_57_53.0/S46193/ADNI_137_S_1414_MR_MP-RAGE__br_raw_20080226130530486_1_S46193_I92752.dcm 0.5
137_S_1414_S72806	ADNI/137_S_1414/MP-RAGE/2009-08-26_11_06_33.0/S72806/ADNI_137_S_1414_MR_MP-RAGE__br_raw_20090827101803061_1_S72806_I153787.dcm  0.3
```
### Run **edit**
Now you can run the `edit` command using Docker.

```bash
docker run --rm -it -v $(pwd):/root/freesurfer_wrapper fs_wrapper \
python run.py edit -i edit_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

You can check the resulting edited mask using `freeview`:
```bash
SUBJECTS_DIR=$(pwd)/FS_OUTPUTS
freeview -recon <UNIQUE_ID> -v brainmask.gcutsT$<TISSUE_RATIO>.mgz:colormap=heat:opacity=0.5
```

If still not good, change the tissue ratio value in the input file and run `edit` again.
When all masks are OK, proceed to `recon_edit` command.

## How to run recon_edit
### Create the input file
The input file is the table used for `edit` with the final values for tissue ratio.

### Run **recon_edit**
`recon_edit` will re-run parts of FS recon-all using the edited masks. This can take several hours.

```bash
docker run --rm -it -v $(pwd):/root/freesurfer_wrapper fs_wrapper python run.py recon_edit -i edit_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

## How to check for completed runs and hard errors
FreeSurfer's recon-all command creates different logs while running.
The `recon-all.done` log is created only for completed runs. The `recon-all.error` is created for hard failures. 

You can check these logs using a custom script. The script was written to work on ADNI folder structure. For other datasets you can try to edit the PATH_PATTERN variable in scripts/check_logs.py.


### Done
```bash
docker run --rm -it -v $(pwd):/root/freesurfer_wrapper fs_wrapper \
python scripts/check_logs.py done
```

You can also pipe the output to bash word count command to get a quick count:

```bash
docker run --rm -it -v $(pwd):/root/freesurfer_wrapper fs_wrapper \
python scripts/check_logs.py done | wc -l
```

### Error
```bash
docker run --rm -it -v $(pwd):/root/freesurfer_wrapper fs_wrapper \
python scripts/check_logs.py error
```

## Quality control

The tool is packaged with [**qatools-python**](https://github.com/Deep-MI/qatools-python) version 1.2 for quality control measurements.
This script was developed by [Reuter DeepMI Lab](https://deep-mi.org/) as a revision, extension, and translation to the Python language of the Freesurfer QA Tools.

```bash
docker run --rm -it -v $(pwd):/root/freesurfer_wrapper fs_wrapper \
python scripts/qatools-python/qatools.py --subjects_dir FS_OUTPUTS --output_dir QC \
--screenshots --outlier --fornix
```

This will create `qatools-results.csv` file; `screenshots`, `outliers` and `fornix` folders inside the QC folder. Please consult [qatools-python docs](scripts/qatools-python/README.md#description) for a full explanation of each QC measurement.
