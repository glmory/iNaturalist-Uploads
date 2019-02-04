# iNaturalist-Uploads
Uses pyinaturalist to batch upload photos to iNaturalist

This script assumes a large number of photos of the same species. This might happen for example if you were trying to map every
tree on a property. The workflow would consist of taking a single geotagged photo of each individual then separating out the 
photos so each one is in a folder which starts with its taxon ID. You can find the taxon id by going to the iNaturalist species
page and noting the number in the url. 

For example aphids the aphids site is https://www.inaturalist.org/taxa/52381-Aphididae so aphids would go in a folder named '52381'
or '52381 Aphids' or '52381-Aphididae' 

If you don't have python, I suggest installing Anaconda then pyinaturalist(https://pypi.org/project/pyinaturalist/) . You will 
then need to get an app ID (https://www.inaturalist.org/oauth/applications/new). It might be necessary to also update a 
dependency of pyinaturalist to get it to install. 

Before running the script first open this script, add your user name, password, app id, secret, and the time zone of the photos. 
Then run the script. It should upload every jpg file in the folder as the file you select as a separate observation.
