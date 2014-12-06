import os
import pandas as pd

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

# ***There were some anomalies in the data where there were 0 electors
# in a polling district, yet there were a positive number of votes cast
# so I had to scrap this part ***

# Save the polling station number/electors number since they will be 
# destroyed when we create a pivot table
# pollNumberElectors = pollData[['Polling Station Number', 'Electors for Polling Station']]
# pollNumberElectors = pollNumberElectors.drop_duplicates()


# Create a pivot table of the data by polling district/candidate name
pollData = pollData.pivot(index='Polling Station Number', columns='CandidateParty', values='Candidate Poll Votes Count')
pollData.reset_index(level=0, inplace=True) # Turn the index back into a column

# *** See note above about data anomalies ***

# Merge the newly made pivot table with the electors/poll numbers
# pollData = pd.merge(pollData, pollNumberElectors, on="Polling Station Number")

# Strip the letters off polling stations since the geodata does not include 
# these letters.
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
pollDataPercent = pollData.iloc[:,range(1,numColsPollData-1)]

# Divide it by the total votes for each polling district
numColsPerData = len(pollDataPercent.columns)
for i in range(0,numColsPerData):
    pollDataPercent.ix[:,i] = pollDataPercent.ix[:,i]/pollData['Vote Totals']
pollDataPercent = pollDataPercent*100
# Rename columns
colNames = list(pollDataPercent.columns.values)
colNames = [x + " (%)" for x in colNames]
pollDataPercent.columns = colNames

# Merge it with the original data set
pollData = pd.concat([pollData,pollDataPercent], axis=1)

# Write out the data
outFile = "pollresults_resultatsbureau" + str(riding[0]) + "Test001.csv"
outPath = currDir + "/Output/" + outFile
pollData.to_csv(outPath, index=False)


# pollDataTest = pollData.copy() # For testing
