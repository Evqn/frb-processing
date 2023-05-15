import frb_process_config as par
import subprocess

"""
Runs entire pipeline from vrad -> filterbank
"""

def vrad_2_cs():
    """
    Conversion from vrad to cs files
    """
    # Hold dict of params
    params = {"in": par.indir, "inf": par.inf_file, "sp": par.sp_file, "vrad_dir": par.vrad_dir,
              "vrad_base": par.vrad_base, "out": par.outdir, 
              "freq": par.freq_band, "source": par.source, \
              "tele": par.telescope, "amount": par.data_amount}
    
    cmd = "python3 vrad2cs/vrad2cs.py --inf_file %(in)s%(inf)s --sp_file %(in)s%(sp)s" \
           " --vrad_dir %(in)s%(vrad_dir)s --vrad_base %(vrad_base)s --out_dir %(out)s" \
           " --freq_band %(freq)s --source %(source)s --telescope %(tele)s --data_amount %(amount)i" % params
    
    print(cmd)
    subprocess.run(cmd, shell=True)


def cs_2_fil():
    """
    Converts cs to filterbank for all the channel numbers given
    """
    # Go through each channel number
    params = {"out": par.outdir, "base": par.cs_base, "cs_dir": par.cs_dir, 
                "dada_dir": par.dada_dir, "fil_dir": par.fil_dir, "dm": 219.46}
    
    for num in par.nchans:    
        params["num"] = num
        cmd = "python3 cs2fil/cs2fil.py --basename %(base)s --cs_dir %(out)s%(cs_dir)s \
              --dada_dir %(out)s%(dada_dir)s \
              --fil_dir %(out)s%(fil_dir)s --dm %(dm)f --nchan %(num)i" % params
        
        print(cmd)
        subprocess.run(cmd, shell=True)



debug = 0

if __name__ == "__main__":
    if not debug: 
        vrad_2_cs()
        cs_2_fil()