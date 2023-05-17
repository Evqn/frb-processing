import numpy as np
import os 
import glob
import time
import subprocess
import click
import pandas as pd
import re
from datetime import datetime, timedelta
from astropy.time import Time, TimeDelta
import sp_spec as sp
import multiprocessing as mp

def read_offsets(offset_file):
    """
    Read in offset
    """
    df = pd.read_csv(offset_file)
    return df["Offset Times"]

def generate_plots(offsets, file, png_dir, dm, tavg, tdur):
    """
    Creates *.png plots of filterbank files
    Takes in offset times to find where to plot
    """
    # Get corresponding offset value by checking which pulse num
    filename = os.path.basename(file)

    # Use regex to find the pattern. We are looking for p followed by 4 digits
    match = re.search(r'p(\d{4})', filename)
    index = -1
    if match:
        # Convert the digit part to an integer
        index = int(match.group(1))
    else:
        print("Pattern not found in filename.")
    offset = offsets[index]

    basename = os.path.splitext(filename)[0]
    # plot using sp_spec
    sp.make_plot('%s' % file, dm, tavg=int(307), tp=None, 
                    tdur=None, outbins=500, outfile="%s%s.png" % (png_dir, basename))


@click.command()
@click.option("--off_file", type=str, 
              help="Full path of offset file", required=True)
@click.option("--fil_dir", type=str, 
              help="Dir of *fil files", required=True)
@click.option("--png_dir", type=str, 
              help="Dir of *png file", required=True)
@click.option("--dm", type=float, 
              help="Disperion Measure", required=True)
@click.option("--tavg", type=float, 
              help="Average time", required=True)
@click.option("--tdur", type=float, 
              help="Duration of pulse", required=True)
def plotfil(off_file, fil_dir, png_dir, dm, tavg, tdur):
    """
    Creates plot of filterbank files.

    Takes in filterbank directory and plots burst given an offset value for each file.
    """
    offsets = read_offsets(off_file)
    fil_files = glob.glob('%s/*fil' % (fil_dir))
    with mp.Pool() as pool:
        # Create a list of arguments for each call to process_file
        args_list = [(offsets, file, png_dir, dm, tavg, tdur) for file in fil_files]

        # Use the pool to map the process_file function to the args_list
        pool.starmap(generate_plots, args_list)


debug = 0

if __name__ == "__main__":
    if not debug: 
        plotfil()


