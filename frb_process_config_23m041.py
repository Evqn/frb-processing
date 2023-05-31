"""
Parameter file for frb_process.py
"""


# Input directory
indir = "/src/in/"

# Output directory
outdir = "/out/23m041/"

# Inputs for vrad2cs conversion
inf_file = "scan.table.23m041"
sp_file = "one.singlepulse"
vrad_dir = "vrad/"
vrad_base = "23" # set last char to X or S

freq_band = "x" # set to x or s 
source = "j1810" 
telescope = "robledo" 
data_amount = 3

# Inputs for cs2fil conversion
cs_base = "x" # set to x or s
cs_dir = "cs/"
dada_dir = "dada/"
fil_dir = "fil/"
dm = 178.85
nchans = [8]

# inputs for plotfil
offset_file = "offset_times.txt"
png_dir = "png/"
npy_dir = "npy/"
tavg = 100
tdur = 0.2


# Conversions to run
vrad_to_cs = True
cs_to_fil = True
plot_fil = True

# Optimizations to run
dm_opt = False

# DM Optimizition
dm_lo = 0
dm_hi = 400
dm_step = 20
dm_dir = "dm/"

# Cleanup (remove dada and vdr files)
cleanup = True
vdr_dir = "vdr/"