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
vrad_base = "22-295" # first 5 digits identifying telescope reading

freq_band = "s" # set to x or s 
source = "m81" 
telescope = "robledo" 
data_amount = 3 # in seconds

# Inputs for cs2fil conversion
cs_base = "s" # set to x or s if you want same files to be converted
cs_dir = "cs/"
dada_dir = "dada/"
fil_dir = "fil/"
dm = 219.46
nchans = [100]

# Inputs for combine_pol
lcp_base = "slcp"
rcp_base = "srcp"
comb_base = "sbnd"
ez = 0.15 # edge zap
dthresh = 0.25 # Fractional diff threshold
nwin = 5 # window size

# inputs for plotfil
offset_file = "offset_times.txt"
fil_base = "s" # set to x or s if you want same files to be converted
png_dir = "png/"
npy_dir = "npy/"
tavg = 100
tdur = 0.2

# scintilation inputs
npy_base = "s" # set to x or s if you want same files to be converted

# Conversions to run
vrad_to_cs = True
cs_to_fil = True
plot_fil = True
plot_scint = True
combine_pol = True

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