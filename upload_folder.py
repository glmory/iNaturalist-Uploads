# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 20:30:51 2019

@author: Jesse
"""

# Input your user name here:
user = ''

# Input your password here:
passw = ''

# Input your app ID and secret here:
app = ''
secret = ''


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

# This is used to upload the photos. 
import pyinaturalist

from pyinaturalist.rest_api import create_observations
from pyinaturalist.rest_api import get_access_token

print("Running")

# This code lets you choose a photo, can delete and replace with folder_name=''
root = Tk()
filename =  filedialog.askopenfilename(initialdir = "/",
                                    title = "Select one of the .jpg files in "
                                    "the folder to be uploaded. All files in "
                                    "the folder will be uploaded. The folder "
                                    "name should start with the taxon number",
                                    filetypes = (("jpeg files","*.jpg"),
                                    ("all files","*.*")))
root.withdraw()

# 
folder_name = os.path.dirname(filename) +'/'
print('Uploading all photos in ' + folder_name + 'as a unique observation')

# Makes a list of all files in the folder inside element 2 of a tuple
for file in os.walk(folder_name):
    if file[0] == folder_name:
        files = file

# Creates list of all the file paths for every file in the folder.
file_paths = []
for file in files[2]:   # All files are in files[2]
    file_path = files[0] + file  # files[0] has the path to the folder
    file_paths.append(file_path) # Makes a big list of paths


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
    
    # The sign is changed depending on if this is N or S
    if latitude_direction == 'N' or latitude_direction == 'n':
        latitude = latitude_degrees+latitude_minutes/60
    elif latitude_direction == 'S' or latitude_direction == 's':
        latitude = -(latitude_degrees+latitude_minutes/60)
        
    longitude_direction = gps_info.get(3)[0]
    longitude_degrees = gps_info.get(4)[0][0]
    minutes = float(gps_info.get(4)[1][0])
    multiplier = float(gps_info.get(4)[1][1])
    longitude_minutes = minutes/multiplier
    # The sign is changed depending on if this is E or W
    if longitude_direction == 'E' or longitude_direction == 'e':
        longitude = longitude_degrees+longitude_minutes/60
    elif longitude_direction == 'W' or longitude_direction == 'w':
        longitude = -(longitude_degrees+longitude_minutes/60)
    
    latitude_longitude = [latitude, longitude]
    
    # Returns a list with both latitude and longiude in decimal format.
    return latitude_longitude
    
# Pulls the date information from 
def get_date(image):
    # Gets all the exif data from the photo
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
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


# This presumes the name of the folder starts with the taxon number.It finds 
# the taxon number by looking at the folder name and taking all the digits it 
# sees. This allows you to name the folder "##### species name" to quickly
# tell where photos go. For example anything in '52381-Aphididae' is uploaded
# as an aphid.
def get_taxon(folder):
    taxon = ''
    folder =os.path.split(os.path.dirname(folder_name))[-1]
    for character in folder:
        if character.isdigit():
            taxon = taxon + character
    return taxon


# This is getting a token to allow photos to be uploaded.
token = get_access_token(username=user, password=passw,
                         app_id=app,
                         app_secret=secret)

# This goes to every file, checks if it is a jpg, gets the gps coordinates,
# get the time, and uploads it to iNaturalist.
for file in file_paths:
   if file[-3:] == 'jpg' or file[-3:] == 'JPG' or file[-3:] == 'Jpg':
       print('Uploading ' + file)
       try:
           img = PIL.Image.open(file)
           coordinates = get_lat_long(img)
       except:
           coordinates = 'No Coordinates'
       try:
           img = PIL.Image.open(file)
           date_time = get_date(img)
       except:
           date_time = 'No Date or Time'  
           
       # This requires the folder name to start with the taxon number. 
       taxon = get_taxon(folder_name)    

       params = {'observation':
                    {'taxon_id': taxon,  # Vespa Crabro
                     'observed_on_string': date_time,
                     'time_zone': time_zone,
                     'description': 'This is a test upload',
                     'tag_list': '',
                     'latitude': coordinates[0],
                     'longitude': coordinates[1],
                     'positional_accuracy': 50, # meters,
        

                     'observation_field_values_attributes':
                        [{'observation_field_id': '','value': ''}],
                     },}
       r = create_observations(params=params, access_token=token)
        
       new_observation_id = r[0]['id']

       
       from pyinaturalist.rest_api import add_photo_to_observation

       r = add_photo_to_observation(observation_id=new_observation_id,
                        file_object=open(file, 'rb'),
                        access_token=token)

print("Program complete")
