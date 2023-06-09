# import frb_process_config as par
import frb_process_config_23m041 as par
import subprocess
import time
from tabulate import tabulate
import os
import shutil
import glob

"""
Runs entire pipeline from vrad -> filterbank
"""

def vrad_2_cs():
    """
    Conversion from vrad to cs files
    """
    # Hold dict of params
    print("---------------------------------------------")
    print("Converting from vrad to cs")
    print("---------------------------------------------")
    params = {"in": par.indir, "inf": par.inf_file, "sp": par.sp_file, "vrad_dir": par.vrad_dir,
              "vrad_base": par.vrad_base, "out": par.outdir, 
              "freq": par.freq_band, "source": par.source, \
              "tele": par.telescope, "amount": par.data_amount, "dm": par.dm}
    
    cmd = "python3 -u vrad2cs/vrad2cs.py --inf_file %(in)s%(inf)s --sp_file %(in)s%(sp)s" \
           " --vrad_dir %(in)s%(vrad_dir)s --vrad_base %(vrad_base)s --out_dir %(out)s" \
           " --freq_band %(freq)s --dm %(dm)f --source %(source)s --telescope %(tele)s --data_amount %(amount)i" % params
    
    print(cmd)
    subprocess.run(cmd, shell=True)


def cs_2_fil():
    """
    Converts cs to filterbank for all the channel numbers given
    """
    print("---------------------------------------------")
    print("Converting from cs to fil")
    print("---------------------------------------------")
    # Go through each channel number
    params = {"out": par.outdir, "base": par.cs_base, "cs_dir": par.cs_dir, 
                "dada_dir": par.dada_dir, "fil_dir": par.fil_dir, "dm": par.dm}
    
    for num in par.nchans:    
        params["num"] = num
        cmd = "python3 -u cs2fil/cs2fil.py --basename %(base)s --cs_dir %(out)s%(cs_dir)s \
              --dada_dir %(out)s%(dada_dir)s \
              --fil_dir %(out)s%(fil_dir)s --dm %(dm)f --nchan %(num)i" % params
        
        print(cmd)
        subprocess.run(cmd, shell=True)

def combine_pol():
    """
    Combines lcp and rcp files
    """
    print("---------------------------------------------")
    print("Combining polarizations")
    print("---------------------------------------------")
    # Go through each channel number
    params = {"out": par.outdir, "lcp_base": par.lcp_base, "rcp_base": par.rcp_base, 
              "comb_base": par.comb_base, "fil_dir": par.fil_dir, "png_dir": par.png_dir, "ez": par.ez, "dthresh": par.dthresh,
              "nwin": par.nwin}
    
    cmd = "python3 -u combine_pol/combine_pol.py --lcp_base %(lcp_base)s \
            --rcp_base %(rcp_base)s --comb_base %(comb_base)s --fil_dir %(out)s%(fil_dir)s \
            --png_dir %(out)s%(png_dir)s --edgezap %(ez)f --dthresh %(dthresh)f --chanwin %(nwin)i " % params
        
    print(cmd)
    subprocess.run(cmd, shell=True)

def plot_fil():
    """
    Plots filterbank files
    """
    print("---------------------------------------------")
    print("Converting from fil to plot")
    print("---------------------------------------------")
    params = {"out": par.outdir, "offset": par.offset_file, "fil_base": par.fil_base,
        "fil_dir": par.fil_dir, "png_dir": par.png_dir, "npy_dir": par.npy_dir, "dm": par.dm, "tavg": par.tavg, "tdur": par.tdur, "comb_base":par.comb_base}
    
    cmd = "python3 -u plotfil/plotfil.py --off_file %(out)s%(offset)s --fil_dir %(out)s%(fil_dir)s --fil_base %(fil_base)s \
            --comb_base %(comb_base)s --png_dir %(out)s%(png_dir)s --npy_dir %(out)s%(npy_dir)s --dm %(dm)f --tavg %(tavg)f --tdur %(tdur)f" % params
    print(cmd)
    subprocess.run(cmd, shell=True)

def dm_opt():
    """
    Optimizes dm
    """
    print("---------------------------------------------")
    print("Finding optimal dm value")
    print("---------------------------------------------")
    params = {"out_dir": par.outdir, "dm_dir": par.dm_dir, "fil_dir": par.fil_dir, "offset": par.offset_file,
        "dm_lo": par.dm_lo, "dm_hi": par.dm_hi, "dm_step": par.dm_step}
    
    cmd = "python3 -u dm_opt/dm_opt.py --out_dir %(out_dir)s --dm_dir %(dm_dir)s --fil_dir %(fil_dir)s --offsets %(offset)s --dm_lo %(dm_lo)f \
            --dm_hi %(dm_hi)f --dm_step %(dm_step)f" % params
    print(cmd)
    subprocess.run(cmd, shell=True)

def plot_scint():
    """
    Plots scintilation bandwidth
    """
    print("---------------------------------------------")
    print("Plotting Scintilation Bandwidth")
    print("---------------------------------------------")
    params = {
        "out_dir": par.outdir, "npy_dir": par.npy_dir, "png_dir": par.png_dir, "npy_base": par.npy_base, "freq_band": par.freq_band, 
    }

    cmd = "python3 -u plot_scint/plot_scint.py --out_dir %(out_dir)s --npy_dir %(npy_dir)s --png_dir %(png_dir)s --npy_base %(npy_base)s \
            --freq_band %(freq_band)s" % params
    print(cmd)
    subprocess.run(cmd, shell=True)



debug = 0

if __name__ == "__main__":
    if not debug: 
        times = []
        if par.vrad_to_cs:
            st = time.time()
            vrad_2_cs()
            times.append(["vrad->cs", round(time.time()-st, 2)])
        if par.cs_to_fil:
            st = time.time()
            cs_2_fil()
            times.append(["cs->fil", round(time.time()-st, 2)])
        if par.combine_pol:
            st = time.time()
            combine_pol()
            times.append(["Combine polarizations", round(time.time()-st, 2)])
        if par.plot_fil:
            st = time.time()
            plot_fil()
            times.append(["fil->plot", round(time.time()-st, 2)])
        if par.plot_scint:
            st = time.time()
            plot_scint()
            times.append(["scintilation plot", round(time.time()-st, 2)])
        if par.dm_opt:
            st = time.time()
            dm_opt()
            times.append(["dm optimize", round(time.time()-st, 2)])
        total = sum(item[1] for item in times)
        times.append(["total", total])
        print(tabulate(times, headers =['Step','Time (s)'],tablefmt = 'fancy_grid'))
        
        # clean up dada and vdr files
        if par.cleanup:
            dada_path = "%s%s" % (par.outdir, par.dada_dir)
            if os.path.exists(dada_path):
                files = glob.glob(dada_path + '/*')
                for file in files:
                    os.remove(file)
            vdr_path = "%s%s" % (par.outdir, par.vdr_dir)
            if os.path.exists(vdr_path):
                files = glob.glob(vdr_path + "/*")
                for file in files:
                    os.remove(file)



