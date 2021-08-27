# Use this script to create a new recon_input file after a PC failure (power, restart, ...).
# This will remove all "done" samples from the original recon_input.
# It will also delete the folders from the samples that were running when the failure happened. These samples will run again from scratch.

ls FS_OUTPUTS/*/scripts/*.done | cut -f 2 -d / > done.list
grep -v -f done.list recon_input.txt > "$(date '+%Y-%m-%d')"_recon_input.txt
rm done.list
rm -R $(ls FS_OUTPUTS/*/scripts/*IsRunning* | cut -f 1,2 -d /)