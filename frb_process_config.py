"""
Parameter file for frb_process.py
"""


# Input directory
indir = "/src/in/"

# Output directory
outdir = "/src/out/"

# Inputs for vrad2cs conversion
inf_file = "slcp-0001_DM219.460.inf"
sp_file = "one.singlepulse"
vrad_dir = "vrad/"
vrad_base = "s"

freq_band = "s" 
source = "m81" 
telescope = "robledo" 
data_amount = 3

# Inputs for cs2fil conversion
cs_base = "slcp"
cs_dir = "cs/"
dada_dir = "dada/"
fil_dir = "fil/"
dm = 219.46
nchans = [100]

# inputs for plotfil
offset_file = "offset_times.txt"
png_dir = "png/"
tavg = 100
tdur = 0.2

# Conversions to run
vrad_to_cs = True
cs_to_fil = True
plot_fil = True



