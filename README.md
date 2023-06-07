# FRB Processing

## Introduction

Fast Radio Bursts (FRBs) are brief, bright pulses of radio emission from distant galaxies. They're one of the universe's most perplexing mysteries, offering intriguing opportunities for investigating the intergalactic medium and cosmology. This project is designed to process raw data (in *.vrad files) associated with these FRBs, execute multiple preprocessing steps, generate detailed plots of bursts and their characteristics, and conduct burst analysis.
## Objective

The primary goal of this project is to convert raw FRB data into a more interpretable and usable formatting, allowing it for detailed analysis and visualization of FRBs.

## Methodology

The project pipeline consists of four main stages:

1. **Vrad to CS**: The project inputs are scan_table (containing start time of observation) and a singlepulse file (containing all the pulses and the offsets from the start observation). Each pulse in the singlepulse file is processed to calculate the observation time and converted into *.cs file format (after passing through an intermediate *.vdr format). The pipeline also manages differences in x-band and s-band files, grouping and assigning frequencies as required.

2. **CS to Filterbank**: The *.cs files are converted into filterbank files, which are more suitable for analysis. For x-band files, aggregation occurs at this stage. The number of channels can be set here, defining the time series for the data.

3. **Plot**: This stage uses the filterbank files to generate detailed plots of the FRBs. The plots present a dynamic spectrum, time-series, and spectrum for each pulse. The pipeline can handle switching between s and x bands and applies time-channel averaging to improve pulse visibility.

4. **Dispersion Measure Optimization**: This stage optimizes the dispersion measure (DM) of the FRBs. By iterating through a range of possible DM values, the optimal DM is identified as the one that maximizes the Signal-to-Noise Ratio (SNR).

## Setup and Usage

1. This project has a modular structure with a master script (frb_process) and several subscripts, each housed in their own subdirectory of the same name. In of the stages described above has a separate script located in its corresponding subdirectory. 
```bash
.
├── frb_process.py
├── vrad2cs/
│   └── vrad2cs.py
├── cs2fil/
│   └── cs2fil.py
├── plotfil/
│   └── plotfil.py
└── dmopt/
    └── dmopt.py
 ```
 
 2. Place the \*.vrad files in their 

Finally, to run the python, run `python3 frb_process.py`. Modify `frb_process_config` to change settings, including:

- Raw *.vrad file locations
- Output file destinations
- DM value
- Number of channels
- Time average
- S-band or X-band frequency processing

Flags can also be set to determine which processing steps to run.

## Results
