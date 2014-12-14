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
import numpy as np
import shapefile

# Create an array for the years we're interested in
years = [2011]

# Get the folder where the data is
cwd = os.path.dirname(os.path.abspath(__file__))
dataFolder = os.path.join(cwd, str(years[0]))

# Get list of riding numbers
folderName = "pollresults_resultatsbureau_canada"
ridingFile = os.path.join(dataFolder, folderName, "table_tableau11.csv")
ridingList = pd.read_csv(ridingFile)
ridingList = ridingList.iloc[:, 1:3]


def percent_by_polling_district(riding, year):
    fileName = "pollresults_resultatsbureau" + str(riding) + ".csv"

    # Directory + Filename
    filePath = os.path.join(dataFolder, folderName, fileName)
    # Load the data
    pollData = pd.read_csv(filePath)

    # Get column names, and remove French portions
    colNames = list(pollData.columns.values)
    colNames = [x.split('/')[0] for x in colNames]
    pollData.columns = colNames

    # Drop unnecessary columns
    listColDrop = ['Electoral District Name_English',
                   'Electoral District Name_French',
                   'Electoral District Number', 'Void Poll Indicator',
                   'No Poll Held Indicator', 'Merge With',
                   'Rejected Ballots for Polling Station',
                   'Political Affiliation Name_French',
                   "Candidate's Middle Name", 'Incumbent Indicator',
                   'Elected Candidate Indicator']

    pollData = pollData.drop(listColDrop, axis=1)

    # Clean up the column names a bit more
    colNames = list(pollData.columns.values)
    colNames = [x.split('_')[0] for x in colNames]
    pollData.columns = colNames

    # Strip the polling ID column of whitespace.
    polCol = 'Polling Station Number'
    s = lambda x: str(x).strip(" ")
    pollData[polCol] = pollData[polCol].map(s)

    # Merge some of the columns so that we can create a pivot table
    nameParty = (pollData["Candidate's First Name"] + " " +
                 pollData["Candidate's Family Name"] + " / " +
                 pollData["Political Affiliation Name"])
    pollData['CandidateParty'] = nameParty

    # Drop the ones we don't need
    listColDrop = ["Candidate's First Name",
                   "Candidate's Family Name",
                   "Political Affiliation Name"]
    pollData = pollData.drop(listColDrop, axis=1)

    # Create a pivot table of the data by polling district/candidate name
    pollData = pollData.pivot(
        index='Polling Station Number',
        columns='CandidateParty',
        values='Candidate Poll Votes Count')
    # Turn the index back into a column
    pollData.reset_index(level=0, inplace=True)

    # Strip the letters off polling stations since the geospatial data
    #  does not include these letters.
    stripCharacters = "ABCDEFG"
    s = lambda x: str(x).strip(stripCharacters)
    statCol = 'Polling Station Number'
    pollData[statCol] = pollData[statCol].map(s)

    # Merge polling stations
    pollData = pollData.groupby('Polling Station Number').sum()
    pollData.reset_index(level=0, inplace=True)

    # Get the vote totals
    pollData['Vote Totals'] = pollData.sum(axis=1, numeric_only=True)

    # Calculate the percent for each

    # Grab the data we want converted to a percent
    numColsPollData = len(pollData.columns)
    pollDataPercent = pollData.iloc[:, range(1, numColsPollData-1)].copy()

    # Divide it by the total votes for each polling district
    pollDataPercent = pollDataPercent.div(pollData['Vote Totals'], axis=0)

    pollDataPercent = np.round(pollDataPercent*100, decimals=2)

    # Rename columns
    colNames = list(pollDataPercent.columns.values)
    colNames = [x + " (%)" for x in colNames]
    pollDataPercent.columns = colNames

    # Merge it with the original data set
    pollData = pd.concat([pollData, pollDataPercent], axis=1)

    # Write out the data
    # outName = str(year) + "Results" + str(riding) + ".csv"
    # outDir = os.path.join(dataFolder, "Output")

    # if not os.path.exists(outDir):
    #    os.makedirs(outDir)

    # outFile = os.path.join(outDir, outName)
    # pollData.to_csv(outFile, index=False)

    # Create the shapefile for this riding with data appended
    create_riding_shapefile(riding, pollData)


def read_shapefile(year):
    """ Read in a shapefile and return it """
    fileName = "pd_a"
    filePath = os.path.join(dataFolder, "pd308.2011", fileName)

    # Return the entire shapefile of polling districts
    return shapefile.Reader(filePath)


def create_riding_shapefile(ridingNum, pollData):
    # Create writer
    riding = shapefile.Writer(shapeType=shapefile.POLYGON)
    # Copy the original fields
    riding.fields = list(pollDistShp.fields)

    # Get the subset of the shapefile for the riding
    subset = []
    for rec in pollDistEnum:
        if rec[1][6] == ridingNum:
            subset.append(rec)

    # Add all the shapes and records to the file
    for rec in subset:
        riding._shapes.append(pollDistShp.shape(rec[0]))
        riding.records.append(rec[1])

    outDir = os.path.join(dataFolder, "RidingFiles")
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    outFile = os.path.join(outDir, str(ridingNum))
    print(ridingNum)
    riding.save(outFile)


# Load the shapefile that has all the polling district shapes
pollDistShp = read_shapefile(years[0])
# Enumerate so that we can use the index number later when we subset it
pollDistEnum = list(enumerate(pollDistShp.records()))

# Create an array for the riding IDs we're interested in
ridings = [13003, 13008]  # For testing at small scale
# ridings = ridingList.ix[:, 1] # The full list

for riding in ridings:
    percent_by_polling_district(riding, years[0])
