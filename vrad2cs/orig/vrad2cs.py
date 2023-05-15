import numpy as np
import os 
import glob
import time
import subprocess
import click
import pandas as pd
from datetime import datetime, timedelta
from astropy.time import Time

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
    return formatted_time


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

def vrad_2_vdr(pulse_times, vrad_file, out_dir, data_amount, rdef_loc):
    """
    Converts raw telescope data (*.vrad) given list of times of pulses to vdr format
    Executes script in format:

    rdef_io -V -f TIME -n 60 INPUT_FILE OUTPUT_FILE

    rdef_loc: location of rdef_io script


    """
    # Create directory to put vdr files in 
    vdr_dir = "%svdr" % (out_dir)
    if not os.path.exists(vdr_dir):
        os.mkdir(vdr_dir)

    for i, t in enumerate(pulse_times):
        # replace with vdr suffix to create output path + place in vdr folder
        basename = os.path.basename(vrad_file)
        basename = os.path.splitext(basename)[0]

        out_file = "%s/%s_pulsenum%i.vdr" % (vdr_dir, basename, i)

        # if file exists already, remove it to rewrite
        if os.path.isfile(out_file):
            os.remove(out_file)

        # wait for process to finish before executing another
        cmd = "%s -V -f %s -n %f %s %s" % (rdef_loc, t, data_amount, vrad_file, out_file)
        subprocess.run(cmd, shell=True)

def vdr_2_cs(vdr_file, out_dir, source_name, freq, telescope, vsrdump_loc):
    """
    Converts *.vdr files to *.cs files
    Executes script in format:

    vsrdump_char_100 {vdr_file} -o {output_file} 
    -name {source_name} -comp -freq {freq} -bw 100 -{telescope} -vsr
    """
    # Create directory to put cs files in 
    cs_dir = "%scs" % (out_dir)
    if not os.path.exists(cs_dir):
        os.mkdir(cs_dir)


    # replace with cs suffix to create output path + place in cs folder
    basename = os.path.basename(vdr_file)
    basename = os.path.splitext(basename)[0]
    out_file = "%scs/%s.cs" % (out_dir, basename)

    # if file exists already, remove it to rewrite
    if os.path.isfile(out_file):
        os.remove(out_file)

    cmd = "%s %s -o %s -name %s -comp -freq %f -%s -vsr" \
        % (vsrdump_loc, vdr_file, out_file, source_name, freq, telescope)
    subprocess.run(cmd, shell=True)


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
              freq_band, source, telescope, data_amount):
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

        {out_dir/vdr/{base_name}_pulsenum{num}.vdr} 
        Ex: /data/vdr/22-295-001_d63_PSR2_SLCP_pulsenum1.vdr

    The *.vdr files will be converted to *.cs files and placed in

        {out_dir/cs/{burst_num}_{base_name}.cs}  
        Ex: /data/cs/22-295-001_d63_PSR2_SLCP_pulsenum1.cs

    """
    # dictionary containing freq for every freq band
    freq_dct = {"s": 2250, "x0": 2250, "x1": 2250, "x2": 2250, "x3": 2250}

    # Extract starting time from .inf file
    start_time = extract_start_time(inf_file)
    times_after_start = extract_pulses(sp_file)

    # Add list of times to start time
    converted_times = convert_times(times_after_start, start_time, data_amount)
    
    # Take each vrad file and convert to vdr
    print("vrad -> vdr...")
    vrad_infiles = glob.glob("%s/%s*.vrad" % (vrad_dir, vrad_base))
    for vrad_file in vrad_infiles:
        vrad_2_vdr(converted_times, vrad_file, out_dir, data_amount, "/home/evanz/scripts/22m295/rdef_io")

    # Take vdr files and convert to cs
    print("vdr -> cs...")
    # We know all vdr files will be contained in vdr directory
    vdr_infiles = glob.glob("%s/vdr/*" % (out_dir))

    # if frequency band is s they will have same frequency
    if freq_band == "s":
        for vdr_file in vdr_infiles:
            vdr_2_cs(vdr_file, out_dir, source, 
                    freq_dct[freq_band], telescope, "/home/evanz/scripts/22m295/vsrdump_char_100")
    # we have four different subbands for x band
    else:
        for i, vdr_file in enumerate(sorted(vdr_infiles)):
            subband = "x" + str(i%2)
            vdr_2_cs(vdr_file, out_dir, source, 
            freq_dct[subband], telescope, "/home/evanz/scripts/22m295/vsrdump_char_100")


        

if __name__ == "__main__":
    vrad_2_cs()
