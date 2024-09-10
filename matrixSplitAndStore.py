import bct
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as pyplot
import glob
import os

# code for processing matrices from BrainWave which is a file with varying number of 
# matrices consisting of three rows of texts or NaNs followed by number of rows (row with filename, row with epoch name and 
# blank row between matrices)
# The rows of the matrices correspond to the number of rois from the atlas used.
# the code checks dimensions, removes columns and rows that contain NaNs
# and stores all separate matrices into different files containing part of the filename and an epochnumber

###### Adjust according to needs: ########

# Read the CSV file into a DataFrame, no header 
df_mymatrix = pd.read_csv('/Users/ilsevanstraaten/Documents/research/MEG_TUe/MergedMatricesMaartje/aeccmatrices_merged/Matrix_1031_1040_vectorview_8_16hz_aecc', delimiter='\t', header = None, low_memory=False)

# output path:
outputpath = '/Users/ilsevanstraaten/Documents/research/MNEandBCT/BWmatrices/output/matrices/'

# indicate matrix dimensions
number_of_rois = 246 # adjust according atlas used, default BNA

# indicate how many characters of the filename to be included in the matrixnames
number_of_title_letters = 4

# indicate other title text
titleInfo = 'AECc_8_16Hz'

##############################################################################################

outputpath = ('/Users/ilsevanstraaten/Documents/research/MNEandBCT/BWmatrices/output/matrices/')
# check file
if (len(df_mymatrix)<1):
    print("No file found")
else:
    print("file read")

# variables
titlepart = "File" # matrixheader cells containing the identifier end with ,asc
titlelist = []
titlelist_short = []
epoch_word = "Epoch"
epoch_list = []

# definitions
def check_file(df):
    print(df.shape)
    if df.shape[1] != number_of_rois:
        print("input matrix has different shape than indicated")
        print("Dimensions are: ", df.shape[1])
        # Check if all columns are collapsed into one column
        if df.shape[1] == 1:
            df_split = df.loc[:, 0].str.split(expand=True)
            print('shape is now:', df_split.shape)
            if df_split.shape[1] == number_of_rois: #when dimensions are correct
                df = df_split
        # Check if the last column contains only NaNs and remove column if it does
        if df.iloc[:, -1].isna().all():
            # Remove the last column
            df = df.iloc[:, :-1]
            print("last row containing NaNs removed")
            print("Dimensions are now: ", df.shape[1])
    else:
        print("matrix dimensions are correct")
    print(df.shape)

    return df

# matrices that are stored as single matrices containing only numbers need a filename that identifies the matrix
# therefore, information from the header of each matrix is extracted and stored for later use in the matrix file names
# first row of the header, second cell, gives the filename of the ascii file of the signal, the second row, second cell
# gives the epoch number of the analysed file 
def storeTitle(df):
    if df.shape[1] != number_of_rois:
        print('dimensions are still not correct')
    
    # if correct dimensions, loop over all rows in the df 
    else: 
        for index, row in df.iterrows():
           #print(index)
            if titlepart in str(row[0]): 
                titlelist.append(row[1])
            if epoch_word in str(row[0]):
                epoch_list.append(row[1]) 
    
        # Select the first 4 letters of each string
        titlelist_short = [string[:4] for string in titlelist]  
        # Combine the lists by row
        filenames = [a + '_' + b for a, b in zip(titlelist_short, epoch_list)]
        print(f"Filenames are: {filenames}")
        return filenames, titlelist_short

def checkType(df):
    # Check the type of the value in the first row and second column (indexing starts from 0)
    cell_value = df.iloc[100, 100]
    print(type(cell_value), cell_value)
    # concluding: cells are strings and
    # cells in column 100 are None in rows 0 and 1, and a value stored as string in row 2, 3, 100 etc

    # Convert columns and coerce errors (invalid strings will be NaN)
    df_numbers = df.apply(pd.to_numeric, errors='coerce')
    return df_numbers 

# split matrices according to the NaN rows in between
def split_and_store(df, filenames):
    # Step 1: Identify rows where any number exists (rows that are not all NaN)
    # This creates a boolean column (valid_row) that is True if any value in that row is a valid number 
    # (not NaN), and False otherwise.
    df['valid_row'] = df.notna().any(axis=1)

    # Step 2: Identify consecutive groups of valid rows
    # Every time a True switches to False or vice versa, a new group is started.
    df['group'] = (df['valid_row'] != df['valid_row'].shift()).cumsum()
   
    # Step 3: Group consecutive rows and save the valid ones to separate files
    # This filters out the NaN rows and groups the valid rows by their group number. 
    # The for loop iterates through each group, drops the helper columns (valid_row, group), 
    # and saves the result to separate CSV files.
    grouped = df[df['valid_row']].groupby('group')

    # check dimensions of titlelist_short and filenames lists
    print('shape titlelist_short: ', len(titlelist_short) )
    print('shape of filenames: ', len(filenames) )

    # Iterate through each group and save the consecutive rows with numbers to separate files
    i = 0
    for idx, group in grouped:
        file_name = filenames[i]
        group2 = group.drop(columns=['valid_row', 'group'])
        group3 = group2.iloc[1:] # leave first row with epoch number out of matrix

        # Directory name
        directory = titlelist_short[i]
        # Create the directory if it doesn't exist
        try:
        # Attempt to create the directory
            os.mkdir(outputpath+directory)
        except FileExistsError:
            # Handle the case where the directory already exists
            print(f"The directory '{outputpath+directory}' already exists.")

        if (group3.iloc[-1] == 0).all(): # save only if group (= individual matrix) is complete, no zero's only in last row
            print('alleen nullen')
        else:
            group3.to_csv(outputpath+directory+'/'+file_name+'_'+titleInfo+'.csv', index=False)
            print(f"Saved {file_name}")
        i = i+1

########### Run code #########################################################################
# check and correct matrix dimensions
df_mymatrix2 = check_file(df_mymatrix)

# make list with names of ascii and epochs to be used as matrix file names
filenameslist, titlelist_short = storeTitle(df_mymatrix2)
df_mymatrix3 = checkType(df_mymatrix2)

# split file with matrices into separate matrices
split_and_store(df_mymatrix3, filenameslist)



