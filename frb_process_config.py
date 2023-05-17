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
vrad_to_cs = False
cs_to_fil = False
plot_fil = False


#Optimizations to run
dm_opt = True

#DM Optimizition
dm_lo = 219.40
dm_hi = 219.50
dm_step = 0.01
dm_dir = "dm/"
fil_file = "/src/out/fil/slcp_p0000-0001_n100.fil"



