#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 14:57:08 2024

@author: robertsoncl
"""
import pandas as pd
import os
import numpy as np
from topas2numpy import BinnedResult
import matplotlib.pyplot as plt

# combines histogrm files together by looping through chosen directory
# combines all files with chosen similar prefix
# easy to combine incremented topas csvs using this


def combineDosemaps(directory, prefix):
    # get relevant filenames
    files = [filename for filename in os.listdir(
        directory) if filename.startswith(prefix)]
    # create empty array for holding summed dosemaps, of the correct shape
    combinedDosemap = np.zeros(
        np.shape(np.squeeze(BinnedResult(directory+'/'+files[0]).data['Sum'])))
    # loop through the files and sum them all together
    for i in range(len(files)):

        dosemap = np.squeeze(BinnedResult(directory+'/'+files[i]).data['Sum'])
        combinedDosemap = combinedDosemap+dosemap
    # verify improved statistics
    plt.figure()
    plt.imshow(dosemap)

    plt.figure()
    plt.imshow(combinedDosemap)
    # return array
    return combinedDosemap


#combineDosemaps('/home/robertsoncl/SplitFiles', 'DoseAt')
