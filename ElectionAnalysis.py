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
import urllib
import zipfile
import shapefile as sf
from dataIO import df2dbf, dbf2df

# Create an array for the years we're interested in
years = [2011]
urls = {"pollDivs":
            {2011: "http://elections.ca/scripts/OVR2011/34/data_donnees/pollresults_resultatsbureau_canada.zip"},
        "geodata" : 
            {2011: "http://ftp2.cits.rncan.gc.ca/pub/geott/electoral/2011/pd308.2011.zip"}}

# Get the folder where the data is
cwd = os.path.dirname(os.path.abspath(__file__))
dataFolder = os.path.join(cwd, str(years[0]))
if not os.path.exists(dataFolder):
        os.makedirs(dataFolder)


def download_extract(url, year):
    """Downloads and extracts the data"""
    pollFile = os.path.join(dataFolder, url.split("/")[-1])
    if not os.path.isfile(pollFile):
        print("Downloading.")
        urllib.urlretrieve(url, pollFile)
        # Takes the filename out of the url
        d = os.path.join(dataFolder, "".join(url.split("/")[-1].split(".")[:-1]))
        os.makedirs(d)
        # Unzips it
        with zipfile.ZipFile(pollFile) as zf:
            zf.extractall(d)
        print("Download and extraction complete.")

download_extract(urls["pollDivs"][2011], 2011)
download_extract(urls["geodata"][2011], 2011)

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

    # Create the shapefile for this riding with data appended
    outFile = create_riding_shapefile(riding, pollData)

    # Load the dbf part of the shapefile into a data frame
    dbfFile = outFile + ".dbf"
    dbfDF = dbf2df(dbfFile)
    # Keep only the columns we need to merge
    dbfDF = dbfDF[["EMRP_NAME", "FED_NUM", "POLL_NAME"]]

    # Merge the two sets together
    left = "EMRP_NAME"
    right = "Polling Station Number"
    merged = pd.merge(dbfDF, pollData, left_on=left, right_on=right)
    df2dbf(merged, dbfFile)
    print(riding)


def read_shapefile(year):
    """ Read in a shapefile and return it """
    fileName = "pd_a"
    filePath = os.path.join(dataFolder, "pd308.2011", fileName)
    wmFilePath = filePath + "WM.shp"
    filePath += ".shp"
    # Checks to see if the file has been converted to Web Mercator
    # If not, it converts it
    if (not os.path.isfile(wmFilePath)):
        print("Converting shapefile to Web Mercator.")
        command = ("ogr2ogr -t_srs EPSG:3857 '" +
                   wmFilePath + "' '" + filePath + "'")
        os.system(command)
        print("Done conversion.")

    # Return the entire shapefile of polling districts
    return sf.Reader(wmFilePath)

# Set the projection for Mapbox
prj = 'PROJCS[ "WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],EXTENSION["PROJ4","+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext  +no_defs"],AUTHORITY["EPSG","3857"]]'


def create_riding_shapefile(ridingNum, pollData):
    # Create writer
    riding = sf.Writer(shapeType=sf.POLYGON)
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
    riding.save(outFile)

    # Create the prj file
    prjfile = open("%s.prj" % outFile, 'w')
    prjfile.write(prj)
    prjfile.close()
    # set_trace()
    return outFile


# Load the shapefile that has all the polling district shapes
pollDistShp = read_shapefile(years[0])

# Enumerate so that we can use the index number later when we subset it
pollDistEnum = list(enumerate(pollDistShp.records()))

# Create an array for the riding IDs we're interested in
ridings = [13003, 13008]  # For testing at small scale
# ridings = ridingList.ix[:, 1]  # The full list

for riding in ridings:
    percent_by_polling_district(riding, years[0])
