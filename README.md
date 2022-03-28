# freesurfer_wrapper
> **freesurfer_wrapper** aims to facilitate the creation of a multiprocessing pipeline using FreeSurfer.
> It is a Python wrapper to execute parallel runs of cross, base and long recon-all. Some pial edits algorithms are also available.

## Requirements
 - [Docker](https://www.docker.com/)
 - [FreeSurfer license key](https://surfer.nmr.mgh.harvard.edu/registration.html)
 - [Ubuntu OS](https://ubuntu.com/desktop): instructions are given, and were tested, considering an Ubuntu OS. It is possible to run using other OS, like Windows, since the wrapper uses Docker. However, keep in mind that adaptations may be necessary.

## Files and folders overview

```
├── ADNI  # ADNI test data           
│   └── ...
├── docs # documentation files
│   └── ...
├── FS_OUTPUTS # output folder for processing (freesurfer SUBJECTS_DIR).
│
├── QC # output folder for quality control analysis
│
├── scripts # additional scripts used by the wrapper
│   └── ...
├── run.py # wrapper main script
```

## Preparation
1) Place the license in a `license.txt` file in the same folder as the Dockerfile.

2) Place your dataset folder in the same folder as the Dockerfile.

3) Build the docker image:

```bash
sudo docker build -t fs_wrapper .
```
## Workflow overview

