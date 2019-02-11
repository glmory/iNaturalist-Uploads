# iNaturalist-Uploads

There are two scripts here, one basic one which uploads all photos in a folder (upload_folder.py) as one species, and a more complicated one which can handle cases where multiple photos go to one observation(upload_folder.py + import_functions.py + import_gui.py. 

Both use pyinaturalist to batch upload photos to iNaturalist

I will skip the simpler script as it is much less useful. 

Scripts make the most sense when you have a large number of photos of the same species. This might happen for example if you were trying to map every tree on a property. The workflow for upload_folders.py consists of separating out the photos so each one is in a folder which contains its common name, scientific name, or taxon ID. You can find the taxon id by going to the iNaturalist species page and noting the number in the url. Taxon numbers are the most likely to work as they are always unique, but in general if you just write any name you remember for a species as the name of the folder it will usually work. 

For example aphids the aphids site is https://www.inaturalist.org/taxa/52381-Aphididae so individual photos of aphids could go in a folder named:

.../main_folder/52381-Aphididae
.../main_folder/52381
.../main_folder/Aphididae 52381
.../main_folder/Aphids

To upload multiple photos to an observation it is necessary to create a subfolder in the species folder. So if you have five photos of an aphid it could go into any of the following paths:
.../main_folder/52381-Aphididae/New Folder
.../main_folder/52381/Aphids
.../main_folder/Aphididae 52381/ABCDEFGH
.../main_folder/Aphids/123456

Thus far I have not seen a limit on how many photos can be put in one folder. If you have ten thousand photos of pigeons you want to upload it should work to upload the whole batch. Definitely try it on a small number of photos first though to make sure you don't end up uploading ten thousand photos which you then have to manually edit. 

If you don't have python, I suggest installing Anaconda then pyinaturalist(https://pypi.org/project/pyinaturalist/) . You will 
then need to get an app ID (https://www.inaturalist.org/oauth/applications/new). It might be necessary to also update a 
dependency of pyinaturalist to get it to install. 

You will need an app ID and secret before running this, or other, pyinaturalist scripts:
https://www.inaturalist.org/oauth/applications/new

Before running the script first open this script, add your user name, password, app id, secret, and the time zone of the photos. 
Then run the script. It should upload every jpg file in the folder as the file you select as a separate observation.
