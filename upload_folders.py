# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 20:30:51 2019

@author: Jesse
"""

# Input your user name here:
user = 'glmory'

# Input your password here:
passw = 'R3almz1!'

# Input your app ID and secret here:
app = 'e4d9505ef7e814513d0a225e2e6555846765a84ceda7034eb454722e8047b68b'
secret = 'b3766331e211b4a3e5fe34d4b51dd67f96d5deabd87c5837d823ce326a7bd0cd'


# Input the time zone for the photos here, options can be found at the 
# website below
# https://gist.github.com/mjrulesamrat/0c1f7de951d3c508fb3a20b4b0b33a98
time_zone = 'America/Los_Angeles'



# tkinter used to choose a file
from tkinter import filedialog
from tkinter import Tk 

# os used to get a folder name
import os

# pillow used to get exif data from the photos
import PIL

from PIL import ExifTags

# This is used to upload the photos. 
import pyinaturalist

from pyinaturalist.rest_api import create_observations
from pyinaturalist.rest_api import get_access_token
from pyinaturalist.rest_api import add_photo_to_observation

print("Running")

## This code lets you choose a photo, can delete and replace with folder_name=''
#root = Tk()
#filename =  filedialog.askopenfilename(initialdir = "/",
#                                    title = "Select one of the .jpg files in "
#                                    "the folder to be uploaded. All files in "
#                                    "the folder will be uploaded. The folder "
#                                    "name should start with the taxon number",
#                                    filetypes = (("jpeg files","*.jpg"),
#                                    ("all files","*.*")))
#root.withdraw()
#
## 
#folder_name = os.path.dirname(filename) +'/'

folder_name = 'E:/My Documents/Pictures/a6300/Test Folder'

print('Uploading all photos in folders contained in ' + folder_name )

directories = []
for root, dirs, files in os.walk(folder_name):
    directories.append(dirs)
directories = directories[0]

# This function returns the latitude and longitude of a .jpg image
def get_lat_long(image):
    # Gets all the exif data from the photo
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in image._getexif().items()
        if k in PIL.ExifTags.TAGS
    }

    # From all the exif data, pulls the GPS data
    gps_info = exif.get('GPSInfo')
    # The GPS data is in a odd format, so have to dig for it a bit. This was
    # only tested on files lightroom tagged. 
    latitude_direction = str(gps_info.get(1)[0])
    latitude_degrees = float(gps_info.get(2)[0][0])
    minutes = float(gps_info.get(2)[1][0])
    multiplier = float(gps_info.get(2)[1][1])
    latitude_minutes = minutes/multiplier
    seconds = float(gps_info.get(2)[2][0])
    multiplier = float(gps_info.get(2)[2][1])
    latitude_seconds = seconds/multiplier
    
    
    # The sign is changed depending on if this is N or S
    if latitude_direction == 'N' or latitude_direction == 'n':
        latitude = latitude_degrees+latitude_minutes/60 + latitude_seconds/3600
    elif latitude_direction == 'S' or latitude_direction == 's':
        latitude = -(latitude_degrees+latitude_minutes/60 + latitude_seconds/3600)
        
    longitude_direction = gps_info.get(3)[0]
    longitude_degrees = gps_info.get(4)[0][0]
    minutes = float(gps_info.get(4)[1][0])
    multiplier = float(gps_info.get(4)[1][1])
    longitude_minutes = minutes/multiplier
    seconds = float(gps_info.get(4)[2][0])
    multiplier = float(gps_info.get(4)[2][1])
    longitude_seconds = seconds/multiplier
    # The sign is changed depending on if this is E or W
    if longitude_direction == 'E' or longitude_direction == 'e':
        longitude = longitude_degrees+longitude_minutes/60 +longitude_seconds/3600
    elif longitude_direction == 'W' or longitude_direction == 'w':
        longitude = -(longitude_degrees+longitude_minutes/60 +longitude_seconds/3600)
    
    latitude_longitude = [latitude, longitude]
    
    # Returns a list with both latitude and longiude in decimal format.
    return latitude_longitude
    
# Pulls the date information from 
def get_date(image):
    # Gets all the exif data from the photo
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in image._getexif().items()
        if k in PIL.ExifTags.TAGS
    }
    # Pulls the date and time from the exif format
    date = exif.get('DateTime').split()[0]
    time = exif.get('DateTime').split()[1]
    # Reformats the date to use - instead of : 
    for character in date:
        if character == ':':
            date = date.replace(character, '-')
    # Combines the date and time to match the format pyinaturalist wants, 
    date_time = str(date) + 'T' + str(time)
    # returns a date and time formatted to submit to iNaturalist with
    # pyinaturalist
    return date_time


# This presumes the name of the folder ends with the taxon number.It finds 
# the taxon number by looking at the folder name and taking all the digits it 
# sees at the end. This allows you to name the folder " species name #####" to 
# quickly tell where photos go. For example anything in 'Aphididae-52381' is 
# uploaded as an aphid.
def get_taxon(folder):
    reverse_taxon = ''
    
    # This pulls out just the folder name
    folder =os.path.split(os.path.dirname(folder))[-1]
    
    # this reverses the folder name
    reverse_folder = ''.join(reversed(folder))
    
    # This finds the numbers at the end of the folder name and stores them 
    # but they are in reverse order
    for character in reverse_folder:
        if character.isdigit():
            reverse_taxon = reverse_taxon + character
            
    # Reverses the order of the digits to get a correct taxon number
    taxon = ''.join(reversed(reverse_taxon))
    return taxon

#Uploads all photos in a folder, each photo is an individual observation.
def upload_folder_single(folder):
    # Makes a list of all files in the folder inside element 2 of a tuple
    for file in os.walk(folder):
        if file[0] == folder:
            files = file

    # Creates list of all the file paths for every file in the folder.
    file_paths = []
    for file in files[2]:   # All files are in files[2]
        file_path = files[0] + file  # files[0] has the path to the folder
        file_paths.append(file_path) # Makes a big list of paths
    
    # This is getting a token to allow photos to be uploaded.
    token = get_access_token(username=user, password=passw,
                             app_id=app,
                             app_secret=secret)
    
    # This goes to every file, checks if it is a jpg, gets the gps coordinates,
    # get the time, and uploads it to iNaturalist.
    for file in file_paths:
       if file[-3:].lower() == 'jpg':
           print('Uploading ' + file)
           try:
               img = PIL.Image.open(file)
               coordinates = get_lat_long(img)
           except:000000000000000000000000000000000000000000000000
               coordinates = 'No Coordinates'
           try:
               img = PIL.Image.open(file)
               date_time = get_date(img)
           except:
               date_time = 'No Date or Time'
           taxon = get_taxon(folder)    

           params = {'observation':
                        {'taxon_id': taxon,  # Vespa Crabro
                         'observed_on_string': date_time,
                         'time_zone': time_zone,
                         'description': '',
                         'tag_list': '',
                         'latitude': coordinates[0],
                         'longitude': coordinates[1],
                         'positional_accuracy': 50, # meters,
            
    
                         'observation_field_values_attributes':
                            [{'observation_field_id': '','value': ''}],
                         },}
           r = create_observations(params=params, access_token=token)
            
           new_observation_id = r[0]['id']
           print('Uploaded as observation #' + str(new_observation_id))
           print('Uploading photo')
    
            
           r = add_photo_to_observation(observation_id=new_observation_id,
                            file_object=open(file, 'rb'),
                            access_token=token)
           
           
# Uploads all photos in a folder to a single observation.
def upload_folder_multiple(species_folder, folder):
    # Makes a list of all files in the folder inside element 2 of a tuple
    for file in os.walk(folder):
        if file[0] == folder:
            files = file

    # Creates list of all the file paths for every file in the folder.
    file_paths = []
    for file in files[2]:   # All files are in files[2]
        file_path = files[0] + file  # files[0] has the path to the folder
        file_paths.append(file_path) # Makes a big list of paths

    # This is getting a token to allow photos to be uploaded.
    token = get_access_token(username=user, password=passw,
                             app_id=app,
                             app_secret=secret)
    
    # This goes to every file, checks if it is a jpg, gets the gps coordinates,
    # get the time, and uploads it to iNaturalist.
    jpgs=[]
    for file in file_paths:
        if file[-3:].lower() == 'jpg':
            jpgs.append(file)

    try:
        img = PIL.Image.open(jpgs[0])
        coordinates = get_lat_long(img)
    except:
        coordinates = 'No Coordinates'
    try:
        img = PIL.Image.open(file)
        date_time = get_date(img)
    except:
        date_time = 'No Date or Time'
    taxon = get_taxon(species_folder)
#    print(coordinates)
#    print(date_time)
#    print(' the taxon is ' + str(taxon))

    params = {'observation':
                {'taxon_id': taxon,  # Vespa Crabro
                 'observed_on_string': date_time,
                 'time_zone': time_zone,
                 'description': '',
                 'tag_list': '',
                 'latitude': coordinates[0],
                 'longitude': coordinates[1],
                 'positional_accuracy': 50, # meters,
    

                 'observation_field_values_attributes':
                    [{'observation_field_id': '','value': ''}],
                 },}
    r = create_observations(params=params, access_token=token)
    
    new_observation_id = r[0]['id']

    for file in jpgs:
        print('uploading' + str(file) + ' TO ' + str(jpgs[0]))
        r = add_photo_to_observation(observation_id=new_observation_id,
                    file_object=open(file, 'rb'),
                    access_token=token)           
           
           


for folder in directories:
    subfolder = folder_name +'/' + folder + '/'
#    print(subfolder)
    upload_folder_single(subfolder)

subdirectories = []
for folder in directories:
        subfolder = folder_name +'/' + folder + '/'
        for root, dirs, files in os.walk(subfolder):
#            subdirectories.append(dirs)

            if dirs:
                subsubfolder = subfolder + dirs[0]+ '/'
                upload_folder_multiple(subfolder, subsubfolder)



        

print("Program complete")
