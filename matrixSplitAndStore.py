import bct
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as pyplot
import glob
import os

# code for processing matrices from BrainWave which is a file with varying number of 
# matrices consisting of three rows of texts of NaNs followed by number of rows
# corresponding to the number of rois from the atlas used.
# the code checks dimensions, removes columns and rows that contain NaNs
# and stores all separate matrices into different files containing part of the filename and an epochnumber

############### INSERT fixed variables #####################################################################

# insert fixed part
baseFileName = "AECcTheta_" # to indicate the fixed filename

# Read the CSV file into a DataFrame, no header 
df_mymatrix = pd.read_csv('/Users/ilsevanstraaten/Documents/research/MNEandBCT/BWmatrices/myMatrixAECcTheta141_143 kopie.csv', delimiter=';', header = None)

# indicate matrix dimensions
number_of_rois = 246 # adjust according atlas used, default BMA

# indicate how many characters of the filename to be included in the matrixnames
number_of_title_letters = 4 # default 4

##############################################################################################

outputpath = ('/Users/ilsevanstraaten/Documents/research/MNEandBCT/BWmatrices/output/')
# check file
if (len(df_mymatrix)<1):
    print("No file found")
else:
    print("file read")

# variables
titlepart = ".asc" # matrixheader cells containing the identifier end with ,asc
titlelist = []
epoch_word = "Epoch"
epoch_list = []

# definitions
def check_file(df):
    if df.shape[1] != number_of_rois:
        print("input matrix has different shape than indicated")
        # Check if the last column contains only NaNs
        if df.iloc[:, -1].isna().all():
            # Remove the last column
            df = df.iloc[:, :-1]
            print("last row containing NaNs removed")
            print("Dimensions are now: ", df.shape[1])
    else:
        print("matrix dimensions are correct")
    return df

def split_and_store(df, base_filename):
    # Identify rows containing any NaN
    nan_indices = df[df.isna().any(axis=1)].index.tolist()

    # store matrix names, containing file and epochnumber
    df.applymap(store_matrixtitles)
    store_epochnumber(df)
    # Combine the lists
    filenames = [a + '_' + b for a, b in zip(titlelist, epoch_list)]
    print(f"Filenames are: {filenames}")

    # Initialize start index
    start_idx = 0
    counter = 0 # for looping over filenames list
    # Split and save chunks
    for i, nan_idx in enumerate(nan_indices):
        # Extract chunk
        chunk = df.iloc[start_idx:nan_idx]
        
        # If chunk is not empty, save it to a file
        if not chunk.empty:
            #filename = f"{base_filename}_part{i + 1}.csv"
            filename = f"{base_filename}_{filenames[counter]}.csv"
            chunk.to_csv(outputpath+filename, index=False)
            print(f"Saved {filename}")
            counter = counter +1
        
        # Update start index to the row after the current NaN row
        start_idx = nan_idx + 1

    # Handle the last chunk if there are rows after the last NaN row
    chunk = df.iloc[start_idx:]
    if not chunk.empty:
        #filename = f"{base_filename}_part{len(nan_indices) + 1}.csv"
        filename = f"{base_filename}_{filenames[counter]}.csv"
        chunk.to_csv(outputpath+filename, index=False)
        print(f"Saved {filename}")

    # Remove rows with NaNs
    df_cleaned = df.dropna()
    return df_cleaned

def store_matrixtitles(cell):
    if titlepart in str(cell):
        titlelist.append(cell)
    # Modify each entry to contain only the first characters
    for i in range(len(titlelist)):
        titlelist[i] = titlelist[i][:number_of_title_letters] 

def store_epochnumber(df):
    # Iterate through the DataFrame
    for index, row in df.iterrows():
        for col in range(df.shape[1] - 1):  # Exclude the last column as there is no next cell
            if epoch_word in str(row[col]):
                epoch_list.append(row[col + 1])

########### Run code #########################################################################
# check and correct matrix dimensions
df_mymatrix = check_file(df_mymatrix)

# split file with matrices into separate matrices
df_cleaned = split_and_store(df_mymatrix, baseFileName)
print(df_cleaned)
print(f"Matrix dimensions: {df_cleaned.shape}")



