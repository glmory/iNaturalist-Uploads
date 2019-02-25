""" This file includes all the functions used in the associated file
upload_folders.py. This is primarily functions associated with getting exif 
data from the photos, choosing a taxa based on the name of the folder
and uploading the files to iNaturalist."""

import shutil
import os
import PIL
from PIL import ExifTags
import pyinaturalist
from pyinaturalist.rest_api import create_observations
from pyinaturalist.rest_api import get_access_token
from pyinaturalist.rest_api import add_photo_to_observation

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
        latitude = latitude_degrees+latitude_minutes/60 \
                    + latitude_seconds/3600
    elif latitude_direction == 'S' or latitude_direction == 's':
        latitude = -(latitude_degrees+latitude_minutes/60 \
                    + latitude_seconds/3600)
        
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
        longitude = longitude_degrees+longitude_minutes/60 \
                    + longitude_seconds/3600
    elif longitude_direction == 'W' or longitude_direction == 'w':
        longitude = -(longitude_degrees+longitude_minutes/60 \
                    + longitude_seconds/3600)
    
    latitude_longitude = [latitude, longitude]
    
    # Returns a list with both latitude and longiude in decimal format.
    return latitude_longitude



# Pulls the date information from 
def get_date(image):

    # Pulls the date and time from the exif format, had to use 36867 to get
    # the time the image was taken
    
    date_and_time = PIL.Image.open(image)._getexif()[36867]
    
    # Splits it to separate date and time
    date = date_and_time.split()[0]
    time = date_and_time.split()[1]

    # Reformats the date to use - instead of : 
    for character in date:
        if character == ':':
            date = date.replace(character, '-')
    # Combines the date and time to match the format pyinaturalist wants, 
    date_time = str(date) + 'T' + str(time)
    # returns a date and time formatted to submit to iNaturalist with
    # pyinaturalist
    return date_time


# This presumes the name of the folder is the species name, taxon number or 
# both. For example anything in 'Aphididae-52381' or 'Aphididae' or 'Aphids' 
# or 52381 is uploaded as an aphid. If the name and taxon number conflict it
# seems to take the taxon number as the correct value. 

def get_taxon(folder):   
    # This pulls out just the folder name
    folder =os.path.split(os.path.dirname(folder))[-1]
    species = ''
    taxon = ''
    for character in folder:
        if not character.isdigit():
            species = species + character
    
    for character in folder:
        if character.isdigit():
            taxon = taxon + character
    

    return [species, taxon]


#Uploads all photos in a folder, each photo is an individual observation.
def upload_folder_single(folder, uploaded_folder, time_zone, accuracy, 
                         user, passw, app, secret):
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
                img.close()
            except:
                coordinates = 'No Coordinates'
            try:
                date_time = get_date(file)
                img.close()
            except:
                date_time = 'No Date or Time'
            [species, taxon] = get_taxon(folder)    

            params = {'observation':
                        {'taxon_id': taxon,  
                         'species_guess': species,
                         'observed_on_string': date_time,
                         'time_zone': time_zone,
                         'description': '',
                         'tag_list': '',
                         'latitude': coordinates[0],
                         'longitude': coordinates[1],
                         'positional_accuracy': int(accuracy), # meters,
            
    
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
           
            folder_name = os.path.split(folder)
            folder1_name = os.path.split(folder_name[0])
            destination = uploaded_folder +folder1_name[1] + '/'

            if new_observation_id:       
                try:
                    os.mkdir(destination)
                except:
                    pass
                try:
                    shutil.copy2(file, destination)
                    os.remove(file)
                except:
                    print('failed file move')
                    pass
           
# Uploads all photos in a folder to a single observation.
def upload_folder_multiple(species_folder, folder, uploaded_folder,
                           time_zone, accuracy, user, passw, app, secret):
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
        img.close()
    except:
        coordinates = 'No Coordinates'
    try:
        date_time = get_date(file)
        img.close()
    except:
        date_time = 'No Date or Time'
    
    [species, taxon] = get_taxon(species_folder)
    print(species)
#    print(coordinates)
#    print(date_time)
#    print(' the taxon is ' + str(taxon))

    params = {'observation':
                {'taxon_id': taxon,  
                 'species_guess': species,
                 'observed_on_string': date_time,
                 'time_zone': time_zone,
                 'description': '',
                 'tag_list': '',
                 'latitude': coordinates[0],
                 'longitude': coordinates[1],
                 'positional_accuracy': int(accuracy), # meters,
    

                 'observation_field_values_attributes':
                    [{'observation_field_id': '','value': ''}],
                 },}
    r = create_observations(params=params, access_token=token)
    
    new_observation_id = r[0]['id']

    print('Uploaded as observation #' + str(new_observation_id))
    print('Uploading photos')
    for file in jpgs:
        print('uploading ' + str(file) + ' TO ' + str(new_observation_id))
        r = add_photo_to_observation(observation_id=new_observation_id,
                    file_object=open(file, 'rb'),
                    access_token=token) 
          
    folder_name = os.path.split(folder)
    folder1_name = os.path.split(folder_name[0])
    folder2_name = os.path.split(folder1_name[0])

    new_species_folder = uploaded_folder +folder2_name[1] +'/'
    destination = new_species_folder + folder1_name[1]

    if new_observation_id:       

        try:
            os.mkdir(new_species_folder)
        except:
            pass
        try:
            shutil.move(folder, destination)
        except:
            print('failed file move')
            pass
