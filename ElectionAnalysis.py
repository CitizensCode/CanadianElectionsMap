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
from electionfunctions import percent_by_polling_district

# Data downloaded from this page: http://elections.ca/scripts/resval/ovr_41ge.asp?prov=&lang=e
# Specifically, the data for all ridings in the single zip file here: http://elections.ca/scripts/OVR2011/34/data_donnees/pollresults_resultatsbureau_canada.zip
# Create a folder for the date of the file in your working directory and
# unzip the file in that directory.

# Create an array for the years we're interested in
years = [2011]
dataFolder = os.getcwd() + "/" + str(years[0]) + "/pollresults_resultatsbureau_canada/"

# Get list of riding numbers
ridingFile = dataFolder + "table_tableau11.csv"
ridingList = pd.read_csv(ridingFile)
ridingList = ridingList.iloc[:,1:3]

# Create an array for the riding IDs we're interested in
# ridings = [13003, 13008]
ridings = ridingList.ix[:,1]

for year in years:
    for riding in ridings:
        percent_by_polling_district(riding, year, dataFolder)
