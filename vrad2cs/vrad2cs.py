import numpy as np
import os 
import glob
import time
import subprocess
import click
import pandas as pd
from datetime import datetime, timedelta
from astropy.time import Time, TimeDelta
import sigproc as fb
import multiprocessing as mp
import re

srcdir = '/home/evanz/scripts/vrad2cs'

def extract_start_time(inf_file):
    """
    Given inf_file, find MJD time and return it in YY/Day_HH:MM:SS format
    """
    epoch_key = "Epoch of observation (MJD)"
    mjd = None

    with open(inf_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if epoch_key in line:
                _, value = line.split('=', 1)
                mjd = value.strip()
                break

    t = Time(mjd, scale='utc', format='mjd')

    # convert to required format
    input_format = "%Y:%j:%H:%M:%S.%f"
    dt = datetime.strptime(t.yday, input_format)

    # Format the datetime object using strftime
    output_format = "%y/%j_%H:%M:%S"
    formatted_time = dt.strftime(output_format)
    return t, formatted_time


def extract_pulses(sp_file):
    """
    Takes text file of pulses and returns list of time during which pulses occured.

    spfile: single pulse file
    start_time: start time of data file
    """
    pulse_column = 2

    df = pd.read_csv(sp_file, sep=" ")
    times_after_start = df.iloc[:, pulse_column]
    return times_after_start

def convert_times(times_after_start, start_time, record_time):
    """
    Takes pulse times in seconds and adds it to start_time 
    to return new list of times in correct format.
    ***We center the time such that the pulse occurs in the middle.
    Format of start_time is in YY/Day_HH:MM:SS
    """
    format_str = "%y/%j_%H:%M:%S"
    new_times = []

    for time in times_after_start:
        # convert to dt format
        dt = datetime.strptime(start_time, format_str)

        # add time and subtract half the record time to center it
        dt += timedelta(seconds=time)
        dt -= timedelta(seconds=record_time/2)
        new_times.append(dt.strftime(format_str))
    return new_times

def vrad_2_vdr(pulse_times, vrad_file, out_dir, data_amount, srcdir=srcdir):
    """
    Converts raw telescope data (*.vrad) given list of times of pulses to vdr format
    Executes script in format:

    rdef_io -V -f TIME -n 60 INPUT_FILE OUTPUT_FILE

    rdef_loc: location of rdef_io script


    """
    # Create directory to put vdr files in 
    vdr_dir = "%s/vdr" % (out_dir)
    if not os.path.exists(vdr_dir):
        os.makedirs(vdr_dir, exist_ok=True)

    for i, t in enumerate(pulse_times):
        # replace with vdr suffix to create output path + place in vdr folder
        basename = os.path.basename(vrad_file)
        basename = os.path.splitext(basename)[0]

        # zero pad pulse_str
        pulse_str = str(i).zfill(4)
        out_file = "%s/%s_p%s.vdr" % (vdr_dir, basename, pulse_str)


        # wait for process to finish before executing another
        rdef_loc = "%s/rdef_io" %srcdir
        cmd = "%s -V -f %s -n %d %s %s" % (rdef_loc, t, data_amount, 
                                           vrad_file, out_file)
        
        # if file exists already, we don't need to run
        if os.path.isfile(out_file):
            os.remove(out_file)
            # print("File: %s already exists" %out_file)
        else:
            print(cmd)
            subprocess.run(cmd, shell=True)


def vdr_2_cs(vdr_file, out_dir, freq_band, source_name, freq, bw, 
             telescope, srcdir=srcdir):
    """
    Converts *.vdr files to *.cs files
    Executes script in format:

    vsrdump_char_100 {vdr_file} -o {output_file} 
    -name {source_name} -comp -freq {freq} -bw {bw} -{telescope} -vsr
    """
    # Create directory to put cs files in 
    cs_dir = "%s/cs" % (out_dir)
    if not os.path.exists(cs_dir):
        os.makedirs(cs_dir, exist_ok=True)

    # replace with cs suffix to create output path + place in cs folder
    basename = os.path.basename(vdr_file)
    basename = os.path.splitext(basename)[0]
    out_file = "%s/cs/%s-0001-01.cs" % (out_dir, basename)

    if freq_band == "s":
        vsrdump_loc = "%s/vsrdump_char_100" %srcdir
    else: 
        vsrdump_loc = "%s/vsrdump_char" %srcdir 
    cmd = "%s %s -o %s -name %s -comp -freq %.2f -bw %.2f -%s -vsr" \
        % (vsrdump_loc, vdr_file, out_file, source_name, 
           freq, bw, telescope)

    # if file exists already, don't need to run
    if os.path.isfile(out_file):
        os.remove(out_file)
        # print("File: %s already exists" %out_file)
    else:
        print(cmd)
        subprocess.run(cmd, shell=True)

def calculate_offsets(mjd_start, times_after_start, cs_files, out_dir):
    """
    Calculates offset time for each burst.
    Writes offset to txt file for burst plotting
    
    delta_t = t_sp - t_cs
    """
    offsets = [0 for _ in range(len(cs_files))]

    for i, time in enumerate(times_after_start):

        # calculate t_sp by adding pulse time to mjd start time
        dt = TimeDelta(time, format='sec')
        t_sp = mjd_start+dt

        # get cs file time
        hd, hsize, err = fb.read_header(cs_files[i], 4, fb.fmtdict)
        t_cs = Time(hd['tstart'], format='mjd')
        

        # subtract and return value in seconds
        off_set = t_sp-t_cs
        off_set = off_set.to_value('s')

        # Use regex to find the pattern. We are looking for p followed by 4 digits
        match = re.search(r'p(\d{4})', cs_files[i])
        index = -1
        if match:
            # Convert the digit part to an integer
            index = int(match.group(1))
        else:
            print("Pattern not found in filename.")
        offsets[index] = off_set
    offsets = pd.Series(offsets, name="Offset Times")
    print(offsets)
    offsets.to_csv('%soffset_times.txt' % out_dir)
    return offsets



@click.command()
@click.option("--inf_file", type=str, 
              help="Full path of .inf file", required=True)
@click.option("--sp_file", type=str, 
              help="Full path of single pulse file", required=True)
@click.option("--vrad_dir", type=str,
              help="Directory containing vrad files", required=True)
@click.option("--vrad_base", type=str,
              help="Basename of vrad files {vrad_base}*.vrad", required=True)
@click.option("--out_dir", type=str,
              help="Output directory of *.cs and intermediate *.vdr files", required=True)
@click.option("--freq_band", type=str,
              help="Frequency band to process (s/x)", required=True)
@click.option("--source", type=str,
              help="Name of the pulse source", required=True)
@click.option("--telescope", type=str,
              help="Name of telescope", required=True)
@click.option("--data_amount", type=float,
              help="Amount of data to write (in seconds)", required=True)
def vrad_2_cs(inf_file, sp_file, vrad_dir, vrad_base, out_dir, 
              freq_band, source, telescope, data_amount, srcdir=srcdir):
    """
    ***EXAMPLE CALL***
    python3 vrad2cs.py --inf_file /home/evanz/scripts/22m295/data/slcp-0001_DM219.460.inf --sp_file /home/evanz/scripts/22m295/sband/sp_list_merged.singlepulse --vrad_dir /home/evanz/scripts/22m295/data --vrad_base data1 --out_dir /home/evanz/scripts/22m295/data/ --freq_band s --source m81 --telescope robledo --data_amount 1

    Converts sections of *.vrad files into *.cs files around pulse times.

    Pulse times are located in a .singlepulse file. These times are equal to time after start

    Starting time is located in *.inf file. 
    The pulse times will have to be converted by adding the starting time.

    Input *.vrad files are in the form:
    
        {vrad_base}.{band}.vrad 
        Ex: 22-295-001_d63_PSR2_SLCP.vrad

    These *.vrad files will first be converted to *.vdr files and named:

        {out_dir/vdr/{base_name}_p{num}.vdr} 
        Ex: /data/vdr/22-295-001_d63_PSR2_SLCP_p1.vdr

    The *.vdr files will be converted to *.cs files and placed in

        {out_dir/cs/{burst_num}_{base_name}.cs}  
        Ex: /data/cs/22-295-001_d63_PSR2_SLCP_p1.cs

    """
    # dictionary containing freq for every freq band
    freq_dct = {"s": 2250, "x1": 8224, "x2": 8256, "x3": 8288, "x4": 8320}
    bw_dct = {"s": 100, "x": 32}

    # Extract starting time from .inf file
    mjd_start, start_time = extract_start_time(inf_file)
    
    times_after_start = extract_pulses(sp_file)


    # Add list of times to start time
    converted_times = convert_times(times_after_start, start_time, 
                                    data_amount)
    
    # Take each vrad file and convert to vdr
    print("\n\nvrad -> vdr...")
    vrad_infiles = glob.glob("%s/%s*.vrad" % (vrad_dir, vrad_base))

    with mp.Pool() as pool:
        # Create a list of arguments for each call to vrad_2_vdr
        args_list = [(converted_times, vrad_file, out_dir, data_amount, srcdir) for vrad_file in vrad_infiles]

        # Use the pool to map the vrad_2_vdr function to the args_list
        pool.starmap(vrad_2_vdr, args_list)

    # Take vdr files and convert to cs
    print("\n\nvdr -> cs...")
    # We know all vdr files will be contained in vdr directory
    vdr_infiles = glob.glob("%s/vdr/*" % (out_dir))

    # if frequency band is s they will have same frequency
    if freq_band == "s":
        s_freq = freq_dct[freq_band]
        s_bw   = bw_dct[freq_band]
        with mp.Pool() as pool:
            # Create a list of arguments for each call to vdr_2_cs
            args_list = [(vdr_file, out_dir, freq_band, source, s_freq, s_bw, telescope, srcdir) for vdr_file in vdr_infiles]
            # Use the pool to map the vdr_2_cs function to the args_list
            pool.starmap(vdr_2_cs, args_list)

    # we have four different subbands for x band
    elif freq_band == "x":
        for i, vdr_file in enumerate(sorted(vdr_infiles)):
            # subband changes
            subband = "x" + str(i//(len(vdr_infiles)//4)+1)
            x_freq_sb = freq_dct[subband]
            x_bw_sb = bw_dct[freq_band]
            with mp.Pool() as pool:

                # Create a list of arguments for each call to vdr_2_cs
                args_list = [(vdr_file, out_dir, freq_band, source, x_freq_sb, x_bw_sb, telescope, srcdir) for vdr_file in vdr_infiles]

                # Use the pool to map the vdr_2_cs function to the args_list
                pool.starmap(vdr_2_cs, args_list)

    else:
        print("freq_band must be s or x")

    # find cs files to calculate offset times
    cs_infiles = sorted(glob.glob("%s/cs/*" % (out_dir)))
    print(times_after_start)
    print(cs_infiles)
    calculate_offsets(mjd_start, times_after_start, cs_infiles, out_dir)

    return 

debug = 0

if __name__ == "__main__":
    if not debug: 
        vrad_2_cs()
