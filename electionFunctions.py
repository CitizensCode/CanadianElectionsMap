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

import pandas as pd
import numpy as np
import os
from shapefilefunctions import subset_shapefile_by_riding

def percent_by_polling_district(riding, year, pollDistShp, pollDistEnum, dataFolder):
    fileName = "pollresults_resultatsbureau" + str(riding) + ".csv"

    # Directory + Filename
    filePath = os.path.join(dataFolder, "pollresults_resultatsbureau_canada", fileName)
    # Load the data
    pollData = pd.read_csv(filePath)
    
    # Get column names, and remove French portions
    colNames = list(pollData.columns.values)
    colNames = [x.split('/')[0] for x in colNames]
    pollData.columns = colNames
    
    # Drop unnecessary columns
    listColDrop = ['Electoral District Name_English']
    listColDrop.extend(['Electoral District Name_French'])
    listColDrop.extend(['Electoral District Number', 'Void Poll Indicator'])
    listColDrop.extend(['No Poll Held Indicator', 'Merge With'])
    listColDrop.extend(['Rejected Ballots for Polling Station'])
    listColDrop.extend(['Political Affiliation Name_French'])
    listColDrop.extend(["Candidate's Middle Name", 'Incumbent Indicator'])
    listColDrop.extend(['Elected Candidate Indicator'])
    
    pollData = pollData.drop(listColDrop, axis=1)
    
    # Clean up the column names a bit more
    colNames = list(pollData.columns.values)
    colNames = [x.split('_')[0] for x in colNames]
    pollData.columns = colNames
    
    # Strip the polling ID column of whitespace.
    stripCharacters = " " #+ string.ascii_uppercase
    pollData['Polling Station Number'] = pollData['Polling Station Number'].map(lambda x: str(x).strip(stripCharacters))
    
    # Merge some of the columns so that we can create a pivot table
    nameParty = pollData["Candidate's First Name"] + " "
    nameParty = nameParty + pollData["Candidate's Family Name"] + " / "
    nameParty = nameParty + pollData["Political Affiliation Name"]
    pollData['CandidateParty'] = nameParty
    
    # Drop the ones we don't need
    listColDrop = ["Candidate's First Name"]
    listColDrop.extend(["Candidate's Family Name"])
    listColDrop.extend(["Political Affiliation Name"])
    pollData = pollData.drop(listColDrop, axis=1)    
    
    # Create a pivot table of the data by polling district/candidate name
    pollData = pollData.pivot(index='Polling Station Number', columns='CandidateParty', values='Candidate Poll Votes Count')
    pollData.reset_index(level=0, inplace=True) # Turn the index back into a column
    
    # Strip the letters off polling stations since the geospatial data does not  
    # include these letters.
    stripCharacters = "ABCDEFG"
    pollData['Polling Station Number'] = pollData['Polling Station Number'].map(lambda x: str(x).strip(stripCharacters))
    
    # Merge polling stations
    pollData = pollData.groupby('Polling Station Number').sum()
    pollData.reset_index(level=0, inplace=True)
    
    # Get the vote totals
    pollData['Vote Totals'] = pollData.sum(axis=1, numeric_only=True)
    
    # Calculate the percent for each
    
    # Grab the data we want converted to a percent
    numColsPollData = len(pollData.columns)
    pollDataPercent = pollData.iloc[:,range(1,numColsPollData-1)].copy()
    
    # Divide it by the total votes for each polling district
    pollDataPercent = pollDataPercent.div(pollData['Vote Totals'], axis=0)

    pollDataPercent = pollDataPercent*100
    pollDataPercent = np.round(pollDataPercent, decimals=2)
    
    # Rename columns
    colNames = list(pollDataPercent.columns.values)
    colNames = [x + " (%)" for x in colNames]
    pollDataPercent.columns = colNames
    
    # Merge it with the original data set
    pollData = pd.concat([pollData,pollDataPercent], axis=1)
    
    # Write out the data
    outFile = str(year) + "Results" + str(riding) + ".csv"
    outPath = os.path.join(os.getcwd(), "Output", outFile)
    pollData.to_csv(outPath, index=False)    
    
    # Subset the shapefile for this riding
    subset_shapefile_by_riding(pollDistShp, pollDistEnum, riding, dataFolder)
