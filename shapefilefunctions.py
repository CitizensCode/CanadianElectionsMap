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
import shapefile

def read_shapefile(year, dataFolder):
    """ Read in a shapefile and return it """
    fileName = "pd_a"
    filePath = os.path.join(dataFolder, "pd308.2011", fileName)
    
    # Return the entire shapefile of polling districts
    return shapefile.Reader(filePath)


def subset_shapefile_by_riding(pollDistShp, pollDistEnum, ridingNum, dataFolder):
    # Create writer
    riding = shapefile.Writer(shapeType=shapefile.POLYGON)
    # Copy the original fields
    riding.fields = list(pollDistShp.fields)

    subset = []
    for rec in pollDistEnum:
        if rec[1][6] == ridingNum:
            subset.append(rec)

    for rec in subset:
        riding._shapes.append(pollDistShp.shape(rec[0]))
        riding.records.append(rec[1])

    outDir = os.path.join(dataFolder, "RidingFiles")
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    outFile = os.path.join(outDir, str(ridingNum))
    print ridingNum
    riding.save(outFile)

# Testing
#years = [2011]
#cwd = os.getcwd()
#dataFolder = os.path.join(cwd, str(years[0]))
#
#pollSF = read_shapefile(years[0], dataFolder)
#pollDistEnum = list(enumerate(pollSF.records()))
#
#subset_shapefile_by_riding(pollSF, pollDistEnum, 13008, dataFolder)
