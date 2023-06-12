import click
import multiprocessing as mp
import subprocess
import glob
import os

def zap_combine(lcp_file, rcp_file, png_dir, outbase, ez, dthresh, nwin):
    cmd = "python3 -u combine_pol/zap_combine.py %s %s %s -o %s -ez %f -dthresh %f -nwin %i" % (lcp_file, rcp_file, png_dir, outbase, ez, dthresh, nwin)
    print(cmd)
    subprocess.run(cmd, shell=True)

@click.command()
@click.option("--lcp_base", type=str, 
              help="Basename of lcp files", required=True)
@click.option("--rcp_base", type=str, 
              help="Basename of rcp files", required=True)
@click.option("--comb_base", type=str, 
              help="Basename of combined files", required=True)
@click.option("--fil_dir", type=str, 
              help="Dir of *fil files", required=True)
@click.option("--png_dir", type=str, 
              help="Dir of *png files", required=True)
@click.option('--edgezap',
              help='Fraction of band to zap at edges',
                        required=False, type=float, default=0.15)
@click.option('--dthresh',
                help='Fractional diff threshold for bp flagging',
                required=False, type=float, default=0.25)
@click.option('--chanwin',
                help='Window size for bandpass flagging (chans)',
                required=False, type=int, default=5)
def get_cp_pairs(lcp_base, rcp_base, comb_base, fil_dir, png_dir, edgezap, dthresh, chanwin):
    lcp_files = sorted(glob.glob('%s/%s*fil' % (fil_dir, lcp_base)))
    rcp_files = sorted(glob.glob('%s/%s*fil' % (fil_dir, rcp_base)))

    # replace with new basename
    basename_files = []
    for file in lcp_files:
        basename = os.path.basename(file)
        dirname = os.path.dirname(file) + "/"
        combined_base = dirname + comb_base + basename[len(comb_base):]
        # remove extension
        root, _ = os.path.splitext(combined_base)
        basename_files.append(root)
    
    args = [(lcp, rcp, png_dir, comb, edgezap, dthresh, chanwin) for lcp, rcp, comb in zip(lcp_files, rcp_files, basename_files)]
    with mp.Pool() as pool:
        # Use starmap to pass triplets of arguments to the function
        pool.starmap(zap_combine, args)
    
debug = 0

if __name__ == "__main__":
    if not debug: 
        get_cp_pairs()
    

    


    
