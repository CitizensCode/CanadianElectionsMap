# Copyright 2014 Citizens Code Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pandas as pd
from datetime import datetime
from electionfunctions import percent_by_polling_district
from shapefilefunctions import read_shapefile

# 2011 voting data downloaded from this page: http://elections.ca/scripts/resval/ovr_41ge.asp?prov=&lang=e
# Specifically, the data for all ridings in the single zip file here: http://elections.ca/scripts/OVR2011/34/data_donnees/pollresults_resultatsbureau_canada.zip
# Create a folder for the date of the file in your working directory and
# unzip the file in that directory.
# Do the same for the 2011 polling districts from:
# http://geogratis.gc.ca/api/en/nrcan-rncan/ess-sst/c0fdfa13-8851-5ade-abaf-09445d390d31.html

start = datetime.now()

# Create an array for the years we're interested in
years = [2011]

# Used for testing
# cwd = os.getcwd()

# Get the folder where the data is
cwd = os.path.dirname(os.path.abspath(__file__))
dataFolder = os.path.join(cwd, str(years[0]))

# Get list of riding numbers
ridingFile = os.path.join(dataFolder, "pollresults_resultatsbureau_canada", "table_tableau11.csv")
ridingList = pd.read_csv(ridingFile)
ridingList = ridingList.iloc[:,1:3]

# Load the shapefile that has all the polling distrct shapes
pollDistShp = read_shapefile(years[0], dataFolder)
# Enumerate so that we can use the index number later when we subset it
pollDistEnum = list(enumerate(pollDistShp.records()))

# Create an array for the riding IDs we're interested in
# ridings = [13003, 13008] # For testing at small scale
ridings = ridingList.ix[:,1]

def main():
    for riding in ridings:
        percent_by_polling_district(riding, years[0], pollDistShp, pollDistEnum, dataFolder)
    
    end = datetime.now()
    print end - start

if __name__ == '__main__':
    main()