In this section, a usage example is shown using data from the [Alzheimer's Disease Neuroimaging Initiative](https://adni.loni.usc.edu/) dataset.
The [ADNI](ADNI) folder contains MP-RAGE data from 3 visits of subject `137_S_1414`.

### recon-all [CROSS] processing

Cross-sectionally process all time points with the default workflow.

#### Input file

CROSS processing requires a tab separated file with named columns:

- Mandatory columns:
  - id: unique id.
  - dcm_path: path to one dcm/nii file.

- Additional columns (**required only in case of BASE and LONG processing**):
  - subject: subject base ID
  - session: session ID
  - date: folder named with scan date
  - visit: time point relative to the ones contained in the subject folder.

For the ADNI dataset example, you can create this file using `create_recon_input.py all -i <PATH_TO_SAMPLES_FOLDER>`. This will create a `recon_all_input.txt` file. The script will combine the subject ID and the session ID to create the unique ID.

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 scripts/create_recon_input.py all -i ADNI/
```

`recon_all_input.txt` example:

```bash
id	subject	session	date	visit	dcm_path
137_S_1414_I64472	137_S_1414	I64472	2007-08-01_10_14_02.0	1	ADNI/137_S_1414/MP-RAGE/2007-08-01_10_14_02.0/I64472/ADNI_137_S_1414_MR_MP-RAGE__br_raw_20070803075521213_1_S36840_I64472.dcm
137_S_1414_I153787	137_S_1414	I153787	2009-08-26_11_06_33.0	2	ADNI/137_S_1414/MP-RAGE/2009-08-26_11_06_33.0/I153787/ADNI_137_S_1414_MR_MP-RAGE__br_raw_20090827101803061_1_S72806_I153787.dcm
137_S_1414_I190917	137_S_1414	I190917	2010-08-18_14_20_16.0	3	ADNI/137_S_1414/MP-RAGE/2010-08-18_14_20_16.0/I190917/ADNI_137_S_1414_MR_MP-RAGE__br_raw_20100819090950301_1_S90858_I190917.dcm
```

#### Run recon-all [CROSS]

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 run.py recon_all -i recon_all_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

### recon-all [BASE] processing

Create an unbiased template from all time points for each subject.

#### Input file

BASE processing requires a single column file were each line must be a command string with the following template:

`recon-all -base <subject> -tp <unique_id> -tp <unique_id> ... -all`

For the ADNI dataset example, you can create this file using `create_recon_input.py base -i recon_all_input.txt`. This will use the `recon_all_input.txt` file created previously for the CROSS processing. If necessary, edit this `recon_all_input.txt` to contain **only the samples that have been successfully processed**.

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 scripts/create_recon_input.py base -i recon_all_input.txt
```

`recon_base_input.txt` example:

```bash
recon-all -base 137_S_1414 -tp 137_S_1414_I64472 -tp 137_S_1414_I153787 -tp 137_S_1414_I190917 -all
```
#### Run recon-all [BASE]

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 run.py recon_base -i recon_base_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

### recon-all [LONG] processing

Longitudinally process all timepoints.

#### Input file

LONG processing requires a single column file were each line must be a command string with the following template:

`recon-all -long <unique_id> <subject> -all`

For the ADNI dataset example, you can create this file using `create_recon_input.py long -i recon_all_input.txt`. This will use the `recon_all_input.txt` file created previously for the CROSS processing. If necessary, edit this `recon_all_input.txt` to contain **only the samples that have been successfully processed**.

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 scripts/create_recon_input.py long -i recon_all_input.txt
```

`recon_long_input.txt` example:

```bash
recon-all -long 137_S_1414_I64472 137_S_1414 -all
recon-all -long 137_S_1414_I153787 137_S_1414 -all
recon-all -long 137_S_1414_I190917 137_S_1414 -all
```

#### Run recon-all [LONG]

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 run.py recon_long -i recon_long_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

### Segmentation of hippocampal subfields and nuclei of the amygdala [CROSS] processing

Original script by Juan Eugenio Iglesias. For more information and citation requirements, please consult [FS official documentation](https://surfer.nmr.mgh.harvard.edu/fswiki/HippocampalSubfieldsAndNucleiOfAmygdala).

#### Input file

CROSS processing requires a tab separated file with named columns:

- Mandatory columns:
  - id: unique id.

For the ADNI dataset example, you can use the `recon_all_input.txt` file created previously for the recon-all CROSS processing. If necessary, edit this `recon_all_input.txt` to contain **only the samples that have been successfully processed**.

#### Run segment_HA [CROSS]

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 run.py segment_HA -i recon_all_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

### Segmentation of hippocampal subfields and nuclei of the amygdala [LONG] processing

Original script by Juan Eugenio Iglesias. For more information and citation requirements, please consult [FS official documentation](https://surfer.nmr.mgh.harvard.edu/fswiki/HippocampalSubfieldsAndNucleiOfAmygdala).

#### Input file

LONG processing requires a tab separated file with named columns:

- Mandatory columns:
  - subject: base ID from subject processed with recon-all [BASE]

For the ADNI dataset example, you can use the `recon_all_input.txt` file created previously for the recon-all CROSS processing. If necessary, edit this `recon_all_input.txt` to contain **only the samples that have been successfully processed**.

#### Run segment_HA [LONG]

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 run.py segment_HA_long -i recon_all_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

## Tissue ratio correction

After running `recon_all` you can check your results using `freeview`. Please refer to [Manual quality analysis section](#manual-quality-analysis) to use a custom script.

If any skull edits are necessary, you need to create an input table to run `edit` with the following characteristics:

- Mandatory columns:
  - id: unique id.
  - ratio: the threshold to value (%) of WM intensity. The value should be >0 and <1; larger values would correspond to cleaner skull-strip but higher chance of brain erosion.

You can copy the `recon_all_input.txt` content, keep only the lines for the scans that need edits, and add the column with the tissue ratio values.

As an example, an `edit_input.txt` file for some ADNI records would look like this:

```bash
id	subject	session	date	visit	dcm_path	ratio
137_S_1414_I64472	137_S_1414	I64472	2007-08-01_10_14_02.0	1	ADNI/137_S_1414/MP-RAGE/2007-08-01_10_14_02.0/I64472/ADNI_137_S_1414_MR_MP-RAGE__br_raw_20070803075521213_1_S36840_I64472.dcm 0.5
137_S_1414_I153787	137_S_1414	I153787	2009-08-26_11_06_33.0	2	ADNI/137_S_1414/MP-RAGE/2009-08-26_11_06_33.0/I153787/ADNI_137_S_1414_MR_MP-RAGE__br_raw_20090827101803061_1_S72806_I153787.dcm 0.8
```

### Run edit

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper \
python3 run.py edit -i edit_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

You can check the resulting edited mask using `freeview`:
```bash
SUBJECTS_DIR=$(pwd)/FS_OUTPUTS
freeview -recon <UNIQUE_ID> -v brainmask.gcutsT$<TISSUE_RATIO>.mgz:colormap=heat:opacity=0.5
```

If still not good, change the tissue ratio value in the input file and run `edit` again.
When all masks are OK, proceed to `recon_edit` command.

### recon_edit
`recon_edit` will re-run parts of FS recon-all using the edited masks.
The input file is the table used for `edit` with the final values for tissue ratio.

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 run.py recon_edit -i edit_input.txt
```

This command will use the maximum number of CPUs. You can append the `-p <INT>` flag where `<INT>` is the number of parallel runs you want.

## How to check for completed runs and hard recon-all errors
FreeSurfer's recon-all command creates different logs while running.
The `recon-all.done` log is created only for completed runs. The `recon-all.error` is created for hard failures. 

You can check these logs using a custom script. The script was written to work on ADNI folder structure. For other datasets you can try to edit the PATH_PATTERN variable in scripts/check_logs.py.

### Done
```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper \
python3 scripts/check_logs.py done
```

You can also pipe the output to bash word count command to get a quick count:

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper \
python3 scripts/check_logs.py done | wc -l
```

### Error
```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper \
python3 scripts/check_logs.py error
```

## How to restart after a computer failure
If the execution of the pipeline is halted by a computer failure or system restart then you have to update the input file of the `recon` commands.

To update `recon_all_input.txt`:

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 scripts/update_recon_input.py all -i recon_all_input.txt
```

To update `recon_base_input.txt`:

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 scripts/update_recon_input.py base -i recon_base_input.txt
```

To update `recon_long_input.txt`:

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper python3 scripts/update_recon_input.py long -i recon_long_input.txt
```

This will remove all "done" samples from the original input and create a new input file (`<YYYY-MM-DD>_recon_<all|base|long>_input.txt`).

To delete the folders from the samples that were running when the failure happened:

```bash
# first check the list
IsRunning=(ls FS_OUTPUTS/*/scripts/*IsRunning* | cut -f 1,2 -d /)
echo $IsRunning

# if it is ok, delete
sudo rm -R $IsRunning
```

## Quality control

### Automated quality analysis

The tool is packaged with [**qatools-python**](https://github.com/Deep-MI/qatools-python) version 1.2 for quality control measurements.
This script was developed by [Reuter DeepMI Lab](https://deep-mi.org/) as a revision, extension, and translation to the Python language of the Freesurfer QA Tools.

```bash
sudo docker run --rm -it -v "$(pwd):/root/freesurfer_wrapper" fs_wrapper \
python3 scripts/qatools-python/qatools.py --subjects_dir FS_OUTPUTS --output_dir QC \
--screenshots --outlier --fornix
```

This will create `qatools-results.csv` file; `screenshots`, `outliers` and `fornix` folders inside the QC folder. Please consult [qatools-python docs](scripts/qatools-python/README.md#description) for a full explanation of each QC measurement.

### Manual quality analysis
You can visually inspect each result using `freeview`. We provide a script to speed up the opening process of each scan. 
The script also prompts the user about the result of the QC after each window of `freeview` is closed. The result is saved to manual_QC.txt

It is not possible to run `freeview` using Docker, the graphical user interface cannot be displayed. Therefore, you need to have FreeSurfer/freeview installed in your host machine.

#### Step 1
Set SUBJECTS_DIR environment variable. Here, the results are stored inside the FS_OUTPUTS directory.

```bash
export SUBJECTS_DIR=$(pwd)/FS_OUTPUTS
```

#### Step 2
Run the `view.py` script.

```bash
python3 scripts/view.py
```