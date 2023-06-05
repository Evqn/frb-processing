"""
Parameter file for frb_process.py

All output directories are assumed to be in the outdir
"""


# Input directory
indir = "/src/in/"

# Output directory
outdir = "/out/22m295/"

# Inputs for vrad2cs conversion
inf_file = "slcp-0001_DM219.460.inf"
sp_file = "one.singlepulse"
vrad_dir = "vrad/"
vrad_base = "22-295-001_d63_PSR2_S" # set last char to X or S

freq_band = "s" # set to x or s 
source = "m81" 
telescope = "robledo" 
data_amount = 3

# Inputs for cs2fil conversion
cs_base = "s" # set to x or s
cs_dir = "cs/"
dada_dir = "dada/"
fil_dir = "fil/"
dm = 219.46
nchans = [100]

# inputs for plotfil
offset_file = "offset_times.txt"
png_dir = "png/"
npy_dir = "npy/"
tavg = 100
tdur = 0.2


# Conversions to run
vrad_to_cs = False
cs_to_fil = False
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