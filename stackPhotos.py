import os
import subprocess
import tempfile
import shutil

'''To use: 

python stackPhotos.py <input_dir> <output_dir_base> <helicon_focus_path> <nconvert_path> <backup_dir_base>

The defaults are:
input_dir = "D:/Unstacked/"
output_dir_base = "D:/Stacked/"
helicon_focus_path = "C:/Program Files/Helicon Software/Helicon Focus 8/HeliconFocus.exe"
nconvert_path = "C:/XnView/nconvert.exe"
backup_dir_base = "D:/Backup_Permanent"

Written by Michele Wiseman of Oregon State University
June 22nd, 2023
Version 1.0
'''

input_dir = "D:/Unstacked/"
output_dir_base = "D:/Stacked/"
helicon_focus_path = "C:/Program Files/Helicon Software/Helicon Focus 8/HeliconFocus.exe"
nconvert_path = "C:/XnView/nconvert.exe"
backup_dir_base = "D:/Backup_Permanent"

processed_stack_groups = 0
total_stack_groups = 0

# Count the total number of stack groups
for experiment in os.listdir(input_dir):
    experiment_path = os.path.join(input_dir, experiment)
    for date in os.listdir(experiment_path):
        date_path = os.path.join(experiment_path, date)
        for tray in os.listdir(date_path):
            tray_path = os.path.join(date_path, tray)
            total_stack_groups += len(os.listdir(tray_path))

# Iterate over all experiments
for experiment in os.listdir(input_dir):
    print(f'Processing experiment: {experiment}')
    experiment_path = os.path.join(input_dir, experiment)
    #print(f'Experiment path: {experiment_path}')

    # Iterate over all trays in the experiment
    for date in os.listdir(experiment_path):
        date_path = os.path.join(experiment_path, date)
        print(f'Processing date: {date}')

        # Iterate over all plant identifiers in the tray
        for tray in os.listdir(date_path):
            tray_path = os.path.join(date_path, tray)
            #print(f'Date path: {date_path}')
            #print(f'Tray path: {tray_path}')

            # Iterate over all stack groups under each plant identifier
            for stack_group in os.listdir(tray_path):
                print(f'Processing stack group: {stack_group}')
                stack_group_path = os.path.join(tray_path, stack_group)
                #print(f'Stack group path: {stack_group_path}')

                # Create output directory
                output_dir = os.path.join(output_dir_base, experiment, date, tray)
                os.makedirs(output_dir, exist_ok=True)

                # Create backup directory
                backup_dir = os.path.join(backup_dir_base, experiment, date, tray)
                os.makedirs(backup_dir, exist_ok=True)

                # Prepare list of source files for Helicon Focus
                source_files = [os.path.join(stack_group_path, file) for file in os.listdir(stack_group_path) if
                                file.endswith('.nef')]

                # Run Helicon Focus
                with tempfile.NamedTemporaryFile(delete=False, suffix='.lst') as f:
                    temp_file_path = f.name
                    f.write('\n'.join(source_files).encode())

                helicon_output_file_path = os.path.join(output_dir, f'{stack_group}.tiff')
                #print(f'Running Helicon Focus on stack group {stack_group}...')
                subprocess.run([
                    helicon_focus_path, '-silent', '-i', temp_file_path, '-save:' + helicon_output_file_path,
                    '-mp:1', '-rp:4', '-sp:2', '-tif:u'
                ])

                # Convert TIFF to PNG using NConvert
                png_output_file_path = os.path.join(output_dir, f'{stack_group.rsplit("_", 1)[0]}.png')
                #print(f'Converting TIFF to PNG: {png_output_file_path}')
                subprocess.run([
                    nconvert_path, '-out', 'png', '-o', png_output_file_path, helicon_output_file_path
                ])

                # Remove the TIFF file
                print(f'Removing TIFF file: {helicon_output_file_path}')
                os.remove(helicon_output_file_path)

                # Move unstacked files
                print(f'Moving unstacked files to backup directory: {backup_dir}')
                shutil.move(stack_group_path, backup_dir)

                print(f'Stack group {stack_group} done.')

                # Update the counter
                processed_stack_groups += 1
                remaining_stack_groups = total_stack_groups - processed_stack_groups
                print(f'{remaining_stack_groups} stack groups remaining in the unstacked folder.')