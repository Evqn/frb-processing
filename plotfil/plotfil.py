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

def read_data(offset_file):
    """
    Read in offset, SNR
    """
    df = pd.read_csv(offset_file)
    return df["Offset Times"], df["SNR"]

def generate_plots(offsets, snrs, file, png_dir, dm, tavg, tdur):
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
    snr = snrs[index]

    basename = os.path.splitext(filename)[0]
    # plot using sp_spec
    sp.make_plot('%s' % file, dm, index, snr, tavg=int(tavg), tp=offset, 
                    tdur=tdur, outbins=1024, outfile="%s%s.png" % (png_dir, basename))

def get_2D_data(offsets, fil_file, npy_dir, dm, tavg, tdur):
    """
    Returns dedispered data before averaging around time and freq channels.
    """
    filename = os.path.basename(fil_file)
    basename = os.path.splitext(filename)[0]
    # Use regex to find the pattern. We are looking for p followed by 4 digits
    match = re.search(r'p(\d{4})', filename)
    index = -1
    if match:
        # Convert the digit part to an integer
        index = int(match.group(1))
    else:
        print("Pattern not found in filename.")

    offset = offsets[index]
    _, _, dout = sp.get_snippet_data(fil_file, dm, favg=0, tavg=0, bpass=True,
                     tp=offset, tdur=tdur)
    np.save(f'{npy_dir}{basename}.npy', dout)
    
    


@click.command()
@click.option("--off_file", type=str, 
              help="Full path of offset file", required=True)
@click.option("--fil_dir", type=str, 
              help="Dir of *fil files", required=True)
@click.option("--png_dir", type=str, 
              help="Dir of *png file", required=True)
@click.option("--npy_dir", type=str,
              help='Dir of *npy file', required=True)
@click.option("--freq_band", type=str,
              help="frequency band (x or s)", required=True)
@click.option("--dm", type=float, 
              help="Disperion Measure", required=True)
@click.option("--tavg", type=float, 
              help="Average time", required=True)
@click.option("--tdur", type=float, 
              help="Duration of pulse", required=True)
def plotfil(off_file, fil_dir, png_dir, npy_dir, freq_band, dm, tavg, tdur):
    """
    Creates plot of filterbank files.

    Takes in filterbank directory and plots burst given an offset value for each file.
    """
    offsets, snrs = read_data(off_file)
    fil_files = glob.glob('%s/%s*fil' % (fil_dir, freq_band))

    with mp.Pool() as pool:
        args_list = [(offsets, fil_file, npy_dir, dm, tavg, tdur) for fil_file in fil_files]
        pool.starmap(get_2D_data, args_list)


    with mp.Pool() as pool:
        args_list = [(offsets, snrs, file, png_dir, dm, tavg, tdur) for file in fil_files]
        pool.starmap(generate_plots, args_list)



debug = 0

if __name__ == "__main__":
    if not debug: 
        plotfil()


