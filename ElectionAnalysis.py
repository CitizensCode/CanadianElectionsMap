import os
import pandas as pd
import string
# Data download from this page: http://elections.ca/scripts/resval/ovr_41ge.asp?prov=&lang=e
# Specifically, the data for all ridings in the single zip file
# here: http://elections.ca/scripts/OVR2011/34/data_donnees/pollresults_resultatsbureau_canada.zip
# Unzip it in your working directory and put it in a folder named
# for the year of the data.

# Get working directory
currDir = os.getcwd()

# Create an array for the years we're interested in
year = [2011]
fileFolder = currDir + "/" + str(year[0]) + "/pollresults_resultatsbureau_canada/"

# Create an array for the riding IDs we're interested in
riding = [13003]
fileName = "pollresults_resultatsbureau" + str(riding[0]) + ".csv"

# Directory + Filename
filePath = fileFolder + fileName


# Load the data
pollData = pd.read_csv(filePath)

# Clear unmeeded variables
# currDir = FileFolder = fileName = filePath = None

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

# Strip the letters off polling stations since the geodata does not include 
# these letters. We will merge them next.
stripCharacters = string.ascii_uppercase
pollData['Polling Station Number'] = pollData['Polling Station Number'].map(lambda x: str(x).strip(stripCharacters))

# Merge polling stations
pollDataTest = pollData.groupby('Polling Station Number')


# Write out the data
outFile = "pollresults_resultatsbureau" + str(riding[0]) + "Test001"
outPath = fileFolder + outFile
pollDataTest.to_csv(outPath)
