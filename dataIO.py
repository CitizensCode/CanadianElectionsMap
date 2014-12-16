# Copyright (c) 2007-2011, GeoDa Center for Geospatial Analysis and Computation
# All rights reserved.

# SOURCE: https://github.com/GeoDaSandbox/sandbox/blob/master/pyGDsandbox/dataIO.py

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.

# * Neither the name of the GeoDa Center for Geospatial Analysis and Computation
#   nor the names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

'''
dataIO: module for code related to data files manipulation

Find here classes and functions to deal with DBFs, CSVs as well as Numpy
arrays, pandas DataFrames, etc.
'''

import pysal as ps
import numpy as np
import pandas as pd
import os
import ast
from shutil import copyfile


def df2dbf(df, dbf_path, my_specs=None):
    '''
    Convert a pandas.DataFrame into a dbf.

    __author__  = "Dani Arribas-Bel <darribas@asu.edu> "
    ...

    Arguments
    ---------
    df          : DataFrame
                  Pandas dataframe object to be entirely written out to a dbf
    dbf_path    : str
                  Path to the output dbf. It is also returned by the function
    my_specs    : list
                  List with the field_specs to use for each column.
                  Defaults to None and applies the following scheme:
                    * int: ('N', 14, 0)
                    * float: ('N', 14, 14)
                    * str: ('C', 14, 0)
    '''
    if my_specs:
        specs = my_specs
    else:
        type2spec = {int: ('N', 20, 0),
                     np.int64: ('N', 20, 0),
                     float: ('N', 36, 2),
                     np.float64: ('N', 36, 2),
                     str: ('C', 14, 0),
                     object: ('C', 14, 0)
                     }
        types = [type(df[i][0]) for i in df.columns]
        specs = [type2spec[t] for t in types]
    db = ps.open(dbf_path, 'w')
    db.header = list(df.columns)
    db.field_spec = specs
    for i, row in df.T.iteritems():
        db.write(row)
    db.close()
    return dbf_path


def dbf2df(dbf_path, index=None, cols=False, incl_index=False):
    '''
    Read a dbf file as a pandas.DataFrame, optionally selecting the index
    variable and which columns are to be loaded.

    __author__  = "Dani Arribas-Bel <darribas@asu.edu> "
    ...

    Arguments
    ---------
    dbf_path    : str
                  Path to the DBF file to be read
    index       : str
                  Name of the column to be used as the index of the DataFrame
    cols        : list
                  List with the names of the columns to be read into the
                  DataFrame. Defaults to False, which reads the whole dbf
    incl_index  : Boolean
                  If True index is included in the DataFrame as a
                  column too. Defaults to False

    Returns
    -------
    df          : DataFrame
                  pandas.DataFrame object created
    '''
    db = ps.open(dbf_path)
    if cols:
        if incl_index:
            cols.append(index)
        vars_to_read = cols
    else:
        vars_to_read = db.header
    data = dict([(var, db.by_col(var)) for var in vars_to_read])
    if index:
        index = db.by_col(index)
        db.close()
        return pd.DataFrame(data, index=index)
    else:
        db.close()
        return pd.DataFrame(data)


def appendcol2dbf(dbf_in, dbf_out, col_name, col_spec, col_data,
                  replace=False):
    """
    Function to append a column and the associated data to a DBF.

    __author__ = "Nicholas Malizia <nmalizia@asu.edu>"

    Arguments
    ---------
    dbf_in      : string
                  name and path of the dbf file to be updated, including
                  extension.
    dbf_out     : string
                  name and path of the new file to be created, including
                  extension.
    col_name    : string
                  name of the field to be added to dbf.
    col_spec    : tuple
                  the format for the tuples is (type,len,precision).
                  valid types are 'C' for characters, 'L' for bool, 'D' for
                  data, 'N' or 'F' for number.
    col_data    : list
                  a list of values to be written in the column, note the length
                  of this list should match the number of records in the
                  original dbf.
    replace     : boolean
                  if true, replace existing dbf file

    Example
    -------

    Just a simple example using the ubiquitous Columbus dataset. First,
    specify the names of the input and output DBFs.

    >>> dbf_in = 'columbus.dbf'
    >>> dbf_out = 'columbus_copy.dbf'

    Next, give the name of the column to be added.

    >>> col_name = 'test'

    Also, provide the specifications associated with the new column. See the
    documentation above for a further explanation of this requirement.
    Essentially it's a tuple with three parameters: type, length and precision.

    >>> col_spec = ('N',9,0)

    Finally, we need to provide the data to populate the column. Ideally, this
    would be something that you'd already have handy (that's why you're adding
    a new column to the DBF right?). Here though we'll just create something
    simple like an integer ID. This could be a list of null values if the data
    aren't ready yet and you want a placeholder.

    >>> db = ps.open(dbf_in)
    >>> n = db.n_records
    >>> col_data = range(n)

    We pull it all together with the function created here.

    >>> appendcol2dbf(dbf_in,dbf_out,col_name,col_spec,col_data)

    This will output a second DBF that can then be used to replace the
    original DBF (this will often be the case when working with shapefiles). I
    figured it would be more prudent to have the function by default create a
    second file which the user can then inspect and manually replace if they
    want rather than just blindly overwriting the original. The latter is an
    option. Use at your own risk - I don't want complaints that I deleted your
    data ;)

    """

    # open the original dbf and create a new one with the new field
    db = ps.open(dbf_in)
    db_new = ps.open(dbf_out, 'w')
    db_new.header = db.header
    db_new.header.append(col_name)
    db_new.field_spec = db.field_spec
    db_new.field_spec.append(col_spec)

    # populate the dbf with the original and new data
    item = 0
    for rec in db:
        rec_new = rec
        rec_new.append(col_data[item])
        db_new.write(rec_new)
        item += 1

    # close the files
    db_new.close()
    db.close()

    # the following text will delete the old dbf and replace it with the new
    #one retaining the name of the original file.
    if replace is True:
        os.remove(dbf_in)
        os.rename(dbf_out, dbf_in)

    # copy shp and shx
    if not os.path.exists(dbf_out[:-4] + '.shp'):
        copyfile(dbf_in[:-4] + '.shp', dbf_out[:-4] + '.shp')
    if not os.path.exists(dbf_out[:-4] + '.shx'):
        copyfile(dbf_in[:-4] + '.shx', dbf_out[:-4] + '.shx')
