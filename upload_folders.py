# -*- coding: utf-8 -*-
"""
This script uploads all photos in a folder to iNaturalist. It requires that
all photos are in a subfolder with the common or scientific name and/or the 
taxon number. 

Examples of acceptable folders to hold the individual photos in are:

.../main_folder/52381-Aphididae
.../main_folder/52381
.../main_folder/Aphididae 52381
.../main_folder/Aphids

All photos in any of those folders would be uploaded to a separate observation.

To upload multiple photos to an individual observation put those photos in a
subfolder. For example all photos in:

.../main_folder/52381/New Folder
would be uploaded to a single observation.

Dates, times, gps coordinates are taken from exif data. 

After upload the photos are moved to a folder 'Uploaded' in the same directory
as the main photo. The folder remains in place in case it will be used in 
future observations.
"""

# os used to get a folder name
import os

# This requires the file import_function.py to be in the same folder as this
# script
from import_functions import upload_folder_single
from import_functions import upload_folder_multiple

# This requires the file import_gui.py to be in the same folder as this
# script.
from import_gui import input_data

print("Running")

# Pulls the data from the gui when the script is run. 
[user, passw, app, secret, 
 folder_name, time_zone, accuracy] = input_data()


print('Uploading all photos in folders contained in ' + folder_name )

directories = []
for root, dirs, files in os.walk(folder_name):
    directories.append(dirs)
directories = directories[0]

uploaded_folder = os.path.dirname(folder_name) + '/Uploaded/'

# If the directory to move folders to after upload doesn't exist, create it
try:
    os.mkdir(uploaded_folder)
except:
    pass

    
# Uploads all photos in folders contained in uploaded_folder
for folder in directories:
    subfolder = folder_name +'/' + folder + '/'
#    print(subfolder)
    upload_folder_single(subfolder, uploaded_folder, time_zone, accuracy, 
                         user, passw, app, secret)

# Uploads photos in sub folders contained in species folders. These upload all
# Photos as a single observation.
subdirectories = []
for folder in directories:
        subfolder = folder_name +'/' + folder + '/'
        for root, dirs, files in os.walk(subfolder):
            if dirs:
                subsubfolder = subfolder + dirs[0]+ '/'
                upload_folder_multiple(subfolder, subsubfolder,
                                       uploaded_folder, time_zone, accuracy,
                                       user, passw, app, secret)
      

print("Program complete")
