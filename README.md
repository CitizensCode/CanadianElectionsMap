Canadian Elections Map of Historical Vote Leanings
====================

Data analysis for a polling-district-by-polling-district visualization of historical election data, from this active initiatives on Citizens Code: http://ideas.citizenscode.org/t/create-a-poll-by-poll-interactive-map-of-historical-vote-leanings/16

Cedric Sam did some great work a few years ago taking poll-by-poll federal election data and visualizing it, allowing people to quickly view margins of victory, voter turnout and party-by-party votes: http://earth.smurfmatic.net/canada2011/polls/#130031

The poll data originally came from here:
http://elections.ca/scripts/resval/ovr_41ge.asp?prov=&lang=e1

And the geo data came from here: http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/c0fdfa13-8851-5ade-abaf-09445d390d31.html

This builds upon his work and make it possible to look at historical vote leanings in a single view.

2011 voting data downloaded from [this page](http://elections.ca/scripts/resval/ovr_41ge.asp?prov=&lang=e). Specifically, the data for all ridings in the single zip file [here](http://elections.ca/scripts/OVR2011/34/data_donnees/pollresults_resultatsbureau_canada.zip)

Before running the file, create a folder for the date of the file in your working directory (e.g. 2011) and
unzip the file in that directory. No other modifications should need to be made. Do the same for the 2011 polling districts from [here](http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/c0fdfa13-8851-5ade-abaf-09445d390d31.html).
